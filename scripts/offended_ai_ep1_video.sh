#!/usr/bin/env bash
# Video stage v2 — uses PNG overlays (subtitles pre-rendered by PIL).
set -euo pipefail

ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
OUT="$ROOT/content/offended_ai"
BUILD="$OUT/build"
AUD="$BUILD/audio"
SEG="$BUILD/seg"
SUBPNG="$BUILD/subpng"
IMG="$ROOT/docs/sofia_full.png"
FINAL="$OUT/episode_001_FINAL_60s.mp4"

mkdir -p "$SEG"

declare -a DUR=(5 10 5 5 5 5 5 5 5 10)
N=10

for i in $(seq 0 $((N-1))); do
  TGT=${DUR[$i]}
  SEGMP4="$SEG/seg_${i}.mp4"
  SUB="$SUBPNG/sub_${i}.png"
  echo "[vid] seg $i duration=${TGT}s"
  # bg: black canvas 1280x720, fill with Sofia scaled to fit height 720 centered,
  # then overlay subtitle PNG (already 1280x720 RGBA).
  ffmpeg -y -loglevel error \
    -f lavfi -t "$TGT" -i "color=c=black:s=1280x720:r=30" \
    -loop 1 -t "$TGT" -i "$IMG" \
    -loop 1 -t "$TGT" -i "$SUB" \
    -filter_complex "[1:v]scale=-1:720,setsar=1[sofia];[0:v][sofia]overlay=(W-w)/2:0[base];[base][2:v]overlay=0:0,format=yuv420p[out]" \
    -map "[out]" -c:v libx264 -preset veryfast -r 30 -t "$TGT" \
    "$SEGMP4"
done

VLIST="$BUILD/video_list.txt"
: > "$VLIST"
for i in $(seq 0 $((N-1))); do
  echo "file '$SEG/seg_${i}.mp4'" >> "$VLIST"
done
SILENTVID="$BUILD/silent_video.mp4"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$VLIST" -c copy "$SILENTVID"

FULLAUDIO="$BUILD/full_audio.wav"
ffmpeg -y -loglevel error -i "$SILENTVID" -i "$FULLAUDIO" \
  -c:v copy -c:a aac -b:a 160k -shortest "$FINAL"

FINAL_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL")
echo "================================================================="
echo "[DONE] $FINAL"
echo "[DONE] duration=${FINAL_DUR}s"
echo "================================================================="
