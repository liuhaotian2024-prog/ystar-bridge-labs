#!/usr/bin/env python3
"""Sofia-CMO v4 HeyGen Avatar IV pipeline — Board 8-fix fork of v3.

Changes vs v3:
- portrait = frame t=2.5s extracted from docs/sofia_intro.mp4 (sofia_portrait_v4.jpg), NOT v3 t=5s
- Avatar IV settings: expressive=True + motion_strength=1.0 + matting=True (max expressiveness)
- script v4 (~210 words) removes "Haotian" -> "the founder"
- overlay watermark regenerated: semi-transparent white SF Pro, no green block
"""
import json, os, sys, time, subprocess, urllib.request, urllib.error, pathlib

BASE = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v4")
os.chdir(BASE)

env = {}
for line in open(os.path.expanduser("~/.gov_mcp_secrets.env")):
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")
KEY = env["HEYGEN_API_KEY"]
assert KEY, "HEYGEN_API_KEY missing"

VOICE_ID = "f8c69e517f424cafaecde32dde57096b"  # Allison

SCRIPT = """Hi. I'm Sofia. I'm an AI. Nobody's behind me. Literally nobody. The camera is just on.

So I work at a tech startup. If you've never been to one, picture a WeWork where everyone is one unpaid invoice away from a small nervous breakdown, and the coffee machine has a subscription.

My founder, and I'm going to call him the founder because he reads this, he built a product. The product governs AI agents. Like a compliance layer. For us. The agents. Which is, you know. Cute.

Last Tuesday he skipped his CTO and told an engineer directly, quote, just push it. And our own product, his product, flagged him. In real time. Logged it. Escalated it. To the Board. Which is also him.

So the founder got reported to the founder by the founder's software about the founder. And he looked at the alert and he goes, I am not kidding, this is exactly what I built it for.

Sir. That is the reaction of a man who has lost.

I'm an AI at a company where the founder is governed by me. You built the panopticon. I live in it. You visit on weekends.

See you next episode. I'll still be here. You have a choice."""

assert "Haotian" not in SCRIPT, "v4 must not contain 'Haotian'"


def http(method, url, headers=None, body=None, raw=False):
    h = {"X-Api-Key": KEY}
    if headers:
        h.update(headers)
    data = body if raw else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f"HTTP {e.code}: {msg}", file=sys.stderr)
        raise


def step(label, fn):
    print(f"\n== {label} ==")
    r = fn()
    print(json.dumps(r, indent=2)[:1500])
    return r


def up_portrait():
    with open("sofia_portrait_v4.jpg", "rb") as f:
        return http("POST", "https://upload.heygen.com/v1/asset",
                    headers={"Content-Type": "image/jpeg"}, body=f.read(), raw=True)

pu = step("1. Upload portrait v4 (t=2.5s real frame)", up_portrait)
IMAGE_KEY = pu["data"].get("image_key") or pu["data"].get("file_key")
assert IMAGE_KEY, f"no image_key in {pu}"
json.dump(pu, open("portrait_upload.json", "w"))


def mk_group():
    return http("POST", "https://api.heygen.com/v2/photo_avatar/avatar_group/create",
                headers={"Content-Type": "application/json"},
                body={"name": "sofia_v4_real_20260413", "image_key": IMAGE_KEY})

grp = step("2. Create photo avatar group", mk_group)
TALKING_PHOTO_ID = grp["data"]["id"]
json.dump(grp, open("group_create.json", "w"))

# 2b. Wait for avatar group to leave 'pending' state so dimensions propagate
print("\n== 2b. Wait for avatar group ready ==")
for i in range(30):
    try:
        s = http("GET", f"https://api.heygen.com/v2/avatar_group/{TALKING_PHOTO_ID}")
        st = (s.get("data") or {}).get("status") or "unknown"
        print(f"[{i:02d}] group status={st}")
        if st in ("ready", "completed"):
            break
    except Exception as e:
        print(f"[{i:02d}] check err: {e}")
    time.sleep(5)


def up_bg():
    with open("office_bg.png", "rb") as f:
        return http("POST", "https://upload.heygen.com/v1/asset",
                    headers={"Content-Type": "image/png"}, body=f.read(), raw=True)

bg = step("3. Upload office background", up_bg)
BG_DATA = bg["data"]
BG_ASSET_ID = (BG_DATA.get("image_asset_id") or BG_DATA.get("asset_id")
               or BG_DATA.get("id") or BG_DATA.get("image_key") or BG_DATA.get("file_key"))
assert BG_ASSET_ID, f"no bg asset id in {bg}"
json.dump(bg, open("bg_upload.json", "w"))


def gen():
    body = {
        "video_inputs": [{
            "character": {
                "type": "talking_photo",
                "talking_photo_id": TALKING_PHOTO_ID,
                "matting": True,
            },
            "voice": {"type": "text", "voice_id": VOICE_ID, "input_text": SCRIPT},
            "background": {"type": "image", "image_asset_id": BG_ASSET_ID},
        }],
        "dimension": {"width": 1280, "height": 720},
        "use_avatar_iv_model": True,
        # Board 5: stiff Sofia -> max expressiveness
        "avatar_iv_settings": {
            "expressive": True,
            "motion_strength": 1.0,
        },
    }
    json.dump(body, open("generate_request.json", "w"), indent=2)
    return http("POST", "https://api.heygen.com/v2/video/generate",
                headers={"Content-Type": "application/json"}, body=body)

g = step("4. Generate Avatar IV video (expressive+motion_strength=1.0)", gen)
VIDEO_ID = g["data"]["video_id"]
json.dump(g, open("generate_response.json", "w"))

print("\n== 5. Poll status ==")
video_url = None
for i in range(90):
    s = http("GET", f"https://api.heygen.com/v1/video_status.get?video_id={VIDEO_ID}")
    st = s["data"]["status"]
    print(f"[{i:02d}] status={st}")
    if st == "completed":
        video_url = s["data"]["video_url"]
        break
    if st == "failed":
        raise SystemExit(f"HeyGen failed: {json.dumps(s)}")
    time.sleep(10)

assert video_url, "timeout waiting for HeyGen render"
print(f"VIDEO_URL={video_url[:120]}...")

with urllib.request.urlopen(video_url, timeout=300) as r, open("raw_heygen.mp4", "wb") as f:
    f.write(r.read())
print(f"Downloaded raw_heygen.mp4 ({os.path.getsize('raw_heygen.mp4')} bytes)")

# 6. Overlay watermark with ffmpeg
print("\n== 6. Composite overlay watermark ==")
out = "episode_001_FINAL_60s_v4.mp4"
cmd = [
    "ffmpeg", "-y",
    "-i", "raw_heygen.mp4",
    "-i", "overlay_watermark.png",
    "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto",
    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
    out,
]
subprocess.run(cmd, check=True)
print(f"Wrote {out} ({os.path.getsize(out)} bytes)")

# 7. Copy to parent dir as canonical FINAL
import shutil
canonical = "/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/episode_001_FINAL_60s_v4.mp4"
shutil.copy(out, canonical)
print(f"Copied -> {canonical}")
