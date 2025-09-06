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
