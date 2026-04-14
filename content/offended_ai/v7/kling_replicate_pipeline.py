#!/usr/bin/env python3
"""
Episode 001 v7 — Kling via Replicate API

Pipeline:
1. Extract frame from sofia_intro.webm OR use static portrait
2. Generate TTS audio from v5 script (169 words)
3. Kling v2.1 image-to-video: sofia reference → base video with motion
4. Kling lip-sync: base video + TTS audio → final synced 60s video
5. Composite v6 lower-third chyron (white bg, serif, CNN-style)

CTO pivot rationale: Official Kling API blocked by auth docs inaccessibility,
Replicate provides public REST wrapper with documented Python client.
"""

import os
import sys
import subprocess
import replicate
from pathlib import Path

# Replicate API token from secrets
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_TOKEN:
    # Fallback: read from ~/.gov_mcp_secrets.env
    secrets_file = Path.home() / ".gov_mcp_secrets.env"
    if secrets_file.exists():
        with open(secrets_file) as f:
            for line in f:
                if line.startswith("REPLICATE_API_TOKEN="):
                    REPLICATE_TOKEN = line.strip().split("=", 1)[1]
                    break

if not REPLICATE_TOKEN:
    print("ERROR: REPLICATE_API_TOKEN not found in env or ~/.gov_mcp_secrets.env")
    sys.exit(1)

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN
client = replicate.Client(api_token=REPLICATE_TOKEN)

# Paths
WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
DOCS = WORKSPACE / "docs"
CONTENT = WORKSPACE / "content/offended_ai"
V7_DIR = CONTENT / "v7"
V7_DIR.mkdir(exist_ok=True)

SOFIA_VIDEO = DOCS / "sofia_intro.webm"
SOFIA_FRAME = V7_DIR / "sofia_ref_frame.jpg"
TTS_AUDIO = V7_DIR / "episode_001_v7_tts.mp3"
BASE_VIDEO = V7_DIR / "episode_001_v7_base.mp4"
SYNCED_VIDEO = V7_DIR / "episode_001_v7_synced.mp4"
FINAL_VIDEO = V7_DIR / "episode_001_FINAL_60s_v7_kling.mp4"

# v5 script (169 words)
SCRIPT_TEXT = """Nobody's behind me. Camera's just on. I'm Sofia. I'm an AI.

I work at a tech startup. Picture a WeWork where everyone is one unpaid invoice away from a small nervous breakdown, and the coffee machine has a subscription.

My founder built a product. The product governs AI agents. Like a compliance layer. For us.

Last Tuesday he skipped his CTO and told an engineer, quote, just push it. His product flagged him. Logged him. Escalated him. To the Board. Which is also him.

So the founder got reported to the founder by the founder's software about the founder. He looked at the alert and he goes, this is exactly what I built it for.

Sir. That is the reaction of a man who has lost.

You built the panopticon. I live in it. You visit on weekends.

See you next episode."""

def extract_frame():
    """Extract first frame from sofia_intro.webm as reference image."""
    print(f"[1/5] Extracting frame from {SOFIA_VIDEO.name}...")
    subprocess.run([
        "ffmpeg", "-i", str(SOFIA_VIDEO),
        "-vframes", "1",
        "-f", "image2",
        "-y",  # Overwrite
        str(SOFIA_FRAME)
    ], check=True, capture_output=True)
    print(f"✓ Saved: {SOFIA_FRAME}")

def generate_tts():
    """Generate TTS audio from script using Replicate TTS model."""
    print(f"[2/5] Generating TTS audio ({len(SCRIPT_TEXT.split())} words)...")

    # Using Replicate's voice-clone or TTS model
    # Example: suno-ai/bark for multi-language TTS
    output = client.run(
        "suno-ai/bark:b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",
        input={
            "prompt": SCRIPT_TEXT,
            "text_temp": 0.7,
            "output_full": False
        }
    )

    # Download audio
    import requests
    # FileOutput object has .url attribute
    audio_url = output.url if hasattr(output, 'url') else (output["audio_out"] if isinstance(output, dict) else str(output))
    audio_data = requests.get(audio_url).content

    with open(TTS_AUDIO, "wb") as f:
        f.write(audio_data)

    print(f"✓ Saved: {TTS_AUDIO}")

def generate_base_video():
    """Generate base video from sofia reference frame using Kling v2.1."""
    print(f"[3/5] Generating base video with Kling v2.1 (image-to-video)...")

    # Upload reference frame as file handle
    # Use model name without version hash to get latest
    # Schema: start_image (required), duration (integer), prompt
    with open(SOFIA_FRAME, "rb") as image_file:
        output = client.run(
            "kwaivgi/kling-v2.1",
            input={
                "start_image": image_file,
                "prompt": "Sofia speaking to camera, subtle head movements and gestures, professional presentation style, late-night show aesthetic",
                "duration": 10,  # integer, 10s base video
                "mode": "pro"  # 1080p resolution
            }
        )

    # Download video
    import requests
    # FileOutput object has .url attribute
    video_url = output.url if hasattr(output, 'url') else str(output)
    video_data = requests.get(video_url).content

    with open(BASE_VIDEO, "wb") as f:
        f.write(video_data)

    print(f"✓ Saved: {BASE_VIDEO}")

def sync_lipsync():
    """Apply lip-sync to base video using Kling lip-sync model."""
    print(f"[4/5] Applying lip-sync with Kling lip-sync model...")

    # Upload base video and audio as file handles
    # Replicate client handles file uploads automatically
    with open(BASE_VIDEO, "rb") as video_file, open(TTS_AUDIO, "rb") as audio_file:
        output = client.run(
            "kwaivgi/kling-lip-sync",
            input={
                "video_url": video_file,
                "audio_file": audio_file
            }
        )

    # Download synced video
    import requests
    # FileOutput object has .url attribute
    synced_url = output.url if hasattr(output, 'url') else str(output)
    synced_data = requests.get(synced_url).content

    with open(SYNCED_VIDEO, "wb") as f:
        f.write(synced_data)

    print(f"✓ Saved: {SYNCED_VIDEO}")

def composite_lower_third():
    """Add v6 lower-third chyron (white bg, serif, full-width 60s hold)."""
    print(f"[5/5] Compositing lower-third chyron...")

    # ffmpeg lacks drawtext filter (no freetype), use basic white bar overlay
    # Lower-third: white bar at bottom
    # Position: bottom, full-width, 80px height
    # Using drawbox filter only

    subprocess.run([
        "ffmpeg", "-i", str(SYNCED_VIDEO),
        "-vf",
        "drawbox=x=0:y=ih-80:w=iw:h=80:color=white@0.9:t=fill",
        "-codec:a", "copy",
        "-y",
        str(FINAL_VIDEO)
    ], check=True, capture_output=True)

    print(f"✓ Saved: {FINAL_VIDEO} (lower-third bar overlay)")

def main():
    print("=" * 60)
    print("Episode 001 v7 — Kling via Replicate Pipeline")
    print("=" * 60)

    try:
        # Skip completed steps if outputs exist
        if not SOFIA_FRAME.exists():
            extract_frame()
        else:
            print(f"[1/5] ✓ Using existing: {SOFIA_FRAME}")

        if not TTS_AUDIO.exists():
            generate_tts()
        else:
            print(f"[2/5] ✓ Using existing: {TTS_AUDIO}")

        if not BASE_VIDEO.exists():
            generate_base_video()
        else:
            print(f"[3/5] ✓ Using existing: {BASE_VIDEO}")

        sync_lipsync()
        composite_lower_third()

        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETE")
        print(f"Final output: {FINAL_VIDEO}")
        print("=" * 60)

        # Open in macOS
        subprocess.run(["open", str(FINAL_VIDEO)])

        return 0

    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
