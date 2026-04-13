#!/usr/bin/env python3
"""
YGVCC Framework Validity Test — recover Kling-drifted segments to their own
2-second anchor.

Anchor: first 2s of stage1B (clean Kling output baseline).
Input:  rest of stage1B + stage2 (Kling's natural drift over time).
Goal:   make the input look like the anchor.

This is a TRUE blind test because:
1. All videos come from Kling (we didn't corrupt anything)
2. We don't know what Kling's degradation path is
3. The anchor is just 2 seconds of clean Kling output
4. YGVCC only sees the fingerprint of anchor and input — no degradation params

Pipeline per frame:
1. histogram_match (to anchor average histogram)
2. reinhard_color_transfer (LAB mean+std match)
3. adaptive_sharpen (target = anchor's sharpness, with bisection + multi-metric bound)
"""
import sys, os, subprocess, tempfile, shutil
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from physical_align import histogram_match, reinhard_color_transfer
from sharpen_align import iterative_sharpen, measure_sharpness
from fingerprint_v2 import extract_v2_fingerprint, DEFAULT_V2_WEIGHTS


def compute_rt_to_target(src_fp, target_fp):
    """Weighted L2 excluding face false-positives."""
    EXCLUDE_FACE = ['Yf_mean','Yf_p99','R_face','B_face','color_temp_f','sat_f',
                    'Yf_TL','Yf_TR','Yf_BL','Yf_BR','Yf_LR_diff','R_LR_diff','sat_LR_diff',
                    'face_sharpness','skin_L','skin_a','skin_b',
                    'face_size_pct','face_aspect','face_center_x','face_center_y',
                    'Rf_highlight','warmth_highlight']
    weighted_sq = 0.0
    for k in target_fp:
        if k == 'has_face' or not isinstance(target_fp.get(k), (int, float)):
            continue
        if k in EXCLUDE_FACE or k not in src_fp:
            continue
        d = src_fp[k] - target_fp[k]
        w = DEFAULT_V2_WEIGHTS.get(k, 1.0)
        weighted_sq += w * d * d
    return float(np.sqrt(weighted_sq))


def get_anchor_stats(anchor_path):
    """Compute reference stats from the anchor video."""
    cap = cv2.VideoCapture(anchor_path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    for i in range(n):
        ret, f = cap.read()
        if ret:
            frames.append(f)
    cap.release()

    # Representative frame: middle of anchor
    rep_frame = frames[len(frames) // 2]
    target_sharpness = float(np.mean([measure_sharpness(f) for f in frames]))
    return rep_frame, target_sharpness, frames


def recover_frame(frame, anchor_frame, target_sharpness):
    """Apply 3-layer pipeline: histogram + reinhard + adaptive sharpen."""
    # Layer 1: histogram match to anchor
    l1 = histogram_match(frame, anchor_frame, strength=0.8)
    # Layer 2: reinhard color transfer (LAB match)
    l2 = reinhard_color_transfer(l1, anchor_frame, strength=0.6)
    # Layer 3: adaptive sharpen (to anchor's sharpness level)
    l3 = iterative_sharpen(l2, target_lap_var=target_sharpness,
                             max_iter=6, sigma=1.5)
    return l3


def recover_video(input_path, anchor_path, output_path):
    print(f"Loading anchor: {anchor_path}")
    anchor_frame, target_sharp, _ = get_anchor_stats(anchor_path)
    print(f"  Target sharpness: {target_sharp:.1f}")
    print(f"  Reference frame shape: {anchor_frame.shape}")

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Processing {n} frames from {input_path}...")

    tmpdir = tempfile.mkdtemp()
    for i in range(n):
        ret, frame = cap.read()
        if not ret: break
        recovered = recover_frame(frame, anchor_frame, target_sharp)
        cv2.imwrite(os.path.join(tmpdir, f'f_{i:05d}.png'), recovered)
        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{n}")
    cap.release()

    # Probe audio duration for precise fps
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
    if len(sys.argv) < 4:
        print("Usage: python3 recover_to_anchor.py input.mp4 anchor.mp4 output.mp4")
        sys.exit(1)
    recover_video(sys.argv[1], sys.argv[2], sys.argv[3])
