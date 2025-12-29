# Transcribe

A simple tool to transcribe, analyse and make simple edits for talking head videos.  
I created this because I needed to for a video, no roadmap yet.

<img width="1939" height="1373" alt="aad10251bc9a9cf2b25ab1028cc8a877" src="https://github.com/user-attachments/assets/ab6fcc7e-382f-4c1d-8f5e-6332a5ca379c" />

## Prerequisites

- Python 3.8–3.11
- FFmpeg installed system-wide (e.g., `brew install ffmpeg`, `sudo apt install ffmpeg`)
- LM Studio (or any other local OpenAI compatible api) running at `http://localhost:1234` for topic extraction in the viewer

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python transcribe.py INPUT_VIDEO OUTPUT_JSON [OPTIONS]
```

Examples

```bash
# Basic transcription
python transcribe.py input.mp4 output/transcript.json

# From stdin with custom vocabulary
python transcribe.py - output.json --vocab vocab.txt < input.mp4
```

Options

- `--vocab,-v PATH`: Plain text file with one term per line to bias recognition

## Output JSON

Top-level fields

- `text`: Full transcript
- `language`: Detected language (code)
- `segments[]`: Array of `{ id, start, end, text, words[] }`
- `words[]`: Array of `{ word, start, end, probability }`

## Viewer

There are two ways to run the viewer.

1) Quick start (recommended)

```bash
# From the project root
bash run.sh
# Frontend: http://localhost:8080/viewer.html
# Backend:  http://localhost:8000 (API for in‑browser transcription)
```

In the page, drop your source video and the generated transcript JSON to:
- Navigate segments and word-level timestamps
- (Optional) Extract topics via LM Studio at `http://localhost:1234`

The Transcript panel also shows a “Transcribe” button when a video is loaded; clicking it uploads the video to `http://localhost:8000/api/transcribe` and displays the results.

2) Manual run

```bash
# Serve the static viewer
python -m http.server 8080
# In another terminal, run the local API (for in‑browser transcription)
source .venv/bin/activate && python server.py  # http://localhost:8000
```

Notes:
- Requires FFmpeg on PATH for transcription (CLI and server).
- Uses the same Whisper pipeline as the CLI (Large‑v3, word timestamps).
- CORS is enabled for local use; do not expose the server publicly.

## Notes

- First run downloads the Whisper model; subsequent runs use the cache
- No API keys required for the CLI

## Project Structure

- `transcribe.py`: CLI (FFmpeg audio extraction, Whisper transcription, JSON formatting)
- `server.py`: Local Flask API for in-browser transcription (used by `viewer.html`)
- `viewer.html`: Static transcript viewer + in-browser transcription + LM Studio topic extraction
- `run.sh`: Convenience launcher (sets up venv, installs deps, starts viewer + API)
- `requirements.txt`: Runtime dependencies (CLI + local server)

## License

License will be provided separately.
