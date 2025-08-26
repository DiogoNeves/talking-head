#!/usr/bin/env python3
import json
import tempfile
import os
from pathlib import Path
import gc
from typing import Optional

import typer
import whisper
import ffmpeg


def extract_audio(video_path, audio_path):
    """Extract audio from video file using FFmpeg."""
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to extract audio: {e}")


def load_vocabulary(vocab_path):
    """Load custom vocabulary from text file."""
    if not vocab_path or not os.path.exists(vocab_path):
        return None
    
    try:
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocabulary = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(vocabulary)} words from vocabulary file")
        return vocabulary
    except Exception as e:
        print(f"Warning: Failed to load vocabulary file: {e}")
        return None


def transcribe_audio(audio_path, vocabulary=None):
    """Transcribe audio using Whisper Large with word timestamps."""
    print("Loading Whisper Large model...")
    model = whisper.load_model("large-v3")
    
    print("Transcribing audio...")
    transcribe_options = {
        "word_timestamps": True,
        "verbose": False
    }
    
    if vocabulary:
        transcribe_options["initial_prompt"] = f"The following words may appear in the audio: {', '.join(vocabulary[:50])}"
    
    result = model.transcribe(audio_path, **transcribe_options)
    
    # Clear model from memory
    del model
    gc.collect()
    
    return result


def format_output(result):
    """Format transcription result for detailed output."""
    output = {
        "text": result["text"].strip(),
        "language": result["language"],
        "segments": []
    }
    
    for segment in result["segments"]:
        segment_data = {
            "id": segment["id"],
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip(),
            "words": []
        }
        
        if "words" in segment:
            for word in segment["words"]:
                segment_data["words"].append({
                    "word": word["word"],
                    "start": word["start"],
                    "end": word["end"],
                    "probability": word.get("probability", 0.0)
                })
        
        output["segments"].append(segment_data)
    
    return output


def main(
    video_path: str = typer.Argument(
        help="Path to video file (use '-' for stdin)"
    ),
    output_path: str = typer.Argument(
        help="Path to output JSON file"
    ),
    vocabulary: Optional[str] = typer.Option(
        None, "--vocab", "-v",
        help="Path to vocabulary file (one word per line)"
    )
):
    """Transcribe video using OpenAI Whisper Large with word-level timestamps."""
    
    # Handle stdin input
    stdin_temp_path = None
    if video_path == "-":
        import shutil
        # Create temporary file for stdin data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_stdin:
            stdin_temp_path = temp_stdin.name
            typer.echo("Reading video data from stdin...")
            shutil.copyfileobj(typer.get_binary_stream('stdin'), temp_stdin)
        video_path = stdin_temp_path
    
    if not os.path.exists(video_path):
        typer.echo(f"Error: Video file '{video_path}' not found", err=True)
        raise typer.Exit(1)
    
    # Create temporary audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
    
    try:
        # Extract audio from video
        typer.echo(f"Extracting audio from {video_path}...")
        extract_audio(video_path, temp_audio_path)
        
        # Load custom vocabulary if provided
        vocab_list = load_vocabulary(vocabulary)
        
        # Transcribe audio
        result = transcribe_audio(temp_audio_path, vocab_list)
        
        # Format output
        formatted_result = format_output(result)
        
        # Save to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_result, f, indent=2, ensure_ascii=False)
        
        typer.echo(f"✅ Transcription completed! Output saved to {output_path}")
        typer.echo(f"🗣️  Detected language: {result['language']}")
        typer.echo(f"📝 Total segments: {len(result['segments'])}")
        
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        # Clean up stdin temporary file if created
        if stdin_temp_path and os.path.exists(stdin_temp_path):
            os.unlink(stdin_temp_path)


if __name__ == "__main__":
    typer.run(main)