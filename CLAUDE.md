# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A video transcription tool using OpenAI Whisper (large-v3 model) with word-level timestamps. Includes a CLI for batch processing and a web viewer for interactive transcript navigation with optional LLM-powered topic extraction.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# CLI transcription
python transcribe.py input.mp4 output.json --vocab vocab.txt

# Run viewer with backend (preferred)
bash run.sh
# Frontend: http://localhost:8080/viewer.html
# Backend:  http://localhost:8000

# Manual run (alternative)
python -m http.server 8080 &
python server.py
```

## Architecture

**CLI (`transcribe.py`)**:
- Uses FFmpeg to extract 16kHz mono WAV audio from video
- Loads Whisper large-v3 model for transcription with word timestamps
- Outputs JSON with `text`, `language`, `segments[].{id, start, end, text, words[]}`
- Uses the repository `vocab.txt` to bias recognition via initial prompt

**API Server (`server.py`)**:
- Flask server with CORS enabled on port 8000
- Single endpoint `POST /api/transcribe` accepting multipart form with `media` file
- Reuses core functions from `transcribe.py` (`extract_audio`, `transcribe_audio`, `format_output`)

**Viewer (`viewer.html`)**:
- Static HTML with drag-drop for video and transcript JSON
- Segment/word navigation with video sync
- Optional topic extraction via LM Studio API at `http://localhost:1234`
- In-browser transcription button that calls the local Flask API

## Dependencies

- FFmpeg must be installed system-wide (`brew install ffmpeg` or `apt install ffmpeg`)
- Python 3.8-3.11
- LM Studio (optional) for topic extraction in viewer

## Code Style

- Python: PEP 8, 4-space indentation, type hints
- CLI messages via `typer.echo`
- Functions: `snake_case`, single responsibility
