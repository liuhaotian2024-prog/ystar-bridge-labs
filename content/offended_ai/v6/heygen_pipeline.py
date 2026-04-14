#!/usr/bin/env python3
"""Sofia-CMO v6 HeyGen Avatar IV pipeline — matting + real-bg composite.

Changes vs v5:
- HeyGen Avatar IV: transparent_bg=True in character settings (output alpha video)
- Post-process: ffmpeg matte composite onto sofia_intro.mp4 frames as real bg
- Lower-third: white bg + black text + serif font (Colbert rule)
- API params: motion_strength=1.0, expressive=True (Avatar IV v2 settings)
- Portrait + script inherited from v5 (Board already approved).
"""
import json, os, sys, time, subprocess, urllib.request, urllib.error, pathlib, shutil

BASE = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v6")
V5 = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v5")
os.chdir(BASE)

# --- 0. Inherit portrait from v5 (Board-approved) --------------------------
PORTRAIT_SRC = V5 / "sofia_portrait_v4.jpg"
PORTRAIT = BASE / "sofia_portrait_v4.jpg"
if not PORTRAIT.exists():
    shutil.copy(PORTRAIT_SRC, PORTRAIT)
    print(f"copied portrait from v5: {PORTRAIT}")

# --- 0b. Ensure lower-third exists (v6: white bg + black text + serif) ----
OVERLAY = BASE / "overlay_lower_third.png"
if not OVERLAY.exists():
    subprocess.run([sys.executable, str(BASE / "make_lower_third.py")], check=True)
assert OVERLAY.exists(), "overlay_lower_third.png missing after make_lower_third.py"

# --- 1. Secrets -----------------------------------------------------------
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

SCRIPT = """Nobody's behind me. Camera's just on. I'm Sofia. I'm an AI.

I work at a tech startup. Picture a WeWork where everyone is one unpaid invoice away from a small nervous breakdown, and the coffee machine has a subscription.

My founder built a product. The product governs AI agents. Like a compliance layer. For us.

Last Tuesday he skipped his CTO and told an engineer, quote, just push it. His product flagged him. Logged him. Escalated him. To the Board. Which is also him.

So the founder got reported to the founder by the founder's software about the founder. He looked at the alert and he goes, this is exactly what I built it for.

Sir. That is the reaction of a man who has lost.

You built the panopticon. I live in it. You visit on weekends.

See you next episode."""

assert "Haotian" not in SCRIPT, "must not contain 'Haotian'"
wc = len(SCRIPT.split())
print(f"[v6] script word count = {wc} (target 165-185 for 60s at 3.0 wps)")


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


# --- 2. Upload portrait ---------------------------------------------------
def up_portrait():
    with open(PORTRAIT, "rb") as f:
        return http("POST", "https://upload.heygen.com/v1/asset",
                    headers={"Content-Type": "image/jpeg"}, body=f.read(), raw=True)

pu = step("1. Upload portrait (v5 asset inherited)", up_portrait)
IMAGE_KEY = pu["data"].get("image_key") or pu["data"].get("file_key")
assert IMAGE_KEY, f"no image_key in {pu}"
json.dump(pu, open("portrait_upload.json", "w"))


def mk_group():
    return http("POST", "https://api.heygen.com/v2/photo_avatar/avatar_group/create",
                headers={"Content-Type": "application/json"},
                body={"name": "sofia_v6_matte_20260413", "image_key": IMAGE_KEY})

grp = step("2. Create photo avatar group", mk_group)
TALKING_PHOTO_ID = grp["data"]["id"]
json.dump(grp, open("group_create.json", "w"))

# 2b. Wait for ready
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


# --- 3. Green screen bg (for post chroma-key) ----------------------------
print("\n== 3. Green screen bg (chroma-key in post) ==")
# HeyGen doesn't support transparent bg directly; use green screen + matting


# --- 4. Generate video (green screen bg) ----------------------------------
def gen():
    body = {
        "video_inputs": [{
            "character": {
                "type": "talking_photo",
                "talking_photo_id": TALKING_PHOTO_ID,
                "matting": True,
            },
            "voice": {"type": "text", "voice_id": VOICE_ID, "input_text": SCRIPT},
            "background": {"type": "color", "value": "#00FF00"},  # green screen
        }],
        "dimension": {"width": 1280, "height": 720},
        "use_avatar_iv_model": True,
        "avatar_iv_settings": {
            "expressive": True,
            "motion_strength": 1.0,
        },
    }
    json.dump(body, open("generate_request.json", "w"), indent=2)
    return http("POST", "https://api.heygen.com/v2/video/generate",
                headers={"Content-Type": "application/json"}, body=body)

g = step("4. Generate Avatar IV video (green screen bg, expressive+motion_strength=1.0)", gen)
VIDEO_ID = g["data"]["video_id"]
json.dump(g, open("generate_response.json", "w"))


# --- 5. Poll status -------------------------------------------------------
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

with urllib.request.urlopen(video_url, timeout=300) as r, open("raw_heygen_v6.mp4", "wb") as f:
    f.write(r.read())
print(f"Downloaded raw_heygen_v6.mp4 ({os.path.getsize('raw_heygen_v6.mp4')} bytes)")


# --- 6. Extract sofia_intro.mp4 bg frames ---------------------------------
print("\n== 6. Extract sofia_intro.mp4 frames as bg sequence ==")
BG_VIDEO = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/docs/sofia_intro.mp4")
BG_FRAMES = BASE / "bg_frames"
BG_FRAMES.mkdir(exist_ok=True)
subprocess.run([
    "ffmpeg", "-y", "-i", str(BG_VIDEO),
    "-vf", "fps=30",
    str(BG_FRAMES / "bg_%04d.png"),
], check=True)
print(f"Extracted bg frames to {BG_FRAMES}")


# --- 7. Chroma-key composite onto real bg + lower-third ------------------
print("\n== 7. Chroma-key green screen onto real bg + lower-third ==")
out = "episode_001_FINAL_60s_v6.mp4"
# Chroma-key green screen and overlay onto bg + lower-third
cmd = [
    "ffmpeg", "-y",
    "-framerate", "30", "-i", str(BG_FRAMES / "bg_%04d.png"),
    "-i", "raw_heygen_v6.mp4",
    "-i", str(OVERLAY),
    "-filter_complex",
    "[1:v]chromakey=0x00FF00:0.3:0.2[ckout];[0:v][ckout]overlay=shortest=1[bg_avatar];[bg_avatar][2:v]overlay=0:0:format=auto",
    "-map", "1:a",  # audio from HeyGen
    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
    "-pix_fmt", "yuv420p",
    out,
]
subprocess.run(cmd, check=True)
print(f"Wrote {out} ({os.path.getsize(out)} bytes)")


# --- 8. Canonical copy ----------------------------------------------------
canonical = "/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/episode_001_FINAL_60s_v6.mp4"
shutil.copy(out, canonical)
print(f"Copied -> {canonical}")

# --- 9. Duration probe ----------------------------------------------------
try:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", out],
        check=True, capture_output=True, text=True,
    )
    print(f"duration_sec={r.stdout.strip()}")
except Exception as e:
    print(f"ffprobe skipped: {e}")
