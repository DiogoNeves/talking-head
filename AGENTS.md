# Repository Guidelines

## Project Structure & Module Organization
- `transcribe.py`: Main CLI tool (audio extraction with FFmpeg, transcription with Whisper, JSON formatting).
- `requirements.txt`: Python dependencies for the CLI (no dev extras).
- `viewer.html`: Static viewer to inspect generated transcripts and extract topics via LM Studio.
- `README.md`: Usage overview and examples.
- No package layout or test directory yet; keep modules small and cohesive inside `transcribe.py` unless growth warrants a `src/` package.

## Build, Test, and Development Commands
- Create venv and install deps:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  ```
- Ensure FFmpeg is installed (e.g., `brew install ffmpeg`).
- Transcribe locally:
  ```bash
  python transcribe.py input.mp4 output/transcript.json
  python transcribe.py - output.json --vocab vocab.txt < input.mp4
  ```
- Inspect results: open `viewer.html` in a browser, then drop the video and the generated JSON.

## Coding Style & Naming Conventions
- Python 3.8–3.11, PEP 8, 4‑space indentation; use type hints (`typing`) and concise docstrings.
- Functions: single responsibility, pure where practical; avoid global state.
- Naming: `snake_case` for functions/vars, `lowercase_with_underscores.py` for modules.
- CLI messages via `typer.echo`; keep `print` for non‑user debug only. Avoid adding heavy deps.

## Testing Guidelines
- Current: manual verification. Run the CLI on a short sample and confirm JSON fields: `text`, `language`, `segments[].{id,start,end,text,words[]}`.
- Use `viewer.html` to validate timestamps and navigation.
- If adding automated tests, prefer `pytest` with small audio fixtures; mock `whisper` and `ffmpeg` for unit tests. Name tests `tests/test_*.py`.

## Commit & Pull Request Guidelines
- Commits: imperative, present tense, concise (<72 chars). Example: `Add LLM-powered segment analysis`.
- PRs: clear description, rationale, testing steps (commands), sample JSON snippet; include screenshots/GIFs for `viewer.html` changes; link issues.

## Security & Configuration Tips
- Do not commit media, model files, or large outputs (already ignored). Keep secrets out of code; no API keys are required for the CLI.
- LM Studio usage in `viewer.html` defaults to `http://localhost:1234`; document any local changes in PRs.
