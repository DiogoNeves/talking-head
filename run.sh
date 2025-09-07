#!/usr/bin/env bash
set -euo pipefail

# Minimal launcher: sets up venv, installs deps, starts backend and static server.
# Frontend:  http://localhost:8080/viewer.html
# Backend:   http://localhost:8000 (server.py)

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "[run.sh] Ensuring virtualenv..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "[run.sh] Installing dependencies..."
pip install -r "$PROJECT_DIR/requirements.txt" >/dev/null

# Check ffmpeg availability (warn only)
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[run.sh] Warning: ffmpeg not found on PATH. Transcription will fail until installed." >&2
fi

# Start backend (Flask) and static server
echo "[run.sh] Starting backend on http://localhost:8000 ..."
python "$PROJECT_DIR/server.py" &
BACK_PID=$!

echo "[run.sh] Starting static server on http://localhost:8080 ..."
python -m http.server 8080 --directory "$PROJECT_DIR" &
HTTP_PID=$!

cleanup() {
  echo "\n[run.sh] Stopping servers..."
  kill $BACK_PID $HTTP_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

URL="http://localhost:8080/viewer.html"
echo "[run.sh] Open $URL in your browser."

# Try to open the browser (best-effort)
if command -v open >/dev/null 2>&1; then
  open "$URL" || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" || true
fi

echo "[run.sh] Press Ctrl+C to stop."
wait

