#!/bin/sh
# StreamRemaster trained again FROM SCRATCH, without the fault of the first one: 80 % of the windows
# are degraded like a real stream (realistic.py: blur, a resize, a little noise and two compressions,
# the second one a video codec), so the upscaler learns to clean the compression before it adds
# detail instead of sharpening the blocks. Same size as the built-in model (upscaler 32x4 aligned,
# motion 32x64), pixels only (the critic gave no detail at this size, 12-nov).
# Waits for mint-run-hq.sh to have the data ready (its training is stopped by cancel-hq.sh), then
# trains 100,000 iterations. Validation adds the kinds <source>_real.
# Log: run-real.log; output: runs/real32x4.out; pictures: runs/real32x4/samples/.
# Usage: nohup ./mint-run-real.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: esperando los datos $(date +%H:%M)"
  until grep -qE "ESTADO: (fallo en hq64x4|terminado|fallo con REDS)|Xonotic con" run-hq.log 2>/dev/null; do sleep 60; done
  grep -q "REDS listo" fetch-hq.log || { echo "ESTADO: fallo, REDS no está listo"; exit 1; }
  pgrep -f "runs/hq64x4" > /dev/null && { echo "ESTADO: fallo, el HQ sigue en marcha"; exit 1; }
  echo "ESTADO: entrenando real32x4 $(date +%H:%M); $(df -h . | tail -1)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/real32x4 \
      --sr 32,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 100000 --adversarial-from 1000000000 \
      --real 0.8 --codec 0.75 --weather 0.2 --effects 0.25 --grain 0.1 \
      --games-dirs games-ss --val-games games-ss-val --workers 20 >> runs/real32x4.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en real32x4, ver runs/real32x4.out"
} >> run-real.log 2>&1
