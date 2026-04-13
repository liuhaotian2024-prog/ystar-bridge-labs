#!/usr/bin/env python3
"""
Segment morphing tool for Y*video.

Two main functions:
1. crop_to_match_framing(): zoom-crop wide shots to match closeup framing
2. optical_flow_morph(): generate intermediate frames between segments
                         using OpenCV optical flow + frame interpolation
"""
import cv2
import numpy as np
import sys
import os
import subprocess
import tempfile
import shutil


def crop_zoom(frame, top_pct=0.0, bottom_pct=0.35,
                left_pct=0.0, right_pct=0.0,
                output_size=None):
    """
    Crop a frame and resize to a target size.

    Args:
        frame: BGR
        top_pct, bottom_pct, left_pct, right_pct: fraction to crop from each edge
        output_size: (w, h) to resize to. If None, output is the cropped size.
    """
    h, w = frame.shape[:2]
    top = int(h * top_pct)
    bottom = int(h * (1 - bottom_pct))
    left = int(w * left_pct)
    right = int(w * (1 - right_pct))
    cropped = frame[top:bottom, left:right]
    if output_size is not None:
        return cv2.resize(cropped, output_size, interpolation=cv2.INTER_LANCZOS4)
    return cropped


def crop_video(input_path, output_path, top_pct=0.0, bottom_pct=0.35,
                 left_pct=0.0, right_pct=0.0, target_size=None):
    """Apply crop+resize to every frame of a video."""
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if target_size is None:
        target_size = (w, h)

    tmpdir = tempfile.mkdtemp()
    print(f"Cropping {n} frames...")
    for i in range(n):
        ret, frame = cap.read()
        if not ret: break
        cropped = crop_zoom(frame, top_pct, bottom_pct, left_pct, right_pct,
                              output_size=target_size)
        cv2.imwrite(os.path.join(tmpdir, f'f_{i:05d}.png'), cropped)
    cap.release()

    # Probe audio
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


def optical_flow_morph(frame_a, frame_b, n_intermediate=8):
    """
    Generate N intermediate frames between frame_a and frame_b using
    optical flow + bidirectional warping.

    Returns:
        list of intermediate frames (n_intermediate frames between a and b)
    """
    gray_a = cv2.cvtColor(frame_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY)

    # Compute bidirectional optical flow
    flow_ab = cv2.calcOpticalFlowFarneback(
        gray_a, gray_b, None,
        pyr_scale=0.5, levels=3, winsize=25,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0
    )
    flow_ba = cv2.calcOpticalFlowFarneback(
        gray_b, gray_a, None,
        pyr_scale=0.5, levels=3, winsize=25,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0
    )

    h, w = frame_a.shape[:2]
    x_grid, y_grid = np.meshgrid(np.arange(w, dtype=np.float32),
                                    np.arange(h, dtype=np.float32))

    intermediates = []
    for i in range(1, n_intermediate + 1):
        t = i / (n_intermediate + 1)  # interpolation factor 0 to 1

        # Warp A forward by t × flow_ab
        map_x_a = x_grid + t * flow_ab[..., 0]
        map_y_a = y_grid + t * flow_ab[..., 1]
        warped_a = cv2.remap(frame_a, map_x_a, map_y_a, cv2.INTER_LINEAR)

        # Warp B backward by (1-t) × flow_ba
        map_x_b = x_grid + (1 - t) * flow_ba[..., 0]
        map_y_b = y_grid + (1 - t) * flow_ba[..., 1]
        warped_b = cv2.remap(frame_b, map_x_b, map_y_b, cv2.INTER_LINEAR)

        # Linear blend
        intermediate = ((1 - t) * warped_a.astype(np.float32) +
                        t * warped_b.astype(np.float32))
        intermediates.append(np.clip(intermediate, 0, 255).astype(np.uint8))

    return intermediates


def concat_with_morphing(segment_paths, output_path, morph_frames=8, fps=30):
    """
    Concatenate multiple segments with optical flow morphing between them.

    Args:
        segment_paths: list of mp4 paths
        output_path: where to write the final mp4
        morph_frames: number of intermediate frames at each boundary
        fps: output framerate
    """
    tmpdir = tempfile.mkdtemp()
    print(f"Concatenating {len(segment_paths)} segments with morphing...")

    frame_idx = 0

    for seg_idx, seg_path in enumerate(segment_paths):
        print(f"  segment {seg_idx+1}/{len(segment_paths)}: {seg_path}")
        cap = cv2.VideoCapture(seg_path)
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Read all frames
        frames = []
        while True:
            ret, f = cap.read()
            if not ret: break
            frames.append(f)
        cap.release()

        # If not first segment, generate morph from previous segment's last frame
        if seg_idx > 0:
            print(f"    morphing {morph_frames} frames at boundary...")
            morph = optical_flow_morph(prev_last_frame, frames[0],
                                        n_intermediate=morph_frames)
            for mf in morph:
                cv2.imwrite(os.path.join(tmpdir, f'f_{frame_idx:05d}.png'), mf)
                frame_idx += 1

        # Write segment frames
        for f in frames:
            cv2.imwrite(os.path.join(tmpdir, f'f_{frame_idx:05d}.png'), f)
            frame_idx += 1

        prev_last_frame = frames[-1]

    print(f"Total frames: {frame_idx}")
    print(f"Encoding...")
    cmd = [
        'ffmpeg', '-y', '-framerate', f'{fps}',
        '-i', os.path.join(tmpdir, 'f_%05d.png'),
        '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '12',
        '-pix_fmt', 'yuv420p', '-r', f'{fps}',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    shutil.rmtree(tmpdir)
    print(f"Saved: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    op = sys.argv[1]
    if op == 'crop':
        # python3 segment_morph.py crop input.mp4 output.mp4 top bottom left right
        crop_video(sys.argv[2], sys.argv[3],
                    top_pct=float(sys.argv[4]),
                    bottom_pct=float(sys.argv[5]),
                    left_pct=float(sys.argv[6]),
                    right_pct=float(sys.argv[7]))
    elif op == 'concat_morph':
        # python3 segment_morph.py concat_morph output.mp4 in1.mp4 in2.mp4 ...
        concat_with_morphing(sys.argv[3:], sys.argv[2])
