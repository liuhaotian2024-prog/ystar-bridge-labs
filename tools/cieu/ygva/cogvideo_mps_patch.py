#!/usr/bin/env python3
"""
CogVideoX-2B on Mac M4 with MPS, patching the float64 buffer issue.

The issue: CogVideoX has scheduler/transformer buffers in float64 which
MPS doesn't support. We patch by converting all buffers to float32 before
moving to MPS.
"""
import sys, time
import torch
from PIL import Image
import numpy as np
import imageio

print(f"PyTorch: {torch.__version__}")
device = "mps"
print(f"Device: {device}")

def patch_to_float32(module):
    """Recursively convert all float64 buffers/params to float32."""
    for name, buf in module.named_buffers(recurse=False):
        if buf is not None and buf.dtype == torch.float64:
            module.register_buffer(name, buf.to(torch.float32))
    for name, param in module.named_parameters(recurse=False):
        if param is not None and param.dtype == torch.float64:
            param.data = param.data.to(torch.float32)
    for child in module.children():
        patch_to_float32(child)

print("\nLoading CogVideoX-2B...")
t0 = time.time()
from diffusers import CogVideoXPipeline
pipe = CogVideoXPipeline.from_pretrained(
    "THUDM/CogVideoX-2b",
    torch_dtype=torch.float16,  # use fp16 for MPS efficiency
)
# Patch all components
print("Patching float64 buffers to float32...")
for component_name in ['transformer', 'vae', 'text_encoder']:
    component = getattr(pipe, component_name, None)
    if component is not None:
        patch_to_float32(component)

# Move to MPS
pipe.to(device)
# Memory savings: VAE tiling + slicing (24GB unified memory is tight)
pipe.vae.enable_tiling()
pipe.vae.enable_slicing()
print(f"Loaded + patched + VAE tiling/slicing in {time.time()-t0:.0f}s")

# Smallest possible config
prompt = "asian woman in red blouse standing in office, soft lighting"

print(f"\nGenerating MINIMAL test (8 steps, small dims)...")
t0 = time.time()
try:
    result = pipe(
        prompt=prompt,
        num_frames=9,  # smallest CogVideoX accepts (4n+1)
        height=320,  # multiple of 32
        width=480,   # multiple of 32 (CogVideoX needs specific dims)
        num_inference_steps=8,
        guidance_scale=6.0,
    )
    gen_time = time.time() - t0
    print(f"Generated in {gen_time:.0f}s")

    frames = result.frames[0]
    out_path = "/Users/haotianliu/.openclaw/workspace/ystar-company/docs/cogvideo_mps_hello.mp4"
    with imageio.get_writer(out_path, fps=8, codec='libx264', quality=9) as writer:
        for f in frames:
            writer.append_data(np.array(f))
    print(f"Saved: {out_path}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
