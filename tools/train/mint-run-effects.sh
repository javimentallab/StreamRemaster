#!/bin/sh
# Second fine-tuning round: game effects and moving vegetation (effects.py) over a third of the
# windows, keeping some rain and snow so they are not forgotten. Waits for the rain and snow round
# (mint-run-weather.sh) to finish and starts from its best model; does nothing if that round failed.
# 40,000 iterations, pixels only. Resumes from latest.pt.
# Log: run-effects.log; output: runs/joint-al32x4-fx.out; pictures: runs/joint-al32x4-fx/samples/.
# Usage: nohup ./mint-run-effects.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: esperando a que acabe joint-al32x4-wx $(date +%H:%M)"
  until grep -qE "terminado|fallo" run-weather.log 2>/dev/null; do sleep 60; done
  if grep -q "fallo" run-weather.log; then echo "ESTADO: no arranco, la tanda de lluvia fallo"; exit 1; fi
  echo "ESTADO: entrenando joint-al32x4-fx $(date +%H:%M)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/joint-al32x4-fx \
      --sr 32,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 40000 --adversarial-from 1000000000 \
      --lr 1e-4 --fi-lr 5e-5 --weather 0.2 --grain 0.3 --effects 0.35 --workers 18 \
      --init runs/joint-al32x4-wx/best-pixels.pt >> runs/joint-al32x4-fx.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en joint-al32x4-fx, ver runs/joint-al32x4-fx.out"
} >> run-effects.log 2>&1
