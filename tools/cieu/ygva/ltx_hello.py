#!/usr/bin/env python3
"""
LTX-Video hello-world on Mac M4 — Mission 2 first milestone

Generate a 4-second video continuation from stage1A's last frame as seed.
Uses LTX-Video-0.9.7-distilled (smallest variant, ~6GB).
"""
import sys, os, time
import torch
import cv2
from PIL import Image

print(f"PyTorch: {torch.__version__}")
print(f"MPS available: {torch.backends.mps.is_available()}")
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# Load seed image: stage1A's last real frame
SEED_PATH = "/tmp/stage1A_last_real.png"
if not os.path.exists(SEED_PATH):
    print(f"ERROR: Seed image not found at {SEED_PATH}")
    sys.exit(1)
seed_pil = Image.open(SEED_PATH).convert("RGB")
print(f"Seed image: {seed_pil.size}")

# Load pipeline — use LTXConditionPipeline (matches model_index.json)
print("\nLoading LTX-Video-0.9.7-distilled...")
t0 = time.time()
from diffusers import LTXConditionPipeline
pipe = LTXConditionPipeline.from_pretrained(
    "Lightricks/LTX-Video-0.9.7-distilled",
    torch_dtype=torch.bfloat16 if device == "mps" else torch.float32,
)
# Enable CPU offload to fit in 24GB unified memory (T5XXL alone is 10GB)
try:
    pipe.enable_model_cpu_offload()
    print("CPU offload enabled")
except Exception as e:
    print(f"CPU offload failed: {e}, trying .to(device)")
    pipe.to(device)
print(f"Pipeline loaded in {time.time()-t0:.1f}s")

# Generate
prompt = "A confident asian woman in red shirt walks toward the camera in a modern brick office, then stops and gestures with her right hand toward her chest, professional lighting, cinematic"
negative_prompt = "blurry, distorted, low quality, jittery, artifact"

print(f"\nGenerating...")
print(f"Prompt: {prompt}")
t0 = time.time()
result = pipe(
    image=seed_pil,
    prompt=prompt,
    negative_prompt=negative_prompt,
    num_frames=97,  # ~4 seconds at 24fps
    height=480,
    width=832,
    num_inference_steps=8,  # distilled version uses fewer steps
    guidance_scale=1.0,
)
gen_time = time.time() - t0
print(f"Generation took {gen_time:.1f}s ({gen_time/97*1000:.0f}ms per frame)")

# Save as video
out_path = "/Users/haotianliu/.openclaw/workspace/ystar-company/docs/ltx_hello_continuation.mp4"
frames = result.frames[0]
import numpy as np
import imageio
with imageio.get_writer(out_path, fps=24, codec='libx264', quality=8) as writer:
    for f in frames:
        writer.append_data(np.array(f))

print(f"Saved: {out_path}")
print(f"Total time: {time.time()-t0:.1f}s")
