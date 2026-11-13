#!/bin/sh
# Records Xonotic bot matches as uncompressed 120 fps video for the frame interpolation data.
#
# Two passes, because the listen server always runs on the wall clock:
#  1. a bot match is played in real time while the client, as a spectator following a bot in first
#     person and switching to the next one every few seconds, records a demo, with the server
#     sending 120 updates per second;
#  2. the demo is played back with -capturedemo, which steps the clock by exactly 1/120 s per
#     rendered frame and writes every frame to an uncompressed AVI, however slow the GPU is.
# pack_game.py then cuts the video at the camera switches.
#
# Xonotic (GPL; its maps and art are GPL or CC BY-SA) is unzipped in $GAME. Runs on the X display
# of the Mint (the dummy screen), without sound.
#
# Usage: xonotic_capture.sh <map> <seconds> <out dir> [bots] [skill] [seconds per camera]
set -eu
MAP=$1; LENGTH=$2; OUT=$3; BOTS=${4:-8}; SKILL=${5:-8}; EVERY=${6:-6}
BASE=$(cd "$(dirname "$0")" && pwd)
GAME=${GAME:-$BASE/games/Xonotic}
# optional: USERDIR (another user dir, for tests), VID ("<width> <height>"), PLAY_EXTRA (more
# console commands for the match)
USERDIR=${USERDIR:-$BASE/games/xon-user}
set -- ${VID:-1280 720}
VID_W=$1; VID_H=$2
mkdir -p "$USERDIR/data/video" "$OUT"
OUT=$(cd "$OUT" && pwd)
rm -f "$USERDIR"/data/video/*.avi "$USERDIR"/data/srdemo*.dem
export DISPLAY=${DISPLAY:-:0} XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority}

cat > "$USERDIR/data/sr-common.cfg" <<EOF
vid_fullscreen 0; vid_width $VID_W; vid_height $VID_H; vid_vsync 0; vid_samples 1
menu_sounds 0; volume 0; bgmvolume 0
cl_allow_uid2name 0; cl_allow_uidtracking 0; cl_welcome 0; _cl_name Camera; _menu_initialized 1
g_playerstats_gamereport_uri ""; g_playerstats_playerbasic_uri ""; g_playerstats_playerdetail_uri ""
EOF
cat > "$USERDIR/data/sr-play.cfg" <<EOF
exec sr-common.cfg
bot_number $BOTS; skill $SKILL; sys_ticrate 0.0083333333
cl_autodemo 1; cl_autodemo_nameformat srdemo; cl_autodemo_delete 0
timelimit_override 0; fraglimit_override 0; g_warmup 0
${PLAY_EXTRA:-}
alias sr_next "+attack; wait; wait; -attack"
EOF
# defer counts real seconds: join as a spectator, follow a bot, switch bots, stop, quit. The demo
# starts by itself on connecting (cl_autodemo), so it begins with a few still seconds that
# pack_game.py drops.
START=20
printf 'alias sr_go "spectate; defer 2 sr_next"\n' >> "$USERDIR/data/sr-play.cfg"
DEFERS="+defer $START sr_go"
t=$((START + 3 + EVERY))
while [ $t -lt $((START + 3 + LENGTH)) ]; do
  DEFERS="$DEFERS +defer $t sr_next"
  t=$((t + EVERY))
done
END=$((START + 3 + LENGTH))
cd "$GAME"
# shellcheck disable=SC2086
nice -n 10 timeout $((END + 120)) ./xonotic-linux64-sdl -nosound -userdir "$USERDIR" \
  +exec sr-play.cfg +map "$MAP" $DEFERS +defer $END stop +defer $((END + 2)) quit >"$OUT/$MAP-play.log" 2>&1 || true
[ -s "$USERDIR/data/srdemo_$MAP.dem" ] || { echo "no demo recorded, see $OUT/$MAP-play.log"; exit 1; }

cat > "$USERDIR/data/sr-capture.cfg" <<EOF
exec sr-common.cfg
cl_capturevideo_fps 120; cl_capturevideo_nameformat sr_; cl_capturevideo_ogg 0; cl_capturevideo_printfps 10
chase_active ${CHASE:-0}
togglemenu 0
EOF
nice -n 10 timeout $((LENGTH * 10 + 300)) ./xonotic-linux64-sdl -nosound -userdir "$USERDIR" \
  +exec sr-capture.cfg +defer 0.2 "togglemenu 0" +defer 1 "togglemenu 0" -capturedemo "srdemo_$MAP" >"$OUT/$MAP-capture.log" 2>&1 || true
found=$(ls "$USERDIR"/data/video/*.avi 2>/dev/null | head -1)
[ -n "$found" ] || { echo "no video recorded, see $OUT/$MAP-capture.log"; exit 1; }
name="$MAP-$(date +%m%d-%H%M%S)"
mv "$found" "$OUT/$name.avi"
echo "recorded $OUT/$name.avi"
