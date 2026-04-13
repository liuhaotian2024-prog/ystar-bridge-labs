#!/usr/bin/env python3
"""
Layer-by-layer YGVCC alignment demo on a single frame.

Takes one frame from stage1B (the broken segment), one frame from stage1A
(the anchor), and applies YGVCC interventions one layer at a time. After
each layer, measure the per-dim Rt vs the stage1A target. Build a grid
showing every step so Board can SEE exactly what each layer does.
"""
import sys, os
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fingerprint_v2 import extract_v2_fingerprint, fingerprint_v2_distance, DEFAULT_V2_WEIGHTS
from fingerprint import build_face_mask
from physical_align import histogram_match, tone_curve, reinhard_color_transfer
from sharpen_align import iterative_sharpen, measure_sharpness


def panel_with_text(img, lines, color=(0, 255, 255)):
    """Add multi-line text overlay at the bottom of an image."""
    h, w = img.shape[:2]
    img = img.copy()
    overlay_h = 30 * len(lines) + 10
    cv2.rectangle(img, (0, h - overlay_h), (w, h), (0, 0, 0), -1)
    for i, line in enumerate(lines):
        cv2.putText(img, line, (10, h - overlay_h + 25 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return img


def get_frame(video_path, frame_index, return_mask=False):
    """Extract a single frame and optional face mask."""
    import mediapipe as mp
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise ValueError(f"Could not read frame {frame_index} from {video_path}")
    if return_mask:
        fm = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1,
            min_detection_confidence=0.1
        )
        mask, _ = build_face_mask(frame, fm)
        fm.close()
        return frame, mask
    return frame


def measure_key_dims(frame, ref_fp, face_mask=None):
    """Extract v2 fingerprint and compute key Rt metrics vs reference."""
    fp = extract_v2_fingerprint(frame, face_mask=face_mask)

    # Compare to reference, excluding face dims that are 0 in reference
    EXCLUDE_FACE = ['Yf_mean','Yf_p99','R_face','B_face','color_temp_f','sat_f',
                    'Yf_TL','Yf_TR','Yf_BL','Yf_BR','Yf_LR_diff','R_LR_diff','sat_LR_diff',
                    'face_sharpness','skin_L','skin_a','skin_b',
                    'face_size_pct','face_aspect','face_center_x','face_center_y',
                    'Rf_highlight','warmth_highlight']

    weighted_l2_sq = 0.0
    for k in fp:
        if k == 'has_face' or not isinstance(fp.get(k), (int, float)):
            continue
        if k in EXCLUDE_FACE:
            continue
        if k not in ref_fp:
            continue
        d = fp[k] - ref_fp[k]
        w = DEFAULT_V2_WEIGHTS.get(k, 1.0)
        weighted_l2_sq += w * d * d

    return {
        'sharpness': fp.get('sharpness_laplacian', 0),
        'edge_density': fp.get('edge_density', 0),
        'edge_p99': fp.get('edge_p99', 0),
        'Y_mean': fp.get('Y_mean', 0),
        'sat_mean': fp.get('sat_mean', 0),
        'color_temp': fp.get('color_temp', 0),
        'L_mean': fp.get('L_mean', 0),
        'V_mean': fp.get('V_mean', 0),
        'noise_level': fp.get('noise_level', 0),
        'local_contrast': fp.get('local_contrast_mean', 0),
        'weighted_l2': float(np.sqrt(weighted_l2_sq)),
        'fp': fp,
    }


def main():
    print("=" * 70)
    print("YGVCC Layer-by-Layer Demo")
    print("=" * 70)

    # Pick frames
    print("\n[1] Loading frames...")
    # Stage 1A frame: pick one where Samantha is closest (last few frames)
    target_frame = get_frame('docs/layer1_stage1A_hq.mp4', 165)
    print(f"  TARGET (stage1A frame 165): {target_frame.shape}")

    # Stage 1B frame 140: face is detected at frame 140 area
    source_frame, face_mask = get_frame('docs/layer1_stage1B_hq.mp4', 140, return_mask=True)
    print(f"  SOURCE (stage1B frame 140): {source_frame.shape}")
    print(f"  Face detected: {face_mask.sum() > 0}")

    # Reference fingerprint (target = stage1A)
    print("\n[2] Computing target reference fingerprint...")
    ref_fp = extract_v2_fingerprint(target_frame)
    target_metrics = measure_key_dims(target_frame, ref_fp)
    print(f"  Target sharpness: {target_metrics['sharpness']:.1f}")
    print(f"  Target Y_mean: {target_metrics['Y_mean']:.1f}")
    print(f"  Target sat_mean: {target_metrics['sat_mean']:.1f}")
    print(f"  Target color_temp: {target_metrics['color_temp']:.1f}")

    # Source baseline metrics
    print("\n[3] Source (stage1B) baseline metrics:")
    src_metrics = measure_key_dims(source_frame, ref_fp, face_mask=face_mask)
    print(f"  sharpness: {src_metrics['sharpness']:.1f} (target {target_metrics['sharpness']:.1f})")
    print(f"  Y_mean: {src_metrics['Y_mean']:.1f}")
    print(f"  sat_mean: {src_metrics['sat_mean']:.1f}")
    print(f"  color_temp: {src_metrics['color_temp']:.1f}")
    print(f"  weighted L2 (excl face): {src_metrics['weighted_l2']:.1f}")

    # ===========================================================
    # LAYER-BY-LAYER PIPELINE
    # ===========================================================
    print("\n[4] Applying layers...")

    layers = []
    layers.append(('LAYER 0: ORIGINAL', source_frame, src_metrics))

    # LAYER 1: histogram match
    print("\n  Layer 1: histogram_match (full distribution remap to target)")
    l1 = histogram_match(source_frame, target_frame, strength=1.0)
    m1 = measure_key_dims(l1, ref_fp, face_mask=face_mask)
    print(f"    sharpness: {m1['sharpness']:.1f}")
    print(f"    L2: {m1['weighted_l2']:.1f}")
    layers.append(('LAYER 1: +histogram_match', l1, m1))

    # LAYER 2: reinhard color transfer (LAB statistics)
    print("\n  Layer 2: +reinhard_color_transfer (LAB mean+std match)")
    l2 = reinhard_color_transfer(l1, target_frame, strength=0.7)
    m2 = measure_key_dims(l2, ref_fp, face_mask=face_mask)
    print(f"    sharpness: {m2['sharpness']:.1f}")
    print(f"    color_temp: {m2['color_temp']:.1f}")
    print(f"    L2: {m2['weighted_l2']:.1f}")
    layers.append(('LAYER 2: +reinhard_color', l2, m2))

    # LAYER 3: tone curve (black crush + highlight compress)
    print("\n  Layer 3: +tone_curve (shadow/highlight)")
    l3 = tone_curve(l2, black_crush=0.4, highlight_compress=0.3, midtone_contrast=0.15)
    m3 = measure_key_dims(l3, ref_fp, face_mask=face_mask)
    print(f"    L2: {m3['weighted_l2']:.1f}")
    layers.append(('LAYER 3: +tone_curve', l3, m3))

    # LAYER 4: face_relight (smooth highlight) — apply BEFORE sharpening
    print("\n  Layer 4: +face_relight (smooth highlight, if face)")
    sys.path.insert(0, '/Users/haotianliu/.openclaw/workspace/ystar-company/tools/cieu')
    from face_relight import smooth_face_lighting
    if face_mask is not None and face_mask.sum() > 0:
        l4 = smooth_face_lighting(l3, face_mask, strength=0.5)
    else:
        l4 = l3
    m4 = measure_key_dims(l4, ref_fp, face_mask=face_mask)
    print(f"    L2: {m4['weighted_l2']:.1f}")
    layers.append(('LAYER 4: +face_relight', l4, m4))

    # LAYER 5: sharpen to target Laplacian (LAST so it can compensate for any softening)
    print("\n  Layer 5: +iterative_sharpen (target Laplacian = stage1A's)")
    target_lap = target_metrics['sharpness']
    l5 = iterative_sharpen(l4, target_lap_var=target_lap, max_iter=8, sigma=1.5)
    m5 = measure_key_dims(l5, ref_fp, face_mask=face_mask)
    print(f"    sharpness: {m5['sharpness']:.1f} (target {target_lap:.1f})")
    print(f"    L2: {m5['weighted_l2']:.1f}")
    layers.append(('LAYER 5: +sharpen_to_target', l5, m5))

    # LAYER 6 = FINAL (alias of L5)
    l6 = l5
    m6 = m5
    layers.append(('LAYER 6: FINAL', l6, m6))

    # ===========================================================
    # BUILD VISUALIZATION GRID
    # ===========================================================
    print("\n[5] Building visualization grid...")
    panels = []

    # Top row: target | source baseline
    target_panel = panel_with_text(
        cv2.resize(target_frame, (640, 360)),
        [
            'TARGET (stage1A f165)',
            f'sharp={target_metrics["sharpness"]:.0f}  Y={target_metrics["Y_mean"]:.0f}',
            f'sat={target_metrics["sat_mean"]:.0f}  ct={target_metrics["color_temp"]:.0f}',
        ],
        color=(0, 255, 0)
    )

    # Layer panels (each shows the result + key metrics)
    layer_panels = []
    for label, img, metrics in layers:
        small = cv2.resize(img, (640, 360))
        # Compute relative changes vs source baseline
        delta_l2 = metrics['weighted_l2'] - layers[0][2]['weighted_l2']
        sign = '↓' if delta_l2 < 0 else ('↑' if delta_l2 > 0 else '=')
        text = [
            label,
            f'sharp={metrics["sharpness"]:.0f} sat={metrics["sat_mean"]:.0f} ct={metrics["color_temp"]:.0f}',
            f'L2={metrics["weighted_l2"]:.1f} ({sign}{abs(delta_l2):.0f} from L0)',
        ]
        layer_panels.append(panel_with_text(small, text))

    # Build grid: top row [target, original], then layers in pairs
    grid_rows = []
    grid_rows.append(np.hstack([target_panel, layer_panels[0]]))  # target | original
    grid_rows.append(np.hstack([layer_panels[1], layer_panels[2]]))  # L1, L2
    grid_rows.append(np.hstack([layer_panels[3], layer_panels[4]]))  # L3, L4
    grid_rows.append(np.hstack([layer_panels[5], layer_panels[6]]))  # L5, L6_FINAL

    grid = np.vstack(grid_rows)
    out_path = 'docs/layer_by_layer_demo.png'
    cv2.imwrite(out_path, grid)
    print(f"\n✅ Saved: {out_path}  ({grid.shape})")

    # ===========================================================
    # NUMERIC SUMMARY
    # ===========================================================
    print("\n" + "=" * 70)
    print("NUMERIC RT TRAJECTORY")
    print("=" * 70)
    print(f"{'Layer':<30s}{'Sharp':>8s}{'Y_mn':>8s}{'sat':>8s}{'CT':>8s}{'L_mn':>8s}{'V_mn':>8s}{'L2':>10s}")
    print('-' * 88)
    print(f"{'TARGET (stage1A)':<30s}{target_metrics['sharpness']:>8.1f}"
          f"{target_metrics['Y_mean']:>8.1f}{target_metrics['sat_mean']:>8.1f}"
          f"{target_metrics['color_temp']:>8.1f}{target_metrics['L_mean']:>8.1f}"
          f"{target_metrics['V_mean']:>8.1f}{0.0:>10.1f}")
    for label, _, m in layers:
        print(f"{label:<30s}{m['sharpness']:>8.1f}{m['Y_mean']:>8.1f}"
              f"{m['sat_mean']:>8.1f}{m['color_temp']:>8.1f}"
              f"{m['L_mean']:>8.1f}{m['V_mean']:>8.1f}{m['weighted_l2']:>10.1f}")

    print()
    initial_l2 = layers[0][2]['weighted_l2']
    final_l2 = layers[-1][2]['weighted_l2']
    print(f"Initial L2: {initial_l2:.1f}")
    print(f"Final L2:   {final_l2:.1f}")
    print(f"Reduction:  {(1 - final_l2/initial_l2)*100:+.0f}%")


if __name__ == '__main__':
    main()
