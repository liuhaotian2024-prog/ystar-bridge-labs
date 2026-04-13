#!/usr/bin/env python3
"""
Y*video Long Video Generation — Mission 2 main pipeline.

Uses CogVideoX-2B text-to-video on Mac M4 (with MPS + VAE tiling).
Generates all 6 segments of TL-008 storyboard sequentially.
Applies YGVCC physical alignment to maintain consistency with stage1A.
Concatenates seamlessly (no title cards).

Pipeline per segment:
  1. CogVideoX-2B text-to-video generates 6s clip from prompt
  2. physical_align_pipeline with stage1A as reference (color/tone consistency)
  3. Save segment

Final: concat all 6 segments + the original stage1A as seed
"""
import sys, os, time
import torch
import numpy as np
import cv2
from PIL import Image
import imageio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from physical_align import physical_align_pipeline

# TL-008 prompts (English)
SEGMENTS = [
    {
        'name': '1B_chest',
        'prompt': 'photorealistic close-up of confident asian woman in red silk blouse standing in modern brick office, professional studio lighting, detailed face, natural skin texture, sharp focus',
        'num_frames': 25,
    },
    {
        'name': '2_product',
        'prompt': 'photorealistic asian woman in red silk blouse smiling at camera in modern office with brick walls, soft natural light, detailed facial features, cinematic',
        'num_frames': 25,
    },
    {
        'name': '3_missions',
        'prompt': 'photorealistic asian woman in red silk blouse looks confidently at camera, brick office background, warm cinematic lighting, sharp focus on face',
        'num_frames': 25,
    },
    {
        'name': '4_team',
        'prompt': 'photorealistic asian woman in red silk blouse stands facing camera in modern brick office, warm light, detailed and sharp',
        'num_frames': 25,
    },
    {
        'name': '5_world',
        'prompt': 'photorealistic asian woman in red silk blouse smiles warmly at camera, brick office, professional photography, sharp detailed face',
        'num_frames': 25,
    },
    {
        'name': '6_ending',
        'prompt': 'photorealistic asian woman in red silk blouse looks at camera with friendly expression, modern office background, cinematic lighting, sharp and detailed',
        'num_frames': 25,
    },
]


def patch_to_float32(module):
    """Recursively convert all float64 buffers to float32 (MPS compat)."""
    for name, buf in module.named_buffers(recurse=False):
        if buf is not None and buf.dtype == torch.float64:
            module.register_buffer(name, buf.to(torch.float32))
    for child in module.children():
        patch_to_float32(child)


def main():
    print("Y*video Long Video Generation (Mission 2)")
    print("="*60)

    output_dir = "docs/cogvideo_long"
    os.makedirs(output_dir, exist_ok=True)

    print("Loading CogVideoX-2B...")
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

    # Reference frame from stage1A (for physical alignment)
    print("\nLoading stage1A reference frame...")
    ref_frame = cv2.imread("/tmp/stage1A_last_real.png")
    if ref_frame is None:
        # Re-extract
        cap = cv2.VideoCapture("docs/layer1_stage1A_hq.mp4")
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, n - 5)
        ret, ref_frame = cap.read()
        cap.release()
        cv2.imwrite("/tmp/stage1A_last_real.png", ref_frame)
    print(f"Reference frame: {ref_frame.shape}")

    # Generate each segment
    generated_paths = []
    for i, seg in enumerate(SEGMENTS):
        print(f"\n[{i+1}/{len(SEGMENTS)}] {seg['name']}")
        print(f"  prompt: {seg['prompt']}")

        t0 = time.time()
        try:
            result = pipe(
                prompt=seg['prompt'],
                num_frames=seg['num_frames'],
                height=320,
                width=480,
                num_inference_steps=20,  # bumped from 8 for quality
                guidance_scale=7.0,  # slightly higher for prompt adherence
            )
            gen_time = time.time() - t0
            print(f"  generated {seg['num_frames']} frames in {gen_time:.0f}s")
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            continue

        frames = result.frames[0]

        # Apply YGVCC physical alignment
        print(f"  applying YGVCC physical alignment...")
        # Resize ref frame to match
        ref_resized = cv2.resize(ref_frame, (480, 320))
        aligned_frames = []
        for pil_frame in frames:
            bgr = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
            aligned = physical_align_pipeline(
                bgr, ref_resized,
                histogram_strength=0.7,
                detail_strength=0.0,
                black_crush=0.4,
                highlight_compress=0.3,
                midtone_contrast=0.15,
                color_transfer_strength=0.5,
            )
            aligned_frames.append(cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB))

        # Save segment
        seg_path = f"{output_dir}/{i+1:02d}_{seg['name']}.mp4"
        with imageio.get_writer(seg_path, fps=8, codec='libx264', quality=9) as writer:
            for f in aligned_frames:
                writer.append_data(f)
        generated_paths.append(seg_path)
        print(f"  saved: {seg_path}")

    # Concatenate all segments seamlessly
    print(f"\n[FINAL] Concatenating {len(generated_paths)} segments...")
    concat_list_path = f"{output_dir}/concat.txt"
    with open(concat_list_path, 'w') as f:
        for p in generated_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    final_path = f"{output_dir}/long_video_FINAL.mp4"
    import subprocess
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_list_path,
        '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '18',
        '-pix_fmt', 'yuv420p',
        final_path
    ], capture_output=True)

    cap = cv2.VideoCapture(final_path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    print(f"\nFINAL: {final_path}")
    print(f"  {n} frames @ {fps:.1f}fps = {n/fps:.1f}s")


if __name__ == '__main__':
    main()
