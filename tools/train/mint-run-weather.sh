#!/bin/sh
# Fine-tunes the single model (aligned upscaler + interpolation) of joint-al32x4 with rain and snow
# drawn over a third of the windows (weather.py) and sensor grain on the captured frames of
# another share. Pixels only, lower learning rates, 40,000 iterations. Resumes from latest.pt.
# Iteration 0 scores the starting model on the new validation (with rain and snow) for comparison.
# Log: run-weather.log; output: runs/joint-al32x4-wx.out; pictures: runs/joint-al32x4-wx/samples/.
# Usage: nohup ./mint-run-weather.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: entrenando joint-al32x4-wx $(date +%H:%M)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/joint-al32x4-wx \
      --sr 32,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 40000 --adversarial-from 1000000000 \
      --lr 1e-4 --fi-lr 5e-5 --weather 0.35 --grain 0.3 --workers 18\
      --init runs/joint-al32x4/best-pixels.pt >> runs/joint-al32x4-wx.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en joint-al32x4-wx, ver runs/joint-al32x4-wx.out"
} >> run-weather.log 2>&1
