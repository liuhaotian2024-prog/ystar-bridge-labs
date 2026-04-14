#!/bin/bash
# v10 FINAL composite — ffmpeg-only fix on v9 raw HeyGen output
# No new HeyGen spend. Chromakey removes residual green inside Sofia's scene,
# crops out green+white padding bars (v9's bg_size_too_small root cause),
# scales Sofia's terrace to full 1280x720 (bg 全幅), overlays AI-generated
# dusk terrace UNDER keyed-out holes (fills any residual green spots with dusk),
# then lower-third on top.
V10=/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v10
V9=/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v9
ffmpeg -y \
  -i "$V9/raw_heygen_v9.mp4" \
  -i "$V10/terrace_bg_v10.png" \
  -i "$V10/overlay_lower_third.png" \
  -filter_complex "\
[0:v]crop=1280:540:0:145,chromakey=0x2aff11:0.10:0.02,scale=1280:720:flags=lanczos[keyed];\
[1:v][keyed]overlay=0:0:format=auto[bg_composited];\
[bg_composited][2:v]overlay=0:0:format=auto[out]" \
  -map "[out]" -map "0:a" \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  "$V10/episode_001_FINAL_60s_v10.mp4"
