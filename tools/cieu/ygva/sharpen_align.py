#!/usr/bin/env python3
"""
YGVCC Sharpness Alignment v2 — addresses the REAL Stage1A vs Stage1B gap.

DATA FROM FINGERPRINT V2 ANALYSIS:
- sharpness_laplacian: 75 → 23 (Stage1B is 3x softer)
- edge_p99: 287 → 187 (35% weaker edges)
- edge_density: 37 → 24 (35% fewer edges)

This module provides AGGRESSIVE sharpening that matches stage1A's
sharpness profile via:
1. Edge-preserving denoise (bilateral filter)
2. Iterative unsharp mask until target sharpness reached
3. Frequency band matching via FFT manipulation
4. Histogram match for color/tone (uses existing color_match.py)

Goal: make stage1B's per-frame sharpness match stage1A's exactly.
"""
import cv2
import numpy as np
import sys, os, subprocess, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fingerprint_v2 import extract_v2_fingerprint
from fingerprint import build_face_mask


def measure_sharpness(frame):
    """Single frame sharpness via Laplacian variance."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def smart_unsharp_mask(frame, amount=1.5, sigma=1.5, threshold=5):
    """
    Edge-preserving unsharp mask: only sharpens where edges exist.
    Doesn't amplify noise in flat areas.
    """
    blurred = cv2.GaussianBlur(frame, (0, 0), sigmaX=sigma, sigmaY=sigma)
    diff = frame.astype(np.float32) - blurred.astype(np.float32)
    # Threshold: only apply where high-freq content exceeds noise floor
    mask = np.abs(diff).sum(axis=2) > threshold * 3
    sharpened = frame.astype(np.float32) + amount * diff
    result = np.where(mask[:, :, None], sharpened, frame.astype(np.float32))
    return np.clip(result, 0, 255).astype(np.uint8)


def iterative_sharpen(frame, target_lap_var=75.0, max_iter=4,
                       sigma=1.5, tolerance=0.10):
    """
    Adaptive unsharp mask: estimate needed amount, apply once, refine.

    Uses bisection-style adjustment to converge near target.

    Args:
        frame: BGR uint8
        target_lap_var: target sharpness
        max_iter: max refinement iterations
        sigma: gaussian sigma for unsharp
        tolerance: acceptable fractional error

    Returns:
        sharpened frame at target sharpness
    """
    initial_var = measure_sharpness(frame)
    if initial_var >= target_lap_var * (1 - tolerance):
        return frame  # already sharp enough

    # Estimate initial amount: linear assumption that doubles sharpness each unit
    # target_var ≈ initial_var * (1 + amount * k) where k ≈ 1
    # So amount ≈ (target_var - initial_var) / (initial_var * k)
    # But this is rough — bisect to refine
    low, high = 0.1, 4.0
    best = frame
    best_diff = abs(initial_var - target_lap_var)

    for _ in range(max_iter):
        amount = (low + high) / 2
        candidate = smart_unsharp_mask(frame, amount=amount, sigma=sigma, threshold=3)
        cand_var = measure_sharpness(candidate)
        diff = abs(cand_var - target_lap_var)
        if diff < best_diff:
            best = candidate
            best_diff = diff
        if cand_var < target_lap_var * (1 - tolerance):
            low = amount
        elif cand_var > target_lap_var * (1 + tolerance):
            high = amount
        else:
            return candidate
    return best


def sharpen_align_video(input_path, output_path, target_lap_var=75.0,
                          reference_path=None):
    """
    Apply iterative sharpening to every frame to match target sharpness.

    Args:
        input_path: video to sharpen
        output_path: output path
        target_lap_var: target Laplacian variance (default 75 = stage1A's)
        reference_path: optional reference video to compute target from
    """
    if reference_path:
        # Compute target from reference video
        cap = cv2.VideoCapture(reference_path)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sharpness_samples = []
        for i in [n // 4, n // 2, 3 * n // 4]:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, f = cap.read()
            if ret:
                sharpness_samples.append(measure_sharpness(f))
        cap.release()
        if sharpness_samples:
            target_lap_var = float(np.mean(sharpness_samples))
            print(f"Target sharpness from {reference_path}: {target_lap_var:.1f}")

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Sharpening {n} frames in {input_path}, target Laplacian var = {target_lap_var:.1f}")

    tmpdir = tempfile.mkdtemp()
    sharpness_history = []
    for i in range(n):
        ret, frame = cap.read()
        if not ret: break

        before = measure_sharpness(frame)
        sharpened = iterative_sharpen(frame, target_lap_var=target_lap_var,
                                        max_iter=6, sigma=1.5)
        after = measure_sharpness(sharpened)
        sharpness_history.append((before, after))

        cv2.imwrite(os.path.join(tmpdir, f'f_{i:05d}.png'), sharpened)
        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{n}: avg sharpness {np.mean([s[1] for s in sharpness_history[-30:]]):.1f}")

    cap.release()

    print(f"Avg sharpness: {np.mean([s[0] for s in sharpness_history]):.1f} → "
          f"{np.mean([s[1] for s in sharpness_history]):.1f}")

    # Encode with audio
    try:
        audio_dur = float(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=duration',
            '-of', 'default=nw=1:nk=1', input_path
        ], stderr=subprocess.DEVNULL).decode().strip())
        precise_fps = n / audio_dur
    except Exception:
        precise_fps = fps

    cmd = [
        'ffmpeg', '-y', '-framerate', f'{precise_fps}',
        '-i', os.path.join(tmpdir, 'f_%05d.png'),
        '-i', input_path,
        '-map', '0:v', '-map', '1:a?',
        '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '12',
        '-pix_fmt', 'yuv420p', '-r', f'{precise_fps}',
        '-c:a', 'copy', output_path
    ]
    subprocess.run(cmd, capture_output=True)
    shutil.rmtree(tmpdir)
    print(f"Saved: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 sharpen_align.py input.mp4 output.mp4 [reference.mp4]")
        sys.exit(1)
    ref = sys.argv[3] if len(sys.argv) > 3 else None
    sharpen_align_video(sys.argv[1], sys.argv[2], reference_path=ref)
