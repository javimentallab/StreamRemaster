#!/bin/sh
# StreamRemaster HQ, for powerful graphics cards, trained from scratch: an upscaler of 64 channels
# and 4 blocks (26,740 weights, about three times the built-in one), aligned with the previous frame,
# and the same motion network (32x64), with a critic of our own from scratch from iteration 40,000.
#  1. REDS at 120 fps comes down again (val part 0 and train parts 0-3) while the game clips are
#     recorded at 2560x1440 and packed at 1280x720, as in mint-run-codec.sh;
#  2. the frames out of time are marked with a phase judge made from the installed model's motion
#     network (phase_judge.py), since the old judge was deleted;
#  3. joint.py trains 120,000 iterations: real codecs on 60 % of the windows, rain and snow, effects,
#     some sensor grain. The pixel phase keeps best-pixels.pt; from the critic on, it.pt every 10,000.
# Every step is done once and resumes where it stopped (done-ss/<map>, data/orig/.<part>.done,
# latest.pt). Log: run-hq.log; output: runs/hq64x4.out; pictures: runs/hq64x4/samples/.
# Usage: nohup ./mint-run-hq.sh &
cd "$(dirname "$0")" || exit 1
TRAIN_MAPS="afterslime atelier boil bromine catharsis courtfun dance darkzone erbium finalrage fuse geoplanetary go
implosion leave_em_behind opium runningman silentsiege solarium space-elevator techassault trident vorix warfare xoylent"
VAL_MAPS="stormkeep glowplant"
JUDGE=runs/juez-fases-fx.pt
mkdir -p games/raw-ss games/done-ss data
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
  echo "ESTADO: empieza $(date +%H:%M); $(df -h . | tail -1)"
  [ -e "$JUDGE" ] || .venv/bin/python phase_judge.py runs/joint-al32x4-fx/best-pixels.pt "$JUDGE" || exit 1
  # Xonotic 0.8.6 (GPL), checked against its published sha512, unzipped into games/Xonotic
  if [ ! -x games/Xonotic/xonotic-linux64-sdl ]; then
    echo "ESTADO: instalando Xonotic 0.8.6 $(date +%H:%M)"
    curl -fL --retry 10 -C - --limit-rate 10M -o games/xonotic-0.8.6.zip https://dl.xonotic.org/xonotic-0.8.6.zip || exit 1
    # the published file lists every download of the release: take the line of this one
    want=$(curl -sfL https://dl.xonotic.org/xonotic-0.8.6.sha512 | grep -E " \*?xonotic-0\.8\.6\.zip$" | cut -c1-128)
    got=$(sha512sum games/xonotic-0.8.6.zip | cut -d" " -f1)
    [ -n "$want" ] && [ "$got" = "$want" ] || { echo "ESTADO: Xonotic con sha512 distinto"; exit 1; }
    unzip -q -o games/xonotic-0.8.6.zip -d games && rm games/xonotic-0.8.6.zip || exit 1
    echo "ESTADO: Xonotic instalado $(date +%H:%M)"
  fi
  # REDS: download and pack in the background (the line is shared: 5 MB/s)
  ( ./fetch_reds120.sh data val_orig_part0 train_orig_part0 train_orig_part1 train_orig_part2 train_orig_part3 \
      && nice -n 10 .venv/bin/python pack120.py data && echo "ESTADO: REDS listo $(date +%H:%M)" \
      || echo "ESTADO: fallo con REDS" ) > fetch-hq.log 2>&1 &
  FETCHER=$!
  for map in $VAL_MAPS; do record "$map" games-ss-val 2; done
  for map in $TRAIN_MAPS; do record "$map" games-ss 3; done
  [ -n "${PACKER:-}" ] && wait "$PACKER"
  echo "ESTADO: juegos listos $(date +%H:%M); esperando a REDS"
  wait "$FETCHER"
  grep "ESTADO" fetch-hq.log | tail -1
  grep -q "REDS listo" fetch-hq.log || exit 1
  echo "ESTADO: clips $(ls data/packed120/games-ss/*.npy | grep -vcE 'cuts|phase|offtime') de juego, $(ls data/packed120/train/*.npy | grep -vcE 'cuts|phase|offtime') de REDS; $(df -h . | tail -1)"
  echo "ESTADO: entrenando hq64x4 $(date +%H:%M)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/hq64x4 \
      --sr 64,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 120000 --adversarial-from 40000 \
      --adversarial 0.005 --critic-images 8 --critic-crop 128 \
      --weather 0.2 --grain 0.15 --effects 0.25 --codec 0.6 \
      --games-dirs games-ss --val-games games-ss-val --workers 20 >> runs/hq64x4.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en hq64x4, ver runs/hq64x4.out"
} >> run-hq.log 2>&1
