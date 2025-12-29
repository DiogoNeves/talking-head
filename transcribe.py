#!/usr/bin/env python3
import json
import tempfile
import os
from pathlib import Path
import gc
from typing import Optional, Set

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


def _format_srt_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours, remainder = divmod(total_ms, 3600 * 1000)
    minutes, remainder = divmod(remainder, 60 * 1000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_srt(formatted_result: dict) -> str:
    """Format the transcription result as SRT subtitle content."""
    lines = []
    index = 1
    for segment in formatted_result["segments"]:
        text = segment["text"].strip()
        if not text:
            continue
        start = _format_srt_timestamp(segment["start"])
        end = _format_srt_timestamp(segment["end"])
        lines.append(str(index))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
        index += 1
    if not lines:
        return ""
    return "\n".join(lines).rstrip() + "\n"


def format_plain_text(formatted_result: dict) -> str:
    """Format the transcription result as plain text."""
    text = formatted_result.get("text", "").strip()
    if not text:
        return ""
    return text + "\n"


def parse_output_formats(format_arg: str) -> Set[str]:
    normalized = (format_arg or "").strip().lower()
    if not normalized:
        return set()
    if normalized == "all":
        return {"json", "srt", "text"}
    parts = [part.strip().lower() for part in normalized.split(",") if part.strip()]
    allowed = {"json", "srt", "text"}
    unknown = [part for part in parts if part not in allowed]
    if unknown:
        raise ValueError(f"Unknown format(s): {', '.join(unknown)}. Use all,json,srt,text.")
    return set(parts)


def ensure_output_dir_writable(output_dir: Path) -> None:
    """Ensure the output directory exists and is writable."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Output directory '{output_dir}' is not writable: {e}")

    try:
        with tempfile.NamedTemporaryFile(dir=output_dir, prefix=".write_test_", delete=True) as temp_file:
            temp_file.write(b"")
            temp_file.flush()
    except Exception as e:
        raise RuntimeError(f"Output directory '{output_dir}' is not writable: {e}")


def main(
    video_path: str = typer.Argument(
        help="Path to video file (use '-' for stdin)"
    ),
    output_path: str = typer.Argument(
        help="Path to output directory or base output file"
    ),
    vocabulary: Optional[str] = typer.Option(
        None, "--vocab", "-v",
        help="Path to vocabulary file (one word per line)"
    ),
    format_option: str = typer.Option(
        "all", "--format", "-f",
        help="Output formats: all,json,srt,text (comma-separated). Default: all"
    ),
    srt: bool = typer.Option(
        False, "--srt", hidden=True,
        help="Deprecated. Use --format srt"
    ),
    text: bool = typer.Option(
        False, "--text", hidden=True,
        help="Deprecated. Use --format text"
    )
):
    """Transcribe video using OpenAI Whisper Large with word-level timestamps."""

    source_label = video_path
    try:
        output_formats = parse_output_formats(format_option)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if srt:
        output_formats.add("srt")
    if text:
        output_formats.add("text")
    if not output_formats:
        typer.echo("Error: No output formats selected", err=True)
        raise typer.Exit(1)

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
    
    # Resolve output paths
    output_arg = Path(output_path)
    output_dir = None
    output_path_hint = None

    if output_arg.exists():
        if output_arg.is_dir():
            output_dir = output_arg
        else:
            output_dir = output_arg.parent
            output_path_hint = output_arg
    elif output_arg.suffix:
        output_dir = output_arg.parent
        output_path_hint = output_arg
    else:
        output_dir = output_arg

    ensure_output_dir_writable(output_dir)

    if output_path_hint:
        base_name = output_path_hint.stem or "transcript"
    else:
        if source_label == "-":
            base_name = "transcript"
        else:
            base_name = Path(source_label).stem or "transcript"

    output_base = output_dir / base_name

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
        
        typer.echo("✅ Transcription completed!")
        typer.echo(f"🗣️  Detected language: {result['language']}")
        typer.echo(f"📝 Total segments: {len(result['segments'])}")

        if "json" in output_formats:
            if output_path_hint and output_path_hint.suffix.lower() == ".json":
                output_json_path = output_path_hint
            else:
                output_json_path = output_base.with_suffix(".json")
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(formatted_result, f, indent=2, ensure_ascii=False)
            typer.echo(f"🧾 JSON output saved to {output_json_path}")

        if "srt" in output_formats:
            srt_path = output_base.with_suffix(".srt")
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(format_srt(formatted_result))
            typer.echo(f"💬 SRT output saved to {srt_path}")
        if "text" in output_formats:
            text_path = output_base.with_suffix(".txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(format_plain_text(formatted_result))
            typer.echo(f"📝 Text output saved to {text_path}")
        
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
