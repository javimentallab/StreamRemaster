#!/bin/sh
# Trains upscaling (32 channels, 4 blocks) and frame interpolation (32/64) together in
# runs/joint32x4: 40000 iterations on pixels, then 60000 more with the patch critic. The motion
# network starts from runs/fi32x64-sync/best.pt (our own run). Resumes from runs/joint32x4/latest.pt.
# Log: run-joint.log; training output: runs/joint32x4.out; pictures: runs/joint32x4/samples/.
# Usage: nohup ./mint-run-joint.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: entrenando joint32x4 $(date +%H:%M)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/joint32x4 --sr 32,4 --fi 32,64,2,2,4,1 \
      --init-fi runs/fi32x64-sync/best.pt >> runs/joint32x4.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en joint32x4, ver runs/joint32x4.out"
} >> run-joint.log 2>&1
