#!/bin/sh
# Trains the aligned upscaler (32 channels, 4 blocks, fed with the previous upscaled frame moved
# onto the current one) together with the interpolation network, which starts from the pixel phase
# of joint32x4. Pixels only (no critic), windows of 4 captured frames. Resumes from latest.pt.
# Log: run-aligned.log; output: runs/joint-al32x4.out; pictures: runs/joint-al32x4/samples/.
# Usage: nohup ./mint-run-aligned.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: entrenando joint-al32x4 $(date +%H:%M)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/joint-al32x4 \
      --sr 32,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 60000 --adversarial-from 1000000000 \
      --init-fi runs/joint32x4/best-pixels.pt >> runs/joint-al32x4.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en joint-al32x4, ver runs/joint-al32x4.out"
} >> run-aligned.log 2>&1
