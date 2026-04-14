#!/usr/bin/env python3
"""Generate v6 lower-third overlay PNG — Colbert-style, white bg, black text,
serif font, full-width, 80px tall.

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

# White opaque band — Colbert lower-third feel
BAND_COLOR = (255, 255, 255, 240)  # white, ~94% opacity
d.rectangle([(0, BAND_Y), (W, BAND_Y + BAND_H)], fill=BAND_COLOR)

# Thin red accent line on top edge
d.rectangle([(0, BAND_Y), (W, BAND_Y + 2)], fill=(180, 30, 30, 250))

# Pick a serif font — Times New Roman, Georgia, or fallback
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/Library/Fonts/Times New Roman.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/Library/Fonts/Georgia.ttf",
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
# Black text on white bg (Colbert rule)
d.text((PADX, y_top), "OFFENDED AI  /  EP 001", font=font_big, fill=(0, 0, 0, 255))
d.text((PADX, y_top + 28), "SOFIA — CMO, Y* BRIDGE LABS  |  AI-GENERATED AVATAR + AI-GENERATED VOICE",
       font=font_reg, fill=(30, 30, 30, 245))
d.text((PADX, y_top + 50), "No human is being impersonated. Disclosure per FTC 16 CFR Part 255.",
       font=font_sm, fill=(60, 60, 60, 230))

# Right-side timecode-ish tag (dark red on white)
tag = "LIVE  23:47  /  2026-04-13"
try:
    tw = d.textlength(tag, font=font_reg)
except AttributeError:
    tw, _ = font_reg.getsize(tag)
d.text((W - tw - PADX, y_top + 28), tag, font=font_reg, fill=(150, 30, 30, 245))

out = BASE / "overlay_lower_third.png"
img.save(out)
print(f"wrote {out} ({out.stat().st_size} bytes)")
