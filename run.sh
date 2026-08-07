#!/usr/bin/env bash
# Run the project truck finder. Safe to call from cron.
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
source .venv/bin/activate
python main.py --no-browser >> "$DIR/output/finder.log" 2>&1
