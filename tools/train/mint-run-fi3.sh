#!/bin/sh
# 1. Finishes runs/fi32x64 (it stopped at iteration 100000 when the old interp.py took the new
#    .phase.npy side files for clips), on the same data as before: --ignore-offtime.
# 2. Trains runs/fi32x64-sync on windows whose frames are evenly spaced in time: time_phase.py has
#    marked the game frames that are not (<clip>.offtime.npy, read by interp.py as cuts).
# Each step resumes from its latest.pt. Log: run-fi3.log. Usage: nohup ./mint-run-fi3.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: terminando fi32x64 $(date +%H:%M)"
  nice -n 19 .venv/bin/python interp.py --data data --run runs/fi32x64 --shape 32,64,2,2,4,1 --ignore-offtime >> runs/fi32x64.out 2>&1 \
    || { echo "ESTADO: fallo en fi32x64, ver runs/fi32x64.out"; exit 1; }
  missing=$(for c in data/packed120/games/*.npy data/packed120/games-val/*.npy; do
    case $c in *.cuts.npy|*.offtime.npy|*.phase.npy) continue ;; esac
    [ -e "${c%.npy}.offtime.npy" ] || echo "$c"
  done)
  [ -z "$missing" ] || { echo "ESTADO: faltan fases en: $missing"; exit 1; }
  echo "ESTADO: entrenando fi32x64-sync $(date +%H:%M)"
  nice -n 19 .venv/bin/python interp.py --data data --run runs/fi32x64-sync --shape 32,64,2,2,4,1 > runs/fi32x64-sync.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en fi32x64-sync, ver runs/fi32x64-sync.out"
} >> run-fi3.log 2>&1
