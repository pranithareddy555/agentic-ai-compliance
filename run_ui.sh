#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

export MODE="${MODE:-mock}"

cleanup() {
  if [[ -n "${API_PID:-}" ]]; then kill "$API_PID" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

uvicorn app.main:app --reload &
API_PID=$!

sleep 3
streamlit run streamlit_app.py
