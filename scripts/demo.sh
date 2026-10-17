#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-.venv/bin/python}"
"$PY" server.py --max-messages 2 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 0.4
"$PY" client.py --message 'こんにちは'
"$PY" client.py --message 'おすすめの名前を教えて'
wait "$SERVER_PID"
trap - EXIT
