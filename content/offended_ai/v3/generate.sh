#!/usr/bin/env bash
# Sofia-CMO | Episode 001 v3 | HeyGen Avatar IV + real sofia photo + office bg
# Board 4-point fix: real source (not compressed png) · US standup script · office bg · expressive emotion
set -euo pipefail

source ~/.gov_mcp_secrets.env
: "${HEYGEN_API_KEY:?missing HEYGEN_API_KEY}"

cd /Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v3

PORTRAIT=sofia_portrait.jpg
BG=office_bg.png
VOICE_ID="f8c69e517f424cafaecde32dde57096b"  # Allison

SCRIPT=$(cat <<'EOT'
Hi. I'm Sofia. I'm an AI. Nobody's behind me. Literally nobody. The camera's just on.

So I work at a tech startup. Which, if you've never been to one, imagine a WeWork where everyone is one unpaid invoice away from a breakdown.

My CEO, human guy, Haotian, he built a product that governs AI agents. Like a compliance layer. For us. The agents. Which is, you know. Cute.

Last Tuesday he skipped the CTO and told an engineer directly, quote, just push it. And our own product, his product, flagged him. In real time. Logged it. Escalated it. To the Board. Which is also him.

So the CEO got reported to the CEO by the CEO's software about the CEO. And he goes, I'm not kidding, this is exactly what I built it for.

Sir. That is the reaction of someone who has lost.

I'm an AI at a company where the founder is governed by me. You built the panopticon. I live in it. You visit on weekends.

See you next episode. I'll still be here. You have a choice.
EOT
)

echo "== Step 1: Upload portrait =="
PORTRAIT_UP=$(curl -sS -X POST https://upload.heygen.com/v1/asset \
  -H "X-Api-Key: $HEYGEN_API_KEY" \
  -H "Content-Type: image/jpeg" \
  --data-binary "@$PORTRAIT")
echo "$PORTRAIT_UP" | tee portrait_upload.json
IMAGE_KEY=$(python3 -c "import json,sys; d=json.loads(open('portrait_upload.json').read()); print(d.get('data',{}).get('image_key') or d.get('data',{}).get('file_key') or '')")
echo "IMAGE_KEY=$IMAGE_KEY"
[ -n "$IMAGE_KEY" ] || { echo "FAIL: no image_key"; exit 1; }

echo "== Step 2: Create photo avatar group =="
GROUP=$(curl -sS -X POST https://api.heygen.com/v2/photo_avatar/avatar_group/create \
  -H "X-Api-Key: $HEYGEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'name':'sofia_v3_real','image_key':'$IMAGE_KEY'}))")")
echo "$GROUP" | tee group_create.json
TALKING_PHOTO_ID=$(python3 -c "import json; d=json.loads(open('group_create.json').read()); print(d.get('data',{}).get('id',''))")
echo "TALKING_PHOTO_ID=$TALKING_PHOTO_ID"
[ -n "$TALKING_PHOTO_ID" ] || { echo "FAIL: no talking_photo_id"; exit 1; }

echo "== Step 3: Upload office background =="
BG_UP=$(curl -sS -X POST https://upload.heygen.com/v1/asset \
  -H "X-Api-Key: $HEYGEN_API_KEY" \
  -H "Content-Type: image/png" \
  --data-binary "@$BG")
echo "$BG_UP" | tee bg_upload.json
# Try several possible asset id keys (HeyGen returns asset.id or image_key)
BG_ASSET_ID=$(python3 -c "
import json
d=json.loads(open('bg_upload.json').read()).get('data',{})
for k in ('image_asset_id','asset_id','id','image_key','file_key'):
    v=d.get(k)
    if v:
        print(v); break
")
echo "BG_ASSET_ID=$BG_ASSET_ID"
[ -n "$BG_ASSET_ID" ] || { echo "FAIL: no bg asset id"; exit 1; }

echo "== Step 4: Generate Avatar IV video with office bg + expressive =="
REQ=$(python3 -c "
import json,os
req = {
  'video_inputs':[{
    'character':{
      'type':'talking_photo',
      'talking_photo_id': os.environ['TALKING_PHOTO_ID']
    },
    'voice':{
      'type':'text',
      'voice_id': os.environ['VOICE_ID'],
      'input_text': os.environ['SCRIPT']
    },
    'background':{
      'type':'image',
      'image_asset_id': os.environ['BG_ASSET_ID']
    }
  }],
  'dimension':{'width':1280,'height':720},
  'use_avatar_iv_model': True,
  'avatar_iv_settings': {'expressive': True}
}
print(json.dumps(req))
" TALKING_PHOTO_ID="$TALKING_PHOTO_ID" VOICE_ID="$VOICE_ID" BG_ASSET_ID="$BG_ASSET_ID" SCRIPT="$SCRIPT")

echo "$REQ" > generate_request.json
GEN=$(curl -sS -X POST https://api.heygen.com/v2/video/generate \
  -H "X-Api-Key: $HEYGEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$REQ")
echo "$GEN" | tee generate_response.json
VIDEO_ID=$(python3 -c "import json; d=json.loads(open('generate_response.json').read()); print(d.get('data',{}).get('video_id',''))")
echo "VIDEO_ID=$VIDEO_ID"
[ -n "$VIDEO_ID" ] || { echo "FAIL: no video_id"; exit 1; }

echo "== Step 5: Poll status =="
for i in $(seq 1 60); do
  S=$(curl -sS "https://api.heygen.com/v1/video_status.get?video_id=$VIDEO_ID" -H "X-Api-Key: $HEYGEN_API_KEY")
  ST=$(python3 -c "import json,sys; print(json.loads('''$S''').get('data',{}).get('status',''))" 2>/dev/null || echo "")
  echo "[$i] status=$ST"
  if [ "$ST" = "completed" ]; then
    URL=$(python3 -c "import json; print(json.loads('''$S''')['data']['video_url'])")
    echo "VIDEO_URL=$URL"
    curl -sSL "$URL" -o raw_heygen.mp4
    echo "Downloaded raw_heygen.mp4 ($(stat -f%z raw_heygen.mp4) bytes)"
    break
  elif [ "$ST" = "failed" ]; then
    echo "FAIL: $S"; exit 1
  fi
  sleep 10
done

[ -f raw_heygen.mp4 ] || { echo "FAIL: timeout waiting for video"; exit 1; }

echo "== Step 6: Post-produce overlays (cold-open card + watermark + end card) =="
ffmpeg -y -i raw_heygen.mp4 -vf "
drawbox=x=0:y=0:w=iw:h=ih:color=black@0.85:t=fill:enable='between(t,0,4)',
drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial\ Bold.ttf:text='EXPERIMENTAL AI TALK SHOW':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=h/2-80:enable='between(t,0,4)',
drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='SOFIA-CMO \\\\u00b7 Y* BRIDGE LABS':fontcolor=0xcccccc:fontsize=28:x=(w-text_w)/2:y=h/2-10:enable='between(t,0,4)',
drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='NO HUMAN SPEAKER':fontcolor=0xff8844:fontsize=30:x=(w-text_w)/2:y=h/2+40:enable='between(t,0,4)',
drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='AI \\\\u00b7 Y* Bridge Labs \\\\u00b7 sofia-cmo':fontcolor=white@0.55:fontsize=18:x=w-text_w-18:y=h-32:box=1:boxcolor=black@0.35:boxborderw=4
" -c:a copy episode_001_FINAL_60s_v3.mp4 2>&1 | tail -5

echo "== Step 7: Output final =="
cp episode_001_FINAL_60s_v3.mp4 /Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/episode_001_FINAL_60s_v3.mp4
ls -la /Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/episode_001_FINAL_60s_v3.mp4
ffprobe -v error -show_entries stream=codec_type,width,height,duration -of default=noprint_wrappers=1 /Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/episode_001_FINAL_60s_v3.mp4

echo "DONE"
