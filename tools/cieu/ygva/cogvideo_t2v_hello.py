#!/usr/bin/env python3
"""
CogVideoX-2B Text-to-Video hello-world (validates model works on Mac M4).
"""
import sys, time
import torch
from PIL import Image
import numpy as np
import imageio

print(f"PyTorch: {torch.__version__}")
# MPS doesn't support float64 — use sequential CPU offload to avoid the issue
# CPU is slower but works correctly on Apple Silicon
device = "cpu"
print(f"Device: {device} (forced — MPS has float64 buffer issues)")

print("\nLoading CogVideoX-2B text-to-video pipeline...")
t0 = time.time()
from diffusers import CogVideoXPipeline
pipe = CogVideoXPipeline.from_pretrained(
    "THUDM/CogVideoX-2b",
    torch_dtype=torch.float32,  # use float32 for CPU
)
pipe.to("cpu")
print(f"Loaded in {time.time()-t0:.0f}s")

prompt = "A confident asian woman in a red silk blouse stands in a modern brick office facing camera, her expression calm and professional, soft natural lighting"

print(f"\nGenerating...")
t0 = time.time()
result = pipe(
    prompt=prompt,
    num_frames=49,
    height=480,
    width=720,
    num_inference_steps=30,
    guidance_scale=6.0,
)
print(f"Generated in {time.time()-t0:.0f}s")

frames = result.frames[0]
out_path = "/Users/haotianliu/.openclaw/workspace/ystar-company/docs/cogvideo_t2v_hello.mp4"
with imageio.get_writer(out_path, fps=8, codec='libx264', quality=9) as writer:
    for f in frames:
        writer.append_data(np.array(f))
print(f"Saved: {out_path}")
