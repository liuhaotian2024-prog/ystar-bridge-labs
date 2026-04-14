#!/usr/bin/env python3
"""Apply rembg AI matting to all HeyGen frames."""
import subprocess
import pathlib
import sys

BASE = pathlib.Path("/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v6")
FG_FRAMES = BASE / "fg_frames"
ALPHA_FRAMES = BASE / "alpha_frames"

fg_list = sorted(FG_FRAMES.glob("heygen_*.png"))
total = len(fg_list)
print(f"Applying rembg to {total} frames...")

for i, fg in enumerate(fg_list, 1):
    num = fg.stem.replace("heygen_", "")
    alpha_out = ALPHA_FRAMES / f"alpha_{num}.png"

    subprocess.run(["rembg", "i", str(fg), str(alpha_out)],
                   check=True,
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    if i % 50 == 0 or i == total:
        print(f"  rembg: {i}/{total} ({100*i//total}%)")

print(f"Complete: {total} frames -> {ALPHA_FRAMES}")
