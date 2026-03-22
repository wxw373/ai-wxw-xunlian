#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] Python 3.9+ is required. Set PYTHON_BIN or install python3."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "[SETUP] Creating virtual environment..."
  "$PYTHON_BIN" -m venv .venv
fi

echo "[SETUP] Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[SETUP] Created .env from .env.example. Add a real API key before asking questions."
fi

if [ ! -f "vector_db/chroma.sqlite3" ]; then
  echo "[SETUP] Building vector index. The first run may download the embedding model."
  .venv/bin/python main.py --mode index --force
fi

PORT="${PORT:-8501}"
echo "[START] Web app: http://localhost:${PORT}"
.venv/bin/python -m streamlit run web_app.py --server.port "$PORT" --server.address 0.0.0.0
