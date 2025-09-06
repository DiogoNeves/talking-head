# Transcribe

Lightweight CLI to extract audio with FFmpeg, transcribe with OpenAI Whisper, and export a clean JSON transcript (segments + word timestamps). Includes a static `viewer.html` to inspect results and extract topics via LM Studio.

## Prerequisites

- Python 3.8–3.11
- FFmpeg installed system-wide (e.g., `brew install ffmpeg`, `sudo apt install ffmpeg`)
- Optional: LM Studio running at `http://localhost:1234` for topic extraction in the viewer

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

Open `viewer.html` in a browser and drop the source video and the generated JSON to:
- Navigate segments and word-level timestamps
- (Optional) Extract topics via LM Studio at `http://localhost:1234`

## Notes

- First run downloads the Whisper model; subsequent runs use the cache
- No API keys required for the CLI

## Project Structure

- `transcribe.py`: CLI (FFmpeg audio extraction, Whisper transcription, JSON formatting)
- `viewer.html`: Static transcript viewer + LM Studio topic extraction
- `requirements.txt`: Runtime dependencies

## License

License will be provided separately.
