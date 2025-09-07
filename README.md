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

Serve the viewer over HTTP to avoid cross‑origin errors when loading local files:

```bash
# from the project root
python -m http.server 8000
# then open
open http://localhost:8000/viewer.html  # macOS
# or: xdg-open http://localhost:8000/viewer.html
```

In the page, drop the source video and the generated JSON to:
- Navigate segments and word-level timestamps
- (Optional) Extract topics via LM Studio at `http://localhost:1234`

### Optional: Transcribe from the Viewer

You can transcribe directly from the browser via a tiny local API:

1) Start the API server (once, in a separate terminal):

```bash
source .venv/bin/activate
python server.py   # runs at http://localhost:8000
```

2) In `viewer.html`, load a video in the left panel. In the Transcript panel, click the “Transcribe” button (under the drop zone). The page uploads the video to `http://localhost:8000/api/transcribe` and displays the transcript when done.

Notes:
- Requires FFmpeg installed and available on PATH.
- Uses the same Whisper pipeline as the CLI (Large‑v3, word timestamps).
- CORS is enabled for local use; do not expose the server publicly.

## Notes

- First run downloads the Whisper model; subsequent runs use the cache
- No API keys required for the CLI

## Project Structure

- `transcribe.py`: CLI (FFmpeg audio extraction, Whisper transcription, JSON formatting)
- `viewer.html`: Static transcript viewer + LM Studio topic extraction
- `requirements.txt`: Runtime dependencies

## License

License will be provided separately.
