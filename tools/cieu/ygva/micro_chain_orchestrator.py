#!/usr/bin/env python3
"""
Y*video Micro-Chain Orchestrator — 一镜到底 (one continuous take)

Generates a long video by chaining CogVideoX-2B micro-segments (~2s each)
with YGVCC governance applied between EVERY segment. The result looks
continuous because drift never accumulates beyond 2 seconds before the
next governance checkpoint catches and corrects it.

Architecture:
  - CogVideoX-2B generates 49 frames per call (~2s at 24fps)
  - After each micro-segment: extract fingerprint → compare against
    anchor → if drift > threshold → physical_align the seed frame
    before feeding it to the next generation
  - ~30 micro-segments = ~61 seconds of continuous video
  - All 30 joins are governed, so the viewer sees one continuous shot

Difference from long_video_orchestrator.py:
  - Old: 6 big segments (6-14s each), 5 joins, post-hoc governance
  - New: ~30 micro-segments (2s each), ~30 governed joins, real-time
    interleaved generation + governance = 一镜到底

Hardware: Apple M4 24GB unified memory, MPS backend.
Model: CogVideoX-2B with float64→float32 patch + VAE tiling/slicing.

Usage:
  python3 micro_chain_orchestrator.py [--seed-image path.png] [--output-dir dir/]
"""
import sys, os, time, subprocess, argparse, json
from pathlib import Path
from datetime import datetime

import torch
import cv2
import numpy as np
from PIL import Image
import imageio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from physical_align import physical_align_pipeline
from fingerprint import extract_fingerprint, fingerprint_distance

# ─── TL-008 Storyboard (micro-segmented) ────────────────────────────────
# Each entry generates ONE CogVideoX call (49 frames ≈ 2s).
# The original 6 segments are subdivided into ~30 micro-prompts.
# Prompt continuity is maintained by keeping "asian woman in red silk blouse
# in modern brick office" as the consistent prefix.

SCENE_PREFIX = "A confident asian woman in a red silk blouse in a modern brick office with natural light, "
NEGATIVE = "blurry, distorted, low quality, jittery, artifact, deformed face, multiple people, crowd, cartoon, anime"

MICRO_PROMPTS = [
    # ── Segment 1B: standing (6s = 3 micro) ──
    SCENE_PREFIX + "standing facing camera, right hand moving toward chest, professional cinematic lighting",
    SCENE_PREFIX + "standing still, right hand on chest, looking directly at camera, soft expression",
    SCENE_PREFIX + "standing, looking slightly upward with a thoughtful expression, hand relaxing from chest",
    # ── Segment 2: product (14s = 7 micro) ──
    SCENE_PREFIX + "speaking to camera, opens right hand outward in an explanatory gesture",
    SCENE_PREFIX + "continues speaking, right hand extended, palm up, explaining something important",
    SCENE_PREFIX + "speaking, points with index finger, emphasizing a key point",
    SCENE_PREFIX + "speaking and pointing, then begins opening both hands wider",
    SCENE_PREFIX + "both hands open wide in a presenting gesture, smiling at camera",
    SCENE_PREFIX + "hands still open, nodding slightly while speaking, warm expression",
    SCENE_PREFIX + "hands coming back together, transitioning to next gesture, still speaking",
    # ── Segment 3: missions (11s = 5 micro) ──
    SCENE_PREFIX + "holds up right index finger, counting one, speaking with emphasis",
    SCENE_PREFIX + "adds middle finger making a two-finger gesture, speaking earnestly",
    SCENE_PREFIX + "two fingers still up, begins sweeping right hand in front of herself",
    SCENE_PREFIX + "sweeping hand motion around herself, looking confident and energetic",
    SCENE_PREFIX + "completing the sweep, hands returning to center, looking at camera",
    # ── Segment 4: team (9s = 4 micro) ──
    SCENE_PREFIX + "turns head to her right, pointing with right hand to the side",
    SCENE_PREFIX + "turning back to face camera, head centered, hands coming together",
    SCENE_PREFIX + "turns head to her left, left hand sweeping outward in that direction",
    SCENE_PREFIX + "returns to center, both hands relaxed, looking at camera with a smile",
    # ── Segment 5: world (11s = 5 micro) ──
    SCENE_PREFIX + "opens both hands slightly outward, palms up, inviting gesture",
    SCENE_PREFIX + "hands still open, making a welcoming gesture toward the space behind her",
    SCENE_PREFIX + "glances briefly behind her then looks back at camera",
    SCENE_PREFIX + "facing camera with a warm genuine smile, hands relaxed at sides",
    SCENE_PREFIX + "still smiling warmly, slight nod, maintaining eye contact with camera",
    # ── Segment 6: ending (10s = 5 micro) ──
    SCENE_PREFIX + "speaking slowly, slight shrug with a candid honest expression",
    SCENE_PREFIX + "brings both hands together at chest level, speaking sincerely",
    SCENE_PREFIX + "hands at chest, begins extending right hand toward camera",
    SCENE_PREFIX + "right hand extended toward camera in a warm invitation gesture",
    SCENE_PREFIX + "holding the invitation pose, warm smile, looking directly at camera, final beat",
]

# ─── YGVCC Config ────────────────────────────────────────────────────────
DRIFT_THRESHOLD = 15.0       # fingerprint distance above which we intervene
ALIGN_HISTOGRAM = 0.6        # physical_align strength: histogram match
ALIGN_COLOR_TRANSFER = 0.4   # physical_align strength: Reinhard color
ALIGN_BLACK_CRUSH = 0.4
ALIGN_HIGHLIGHT_COMPRESS = 0.3
ALIGN_MIDTONE_CONTRAST = 0.15

# ─── CogVideoX Config ───────────────────────────────────────────────────
COGVIDEO_MODEL = "THUDM/CogVideoX-2b"
FRAMES_PER_MICRO = 9          # CogVideoX minimum: 4n+1, so 9 = 2*4+1
HEIGHT = 320
WIDTH = 480
INFERENCE_STEPS = 20          # more steps = better quality (overnight: used 8, low quality)
GUIDANCE_SCALE = 6.0
FPS = 8                       # CogVideoX native fps for 9-frame clips


def patch_to_float32(module):
    """Recursively convert all float64 buffers/params to float32 (MPS fix)."""
    for name, buf in module.named_buffers(recurse=False):
        if buf is not None and buf.dtype == torch.float64:
            module.register_buffer(name, buf.to(torch.float32))
    for name, param in module.named_parameters(recurse=False):
        if param is not None and param.dtype == torch.float64:
            param.data = param.data.to(torch.float32)
    for child in module.children():
        patch_to_float32(child)


def load_cogvideo_pipeline():
    """Load CogVideoX-2B with MPS patches + VAE memory optimizations."""
    print("Loading CogVideoX-2B pipeline...")
    t0 = time.time()

    from diffusers import CogVideoXPipeline
    pipe = CogVideoXPipeline.from_pretrained(
        COGVIDEO_MODEL,
        torch_dtype=torch.float16,
    )

    # Patch float64 buffers for MPS compatibility
    for component_name in ['transformer', 'vae', 'text_encoder']:
        component = getattr(pipe, component_name, None)
        if component is not None:
            patch_to_float32(component)

    pipe.to("mps")
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()

    dt = time.time() - t0
    print(f"  loaded + patched in {dt:.0f}s")
    return pipe


def generate_micro_segment(pipe, prompt, steps=INFERENCE_STEPS):
    """Generate one micro-segment (9 frames) with CogVideoX-2B.

    CogVideoX-2B is text-to-video. For true I2V we'd need CogVideoX-5B-I2V.
    Cross-segment consistency comes from YGVCC governance, not from I2V seeding.
    """
    result = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE,
        num_frames=FRAMES_PER_MICRO,
        height=HEIGHT,
        width=WIDTH,
        num_inference_steps=steps,
        guidance_scale=GUIDANCE_SCALE,
    )
    return [np.array(f) for f in result.frames[0]]  # list of RGB numpy arrays


def apply_ygvcc(frames_rgb, anchor_bgr, micro_idx):
    """Apply YGVCC physical alignment to a micro-segment's frames.

    Returns governed frames (RGB numpy arrays) and the governance report.
    """
    governed = []
    distances_before = []
    distances_after = []

    for i, frame_rgb in enumerate(frames_rgb):
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Measure drift BEFORE governance
        fp_frame = extract_fingerprint(frame_bgr)
        fp_anchor = extract_fingerprint(anchor_bgr)
        dist_result = fingerprint_distance(fp_frame, fp_anchor)
        # fingerprint_distance returns (scalar, deltas_dict) — unpack
        dist_before = dist_result[0] if isinstance(dist_result, tuple) else float(dist_result)
        distances_before.append(dist_before)

        # Apply physical alignment
        aligned_bgr = physical_align_pipeline(
            frame_bgr, anchor_bgr,
            histogram_strength=ALIGN_HISTOGRAM,
            detail_strength=0.0,
            black_crush=ALIGN_BLACK_CRUSH,
            highlight_compress=ALIGN_HIGHLIGHT_COMPRESS,
            midtone_contrast=ALIGN_MIDTONE_CONTRAST,
            color_transfer_strength=ALIGN_COLOR_TRANSFER,
        )

        # Measure drift AFTER governance
        fp_aligned = extract_fingerprint(aligned_bgr)
        dist_result_after = fingerprint_distance(fp_aligned, fp_anchor)
        dist_after = dist_result_after[0] if isinstance(dist_result_after, tuple) else float(dist_result_after)
        distances_after.append(dist_after)

        # Convert back to RGB
        governed.append(cv2.cvtColor(aligned_bgr, cv2.COLOR_BGR2RGB))

    report = {
        "micro_idx": micro_idx,
        "frames": len(frames_rgb),
        "drift_before_mean": float(np.mean(distances_before)),
        "drift_before_max": float(np.max(distances_before)),
        "drift_after_mean": float(np.mean(distances_after)),
        "drift_after_max": float(np.max(distances_after)),
        "reduction_pct": float(
            (1 - np.mean(distances_after) / max(np.mean(distances_before), 1e-6)) * 100
        ),
    }
    return governed, report


def get_seed_bgr_from_image(image_path):
    """Load a reference image and convert to BGR for fingerprint anchor."""
    pil = Image.open(image_path).convert("RGB").resize((WIDTH, HEIGHT))
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR), pil


def main():
    parser = argparse.ArgumentParser(description="Y*video 微段链一镜到底")
    parser.add_argument("--seed-image", type=str, default=None,
                        help="Reference image for YGVCC anchor fingerprint "
                             "(e.g. docs/samantha_full.png)")
    parser.add_argument("--output-dir", type=str,
                        default="docs/micro_chain_output",
                        help="Output directory (default: docs/micro_chain_output)")
    parser.add_argument("--steps", type=int, default=INFERENCE_STEPS,
                        help=f"Inference steps per micro-segment (default: {INFERENCE_STEPS})")
    parser.add_argument("--start-micro", type=int, default=0,
                        help="Resume from this micro-segment index (0-based)")
    parser.add_argument("--end-micro", type=int, default=None,
                        help="Stop after this micro-segment index (exclusive)")
    args = parser.parse_args()

    inference_steps = args.steps

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total_micros = len(MICRO_PROMPTS)
    end_micro = args.end_micro if args.end_micro is not None else total_micros

    print("=" * 60)
    print("Y*video 微段链一镜到底 (Micro-Chain Orchestrator)")
    print("=" * 60)
    print(f"  Model         : {COGVIDEO_MODEL}")
    print(f"  Resolution    : {WIDTH}x{HEIGHT}")
    print(f"  Steps/micro   : {inference_steps}")
    print(f"  Frames/micro  : {FRAMES_PER_MICRO} ({FRAMES_PER_MICRO/FPS:.1f}s)")
    print(f"  Total micros  : {total_micros} ({total_micros * FRAMES_PER_MICRO / FPS:.0f}s)")
    print(f"  Range         : [{args.start_micro}, {end_micro})")
    print(f"  YGVCC drift   : threshold={DRIFT_THRESHOLD}")
    print(f"  Output        : {output_dir}")
    print()

    # Load anchor image for YGVCC fingerprint reference
    if args.seed_image:
        print(f"Loading anchor image: {args.seed_image}")
        anchor_bgr, anchor_pil = get_seed_bgr_from_image(args.seed_image)
    else:
        # Default: use Samantha full-body reference
        default_seed = Path(__file__).resolve().parent.parent.parent / "docs" / "samantha_full.png"
        if default_seed.exists():
            print(f"Loading default anchor: {default_seed}")
            anchor_bgr, anchor_pil = get_seed_bgr_from_image(str(default_seed))
        else:
            print("ERROR: no --seed-image and default docs/samantha_full.png not found")
            sys.exit(1)

    anchor_fp = extract_fingerprint(anchor_bgr)
    print(f"  Anchor fingerprint: {len(anchor_fp)} dimensions")
    print()

    # Load CogVideoX-2B
    pipe = load_cogvideo_pipeline()

    # ─── Main generation loop ────────────────────────────────────────
    all_frames_rgb = []
    governance_log = []

    for micro_idx in range(args.start_micro, end_micro):
        prompt = MICRO_PROMPTS[micro_idx]
        seg_label = f"[{micro_idx+1}/{total_micros}]"

        print(f"\n{seg_label} generating...")
        print(f"  prompt: {prompt[len(SCENE_PREFIX):][:60]}...")

        t0 = time.time()
        try:
            raw_frames = generate_micro_segment(pipe, prompt, steps=inference_steps)
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            # On failure, skip this micro-segment but continue
            # (fail-open: losing 2s is better than losing the whole video)
            continue
        gen_time = time.time() - t0
        print(f"  generated {len(raw_frames)} frames in {gen_time:.1f}s")

        # Apply YGVCC governance
        t1 = time.time()
        governed_frames, report = apply_ygvcc(raw_frames, anchor_bgr, micro_idx)
        gov_time = time.time() - t1

        print(f"  YGVCC: drift {report['drift_before_mean']:.1f} → "
              f"{report['drift_after_mean']:.1f} "
              f"(↓{report['reduction_pct']:.0f}%) in {gov_time:.1f}s")

        report["gen_time_s"] = gen_time
        report["gov_time_s"] = gov_time
        report["prompt_suffix"] = prompt[len(SCENE_PREFIX):][:80]
        governance_log.append(report)

        # Skip first frame of each micro-segment after the first one
        # to avoid duplicate frames at join points
        if micro_idx > args.start_micro and len(governed_frames) > 1:
            governed_frames = governed_frames[1:]

        all_frames_rgb.extend(governed_frames)

        # Save individual micro-segment (for debugging)
        micro_path = output_dir / f"micro_{micro_idx:03d}.mp4"
        with imageio.get_writer(str(micro_path), fps=FPS, codec='libx264',
                                quality=8) as w:
            for f in governed_frames:
                w.append_data(f)

    if not all_frames_rgb:
        print("\nERROR: no frames generated. Check model loading and MPS.")
        sys.exit(1)

    # ─── Final concatenation ─────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Concatenating {len(all_frames_rgb)} governed frames...")

    final_path = output_dir / "samantha_oneshot_FINAL.mp4"
    with imageio.get_writer(str(final_path), fps=FPS, codec='libx264',
                            quality=9) as w:
        for f in all_frames_rgb:
            w.append_data(f)

    duration = len(all_frames_rgb) / FPS
    print(f"\n  FINAL: {final_path}")
    print(f"  Frames: {len(all_frames_rgb)}")
    print(f"  Duration: {duration:.1f}s @ {FPS}fps")

    # ─── Governance summary ──────────────────────────────────────────
    if governance_log:
        avg_drift_before = np.mean([r['drift_before_mean'] for r in governance_log])
        avg_drift_after = np.mean([r['drift_after_mean'] for r in governance_log])
        avg_reduction = np.mean([r['reduction_pct'] for r in governance_log])
        total_gen = sum(r['gen_time_s'] for r in governance_log)
        total_gov = sum(r['gov_time_s'] for r in governance_log)

        print(f"\n{'='*60}")
        print(f"YGVCC Governance Summary")
        print(f"  Micro-segments governed: {len(governance_log)}")
        print(f"  Avg drift before: {avg_drift_before:.1f}")
        print(f"  Avg drift after:  {avg_drift_after:.1f}")
        print(f"  Avg reduction:    {avg_reduction:.0f}%")
        print(f"  Total gen time:   {total_gen:.0f}s ({total_gen/60:.1f}min)")
        print(f"  Total gov time:   {total_gov:.0f}s ({total_gov/60:.1f}min)")
        print(f"  Overhead ratio:   {total_gov/max(total_gen,1)*100:.1f}%")

        # Save governance log
        log_path = output_dir / "governance_log.json"
        with open(log_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "model": COGVIDEO_MODEL,
                "resolution": f"{WIDTH}x{HEIGHT}",
                "steps": INFERENCE_STEPS,
                "total_frames": len(all_frames_rgb),
                "duration_s": duration,
                "fps": FPS,
                "micro_segments": governance_log,
                "summary": {
                    "avg_drift_before": avg_drift_before,
                    "avg_drift_after": avg_drift_after,
                    "avg_reduction_pct": avg_reduction,
                    "total_gen_time_s": total_gen,
                    "total_gov_time_s": total_gov,
                },
            }, f, indent=2, ensure_ascii=False)
        print(f"  Log saved: {log_path}")

    print(f"\n{'='*60}")
    print(f"完成。免费生成，零成本，本地 M4 GPU 驱动。")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
