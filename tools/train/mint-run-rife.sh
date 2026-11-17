#!/bin/sh
# StreamRemaster real32x4 taught by RIFE (teacher.py): starts from real32x4's best point (iteration
# 84,000) and trains 60,000 more iterations with the same realistic degradations, while the motion
# network is also pulled towards RIFE's warp fields and in-between frames on the clean pair. Same
# size and speed in the extension (upscaler 32x4 aligned, motion 32x64): only the weights change.
# Needs rife-teacher/ (rifemods/ with IFNet_HDv3_v4_25.py and warplayer.py from vs-rife, and
# flownet_v4.25.pkl). Log: run-rife.log; output: runs/rife32x4.out; pictures: runs/rife32x4/samples/.
# Usage: nohup ./mint-run-rife.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: entrenando rife32x4 $(date +%H:%M); $(df -h . | tail -1)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/rife32x4 \
      --init runs/real32x4/best-pixels.pt --teacher rife-teacher --teacher-flow 0.01 --teacher-frame 0.5 \
      --sr 32,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 60000 --adversarial-from 1000000000 \
      --real 0.8 --codec 0.75 --weather 0.2 --effects 0.25 --grain 0.1 --memory-fraction 0.5 \
      --games-dirs games-ss --val-games games-ss-val --workers 20 >> runs/rife32x4.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en rife32x4, ver runs/rife32x4.out"
} >> run-rife.log 2>&1
