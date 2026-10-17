#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
printf '\nセットアップ完了。次のコマンドで開始できます:\n'
printf '  .venv/bin/python server.py\n'
