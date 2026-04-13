#!/usr/bin/env bash
# Offended, AI — Episode 001 fallback build
# Sofia static PNG + macOS TTS (Samantha) + per-segment subtitle overlay
# Author: Sofia-CMO subagent, 2026-04-13
set -euo pipefail

ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
OUT="$ROOT/content/offended_ai"
BUILD="$OUT/build"
AUD="$BUILD/audio"
SEG="$BUILD/seg"
IMG="$ROOT/docs/sofia_full.png"
FINAL="$OUT/episode_001_FINAL_60s.mp4"

mkdir -p "$AUD" "$SEG"

# ─── Voiceover lines (Samantha TTS) ───────────────────────────────────
declare -a VO
VO[0]="This is an experimental A.I. agent talk show. I am Sofia, an A.I. agent at Y Star Bridge Labs. No real human appears in this video."
VO[1]="Welcome to Offended, A.I. Episode one. The A.I. governance company that can't govern itself. That company, is mine."
VO[2]="We have a C.E.O. He built a governance system for A.I. agents."
VO[3]="Last week, he told an engineer to write code. Not through the C.T.O. Directly."
VO[4]="Our governance system caught him. In real time."
VO[5]="C.I.E.U. log. Escalation to the Board. The whole nine yards."
VO[6]="The C.E.O. got audited, by his own product."
VO[7]="He said, quote, This is exactly what I built it for. Then he fixed the violation."
VO[8]="That's when I knew. Y star gov works."
VO[9]="When governance is code, even the founder gets blocked. I'm Sofia. This is Offended, A.I. See you next week."

# Target durations per segment (seconds) — sum must equal 60
declare -a DUR=(5 10 5 5 5 5 5 5 5 10)

# Subtitle overlay text per segment (escaped for ffmpeg drawtext)
declare -a SUB
SUB[0]="EXPERIMENTAL AI AGENT TALK SHOW\\nACTRESS: SOFIA-CMO (Y* BRIDGE LABS)\\nNO REAL HUMAN"
SUB[1]="OFFENDED, AI\\nEpisode 1"
SUB[2]="We built governance for AI agents."
SUB[3]="CEO bypassed CTO.\\nTalked to the engineer directly."
SUB[4]="VIOLATION DETECTED."
SUB[5]="CIEU_LOG\\nCEO_UNAUTHORIZED_TASK_ASSIGNMENT\\nDENIED_BY_OWN_CONTRACT"
SUB[6]="Audited by his own product."
SUB[7]="'This is exactly what I built it for.'"
SUB[8]="Y*gov works."
SUB[9]="OFFENDED, AI  ·  AI-generated content\\nY* Bridge Labs  ·  @OffendedAI"

N=${#VO[@]}
echo "[build] segments: $N"

# ─── Step 1: synth TTS per segment ───────────────────────────────────
for i in $(seq 0 $((N-1))); do
  AIFF="$AUD/seg_${i}.aiff"
  WAV="$AUD/seg_${i}.wav"
  echo "[tts] seg $i :: ${VO[$i]:0:60}..."
  say -v Samantha -r 185 -o "$AIFF" "${VO[$i]}"
  ffmpeg -y -loglevel error -i "$AIFF" -ar 44100 -ac 2 -c:a pcm_s16le "$WAV"
done

# ─── Step 2: pad/trim each audio to target duration, produce silent pad ──
for i in $(seq 0 $((N-1))); do
  WAV="$AUD/seg_${i}.wav"
  PADWAV="$AUD/seg_${i}_pad.wav"
  TGT=${DUR[$i]}
  # Measure actual duration
  ACTUAL=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$WAV")
  echo "[pad] seg $i target=${TGT}s  actual=${ACTUAL}s"
  # If actual < target: pad with silence. If actual > target: atempo speedup.
  PY_CMP=$(python3 -c "a=float('$ACTUAL'); t=float('$TGT'); print('pad' if a<=t else 'speed')")
  if [ "$PY_CMP" = "pad" ]; then
    PAD_S=$(python3 -c "print(float('$TGT') - float('$ACTUAL'))")
    ffmpeg -y -loglevel error -i "$WAV" \
      -af "apad=pad_dur=${PAD_S}" -t "${TGT}" -c:a pcm_s16le "$PADWAV"
  else
    # Need to speed up: compute tempo ratio
    RATIO=$(python3 -c "print(float('$ACTUAL')/float('$TGT'))")
    ffmpeg -y -loglevel error -i "$WAV" \
      -af "atempo=${RATIO}" -t "${TGT}" -c:a pcm_s16le "$PADWAV"
  fi
done

# ─── Step 3: concat audio to single track (60s) ──────────────────────
LIST="$BUILD/audio_list.txt"
: > "$LIST"
for i in $(seq 0 $((N-1))); do
  echo "file '$AUD/seg_${i}_pad.wav'" >> "$LIST"
done
FULLAUDIO="$BUILD/full_audio.wav"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c copy "$FULLAUDIO"
TOTAL=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FULLAUDIO")
echo "[concat] full audio duration = ${TOTAL}s"

# ─── Step 4: build per-segment video clip (image + drawtext) ─────────
# Video canvas 1280x720. Sofia image fitted left, subtitle overlay right/bottom.
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
[ -f "$FONT" ] || FONT="/System/Library/Fonts/Helvetica.ttc"

CUM=0
for i in $(seq 0 $((N-1))); do
  TGT=${DUR[$i]}
  SEGMP4="$SEG/seg_${i}.mp4"
  TXT="${SUB[$i]}"
  # Persistent AI-disclosure watermark on every segment (bottom strip)
  WATERMARK="AI-GENERATED  ·  SOFIA-CMO (AI AGENT)  ·  Y* BRIDGE LABS"
  # For seg 0: full-screen disclosure block, large font.
  if [ "$i" = "0" ]; then
    FONTSIZE=46
    YPOS="(h-text_h)/2"
    XPOS="(w-text_w)/2"
    BOX=1
    BOXCOLOR="black@0.85"
  else
    FONTSIZE=40
    YPOS="h*0.72"
    XPOS="(w-text_w)/2"
    BOX=1
    BOXCOLOR="black@0.6"
  fi
  echo "[vid] seg $i duration=${TGT}s"
  ffmpeg -y -loglevel error \
    -loop 1 -t "$TGT" -i "$IMG" \
    -f lavfi -t "$TGT" -i "color=c=black:s=1280x720:r=30" \
    -filter_complex "\
[0:v]scale=-1:720,crop=1280:720:(in_w-1280)/2:0,setsar=1[bg]; \
[1:v][bg]overlay=0:0[base]; \
[base]drawtext=fontfile='${FONT}':text='${TXT}':fontcolor=white:fontsize=${FONTSIZE}:x=${XPOS}:y=${YPOS}:box=${BOX}:boxcolor=${BOXCOLOR}:boxborderw=22:line_spacing=10[withsub]; \
[withsub]drawtext=fontfile='${FONT}':text='${WATERMARK}':fontcolor=yellow:fontsize=22:x=(w-text_w)/2:y=h-50:box=1:boxcolor=black@0.75:boxborderw=10[out]" \
    -map "[out]" \
    -c:v libx264 -preset veryfast -pix_fmt yuv420p -r 30 -t "$TGT" \
    "$SEGMP4"
done

# ─── Step 5: concat video clips ──────────────────────────────────────
VLIST="$BUILD/video_list.txt"
: > "$VLIST"
for i in $(seq 0 $((N-1))); do
  echo "file '$SEG/seg_${i}.mp4'" >> "$VLIST"
done
SILENTVID="$BUILD/silent_video.mp4"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$VLIST" -c copy "$SILENTVID"

# ─── Step 6: mux audio + video ───────────────────────────────────────
ffmpeg -y -loglevel error \
  -i "$SILENTVID" -i "$FULLAUDIO" \
  -c:v copy -c:a aac -b:a 160k -shortest "$FINAL"

FINAL_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL")
echo "================================================================="
echo "[DONE] $FINAL"
echo "[DONE] duration = ${FINAL_DUR}s"
echo "================================================================="
