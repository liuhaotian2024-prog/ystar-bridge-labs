#!/usr/bin/env python3
"""
YGVCC Physical Alignment Tools — "Force Alignment at Pixel Level"

4 classical CV tools that physically remap target pixels to match reference.
No ML, no GPU, no external API. All deterministic, all MIT-compatible.

These address the dimensions that linear color transforms CAN'T fix:
  - edge_density: detail_transfer recovers high-frequency texture
  - Y_p10 (black level): tone_curve crushes lifted shadows
  - color_temp: reinhard_color_transfer aligns LAB statistics
  - All percentile-based metrics: histogram_match remaps CDF exactly

Pipeline order (before iterative counterfactual):
  1. histogram_match (strongest — remaps full pixel distribution)
  2. detail_transfer (adds high-frequency detail from reference)
  3. tone_curve (S-curve for shadow/highlight compression)
  4. reinhard_color_transfer (LAB mean+std alignment)

After these 4 tools, the remaining Rt is ONLY spatial/face defects
which the iterative counterfactual solve handles.
"""
import cv2
import numpy as np
from typing import Optional, Tuple


def histogram_match(target: np.ndarray, reference: np.ndarray,
                     strength: float = 1.0) -> np.ndarray:
    """
    Per-channel histogram matching via CDF remapping.

    This is the STRONGEST alignment tool — after application, target's
    pixel distribution is identical to reference's for each channel.
    Fixes Y_p10, Y_p50, Y_p99, color_temp, black levels, white levels
    all in one shot.

    Args:
        target: BGR uint8 frame to modify
        reference: BGR uint8 frame providing the target distribution
        strength: blend factor (0=no change, 1=full match)

    Returns:
        matched BGR uint8 frame
    """
    if strength <= 0:
        return target

    matched = np.zeros_like(target)
    for c in range(3):
        # Compute CDFs
        t_hist, _ = np.histogram(target[:, :, c].flatten(), bins=256, range=(0, 256))
        r_hist, _ = np.histogram(reference[:, :, c].flatten(), bins=256, range=(0, 256))
        t_cdf = t_hist.cumsum().astype(np.float64)
        r_cdf = r_hist.cumsum().astype(np.float64)
        t_cdf /= t_cdf[-1] if t_cdf[-1] > 0 else 1
        r_cdf /= r_cdf[-1] if r_cdf[-1] > 0 else 1

        # Build LUT: for each target value, find reference value with same CDF
        lut = np.zeros(256, dtype=np.uint8)
        for v in range(256):
            idx = np.searchsorted(r_cdf, t_cdf[v])
            lut[v] = min(255, max(0, idx))

        matched[:, :, c] = lut[target[:, :, c]]

    if strength < 1.0:
        matched = cv2.addWeighted(target, 1 - strength, matched, strength, 0)

    return matched


def detail_transfer(target: np.ndarray, reference: np.ndarray,
                      strength: float = 0.5,
                      blur_sigma: float = 15.0) -> np.ndarray:
    """
    Transfer high-frequency detail from reference to target using
    Laplacian decomposition.

    Algorithm:
      1. Decompose both into low-freq (Gaussian blur) + high-freq (residual)
      2. Replace target's high-freq with blend of target + reference high-freq
      3. Reconstruct: target_low + blended_high

    This adds edge detail (sharpness, texture) from reference without
    changing the overall tone/color. Fixes edge_density.

    Args:
        target: BGR uint8 frame to modify
        reference: BGR uint8 frame providing the detail
        strength: blend factor for high-freq (0=keep target, 1=use reference)
        blur_sigma: sigma for low-freq extraction (larger = more detail transferred)

    Returns:
        enhanced BGR uint8 frame
    """
    if strength <= 0:
        return target

    target_f = target.astype(np.float32)
    ref_f = reference.astype(np.float32)

    # Decompose
    ksize = int(blur_sigma * 4) | 1  # ensure odd
    t_low = cv2.GaussianBlur(target_f, (ksize, ksize), blur_sigma)
    r_low = cv2.GaussianBlur(ref_f, (ksize, ksize), blur_sigma)
    t_high = target_f - t_low
    r_high = ref_f - r_low

    # Blend high-frequency
    blended_high = t_high * (1 - strength) + r_high * strength

    # Reconstruct
    result = t_low + blended_high
    return np.clip(result, 0, 255).astype(np.uint8)


def tone_curve(frame: np.ndarray,
                black_crush: float = 0.0,
                highlight_compress: float = 0.0,
                midtone_contrast: float = 0.0) -> np.ndarray:
    """
    Apply a non-linear tone curve to fix shadow lifting and highlight clipping.

    Three independent adjustments:
      - black_crush: push Y < 30 pixels darker (fixes lifted shadows / Y_p10)
      - highlight_compress: pull Y > 220 pixels back (fixes blown highlights)
      - midtone_contrast: S-curve on midtones (adds punch)

    All operate on the Y (luminance) channel to preserve color.

    Args:
        frame: BGR uint8
        black_crush: 0-1, how much to crush shadows (0=off, 1=full)
        highlight_compress: 0-1, how much to compress highlights
        midtone_contrast: 0-1, S-curve strength

    Returns:
        tone-adjusted BGR uint8
    """
    if black_crush <= 0 and highlight_compress <= 0 and midtone_contrast <= 0:
        return frame

    bgr = frame.astype(np.float32)
    Y = 0.114 * bgr[:, :, 0] + 0.587 * bgr[:, :, 1] + 0.299 * bgr[:, :, 2]

    new_Y = Y.copy()

    # Black crush: pixels with Y < 30 get pushed toward 0
    if black_crush > 0:
        shadow_mask = np.clip((30.0 - Y) / 30.0, 0, 1)  # 1 at Y=0, 0 at Y=30
        crush_amount = shadow_mask * black_crush * 15.0  # max 15 units darker
        new_Y = new_Y - crush_amount

    # Highlight compress: pixels with Y > 220 get pulled back
    if highlight_compress > 0:
        hl_mask = np.clip((Y - 220.0) / 35.0, 0, 1)  # 1 at Y=255, 0 at Y=220
        compress_amount = hl_mask * highlight_compress * 20.0  # max 20 units darker
        new_Y = new_Y - compress_amount

    # Midtone S-curve: sigmoid centered at 128
    if midtone_contrast > 0:
        # Normalize Y to [0, 1]
        y_norm = np.clip(new_Y / 255.0, 0, 1)
        # S-curve: steeper sigmoid = more contrast
        steepness = 4.0 + midtone_contrast * 8.0  # 4-12
        s_curve = 1.0 / (1.0 + np.exp(-steepness * (y_norm - 0.5)))
        # Blend original with S-curve
        y_scurved = y_norm * (1 - midtone_contrast) + s_curve * midtone_contrast
        new_Y = y_scurved * 255.0

    new_Y = np.clip(new_Y, 0, 255)

    # Apply ratio to preserve color
    ratio = new_Y / np.maximum(Y, 1.0)
    result = bgr * ratio[:, :, None]
    return np.clip(result, 0, 255).astype(np.uint8)


def reinhard_color_transfer(target: np.ndarray, reference: np.ndarray,
                              strength: float = 1.0) -> np.ndarray:
    """
    Reinhard et al. (2001) color transfer in LAB space.

    Matches mean and standard deviation of L*a*b* channels from reference.
    This aligns overall color feel (warmth, tint, brightness distribution)
    without touching spatial detail.

    Args:
        target: BGR uint8
        reference: BGR uint8
        strength: blend factor (0=no change, 1=full transfer)

    Returns:
        color-transferred BGR uint8
    """
    if strength <= 0:
        return target

    # Convert to LAB
    t_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
    r_lab = cv2.cvtColor(reference, cv2.COLOR_BGR2LAB).astype(np.float32)

    # Compute per-channel stats
    for c in range(3):
        t_mean, t_std = t_lab[:, :, c].mean(), t_lab[:, :, c].std()
        r_mean, r_std = r_lab[:, :, c].mean(), r_lab[:, :, c].std()

        if t_std < 1e-6:
            continue

        # Shift and scale to match reference statistics
        transferred = (t_lab[:, :, c] - t_mean) * (r_std / t_std) + r_mean

        # Blend
        t_lab[:, :, c] = t_lab[:, :, c] * (1 - strength) + transferred * strength

    t_lab = np.clip(t_lab, 0, 255).astype(np.uint8)
    return cv2.cvtColor(t_lab, cv2.COLOR_LAB2BGR)


def physical_align_pipeline(target_frame: np.ndarray,
                              reference_frame: np.ndarray,
                              histogram_strength: float = 0.8,
                              detail_strength: float = 0.3,
                              black_crush: float = 0.5,
                              highlight_compress: float = 0.3,
                              midtone_contrast: float = 0.2,
                              color_transfer_strength: float = 0.5) -> np.ndarray:
    """
    Apply the full physical alignment pipeline.

    Order matters:
      1. histogram_match (strongest, fixes distribution)
      2. reinhard_color_transfer (fixes LAB statistics)
      3. tone_curve (fixes shadow/highlight)
      4. detail_transfer (adds texture, applied LAST to preserve sharpness)

    Args:
        target_frame: BGR uint8 frame to align
        reference_frame: BGR uint8 frame providing the standard
        *_strength/*_crush/etc.: per-tool intensity controls

    Returns:
        physically aligned BGR uint8 frame
    """
    result = target_frame

    # 1. Histogram match — fix pixel distribution
    if histogram_strength > 0:
        result = histogram_match(result, reference_frame, strength=histogram_strength)

    # 2. Reinhard color transfer — fix LAB statistics
    if color_transfer_strength > 0:
        result = reinhard_color_transfer(result, reference_frame,
                                           strength=color_transfer_strength)

    # 3. Tone curve — fix shadow/highlight
    if black_crush > 0 or highlight_compress > 0 or midtone_contrast > 0:
        result = tone_curve(result,
                             black_crush=black_crush,
                             highlight_compress=highlight_compress,
                             midtone_contrast=midtone_contrast)

    # 4. Detail transfer — add texture (LAST to preserve sharpness)
    if detail_strength > 0:
        result = detail_transfer(result, reference_frame, strength=detail_strength)

    return result


def compute_reference_stats(video_path: str, n_samples: int = 20) -> dict:
    """
    Compute stable reference statistics from a video for physical alignment.

    Returns per-channel histograms, LAB stats, and a representative frame
    that can be used as reference for the pipeline.

    Args:
        video_path: path to reference video
        n_samples: number of frames to sample

    Returns:
        dict with 'representative_frame', 'lab_stats', 'channel_histograms'
    """
    cap = cv2.VideoCapture(video_path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, n - 1, n_samples).astype(int)

    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, f = cap.read()
        if ret:
            frames.append(f)
    cap.release()

    if not frames:
        return {}

    # Build representative frame: pixel-wise median across sampled frames
    # (robust to motion, gives stable "average" appearance)
    stacked = np.stack(frames[:min(10, len(frames))], axis=0)
    representative = np.median(stacked, axis=0).astype(np.uint8)

    # LAB stats
    labs = [cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32) for f in frames]
    lab_stack = np.stack(labs, axis=0)
    lab_stats = {
        'L_mean': float(lab_stack[:, :, :, 0].mean()),
        'L_std': float(lab_stack[:, :, :, 0].std()),
        'a_mean': float(lab_stack[:, :, :, 1].mean()),
        'a_std': float(lab_stack[:, :, :, 1].std()),
        'b_mean': float(lab_stack[:, :, :, 2].mean()),
        'b_std': float(lab_stack[:, :, :, 2].std()),
    }

    # Per-channel histograms (average across frames)
    channel_histograms = {}
    for c, name in enumerate(['B', 'G', 'R']):
        hists = []
        for f in frames:
            h, _ = np.histogram(f[:, :, c].flatten(), bins=256, range=(0, 256))
            hists.append(h)
        channel_histograms[name] = np.mean(hists, axis=0)

    return {
        'representative_frame': representative,
        'lab_stats': lab_stats,
        'channel_histograms': channel_histograms,
        'n_frames_sampled': len(frames),
    }


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print(__doc__)
        print("Usage: python3 physical_align.py reference.mp4 target.mp4 output.mp4 [strength]")
        sys.exit(1)

    ref_path = sys.argv[1]
    tgt_path = sys.argv[2]
    out_path = sys.argv[3]
    strength = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7

    print(f"Reference: {ref_path}")
    print(f"Target:    {tgt_path}")
    print(f"Output:    {out_path}")
    print(f"Strength:  {strength}")

    # Compute reference stats
    print("\n[1/3] Computing reference statistics...")
    ref_stats = compute_reference_stats(ref_path, n_samples=20)
    ref_frame = ref_stats['representative_frame']
    print(f"  Reference frame shape: {ref_frame.shape}")

    # Process target video frame by frame
    print("\n[2/3] Processing target video...")
    import subprocess, tempfile, shutil, os
    cap = cv2.VideoCapture(tgt_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    tmpdir = tempfile.mkdtemp()
    for i in range(n):
        ret, frame = cap.read()
        if not ret:
            break
        aligned = physical_align_pipeline(
            frame, ref_frame,
            histogram_strength=strength,
            detail_strength=strength * 0.5,
            black_crush=strength * 0.6,
            highlight_compress=strength * 0.3,
            midtone_contrast=strength * 0.2,
            color_transfer_strength=strength * 0.5,
        )
        cv2.imwrite(os.path.join(tmpdir, f'f_{i:05d}.png'), aligned)
        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{n} frames", flush=True)
    cap.release()

    # Encode
    print("\n[3/3] Encoding...")
    # Probe audio duration
    try:
        audio_dur = float(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=duration',
            '-of', 'default=nw=1:nk=1', tgt_path
        ]).decode().strip())
        precise_fps = n / audio_dur
    except Exception:
        precise_fps = fps

    cmd = [
        'ffmpeg', '-y', '-framerate', f'{precise_fps}',
        '-i', os.path.join(tmpdir, 'f_%05d.png'),
        '-i', tgt_path,
        '-map', '0:v', '-map', '1:a?',
        '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '12',
        '-pix_fmt', 'yuv420p', '-r', f'{precise_fps}',
        '-c:a', 'copy', out_path
    ]
    subprocess.run(cmd, capture_output=True)
    shutil.rmtree(tmpdir)
    print(f"Saved: {out_path}")
