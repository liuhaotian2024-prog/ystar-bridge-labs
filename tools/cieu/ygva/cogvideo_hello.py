#!/usr/bin/env python3
"""
CogVideoX-2B hello-world on Mac M4 — Mission 2 backup model

CogVideoX-2B (Apache 2.0, ~13 GB total) is the cleaner license alternative
to LTX-Video which turned out to be ~50 GB (too big for 24 GB Mac).

Generates a 4-second image-to-video continuation from stage1A's last frame.
"""
import sys, os, time
import torch
import cv2
from PIL import Image
import numpy as np
import imageio

print(f"PyTorch: {torch.__version__}")
print(f"MPS available: {torch.backends.mps.is_available()}")
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# Load seed image
SEED_PATH = "/tmp/stage1A_last_real.png"
if not os.path.exists(SEED_PATH):
    print(f"ERROR: Seed image not found at {SEED_PATH}")
    sys.exit(1)
seed_pil = Image.open(SEED_PATH).convert("RGB")
print(f"Seed image: {seed_pil.size}")

# CogVideoX requires specific dimensions: 720x480 for 2b version
seed_pil = seed_pil.resize((720, 480), Image.LANCZOS)
print(f"Resized seed: {seed_pil.size}")

# Load pipeline
print("\nLoading CogVideoX-2B (Apache 2.0)...")
t0 = time.time()
from diffusers import CogVideoXImageToVideoPipeline
pipe = CogVideoXImageToVideoPipeline.from_pretrained(
    "THUDM/CogVideoX-2b",
    torch_dtype=torch.bfloat16 if device == "mps" else torch.float32,
)
# CPU offload to fit in 24GB unified memory
try:
    pipe.enable_model_cpu_offload()
    print("CPU offload enabled")
except Exception as e:
    print(f"CPU offload failed: {e}")
    pipe.to(device)
print(f"Pipeline loaded in {time.time()-t0:.1f}s")

# Generate
prompt = "A confident asian woman in red silk blouse stands in a modern brick office, walks toward camera, then stops and gestures with right hand toward chest, professional cinematic lighting, smooth camera"
negative_prompt = "blurry, distorted, low quality, jittery, multiple people, deformed face"

print(f"\nGenerating 4-second video...")
print(f"Prompt: {prompt[:80]}...")
t0 = time.time()
result = pipe(
    image=seed_pil,
    prompt=prompt,
    negative_prompt=negative_prompt,
    num_frames=49,  # CogVideoX uses 49 frames at ~8fps = 6.1s
    height=480,
    width=720,
    num_inference_steps=30,
    guidance_scale=6.0,
    use_dynamic_cfg=True,
)
gen_time = time.time() - t0
print(f"Generation took {gen_time:.1f}s ({gen_time/49*1000:.0f}ms per frame)")

# Save as video
out_path = "/Users/haotianliu/.openclaw/workspace/ystar-company/docs/cogvideo_hello_continuation.mp4"
frames = result.frames[0]
with imageio.get_writer(out_path, fps=8, codec='libx264', quality=9) as writer:
    for f in frames:
        writer.append_data(np.array(f))

print(f"Saved: {out_path}")
print(f"Total time: {time.time()-t0:.1f}s")
