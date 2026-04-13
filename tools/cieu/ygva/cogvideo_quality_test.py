#!/usr/bin/env python3
"""
Single segment quality test — 30 steps + larger dims to verify CogVideoX-2B
can produce GOOD quality on Mac M4.
"""
import sys, time, os
import torch
import numpy as np
import cv2
import imageio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def patch_to_float32(module):
    for name, buf in module.named_buffers(recurse=False):
        if buf is not None and buf.dtype == torch.float64:
            module.register_buffer(name, buf.to(torch.float32))
    for child in module.children():
        patch_to_float32(child)

print("Loading CogVideoX-2B for quality test...")
t0 = time.time()
from diffusers import CogVideoXPipeline
pipe = CogVideoXPipeline.from_pretrained(
    "THUDM/CogVideoX-2b",
    torch_dtype=torch.float16,
)
patch_to_float32(pipe.transformer)
patch_to_float32(pipe.vae)
patch_to_float32(pipe.text_encoder)
pipe.to("mps")
pipe.vae.enable_tiling()
pipe.vae.enable_slicing()
print(f"Loaded in {time.time()-t0:.0f}s")

# Larger dim + more steps = better quality
prompt = "A confident asian woman in red silk blouse stands in modern brick office, gestures with right hand, professional cinematic lighting, photorealistic"

print(f"\nGenerating quality test (30 steps, 480x320, 49 frames)...")
t0 = time.time()
result = pipe(
    prompt=prompt,
    num_frames=49,
    height=320,
    width=480,
    num_inference_steps=30,
    guidance_scale=6.0,
)
print(f"Generated in {time.time()-t0:.0f}s")

frames = result.frames[0]
out_path = "/Users/haotianliu/.openclaw/workspace/ystar-company/docs/cogvideo_quality_test.mp4"
with imageio.get_writer(out_path, fps=8, codec='libx264', quality=9) as writer:
    for f in frames:
        writer.append_data(np.array(f))
print(f"Saved: {out_path}")
