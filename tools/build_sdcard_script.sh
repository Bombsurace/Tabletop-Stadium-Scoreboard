#!/bin/bash
# Builds deploy/sdcard/Automation_Custom_Script.sh: the setup script (script_head.sh) with a copy of the
# scoreboard software packed underneath it. Run this after changing any code, before making an SD card.
#   bash tools/build_sdcard_script.sh            -> dist/Automation_Custom_Script.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist/Automation_Custom_Script.sh}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

APP="$STAGE/nfl-scoreboard"          # folder name on the board (deploy files expect ~/nfl-scoreboard)
mkdir -p "$APP"
cd "$ROOT"
# only what runs on the board: no 3D files, docs, settings or logo cache
cp -r server.py espn.py events.py demo.py config.py wifi.py requirements.txt README.md static deploy "$APP/"
rm -rf "$APP/deploy/sdcard"
find "$APP" -name '__pycache__' -prune -exec rm -rf {} +

mkdir -p "$(dirname "$OUT")"
{
  cat "$ROOT/deploy/sdcard/script_head.sh"
  tar -C "$STAGE" -cz nfl-scoreboard | base64
} > "$OUT"
chmod +x "$OUT"
# DietPi reads it from a FAT card written on Windows: keep Unix line endings
if grep -q $'\r' "$OUT"; then echo "error: CRLF line endings in $OUT" >&2; exit 1; fi
echo "built $OUT ($(du -h "$OUT" | cut -f1))"
