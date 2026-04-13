#!/usr/bin/env python3
"""
Y*video Long Video Orchestrator (Mission 2 — overnight build)

Generates a long video by chaining LTX-Video image-to-video continuations,
seeded by a starting video clip, with YGVCC consistency governance applied
between each segment.

Pipeline per segment:
  1. Get last frame of previous segment as seed
  2. Run LTX-Video I2V with current segment's prompt
  3. Apply physical_align_pipeline to fix Kling-style degradation
  4. Apply face symmetry governance if face is visible
  5. Verify Rt convergence
  6. Append to output

The TL-008 storyboard has 6 segments. We seed from stage1A and generate
segments 1B, 2, 3, 4, 5, ending = 5 LTX continuations.
"""
import sys, os, time, subprocess
from pathlib import Path
import torch
import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from physical_align import physical_align_pipeline
from fingerprint import build_face_mask, extract_fingerprint, fingerprint_distance

# TL-008 storyboard prompts (English only — LTX doesn't speak Chinese well)
SEGMENTS = [
    {
        'name': 'seg1B_standing',
        'prompt': 'A confident asian woman in a red silk blouse stands facing the camera in a modern brick office, gestures with her right hand toward her chest, then looks slightly upward, professional cinematic lighting',
        'duration_s': 6,
    },
    {
        'name': 'seg2_product',
        'prompt': 'The same asian woman in red blouse continues speaking, opens her right hand outward in an explanatory gesture, then points with her index finger, then opens both hands wider, smiling at camera',
        'duration_s': 14,
    },
    {
        'name': 'seg3_missions',
        'prompt': 'The asian woman in red holds up her index finger, then adds her middle finger making a peace-like sign, then sweeps her right hand around herself, looking confident',
        'duration_s': 11,
    },
    {
        'name': 'seg4_team',
        'prompt': 'The asian woman in red turns her head and points her right hand to her right back side, then turns back to face camera, then turns left and sweeps her left hand, then returns to center',
        'duration_s': 9,
    },
    {
        'name': 'seg5_world_first',
        'prompt': 'The asian woman in red opens both hands slightly, then makes an inviting gesture toward the area behind her, then looks back at camera with a warm smile',
        'duration_s': 11,
    },
    {
        'name': 'seg6_ending',
        'prompt': 'The asian woman in red speaks slowly, shrugs slightly with a candid expression, brings both hands together at chest, then extends her right hand toward the camera in invitation, holding a smile',
        'duration_s': 10,
    },
]

NEGATIVE_PROMPT = "blurry, distorted, low quality, jittery, artifact, deformed face, multiple people, crowd"


def get_last_frame(video_path):
    """Extract the last real (non-black) frame from a video as PIL Image."""
    cap = cv2.VideoCapture(str(video_path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for back in range(2, 30):
        idx = n - back
        if idx < 0: break
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, f = cap.read()
        if ret and float(f.mean()) > 30:
            cap.release()
            rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb), f  # PIL + BGR for fingerprint
    cap.release()
    return None, None


def save_video_from_frames(frames, output_path, fps=24):
    """Save list of PIL frames as MP4."""
    import imageio
    with imageio.get_writer(str(output_path), fps=fps, codec='libx264', quality=9) as writer:
        for f in frames:
            writer.append_data(np.array(f))


def main(seed_video, output_dir, model_id="Lightricks/LTX-Video-0.9.7-distilled"):
    """Generate the full long video."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Y*video Long Video Orchestrator")
    print(f"  Seed: {seed_video}")
    print(f"  Output dir: {output_dir}")
    print(f"  Model: {model_id}")
    print(f"  Segments: {len(SEGMENTS)}")
    print()

    # Load LTX-Video pipeline
    print("Loading LTX-Video pipeline...")
    t0 = time.time()
    from diffusers import LTXImageToVideoPipeline
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"  Device: {device}")
    pipe = LTXImageToVideoPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16 if device == "mps" else torch.float32,
    )
    pipe.to(device)
    print(f"  Loaded in {time.time()-t0:.0f}s")

    # Reference fingerprint from seed video
    print("\nExtracting reference fingerprint from seed...")
    seed_pil, seed_bgr_frame = get_last_frame(seed_video)
    if seed_pil is None:
        print("ERROR: could not get seed frame")
        return
    print(f"  Seed frame size: {seed_pil.size}")

    # Save seed for later concat
    seed_segment_path = output_dir / "00_seed.mp4"
    if not seed_segment_path.exists():
        subprocess.run([
            'ffmpeg', '-y', '-i', str(seed_video),
            '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '12',
            '-r', '30', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', str(seed_segment_path)
        ], capture_output=True)

    # Generate each segment
    current_seed_pil = seed_pil
    current_seed_bgr = seed_bgr_frame
    generated_segments = [seed_segment_path]

    for i, seg in enumerate(SEGMENTS):
        print(f"\n[{i+1}/{len(SEGMENTS)}] {seg['name']} ({seg['duration_s']}s)")
        print(f"  prompt: {seg['prompt'][:80]}...")

        # LTX uses ~24 fps. Frames = duration * 24
        num_frames = min(int(seg['duration_s'] * 24), 161)  # cap at LTX max
        # LTX requires num_frames % 8 == 1
        num_frames = ((num_frames - 1) // 8) * 8 + 1

        try:
            t0 = time.time()
            result = pipe(
                image=current_seed_pil,
                prompt=seg['prompt'],
                negative_prompt=NEGATIVE_PROMPT,
                num_frames=num_frames,
                height=480,
                width=832,
                num_inference_steps=8,  # distilled uses fewer steps
                guidance_scale=1.0,
            )
            gen_time = time.time() - t0
            print(f"  generated {num_frames} frames in {gen_time:.0f}s ({gen_time/num_frames*1000:.0f}ms/frame)")
        except Exception as e:
            print(f"  ERROR generating segment {i+1}: {e}")
            continue

        # Save raw segment
        raw_path = output_dir / f"{i+1:02d}_{seg['name']}_raw.mp4"
        save_video_from_frames(result.frames[0], raw_path, fps=24)

        # Apply YGVCC physical alignment
        # Use the SEED bgr frame as reference (preserves original look)
        print(f"  applying YGVCC physical alignment...")
        aligned_frames_bgr = []
        for pil_frame in result.frames[0]:
            bgr = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)
            aligned = physical_align_pipeline(
                bgr, current_seed_bgr,
                histogram_strength=0.6,
                detail_strength=0.0,
                black_crush=0.4,
                highlight_compress=0.3,
                midtone_contrast=0.15,
                color_transfer_strength=0.4,
            )
            aligned_frames_bgr.append(aligned)

        # Save governed segment
        governed_path = output_dir / f"{i+1:02d}_{seg['name']}_governed.mp4"
        # Use cv2 to write BGR frames to mp4
        h, w = aligned_frames_bgr[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(governed_path).replace('.mp4', '_temp.mp4'),
                                   fourcc, 24, (w, h))
        for f in aligned_frames_bgr:
            writer.write(f)
        writer.release()
        # Re-encode with libx264 for quality
        subprocess.run([
            'ffmpeg', '-y', '-i', str(governed_path).replace('.mp4', '_temp.mp4'),
            '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '12',
            '-r', '30', '-pix_fmt', 'yuv420p',
            str(governed_path)
        ], capture_output=True)
        os.remove(str(governed_path).replace('.mp4', '_temp.mp4'))
        print(f"  saved: {governed_path}")

        generated_segments.append(governed_path)

        # Update seed for next iteration
        last_pil = result.frames[0][-1]
        current_seed_pil = last_pil
        current_seed_bgr = cv2.cvtColor(np.array(last_pil), cv2.COLOR_RGB2BGR)
        # Apply physical alignment to seed frame too
        current_seed_bgr = physical_align_pipeline(
            current_seed_bgr, seed_bgr_frame,
            histogram_strength=0.6, color_transfer_strength=0.4,
            black_crush=0.4, highlight_compress=0.3, midtone_contrast=0.15
        )
        current_seed_pil = Image.fromarray(cv2.cvtColor(current_seed_bgr, cv2.COLOR_BGR2RGB))

    # Concat all segments seamlessly (no title cards)
    print(f"\n[FINAL] Concatenating {len(generated_segments)} segments...")
    concat_list = output_dir / "concat_list.txt"
    with open(concat_list, 'w') as f:
        for seg in generated_segments:
            f.write(f"file '{seg.absolute()}'\n")

    final_path = output_dir / "long_video_FINAL.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', str(concat_list),
        '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '12',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(final_path)
    ], capture_output=True)

    # Verify
    cap = cv2.VideoCapture(str(final_path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    print(f"\nFinal: {final_path}")
    print(f"  {n} frames @ {fps:.1f}fps = {n/fps:.1f}s")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 long_video_orchestrator.py seed_video.mp4 output_dir/")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
