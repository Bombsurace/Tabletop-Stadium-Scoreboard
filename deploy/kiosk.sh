#!/bin/bash
# Full-screen browser showing the scoreboard. Started on login to tty1 (see README).
URL="http://localhost:8080/"

# DietPi (and other minimal systems) don't run logind, so set up what cage needs ourselves
export XDG_RUNTIME_DIR="/tmp/runtime-$USER"
mkdir -p "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
export LIBSEAT_BACKEND=seatd

# invisible mouse pointer: cage draws its own cursor, so give it a fully transparent cursor theme
BLANK="$HOME/.icons/blank/cursors"
if [ ! -f "$BLANK/default" ]; then
  mkdir -p "$BLANK"
  python3 - "$BLANK/default" <<'PY'
import struct, sys
# Xcursor file: one 1x1 fully transparent image
img = struct.pack("<9I", 36, 0xFFFD0002, 24, 1, 1, 1, 0, 0, 0) + struct.pack("<I", 0)
hdr = b"Xcur" + struct.pack("<3I", 16, 0x10000, 1) + struct.pack("<3I", 0xFFFD0002, 24, 28)
open(sys.argv[1], "wb").write(hdr + img)
PY
  for n in left_ptr arrow pointer hand1 hand2 text xterm watch wait progress crosshair grabbing grab; do
    ln -sf default "$BLANK/$n"
  done
fi
# cage loads the theme named "default" (it ignores XCURSOR_THEME), so make the blank theme the default too
mkdir -p "$HOME/.icons/default" && ln -sfn "$BLANK" "$HOME/.icons/default/cursors"
export XCURSOR_PATH="$HOME/.icons" XCURSOR_THEME=blank XCURSOR_SIZE=24

# wait for the scoreboard server to come up
for i in $(seq 1 60); do
  curl -s -o /dev/null "$URL" && break
  sleep 1
done

BROWSER=$(command -v chromium || command -v chromium-browser)
exec cage -- "$BROWSER" --kiosk --noerrdialogs --disable-infobars --incognito \
  --disable-translate --disable-features=Translate --check-for-update-interval=31536000 \
  --overscroll-history-navigation=0 --disable-pinch --ozone-platform=wayland "$URL" >/tmp/kiosk.log 2>&1
