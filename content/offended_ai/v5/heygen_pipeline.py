#!/usr/bin/env python3
"""Sofia-CMO v5 HeyGen Avatar IV pipeline — late-night 60s template fork of v4.

Changes vs v4:
- SCRIPT rewritten to 5-beat late-night template (169 words, ~57s at 3.0 wps)
  Source: knowledge/cmo/theory/late_night_monologue_60s_template.md
- Background = flat solid #1a1a1a (Burnham rule: bg must not compete with
  avatar). We no longer generate or upload office_bg.png; instead we upload a
  flat 1280x720 PNG we create inline.
- Cold-open spoken preamble deleted (Colbert 2016 reformat: no preamble,
  disclosure to lower-third).
- Overlay is a full-width 80px CNN-style lower-third (overlay_lower_third.png,
  built by make_lower_third.py), NOT a corner watermark.
- Portrait inherited from v4 (sofia_portrait_v4.jpg) — Board already approved.
"""
import json, os, sys, time, subprocess, urllib.request, urllib.error, pathlib, shutil

BASE = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v5")
V4 = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v4")
os.chdir(BASE)

# --- 0. Inherit portrait from v4 (Board-approved) --------------------------
PORTRAIT_SRC = V4 / "sofia_portrait_v4.jpg"
PORTRAIT = BASE / "sofia_portrait_v4.jpg"
if not PORTRAIT.exists():
    shutil.copy(PORTRAIT_SRC, PORTRAIT)
    print(f"copied portrait from v4: {PORTRAIT}")

# --- 0b. Ensure lower-third exists -----------------------------------------
OVERLAY = BASE / "overlay_lower_third.png"
if not OVERLAY.exists():
    subprocess.run([sys.executable, str(BASE / "make_lower_third.py")], check=True)
assert OVERLAY.exists(), "overlay_lower_third.png missing after make_lower_third.py"

# --- 0c. Build flat bg PNG (#1a1a1a, 1280x720) -----------------------------
BG_PATH = BASE / "bg_flat.png"
if not BG_PATH.exists():
    from PIL import Image
    Image.new("RGB", (1280, 720), (26, 26, 26)).save(BG_PATH)
    print(f"wrote {BG_PATH}")

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
print(f"[v5] script word count = {wc} (target 165-185 for 60s at 3.0 wps)")


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

pu = step("1. Upload portrait (v4 asset inherited)", up_portrait)
IMAGE_KEY = pu["data"].get("image_key") or pu["data"].get("file_key")
assert IMAGE_KEY, f"no image_key in {pu}"
json.dump(pu, open("portrait_upload.json", "w"))


def mk_group():
    return http("POST", "https://api.heygen.com/v2/photo_avatar/avatar_group/create",
                headers={"Content-Type": "application/json"},
                body={"name": "sofia_v5_latenight_20260413", "image_key": IMAGE_KEY})

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


# --- 3. Upload flat bg ----------------------------------------------------
def up_bg():
    with open(BG_PATH, "rb") as f:
        return http("POST", "https://upload.heygen.com/v1/asset",
                    headers={"Content-Type": "image/png"}, body=f.read(), raw=True)

bg = step("3. Upload flat #1a1a1a background", up_bg)
BG_DATA = bg["data"]
BG_ASSET_ID = (BG_DATA.get("image_asset_id") or BG_DATA.get("asset_id")
               or BG_DATA.get("id") or BG_DATA.get("image_key") or BG_DATA.get("file_key"))
assert BG_ASSET_ID, f"no bg asset id in {bg}"
json.dump(bg, open("bg_upload.json", "w"))


# --- 4. Generate video ----------------------------------------------------
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

with urllib.request.urlopen(video_url, timeout=300) as r, open("raw_heygen.mp4", "wb") as f:
    f.write(r.read())
print(f"Downloaded raw_heygen.mp4 ({os.path.getsize('raw_heygen.mp4')} bytes)")


# --- 6. Composite lower-third --------------------------------------------
print("\n== 6. Composite lower-third overlay ==")
out = "episode_001_FINAL_60s_v5.mp4"
cmd = [
    "ffmpeg", "-y",
    "-i", "raw_heygen.mp4",
    "-i", str(OVERLAY),
    "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto",
    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
    out,
]
subprocess.run(cmd, check=True)
print(f"Wrote {out} ({os.path.getsize(out)} bytes)")


# --- 7. Canonical copy ----------------------------------------------------
canonical = "/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/episode_001_FINAL_60s_v5.mp4"
shutil.copy(out, canonical)
print(f"Copied -> {canonical}")

# --- 8. Duration probe ----------------------------------------------------
try:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", out],
        check=True, capture_output=True, text=True,
    )
    print(f"duration_sec={r.stdout.strip()}")
except Exception as e:
    print(f"ffprobe skipped: {e}")
