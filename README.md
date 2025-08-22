# Video Transcriber

Simple Python script that uses OpenAI Whisper Large to transcribe videos with detailed word-level timestamps.

## Requirements

- Python 3.8-3.11
- FFmpeg (must be installed system-wide)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure FFmpeg is installed:
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

## Usage

```bash
python transcribe.py <video_file> <output_file> [vocabulary_file]
```

Examples:
```bash
# Basic transcription
python transcribe.py my_video.mp4 transcript.json

# With custom vocabulary
python transcribe.py my_video.mp4 transcript.json vocab.txt
```

### Custom Vocabulary

You can provide a custom vocabulary file to improve recognition of specific terms:
- Create a text file with one word per line
- Include technical terms, names, or domain-specific words
- The vocabulary helps guide the model's transcription

Example vocabulary file (`vocab.txt`):
```
Claude
Anthropic
AI
machine learning
neural network
```

## Output Format

The script generates a JSON file with:
- Full transcript text
- Detected language
- Segments with timestamps
- Word-level timestamps with confidence scores

## Features

- Uses Whisper Large v3 for high accuracy
- Memory efficient processing
- Detailed word-level timestamps
- Automatic audio extraction from video
- Clean temporary file handling
- Custom vocabulary support for improved accuracy

## Notes

- First run will download the Whisper Large model (~3GB)
- Requires ~10GB GPU memory for optimal performance
- Works with any video format supported by FFmpeg