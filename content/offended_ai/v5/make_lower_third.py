#!/usr/bin/env python3
"""Generate v5 lower-third overlay PNG — CNN-style, full-width, 80px tall,
dark-blue semi-transparent, SF Pro 14pt regular.

Output: overlay_lower_third.png (1280x720 RGBA, mostly transparent, chyron
band at y=620..700).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

BASE = pathlib.Path(__file__).resolve().parent
W, H = 1280, 720
BAND_H = 80
BAND_Y = H - BAND_H - 20  # 620

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img, "RGBA")

# Dark-blue semi-transparent band — CNN lower-third feel
BAND_COLOR = (12, 26, 64, 205)  # navy, ~80% opacity
d.rectangle([(0, BAND_Y), (W, BAND_Y + BAND_H)], fill=BAND_COLOR)

# Thin accent line on top edge
d.rectangle([(0, BAND_Y), (W, BAND_Y + 2)], fill=(220, 60, 60, 230))

# Pick a font — try SF Pro, then Helvetica Neue, then DejaVu
FONT_CANDIDATES = [
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/SFNSDisplay.ttf",
    "/Library/Fonts/SF-Pro-Display-Regular.otf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load(size):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


font_big = load(22)   # show title line
font_reg = load(16)   # chyron main line
font_sm = load(13)    # disclosure

PADX = 28
y_top = BAND_Y + 10
d.text((PADX, y_top), "OFFENDED AI  /  EP 001", font=font_big, fill=(255, 255, 255, 255))
d.text((PADX, y_top + 28), "SOFIA — CMO, Y* BRIDGE LABS  |  AI-GENERATED AVATAR + AI-GENERATED VOICE",
       font=font_reg, fill=(230, 230, 230, 235))
d.text((PADX, y_top + 50), "No human is being impersonated. Disclosure per FTC 16 CFR Part 255.",
       font=font_sm, fill=(200, 200, 200, 220))

# Right-side timecode-ish tag
tag = "LIVE  23:47  /  2026-04-13"
try:
    tw = d.textlength(tag, font=font_reg)
except AttributeError:
    tw, _ = font_reg.getsize(tag)
d.text((W - tw - PADX, y_top + 28), tag, font=font_reg, fill=(255, 210, 120, 235))

out = BASE / "overlay_lower_third.png"
img.save(out)
print(f"wrote {out} ({out.stat().st_size} bytes)")
