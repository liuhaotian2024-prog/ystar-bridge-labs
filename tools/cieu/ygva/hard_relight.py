#!/usr/bin/env python3
"""
HARD pixel-level face relight — PIXEL OVERPAINT mode.

Unlike previous mirror_face_reference (which blended via mask),
this tool DIRECTLY REPLACES over-bright pixels on one side of the face
with the corresponding mirror pixels from the dark side.

No statistics, no histogram, no blending math — just pixel paint.

Algorithm:
1. Detect face mask (MediaPipe)
2. Find face center (vertical line)
3. For each side of the face:
   - Compute mean Y of left half and right half of face
   - The brighter side is the "over-bright side"
4. Build a "mirror flip" of the dark side
5. For each pixel in the over-bright side that exceeds Y > 130:
   - Replace it with the mirror pixel from the dark side
6. Smooth boundary between original and replaced regions
"""
import cv2
import numpy as np
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fingerprint import build_face_mask


def hard_face_relight(frame, face_mask, soften_radius=20):
    """
    Hard face relight via DIRECT DIMMING to dark side mean.

    No mirror, no histogram. Just compute the dark side's brightness as the
    target, then dim every over-bright pixel on the bright side until it
    matches that target.

    Args:
        frame: BGR uint8
        face_mask: uint8 mask, 255 inside face
        soften_radius: pixel radius for spatial softening

    Returns:
        modified BGR frame
    """
    if face_mask is None or face_mask.sum() == 0:
        return frame

    h, w = frame.shape[:2]
    cols = np.where(face_mask.sum(axis=0) > 0)[0]
    if len(cols) == 0:
        return frame

    cx = (cols[0] + cols[-1]) // 2

    bgr = frame.astype(np.float32)
    Y = 0.114 * bgr[:, :, 0] + 0.587 * bgr[:, :, 1] + 0.299 * bgr[:, :, 2]

    in_face = face_mask > 0
    L_mask = in_face & (np.arange(w)[None, :] < cx)
    R_mask = in_face & (np.arange(w)[None, :] >= cx)

    if not L_mask.any() or not R_mask.any():
        return frame

    Y_left = float(Y[L_mask].mean())
    Y_right = float(Y[R_mask].mean())

    bright_is_left = Y_left > Y_right
    bright_Y = max(Y_left, Y_right)
    dark_Y = min(Y_left, Y_right)

    # If sides are already balanced, return original
    if bright_Y - dark_Y < 8:
        return frame

    # Use MIDPOINT as the target for the bright side (gentle, not extreme)
    # AND lift the dark side toward midpoint too (bilateral equalization)
    midpoint_Y = (bright_Y + dark_Y) / 2.0

    # Build smooth side weights using face center
    x_coords = np.arange(w, dtype=np.float32)
    sigma = max((cols[-1] - cols[0]) * 0.20, 20.0)
    # left_weight: 1 at left, 0 at right (smoothly)
    left_weight = 1.0 / (1.0 + np.exp((x_coords - cx) / sigma))
    right_weight = 1.0 - left_weight
    left_w_2d = np.broadcast_to(left_weight[None, :], (h, w))
    right_w_2d = np.broadcast_to(right_weight[None, :], (h, w))

    # Soft face mask (only modify inside face)
    face_norm = cv2.GaussianBlur(face_mask.astype(np.float32) / 255.0,
                                   (51, 51), 15)
    face_norm = np.clip(face_norm, 0, 1)

    # Per-pixel target: bright side → midpoint, dark side → midpoint
    if bright_is_left:
        # Left is bright → dim left toward midpoint
        bright_w = left_w_2d * face_norm
        dark_w = right_w_2d * face_norm
    else:
        bright_w = right_w_2d * face_norm
        dark_w = left_w_2d * face_norm

    # Bright side: target = midpoint  (will dim it down)
    # Dark side:   target = midpoint  (will lift it up)
    # Outside face: target = current Y (no change)
    target_per_pixel = (Y * (1 - bright_w - dark_w)
                        + midpoint_Y * (bright_w + dark_w))

    # Compute scale ratio per pixel
    ratio = target_per_pixel / np.maximum(Y, 1.0)
    # Cap the ratio to prevent extreme amplification on very dark pixels
    ratio = np.clip(ratio, 0.4, 2.5)

    # Apply ratio to all 3 channels
    new_b = bgr[:, :, 0] * ratio
    new_g = bgr[:, :, 1] * ratio
    new_r = bgr[:, :, 2] * ratio

    out = np.stack([new_b, new_g, new_r], axis=2)
    return np.clip(out, 0, 255).astype(np.uint8)


def hard_relight_video(input_path, output_path, threshold=130):
    """Apply hard relight to every frame in a video."""
    import mediapipe as mp
    import subprocess, tempfile, shutil

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fm = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.3, min_tracking_confidence=0.3,
    )

    # Pre-scan for first usable mask
    last_mask = None
    for _ in range(min(60, n)):
        ret, f = cap.read()
        if not ret: break
        m, has = build_face_mask(f, fm)
        if has:
            last_mask = m
            break
    cap.release()
    cap = cv2.VideoCapture(input_path)

    tmpdir = tempfile.mkdtemp()
    print(f"Processing {n} frames from {input_path}...")
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        m, has = build_face_mask(frame, fm)
        if has:
            last_mask = m
        elif last_mask is not None:
            m = last_mask
        else:
            m = None

        if m is not None and m.sum() > 0:
            relit = hard_face_relight(frame, m, threshold=threshold)
        else:
            relit = frame

        cv2.imwrite(os.path.join(tmpdir, f'f_{frame_idx:05d}.png'), relit)
        frame_idx += 1
        if frame_idx % 30 == 0:
            print(f"  {frame_idx}/{n}")

    cap.release()
    fm.close()

    # Probe audio duration for precise framerate
    try:
        audio_dur = float(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=duration',
            '-of', 'default=nw=1:nk=1', input_path
        ], stderr=subprocess.DEVNULL).decode().strip())
        precise_fps = frame_idx / audio_dur
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
        print("Usage: python3 hard_relight.py input.mp4 output.mp4 [threshold]")
        sys.exit(1)
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 130
    hard_relight_video(sys.argv[1], sys.argv[2], threshold=threshold)
