#!/usr/bin/env python3
"""
CogVideoX Sanity Test — 生成 10-sec sample video
CTO: Ethan Wright | 2026-04-15
"""

import os
import sys
from pathlib import Path

def test_via_diffusers():
    """Use diffusers library to generate test video (no ComfyUI UI needed)"""
    try:
        from diffusers import CogVideoXPipeline
        import torch
        from PIL import Image
        import numpy as np

        print("[Sanity Test] Loading CogVideoX-2B via diffusers...")

        # Load model
        pipe = CogVideoXPipeline.from_pretrained(
            "THUDM/CogVideoX-2b",
            torch_dtype=torch.float16,
            variant="fp16"
        )

        # Use MPS (Metal Performance Shaders) on Mac
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")
        pipe = pipe.to(device)

        # Generate video from text prompt
        prompt = "A cat walking on a beach, sunset, cinematic, 4k"
        print(f"Generating video: '{prompt}'")

        video_frames = pipe(
            prompt=prompt,
            num_frames=16,  # ~2-sec at 8 fps
            guidance_scale=6.0,
            num_inference_steps=20  # Fast test (default 50)
        ).frames[0]

        # Save as mp4
        output_dir = Path(__file__).parent.parent / "reports"
        output_path = output_dir / "cogvideox_sanity_test.mp4"

        # Convert frames to video
        from moviepy.editor import ImageSequenceClip
        clip = ImageSequenceClip([np.array(f) for f in video_frames], fps=8)
        clip.write_videofile(str(output_path), codec="libx264")

        print(f"\n=== Sanity Test PASSED ===")
        print(f"Video saved: {output_path}")
        print(f"Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"Frames: {len(video_frames)}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("CogVideoX Sanity Test — Y* Bridge Labs")
    print("=" * 50)

    success = test_via_diffusers()

    if not success:
        print("\nManual test fallback:")
        print("  1. cd ~/comfyui_video/ComfyUI")
        print("  2. source venv/bin/activate")
        print("  3. python main.py")
        print("  4. Open http://127.0.0.1:8188")
        sys.exit(1)

    sys.exit(0)
