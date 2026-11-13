#!/bin/sh
# Records the game clips (xonotic_capture.sh + pack_game.py), then trains the larger frame
# interpolation network on REDS + games + stream layers. Each map is done once (games/done/<map>),
# so running it again carries on where it stopped; interp.py resumes from latest.pt.
# Log: run-fi2.log. Usage: nohup ./mint-run-fi2.sh &
cd "$(dirname "$0")" || exit 1
TRAIN_MAPS="afterslime atelier boil bromine catharsis courtfun dance darkzone erbium finalrage fuse geoplanetary go
implosion leave_em_behind opium runningman silentsiege solarium space-elevator techassault trident vorix warfare xoylent"
VAL_MAPS="stormkeep glowplant"
mkdir -p games/raw games/done
n=0
record() {  # map, set, clips to keep
  [ -e "games/done/$1" ] && return 0
  n=$((n + 1))
  rm -f games/raw/*.avi
  chase=0; [ $((n % 3)) -eq 0 ] && chase=1
  bots=$(shuf -i 5-10 -n 1); skill=$(shuf -i 5-10 -n 1)
  echo "ESTADO: grabando $1 ($2, bots $bots, nivel $skill, tercera persona $chase) $(date +%H:%M)"
  # bots think on every server frame (0.001, below the 1/120 s frame, so rounding never skips
  # one): with the default (0.05 scaled by skill) they aim at ~30 Hz and the camera, which
  # follows their aim, jumps every 4th frame at 120 fps
  CHASE=$chase PLAY_EXTRA="bot_ai_thinkinterval 0.001" ./xonotic_capture.sh "$1" 30 games/raw "$bots" "$skill" 6 || return 0
  nice -n 10 .venv/bin/python cadence_avi.py games/raw/*.avi "cadencia $1" | head -1
  nice -n 10 .venv/bin/python pack_game.py games/raw/*.avi data --set "$2" --keep "$3" --delete && touch "games/done/$1"
}
{
  for map in $VAL_MAPS; do record "$map" games-val 2; done
  for map in $TRAIN_MAPS; do record "$map" games 3; done
  echo "ESTADO: clips $(ls data/packed120/games/*.npy | grep -vc cuts) de entrenamiento y $(ls data/packed120/games-val/*.npy | grep -vc cuts) de validación; $(df -h . | tail -1)"
  echo "ESTADO: entrenando fi32x64 $(date +%H:%M)"
  nice -n 19 .venv/bin/python interp.py --data data --run runs/fi32x64 --shape 32,64,2,2,4,1 > runs/fi32x64.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en el entrenamiento, ver runs/fi32x64.out"
} >> run-fi2.log 2>&1
