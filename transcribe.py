#!/usr/bin/env python3
import sys
import json
import tempfile
import os
from pathlib import Path
import gc

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


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python transcribe.py <video_file> <output_file> [vocabulary_file]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2]
    vocab_path = sys.argv[3] if len(sys.argv) == 4 else None
    
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found")
        sys.exit(1)
    
    # Create temporary audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
    
    try:
        # Extract audio from video
        print(f"Extracting audio from {video_path}...")
        extract_audio(video_path, temp_audio_path)
        
        # Load custom vocabulary if provided
        vocabulary = load_vocabulary(vocab_path)
        
        # Transcribe audio
        result = transcribe_audio(temp_audio_path, vocabulary)
        
        # Format output
        formatted_result = format_output(result)
        
        # Save to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_result, f, indent=2, ensure_ascii=False)
        
        print(f"Transcription completed! Output saved to {output_path}")
        print(f"Detected language: {result['language']}")
        print(f"Total segments: {len(result['segments'])}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)


if __name__ == "__main__":
    main()