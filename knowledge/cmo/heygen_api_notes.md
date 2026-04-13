# HeyGen API — Operational Notes (CMO)

**Captured:** 2026-04-13 by Aiden-as-CMO covering Sofia-CMO.
**Key location:** `~/.gov_mcp_secrets.env` → `HEYGEN_API_KEY` (54 chars, verified working).

## Endpoints (verified via live calls)

### 1. Upload Asset (photo → image_key)
- `POST https://upload.heygen.com/v1/asset`
- Headers: `X-Api-Key: $KEY`, `Content-Type: image/png` (match actual file type)
- Body: raw binary (`--data-binary @file.png`)
- Response: `data.image_key` e.g. `image/<asset_id>/original.png`

### 2. Create Photo Avatar Group (image_key → talking_photo_id)
- `POST https://api.heygen.com/v2/photo_avatar/avatar_group/create`
- Headers: `X-Api-Key`, `Content-Type: application/json`
- Body: `{"name":"<name>","image_key":"<image_key_from_step_1>"}`
- Response: `data.id` — this id is ALSO usable directly as `talking_photo_id` in v2/video/generate (confirmed: appears in `/v1/talking_photo.list` immediately).

### 3. Generate Video v2
- `POST https://api.heygen.com/v2/video/generate`
- Body:
```json
{
  "video_inputs":[{
    "character":{"type":"talking_photo","talking_photo_id":"<id>"},
    "voice":{"type":"text","voice_id":"<voice_id>","input_text":"<script>"},
    "background":{"type":"color","value":"#1a1a1a"}
  }],
  "dimension":{"width":1280,"height":720}
}
```
- Response: `data.video_id`
- Notes: `background.type` can be `"color"` with hex, or `"image"` with `url`/`image_asset_id`, or `"video"`. Studio look achieved via dark color + avatar framing.

### 4. Poll Video Status
- `GET https://api.heygen.com/v1/video_status.get?video_id=<id>`
- Status values: `pending` → `processing` → `completed` | `failed`
- On `completed`: `data.video_url` is signed download URL (expires, regenerated per call).

### 5. List Voices
- `GET https://api.heygen.com/v2/voices` → `data.voices[]` with `voice_id`, `name`, `gender`, `language`.
- Picked: **Allison** (female English) voice_id = `f8c69e517f424cafaecde32dde57096b`.

## Error Codes
- 401: key revoked → rotate via Board
- 429: rate limit → backoff 60s retry
- 500: HeyGen outage → fall back to D-ID or wait
- 40001 "asset data must be provided": body not sent as binary in upload

## Credits
- No quota endpoint found (`/v1/user/remaining_quota` returns 404). HeyGen credit balance visible only in dashboard UI. 60s at 1280x720 ≈ 1 credit. Free plan typically 10 credits/mo.

## Duration Control
- HeyGen does NOT accept explicit duration param — length is derived from TTS of `input_text` + voice speed. To hit ~60s with Allison at default speed, target ~150 words of script.
