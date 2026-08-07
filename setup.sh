#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "=== Project Truck Finder Setup ==="

# Create virtualenv if not present
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "Setup complete."
echo ""
echo "To run now:          source .venv/bin/activate && python main.py"
echo "Scheduled daily:     GitHub Actions (.github/workflows/daily_crawl.yml)"
echo ""
