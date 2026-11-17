#!/bin/sh
# Third fine-tuning round, closer to what a viewer gets:
#  1. the game clips are recorded again at 2560x1440 and reduced to 1280x720 when packed
#     (pack_game.py --size): clean, supersampled targets, without the aliasing and the texture
#     shimmer of a 1:1 render (data/packed120/games-ss and games-ss-val). Each map is packed while
#     the next one records; the frames out of time are marked as before (time_phase.py, ±0.1);
#  2. training compresses 60 % of the windows with a real video codec (streamcodec.py: H.264, AV1,
#     VP9) instead of JPEG, adds a loss on the fine detail (--detail) and has less sensor grain.
# Starts from the installed model (joint-al32x4-fx/best-pixels.pt), 40,000 iterations, pixels only.
# Each map is done once (games/done-ss/<map>), so running it again carries on where it stopped;
# joint.py resumes from latest.pt.
# Log: run-codec.log; output: runs/joint-al32x4-cd.out; pictures: runs/joint-al32x4-cd/samples/.
# Usage: nohup ./mint-run-codec.sh &
cd "$(dirname "$0")" || exit 1
TRAIN_MAPS="afterslime atelier boil bromine catharsis courtfun dance darkzone erbium finalrage fuse geoplanetary go
implosion leave_em_behind opium runningman silentsiege solarium space-elevator techassault trident vorix warfare xoylent"
VAL_MAPS="stormkeep glowplant"
JUDGE=runs/juez-fases-it20000.pt
mkdir -p games/raw-ss games/done-ss
n=0
pack() {  # map, set, clips to keep (runs in the background while the next map records)
  if nice -n 10 .venv/bin/python pack_game.py games/raw-ss/"$1"/*.avi data --set "$2" --keep "$3" --size 1280x720 --delete; then
    clips=$(ls data/packed120/"$2"/"$1"-*.npy 2>/dev/null | grep -vE "cuts|phase|offtime")
    # shellcheck disable=SC2086
    [ -n "$clips" ] && nice -n 10 .venv/bin/python time_phase.py "$JUDGE" $clips --tolerance 0.1 --threads 8 | tail -1
    touch "games/done-ss/$1"
    echo "ESTADO: empaquetado $1 $(date +%H:%M)"
  else
    echo "ESTADO: fallo al empaquetar $1"
  fi
  rm -rf "games/raw-ss/$1"
}
record() {  # map, set, clips to keep
  [ -e "games/done-ss/$1" ] && return 0
  n=$((n + 1))
  rm -rf "games/raw-ss/$1"; mkdir -p "games/raw-ss/$1"
  chase=0; [ $((n % 3)) -eq 0 ] && chase=1
  bots=$(shuf -i 5-10 -n 1); skill=$(shuf -i 5-10 -n 1)
  echo "ESTADO: grabando $1 a 1440p ($2, bots $bots, nivel $skill, tercera persona $chase) $(date +%H:%M)"
  VID="2560 1440" CHASE=$chase PLAY_EXTRA="bot_ai_thinkinterval 0.001" \
    ./xonotic_capture.sh "$1" 20 "games/raw-ss/$1" "$bots" "$skill" 6 || { rm -rf "games/raw-ss/$1"; return 0; }
  # one map packing at a time (each raw recording is ~28 GB)
  [ -n "${PACKER:-}" ] && wait "$PACKER"
  pack "$1" "$2" "$3" &
  PACKER=$!
}
{
  for map in $VAL_MAPS; do record "$map" games-ss-val 2; done
  for map in $TRAIN_MAPS; do record "$map" games-ss 3; done
  [ -n "${PACKER:-}" ] && wait "$PACKER"
  echo "ESTADO: clips $(ls data/packed120/games-ss/*.npy | grep -vcE 'cuts|phase|offtime') de entrenamiento y $(ls data/packed120/games-ss-val/*.npy | grep -vcE 'cuts|phase|offtime') de validación; $(df -h . | tail -1)"
  echo "ESTADO: entrenando joint-al32x4-cd $(date +%H:%M)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/joint-al32x4-cd \
      --sr 32,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 40000 --adversarial-from 1000000000 \
      --lr 1e-4 --fi-lr 5e-5 --weather 0.2 --grain 0.15 --effects 0.25 --codec 0.6 --detail 0.5 \
      --games-dirs games-ss --val-games games-val,games-ss-val --workers 20 \
      --init runs/joint-al32x4-fx/best-pixels.pt >> runs/joint-al32x4-cd.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en joint-al32x4-cd, ver runs/joint-al32x4-cd.out"
} >> run-codec.log 2>&1
