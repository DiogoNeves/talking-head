#!/usr/bin/env python3
"""
Lightweight transcription API to be used by viewer.html.

Endpoints:
- POST /api/transcribe : multipart/form-data with fields:
    - media: video file (required)
    - vocab: optional text with one word per line (optional)

Returns JSON with fields matching transcribe.py output.
"""
from __future__ import annotations

import io
import json
import os
import tempfile
from typing import Optional, List

from flask import Flask, request, jsonify
from flask_cors import CORS

# Reuse the existing implementation
from transcribe import extract_audio, transcribe_audio, format_output, load_vocabulary


app = Flask(__name__)
CORS(app)  # Allow all origins for local usage


@app.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


def _load_vocab_from_text(text: Optional[str]) -> Optional[List[str]]:
    if not text:
        return None
    words = [line.strip() for line in text.splitlines() if line.strip()]
    return words or None


@app.post("/api/transcribe")
def api_transcribe():
    if "media" not in request.files:
        return jsonify({"error": "Missing 'media' file"}), 400

    media = request.files["media"]
    vocab_text = request.form.get("vocab")

    # Save uploaded media to a temporary file
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(media.filename or "upload")[1] or ".mp4", delete=False) as tf:
        media.save(tf)
        temp_video = tf.name

    # Prepare temp audio path
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as ta:
        temp_audio = ta.name

    try:
        extract_audio(temp_video, temp_audio)

        # Merge vocab from text field or ignore
        vocab_list = _load_vocab_from_text(vocab_text)

        result = transcribe_audio(temp_audio, vocab_list)
        formatted = format_output(result)
        return jsonify(formatted)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if os.path.exists(temp_audio):
                os.unlink(temp_audio)
        except Exception:
            pass
        try:
            if os.path.exists(temp_video):
                os.unlink(temp_video)
        except Exception:
            pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
