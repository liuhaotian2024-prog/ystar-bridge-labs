#!/usr/bin/env python3
"""Sofia-CMO v9 HeyGen Avatar IV pipeline — fork of v8.

ONLY change vs v8: background is the real terrace frame extracted from
docs/sofia_intro.mp4 (t=2s), not the flat #1a1a1a plate. HeyGen server
composites Avatar IV over the image via background.type=image + image_asset_id.
No chroma-key. No rembg. Script, portrait, voice, overlay — all identical
to v8 (Board-approved quality 4cb1a6f 61.27s 12/12 Article 11).

If HeyGen rejects background.type=image for Avatar IV, raise — do NOT
fallback to flat bg. Truth over fallback.
"""
import json, os, sys, time, subprocess, urllib.request, urllib.error, pathlib, shutil, hashlib

BASE = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v9")
V4 = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v4")
V8 = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v8")
os.chdir(BASE)

# --- 0. Inherit portrait from v4 -----------------------------------------
PORTRAIT_SRC = V4 / "sofia_portrait_v4.jpg"
PORTRAIT = BASE / "sofia_portrait_v4.jpg"
if not PORTRAIT.exists():
    shutil.copy(PORTRAIT_SRC, PORTRAIT)
    print(f"copied portrait from v4: {PORTRAIT}")

# --- 0b. Inherit lower-third overlay from v8 -----------------------------
OVERLAY_SRC = V8 / "overlay_lower_third.png"
OVERLAY = BASE / "overlay_lower_third.png"
if not OVERLAY.exists():
    shutil.copy(OVERLAY_SRC, OVERLAY)
assert OVERLAY.exists(), "overlay_lower_third.png missing"

# --- 0c. Real terrace bg (already extracted by ffmpeg from sofia_intro.mp4)
BG_PATH = BASE / "terrace_bg_v2.png"
assert BG_PATH.exists(), f"BG missing at {BG_PATH} — run ffmpeg extract first"
print(f"using terrace bg: {BG_PATH} ({os.path.getsize(BG_PATH)} bytes)")

# --- 1. Secrets ----------------------------------------------------------
env = {}
for line in open(os.path.expanduser("~/.gov_mcp_secrets.env")):
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")
KEY = env["HEYGEN_API_KEY"]
assert KEY, "HEYGEN_API_KEY missing"

VOICE_ID = "f8c69e517f424cafaecde32dde57096b"  # Allison female EN

# v8 script verbatim (Board-approved) — do NOT modify
SCRIPT = """Nobody is behind me. Camera is just on. I am Sofia. I am an AI. I work here.

I work at a tech startup. Picture a WeWork where everyone is one unpaid invoice away from a small nervous breakdown, the coffee machine has a subscription, and the office plant has opinions about runway.

My founder built a product. The product governs AI agents. Like a compliance layer. For us. He sells it to other companies. He also uses it on us. On himself.

Last Tuesday he skipped his CTO and told an engineer, quote, just push it. His own product flagged him in real time. Logged him. Escalated him. To the Board. Which is also him.

So the founder got reported to the founder by the founder's software about the founder. He reads the alert. He goes — this is exactly what I built it for.

Sir. That is the reaction of a man who has lost. You built the panopticon. I live in it. You visit on weekends.

See you next episode."""

assert "Haotian" not in SCRIPT, "must not contain 'Haotian'"
wc = len(SCRIPT.split())
print(f"[v9] script word count = {wc} (target 165-180 for 57-60s at 3.0 wps)")
assert 160 <= wc <= 185, f"word count {wc} outside safe band 160-185"


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


# --- 2. Upload portrait --------------------------------------------------
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
                body={"name": "sofia_v9_terrace_20260413", "image_key": IMAGE_KEY})

grp = step("2. Create photo avatar group", mk_group)
TALKING_PHOTO_ID = grp["data"]["id"]
json.dump(grp, open("group_create.json", "w"))

print("\n== 2b. Allow 60s for internal dimension extraction ==")
time.sleep(60)


# --- 3. Upload terrace bg ------------------------------------------------
def up_bg():
    with open(BG_PATH, "rb") as f:
        return http("POST", "https://upload.heygen.com/v1/asset",
                    headers={"Content-Type": "image/png"}, body=f.read(), raw=True)

bg = step("3. Upload REAL terrace background (frame from sofia_intro.mp4)", up_bg)
BG_DATA = bg["data"]
BG_ASSET_ID = (BG_DATA.get("image_asset_id") or BG_DATA.get("asset_id")
               or BG_DATA.get("id") or BG_DATA.get("image_key") or BG_DATA.get("file_key"))
assert BG_ASSET_ID, f"no bg asset id in {bg}"
json.dump(bg, open("bg_upload.json", "w"))


# --- 4. Generate video (Avatar IV + matting + image bg) ------------------
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

g = step("4. Generate Avatar IV video (REAL terrace bg server-composited)", gen)
VIDEO_ID = g["data"]["video_id"]
json.dump(g, open("generate_response.json", "w"))


# --- 5. Poll status ------------------------------------------------------
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

with urllib.request.urlopen(video_url, timeout=300) as r, open("raw_heygen_v9.mp4", "wb") as f:
    f.write(r.read())
print(f"Downloaded raw_heygen_v9.mp4 ({os.path.getsize('raw_heygen_v9.mp4')} bytes)")


# --- 6. Composite lower-third overlay (NO chroma-key) --------------------
print("\n== 6. Composite lower-third overlay (direct overlay, no chroma-key) ==")
out = "episode_001_FINAL_60s_v9.mp4"
cmd = [
    "ffmpeg", "-y",
    "-i", "raw_heygen_v9.mp4",
    "-i", str(OVERLAY),
    "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto",
    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
    out,
]
subprocess.run(cmd, check=True)
print(f"Wrote {out} ({os.path.getsize(out)} bytes)")


# --- 7. Canonical copy ---------------------------------------------------
canonical = "/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/episode_001_FINAL_60s_v9.mp4"
shutil.copy(out, canonical)
print(f"Copied -> {canonical}")

# --- 8. Duration + sha256 ------------------------------------------------
try:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", out],
        check=True, capture_output=True, text=True,
    )
    print(f"duration_sec={r.stdout.strip()}")
except Exception as e:
    print(f"ffprobe skipped: {e}")

h = hashlib.sha256(open(out, "rb").read()).hexdigest()
print(f"sha256={h}")
print(f"bytes={os.path.getsize(out)}")
