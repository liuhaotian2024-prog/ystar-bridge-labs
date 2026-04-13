#!/usr/bin/env python3
"""Render per-segment subtitle PNGs (1280x720 RGBA) for Ep.1 fallback build."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = "/Users/haotianliu/.openclaw/workspace/ystar-company"
OUT = f"{ROOT}/content/offended_ai/build/subpng"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# Try common macOS fonts
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
]
def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

SEGS = [
    # (lines, fontsize, y_anchor_frac, big_box)  — big_box=True for disclosure
    (["EXPERIMENTAL AI AGENT TALK SHOW",
      "ACTRESS: SOFIA-CMO  (Y* BRIDGE LABS)",
      "NO REAL HUMAN APPEARS IN THIS VIDEO"], 46, 0.50, True),
    (["OFFENDED, AI", "Episode 1"], 64, 0.72, False),
    (["We built governance for AI agents."], 42, 0.74, False),
    (["CEO bypassed CTO.",
      "Talked to the engineer directly."], 42, 0.72, False),
    (["VIOLATION DETECTED."], 58, 0.72, False),
    (["CIEU_LOG",
      "CEO_UNAUTHORIZED_TASK_ASSIGNMENT",
      "DENIED_BY_OWN_CONTRACT"], 38, 0.70, False),
    (["Audited by his own product."], 46, 0.74, False),
    (['"This is exactly what I built it for."'], 40, 0.74, False),
    (["Y*gov works."], 72, 0.72, False),
    (["OFFENDED, AI   -   AI-generated content",
      "Y* Bridge Labs   -   @OffendedAI"], 38, 0.70, False),
]

WATERMARK = "AI-GENERATED  -  SOFIA-CMO (AI AGENT)  -  Y* BRIDGE LABS"

def draw_text_block(draw, lines, fontsize, y_anchor_frac, big_box):
    font = load_font(fontsize)
    # Compute block size
    line_h = int(fontsize * 1.25)
    widths = []
    for ln in lines:
        bbox = draw.textbbox((0,0), ln, font=font)
        widths.append(bbox[2]-bbox[0])
    block_w = max(widths)
    block_h = line_h * len(lines)
    pad_x = 40
    pad_y = 24
    box_w = block_w + pad_x*2
    box_h = block_h + pad_y*2
    x0 = (W - box_w)//2
    y_center = int(H * y_anchor_frac)
    y0 = y_center - box_h//2
    alpha = 220 if big_box else 160
    draw.rectangle([x0, y0, x0+box_w, y0+box_h], fill=(0,0,0,alpha))
    ty = y0 + pad_y
    for ln, w in zip(lines, widths):
        tx = (W - w)//2
        draw.text((tx, ty), ln, font=font, fill=(255,255,255,255))
        ty += line_h

def draw_watermark(draw):
    font = load_font(22)
    bbox = draw.textbbox((0,0), WATERMARK, font=font)
    w = bbox[2]-bbox[0]; h = bbox[3]-bbox[1]
    pad = 12
    box_w = w + pad*2
    box_h = h + pad*2 + 6
    x0 = (W-box_w)//2
    y0 = H - box_h - 18
    draw.rectangle([x0,y0,x0+box_w,y0+box_h], fill=(0,0,0,200))
    draw.text((x0+pad, y0+pad), WATERMARK, font=font, fill=(255, 235, 59, 255))

for i, (lines, fs, yaf, big) in enumerate(SEGS):
    img = Image.new("RGBA", (W, H), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    draw_text_block(dr, lines, fs, yaf, big)
    draw_watermark(dr)
    p = f"{OUT}/sub_{i}.png"
    img.save(p)
    print(f"[png] {p}")

print("[done] subtitles rendered")
