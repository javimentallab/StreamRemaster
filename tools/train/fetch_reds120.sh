#!/bin/bash
# Downloads part of REDS at 120 fps (CC BY 4.0, Seungjun Nah's own mirror on Hugging Face), checks
# every file against its LFS sha256 and unpacks it into data/orig/<split>/<clip>/*.png.
# Usage: fetch_reds120.sh <data dir> <part>...   e.g. train_orig_part0 val_orig_part0
# The rate is capped: the line is shared.
set -euo pipefail
DATA=$1; shift
BASE=https://huggingface.co/datasets/snah/REDS_orig/resolve/main
mkdir -p "$DATA/zips" "$DATA/orig"
for part in "$@"; do
  zip="$DATA/zips/$part.zip"
  want=$(curl -sf --max-time 30 "https://huggingface.co/api/datasets/snah/REDS_orig/paths-info/main" \
    -d "paths=$part.zip" | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['lfs']['oid'])")
  if [ -f "$DATA/orig/.$part.done" ]; then echo "$part already unpacked"; continue; fi
  echo "$(date +%T) downloading $part"
  curl -fL --retry 20 --retry-delay 30 -C - --limit-rate 5M -o "$zip" "$BASE/$part.zip"
  got=$(sha256sum "$zip" | cut -d' ' -f1)
  if [ "$got" != "$want" ]; then echo "$part: sha256 mismatch ($got)"; exit 1; fi
  echo "$(date +%T) unpacking $part"
  split=${part%%_orig*}
  mkdir -p "$DATA/orig/$split"
  unzip -q -o "$zip" -d "$DATA/orig/$split.tmp"
  # The zips hold <split>/<split>_orig/<clip>/; keep only <clip>/.
  find "$DATA/orig/$split.tmp" -mindepth 1 -maxdepth 3 -type d -regex '.*/[0-9][0-9][0-9]' -exec mv -t "$DATA/orig/$split" {} +
  rm -rf "$DATA/orig/$split.tmp" "$zip"
  touch "$DATA/orig/.$part.done"
  echo "$(date +%T) $part done: $(ls "$DATA/orig/$split" | wc -l) clips in $split"
done
echo finished
