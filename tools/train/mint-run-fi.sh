#!/bin/bash
# Frame interpolation training on the RTX 2060, unattended: waits for the first REDS 120 fps part,
# packs it, checks the code on the CPU and trains; when the download finishes it packs the rest and
# restarts the training, which resumes from runs/fi24x48/latest.pt (losing at most 2000 iterations).
set -u
BASE="$HOME/streamremaster-train"
RUN=$BASE/runs/fi24x48
cd "$BASE" || exit 1
mkdir -p "$RUN"
TRAIN=(nice -n 19 .venv/bin/python interp.py --data "$BASE/data" --run "$RUN")

until [ -f data/orig/.train_orig_part0.done ] && [ -f data/orig/.val_orig_part0.done ]; do
  grep -q mismatch fetch120.log && { echo "ESTADO: descarga corrupta"; exit 1; }
  sleep 30
done
nice -n 19 .venv/bin/python pack120.py "$BASE/data" || { echo "ESTADO: fallo al empaquetar"; exit 2; }
CUDA_VISIBLE_DEVICES= .venv/bin/python interp.py --smoke || { echo "ESTADO: fallo en smoke"; exit 3; }
echo "ESTADO: entrenando con la parte 0 $(date +%T)"
"${TRAIN[@]}" >> "$RUN/train.out" 2>&1 &
PID=$!

until grep -q '^finished' fetch120.log; do
  grep -q mismatch fetch120.log && { echo "ESTADO: descarga corrupta, sigue con lo que hay"; wait $PID; exit 0; }
  kill -0 $PID 2>/dev/null || { echo "ESTADO: el entrenamiento se paro"; exit 4; }
  sleep 60
done
nice -n 19 .venv/bin/python pack120.py "$BASE/data" || { echo "ESTADO: fallo al empaquetar el resto"; wait $PID; exit 0; }
kill $PID; wait $PID 2>/dev/null
echo "ESTADO: entrenando con todo $(date +%T)"
exec "${TRAIN[@]}" >> "$RUN/train.out" 2>&1
