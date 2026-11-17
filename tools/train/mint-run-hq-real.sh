#!/bin/sh
# StreamRemaster HQ, for powerful graphics cards: the upscaler grows to 64x4 (aligned, almost three
# times the weights of the built-in 32x4), trained from scratch with the realistic stream recipe
# (realistic.py) and pixels only, since sharpness from the critic needs capacity first. The motion
# network starts from rife32x4 (the built-in one, taught by RIFE) and keeps learning with RIFE as
# teacher, so the in-between frames do not fall behind.
# Log: run-hq-real.log; output: runs/hq64x4-real.out; pictures: runs/hq64x4-real/samples/.
# Resumes from latest.pt on its own. Usage: nohup ./mint-run-hq-real.sh &
cd "$(dirname "$0")" || exit 1
{
  echo "ESTADO: entrenando hq64x4-real $(date +%H:%M); $(df -h . | tail -1)"
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nice -n 19 .venv/bin/python joint.py --data data --run runs/hq64x4-real \
      --init-fi runs/rife32x4/best-pixels.pt --teacher rife-teacher --teacher-flow 0.01 --teacher-frame 0.5 \
      --sr 64,4 --fi 32,64,2,2,4,1 --aligned --keys 4 --iterations 60000 --adversarial-from 1000000000 \
      --real 0.8 --codec 0.75 --weather 0.2 --effects 0.25 --grain 0.1 --memory-fraction 0.5 \
      --games-dirs games-ss --val-games games-ss-val --workers 20 >> runs/hq64x4-real.out 2>&1 \
    && echo "ESTADO: terminado $(date +%H:%M)" || echo "ESTADO: fallo en hq64x4-real, ver runs/hq64x4-real.out"
} >> run-hq-real.log 2>&1
