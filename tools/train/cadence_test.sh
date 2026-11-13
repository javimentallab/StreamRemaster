#!/bin/sh
# Plays back a recorded demo with -capturedemo at a small size and measures the frame cadence, to
# find the playback settings that give evenly spaced frames. Its own user dir, so the real captures
# are not touched.
#
# Usage: [W=1280 H=720] cadence_test.sh <demo name without .dem> <label> "<extra console commands>"
set -eu
DEMO=$1; LABEL=$2; EXTRA=${3:-}
BASE=$(cd "$(dirname "$0")" && pwd)
GAME=${GAME:-$BASE/games/Xonotic}
USERDIR=${USERDIR:-$BASE/games/xon-test}
mkdir -p "$USERDIR/data/video" "$BASE/games/cadence"
rm -f "$USERDIR"/data/video/*.avi
[ -f "$USERDIR/data/$DEMO.dem" ] || cp "$BASE/games/xon-user/data/$DEMO.dem" "$USERDIR/data/"
export DISPLAY=${DISPLAY:-:0} XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority}
cat > "$USERDIR/data/sr-test.cfg" <<EOF
vid_fullscreen 0; vid_width ${W:-320}; vid_height ${H:-180}; vid_vsync 0; vid_samples 1
menu_sounds 0; volume 0; bgmvolume 0
cl_allow_uid2name 0; cl_allow_uidtracking 0; cl_welcome 0; _cl_name Camera; _menu_initialized 1
cl_capturevideo_fps 120; cl_capturevideo_nameformat sr_; cl_capturevideo_ogg 0
togglemenu 0
$EXTRA
EOF
cd "$GAME"
nice -n 10 timeout 900 ./xonotic-linux64-sdl -nosound -userdir "$USERDIR" \
  +exec sr-test.cfg +defer 0.2 "togglemenu 0" +defer 1 "togglemenu 0" -capturedemo "$DEMO" \
  >"$BASE/games/cadence/$LABEL.log" 2>&1 || true
found=$(ls "$USERDIR"/data/video/*.avi 2>/dev/null | head -1)
[ -n "$found" ] || { echo "$LABEL: no video, see games/cadence/$LABEL.log"; exit 1; }
"$BASE/.venv/bin/python" "$BASE/cadence_avi.py" "$found" "$LABEL"
mv "$found" "$BASE/games/cadence/$LABEL.avi"
