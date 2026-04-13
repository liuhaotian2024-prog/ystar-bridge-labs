#!/usr/bin/env python3
"""
Layer-by-layer DIAGNOSTIC — measures what each layer ACTUALLY does at the
pixel level, not just statistical proxies.

Per layer, computes:
1. SSIM vs L0 ORIGINAL — how much did this layer CHANGE the image?
2. Noise level (high-freq variance in flat regions) — is sharpness REAL or FAKE?
3. Effective sharpness (Laplacian) — the metric we've been using
4. Naturalness ratio (real edges / fake high-freq) — Board's actual concern
5. Pixel diff map vs L0 — where are the changes?

Goal: prove or disprove the hypothesis "L6 is sharper but uglier because
the added high-freq is artifact, not real detail".
"""
import sys, os
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from physical_align import histogram_match, tone_curve, reinhard_color_transfer
from sharpen_align import iterative_sharpen
from fingerprint import build_face_mask


def ssim_simple(img_a, img_b):
    """SSIM via OpenCV / numpy (luminance only, no SciPy needed)."""
    a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY).astype(np.float64)
    b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY).astype(np.float64)

    K1, K2, L = 0.01, 0.03, 255
    C1 = (K1 * L) ** 2
    C2 = (K2 * L) ** 2

    mu_a = cv2.GaussianBlur(a, (11, 11), 1.5)
    mu_b = cv2.GaussianBlur(b, (11, 11), 1.5)
    mu_a_sq = mu_a ** 2
    mu_b_sq = mu_b ** 2
    mu_ab = mu_a * mu_b

    sigma_a_sq = cv2.GaussianBlur(a * a, (11, 11), 1.5) - mu_a_sq
    sigma_b_sq = cv2.GaussianBlur(b * b, (11, 11), 1.5) - mu_b_sq
    sigma_ab = cv2.GaussianBlur(a * b, (11, 11), 1.5) - mu_ab

    ssim_map = ((2 * mu_ab + C1) * (2 * sigma_ab + C2)) / \
               ((mu_a_sq + mu_b_sq + C1) * (sigma_a_sq + sigma_b_sq + C2))
    return float(ssim_map.mean())


def measure_naturalness(frame):
    """
    Diagnose: real edges vs fake high-freq (artifact).

    Method: split the image into edge regions and flat regions.
    - In EDGE regions, high-freq is REAL (it's the edge).
    - In FLAT regions, high-freq is NOISE/ARTIFACT.

    Returns:
        edge_high_freq: high-freq energy at real edges
        flat_high_freq: high-freq energy in flat areas (= noise)
        signal_to_artifact_ratio: edge_high_freq / flat_high_freq
        higher = more natural (real detail dominates)
        lower = more artifact (noise dominates)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Compute gradient strength to find edges
    sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    edge_mag = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    edge_smooth = cv2.GaussianBlur(edge_mag, (15, 15), 5)

    # Define edge vs flat regions
    p70 = np.percentile(edge_smooth, 70)
    p30 = np.percentile(edge_smooth, 30)
    edge_region = edge_smooth > p70
    flat_region = edge_smooth < p30

    # High-freq content (Laplacian)
    laplacian = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    abs_lap = np.abs(laplacian)

    edge_hf = float(abs_lap[edge_region].mean()) if edge_region.any() else 0
    flat_hf = float(abs_lap[flat_region].mean()) if flat_region.any() else 0
    sar = edge_hf / max(flat_hf, 0.01)

    return {
        'edge_hf': edge_hf,
        'flat_hf': flat_hf,
        'signal_to_artifact_ratio': sar,
        'sharpness_lap_var': float(laplacian.var()),
    }


def get_frame(video_path, idx):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, f = cap.read()
    cap.release()
    return f


def main():
    print("=" * 80)
    print("LAYER-BY-LAYER DIAGNOSTIC — Real vs Artifact High-Freq")
    print("=" * 80)

    target = get_frame('docs/layer1_stage1A_hq.mp4', 165)
    source = get_frame('docs/layer1_stage1B_hq.mp4', 140)

    import mediapipe as mp
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.05)
    face_mask, _ = build_face_mask(source, fm)
    fm.close()

    print(f"\nTarget naturalness:")
    t_nat = measure_naturalness(target)
    print(f"  edge_hf={t_nat['edge_hf']:.2f}  flat_hf={t_nat['flat_hf']:.2f}")
    print(f"  signal_to_artifact_ratio = {t_nat['signal_to_artifact_ratio']:.2f}")
    print(f"  laplacian_var = {t_nat['sharpness_lap_var']:.1f}")

    layers = [('L0_ORIGINAL', source)]

    # L1 histogram_match
    l1 = histogram_match(source, target, strength=1.0)
    layers.append(('L1_hist_match', l1))

    # L2 reinhard
    l2 = reinhard_color_transfer(l1, target, strength=0.7)
    layers.append(('L2_reinhard', l2))

    # L3 tone_curve
    l3 = tone_curve(l2, black_crush=0.4, highlight_compress=0.3, midtone_contrast=0.15)
    layers.append(('L3_tone', l3))

    # L4 face_relight
    sys.path.insert(0, '/Users/haotianliu/.openclaw/workspace/ystar-company/tools/cieu')
    from face_relight import smooth_face_lighting
    if face_mask is not None and face_mask.sum() > 0:
        l4 = smooth_face_lighting(l3, face_mask, strength=0.5)
    else:
        l4 = l3
    layers.append(('L4_face_relight', l4))

    # L5 sharpen
    target_lap = t_nat['sharpness_lap_var']
    l5 = iterative_sharpen(l4, target_lap_var=target_lap, max_iter=8, sigma=1.5)
    layers.append(('L5_sharpen', l5))

    # ===== DIAGNOSE EACH LAYER =====
    print(f"\n{'Layer':<20s}{'SSIM_vs_L0':>12s}{'edge_hf':>10s}{'flat_hf':>10s}{'SAR':>8s}{'lap_var':>10s}")
    print('-' * 70)

    target_nat = t_nat
    print(f"{'TARGET':<20s}{'-':>12s}"
          f"{target_nat['edge_hf']:>10.2f}{target_nat['flat_hf']:>10.2f}"
          f"{target_nat['signal_to_artifact_ratio']:>8.2f}"
          f"{target_nat['sharpness_lap_var']:>10.1f}")
    print('-' * 70)

    L0 = layers[0][1]
    for label, img in layers:
        ssim_val = 1.0 if label == 'L0_ORIGINAL' else ssim_simple(L0, img)
        nat = measure_naturalness(img)
        print(f"{label:<20s}{ssim_val:>12.4f}"
              f"{nat['edge_hf']:>10.2f}{nat['flat_hf']:>10.2f}"
              f"{nat['signal_to_artifact_ratio']:>8.2f}"
              f"{nat['sharpness_lap_var']:>10.1f}")

    # ===== INTERPRET =====
    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    target_sar = target_nat['signal_to_artifact_ratio']
    L0_sar = measure_naturalness(L0)['signal_to_artifact_ratio']
    L5_sar = measure_naturalness(layers[-1][1])['signal_to_artifact_ratio']

    print(f"\nSignal-to-Artifact Ratio (SAR):")
    print(f"  HIGHER = more natural (real detail dominates)")
    print(f"  LOWER  = more artifact (noise dominates)")
    print(f"")
    print(f"  TARGET (stage1A natural):     SAR = {target_sar:.2f}")
    print(f"  L0 stage1B original:          SAR = {L0_sar:.2f}")
    print(f"  L5 stage1B sharpened:         SAR = {L5_sar:.2f}")
    print()
    if L5_sar < L0_sar:
        diff = L0_sar - L5_sar
        print(f"  ⚠ L5 SAR DROPPED by {diff:.2f} ({diff/L0_sar*100:.0f}%)")
        print(f"  → Sharpening ADDED ARTIFACTS, not real detail.")
        print(f"  → Board's eye is RIGHT: the 'sharpness' is fake.")
    else:
        diff = L5_sar - L0_sar
        print(f"  ✅ L5 SAR INCREASED by {diff:.2f} ({diff/L0_sar*100:.0f}%)")
        print(f"  → Sharpening added REAL detail (natural sharpness).")

    # Save diff maps
    print()
    print("Saving pixel diff maps for visual inspection...")
    diff_l0_vs_l5 = cv2.absdiff(L0, layers[-1][1])
    diff_amplified = np.clip(diff_l0_vs_l5.astype(np.int16) * 5, 0, 255).astype(np.uint8)
    cv2.imwrite('docs/diag_diff_L0_to_L5_5x.png', diff_amplified)
    print(f"  Saved: docs/diag_diff_L0_to_L5_5x.png")
    print(f"  (Shows where L5 differs from L0, amplified 5x. Bright=changed)")


if __name__ == '__main__':
    main()
