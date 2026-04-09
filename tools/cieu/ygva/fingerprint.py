#!/usr/bin/env python3
"""
YGVA Phase 1 — Reference Fingerprint Extractor

提取一帧图像的全维度参数指纹（30+ 维）作为 Y*gov 治理的 reference state。

每个维度都是连续值，可作为 StructuralEquation 的观测变量。
该指纹是 Y*gov-Governed Video Alignment (YGVA) 的核心 — 治理目标就是
让每一帧的 fingerprint 持续向 reference fingerprint 收敛 (Rt → 0)。

维度类别（共 35 维）:
  Global luminance (6):  Y_mean, Y_std, Y_p10, Y_p50, Y_p90, Y_p99
  Global color (6):      R_mean, G_mean, B_mean, color_temp, tint, sat_mean
  LAB color (3):         L_mean, a_mean, b_mean
  Face global (5):       Yf_mean, color_temp_f, sat_f, R_face, B_face
  Face quadrant (4):     Yf_TL, Yf_TR, Yf_BL, Yf_BR
  Face highlight (3):    Yf_p99, Rf_highlight, warmth_highlight
  Texture (2):           edge_density, patch_variance
  HSV (3):               H_mean, S_mean, V_mean
  Asymmetry (3):         Yf_LR_diff, R_LR_diff, sat_LR_diff
"""
import cv2
import numpy as np
import json
import sys
import mediapipe as mp
from pathlib import Path

# Face oval landmarks (MediaPipe Face Mesh)
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]


def build_face_mask(frame, face_mesh=None):
    """Build face mask via MediaPipe. Returns (mask, success)."""
    h, w = frame.shape[:2]
    if face_mesh is None:
        face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1,
            refine_landmarks=False, min_detection_confidence=0.1
        )
        owns = True
    else:
        owns = False

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = face_mesh.process(rgb)
    mask = np.zeros((h, w), dtype=np.uint8)
    success = False
    if res.multi_face_landmarks:
        for fl in res.multi_face_landmarks:
            pts = np.array(
                [[int(fl.landmark[i].x * w), int(fl.landmark[i].y * h)]
                 for i in FACE_OVAL], dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)
        success = True

    if owns:
        face_mesh.close()
    return mask, success


def extract_fingerprint(frame, face_mesh=None, face_mask=None):
    """
    Extract 35-dimensional fingerprint vector from a single frame.

    Args:
        frame: BGR image (H, W, 3) uint8
        face_mesh: Optional MediaPipe FaceMesh instance (for batch use)
        face_mask: Optional precomputed face mask (skip detection)

    Returns:
        dict with all parameter dimensions, plus 'has_face' flag.
    """
    h, w = frame.shape[:2]

    if face_mask is None:
        face_mask, has_face = build_face_mask(frame, face_mesh)
    else:
        has_face = face_mask.sum() > 0

    bgr = frame.astype(np.float32)
    b, g, r = bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2]
    Y = 0.114 * b + 0.587 * g + 0.299 * r

    fp = {'has_face': bool(has_face)}

    # === Global luminance (6) ===
    fp['Y_mean'] = float(Y.mean())
    fp['Y_std'] = float(Y.std())
    fp['Y_p10'] = float(np.percentile(Y, 10))
    fp['Y_p50'] = float(np.percentile(Y, 50))
    fp['Y_p90'] = float(np.percentile(Y, 90))
    fp['Y_p99'] = float(np.percentile(Y, 99))

    # === Global color (6) ===
    fp['R_mean'] = float(r.mean())
    fp['G_mean'] = float(g.mean())
    fp['B_mean'] = float(b.mean())
    fp['color_temp'] = float(r.mean() - b.mean())
    fp['tint'] = float(g.mean() - 0.5 * (r.mean() + b.mean()))

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    fp['sat_mean'] = float(hsv[:, :, 1].mean())

    # === LAB color (3) ===
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
    fp['L_mean'] = float(lab[:, :, 0].mean())
    fp['a_mean'] = float(lab[:, :, 1].mean() - 128)
    fp['b_mean'] = float(lab[:, :, 2].mean() - 128)

    # === HSV (3) ===
    fp['H_mean'] = float(hsv[:, :, 0].mean())
    fp['S_mean'] = float(hsv[:, :, 1].mean())
    fp['V_mean'] = float(hsv[:, :, 2].mean())

    # === Texture (2) ===
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    edge_mag = np.sqrt(sx * sx + sy * sy)
    fp['edge_density'] = float(edge_mag.mean())
    fp['patch_variance'] = float(np.var(gray.astype(np.float32)))

    if not has_face:
        # Default face fields to global values (won't affect Rt if reference also no face)
        for k in ['Yf_mean', 'Yf_p99', 'color_temp_f', 'sat_f', 'R_face', 'B_face',
                  'Yf_TL', 'Yf_TR', 'Yf_BL', 'Yf_BR',
                  'Rf_highlight', 'warmth_highlight',
                  'Yf_LR_diff', 'R_LR_diff', 'sat_LR_diff']:
            fp[k] = 0.0
        return fp

    in_face = face_mask > 0

    # === Face global (5) ===
    fp['Yf_mean'] = float(Y[in_face].mean())
    fp['Yf_p99'] = float(np.percentile(Y[in_face], 99))
    fp['R_face'] = float(r[in_face].mean())
    fp['B_face'] = float(b[in_face].mean())
    fp['color_temp_f'] = float(r[in_face].mean() - b[in_face].mean())
    fp['sat_f'] = float(hsv[:, :, 1][in_face].mean())

    # === Face quadrants (4) ===
    rows = np.where(face_mask.sum(1) > 0)[0]
    cols = np.where(face_mask.sum(0) > 0)[0]
    cy = (rows[0] + rows[-1]) // 2
    cx = (cols[0] + cols[-1]) // 2

    def quad_mean(y0, y1, x0, x1):
        m = np.zeros_like(face_mask)
        m[y0:y1, x0:x1] = face_mask[y0:y1, x0:x1]
        if m.sum() > 0:
            return float(Y[m > 0].mean())
        return 0.0

    fp['Yf_TL'] = quad_mean(rows[0], cy, cols[0], cx)
    fp['Yf_TR'] = quad_mean(rows[0], cy, cx, cols[-1] + 1)
    fp['Yf_BL'] = quad_mean(cy, rows[-1] + 1, cols[0], cx)
    fp['Yf_BR'] = quad_mean(cy, rows[-1] + 1, cx, cols[-1] + 1)

    # === Face highlight (3) ===
    Yf = Y[in_face]
    hl_thresh = np.percentile(Yf, 95)
    hl_mask = (Y > hl_thresh) & in_face
    if hl_mask.sum() > 0:
        fp['Rf_highlight'] = float(r[hl_mask].mean())
        fp['warmth_highlight'] = float((r[hl_mask] - b[hl_mask]).mean())
    else:
        fp['Rf_highlight'] = 0.0
        fp['warmth_highlight'] = 0.0

    # === Asymmetry (3) — Left vs Right ===
    L_mask = face_mask.copy(); L_mask[:, cx:] = 0
    R_mask = face_mask.copy(); R_mask[:, :cx] = 0
    if L_mask.sum() > 0 and R_mask.sum() > 0:
        Y_L = Y[L_mask > 0].mean()
        Y_R = Y[R_mask > 0].mean()
        R_L = r[L_mask > 0].mean()
        R_R = r[R_mask > 0].mean()
        S_L = hsv[:, :, 1][L_mask > 0].mean()
        S_R = hsv[:, :, 1][R_mask > 0].mean()
        fp['Yf_LR_diff'] = float(Y_L - Y_R)
        fp['R_LR_diff'] = float(R_L - R_R)
        fp['sat_LR_diff'] = float(S_L - S_R)
    else:
        fp['Yf_LR_diff'] = 0.0
        fp['R_LR_diff'] = 0.0
        fp['sat_LR_diff'] = 0.0

    return fp


def extract_video_reference(video_path, frame_index='last', n_average=5,
                              hybrid_ideal_face=False):
    """
    Extract reference fingerprint from a video.

    Args:
        video_path: Path to the reference video.
        frame_index: 'last' (use average of last N frames),
                     'middle', 'first', or int frame number.
        n_average: How many adjacent frames to average for stability.
        hybrid_ideal_face: If True, accept frames without face detection.
                          Face dimensions are set to ideal values:
                          - Yf_LR_diff = 0 (perfect L/R symmetry)
                          - R_LR_diff = 0
                          - sat_LR_diff = 0
                          - All quadrants = global Y_mean
                          This is the right mode when reference video has
                          a small/distant face (eg. wide walking shot) — we
                          take its color/lighting palette but enforce ideal
                          face symmetry as the convergence target.

    Returns:
        Reference fingerprint dict (averaged across adjacent frames).
    """
    cap = cv2.VideoCapture(str(video_path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_index == 'last':
        target = n - 1
    elif frame_index == 'middle':
        target = n // 2
    elif frame_index == 'first':
        target = 0
    else:
        target = int(frame_index)

    start = max(0, target - n_average + 1)
    end = min(n - 1, target)

    fm = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1,
        refine_landmarks=False, min_detection_confidence=0.1
    )

    fps = []
    for idx in range(start, end + 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        fp = extract_fingerprint(frame, face_mesh=fm)
        if fp.get('has_face') or hybrid_ideal_face:
            fps.append(fp)

    cap.release()
    fm.close()

    if not fps:
        raise RuntimeError(f"No frames extracted from {video_path}")

    # Average across collected frames (each dim is a float)
    ref = {}
    for k in fps[0].keys():
        if k == 'has_face':
            ref[k] = any(fp.get('has_face') for fp in fps)
        else:
            ref[k] = float(np.mean([fp[k] for fp in fps]))

    # In hybrid mode: replace face dims with ideal symmetric values
    if hybrid_ideal_face:
        # All quadrants equal to global midtone
        target_y = ref.get('Y_p50', ref['Y_mean'])
        target_R = ref.get('R_mean', 110.0)
        target_B = ref.get('B_mean', 90.0)
        target_color_temp = ref.get('color_temp', 17.0)
        target_sat = ref.get('sat_mean', 113.0)

        ref['Yf_mean'] = target_y
        ref['Yf_p99'] = ref.get('Y_p99', 240.0) * 0.95  # face never fully clipped
        ref['Yf_TL'] = target_y
        ref['Yf_TR'] = target_y
        ref['Yf_BL'] = target_y
        ref['Yf_BR'] = target_y
        ref['R_face'] = target_R
        ref['B_face'] = target_B
        ref['color_temp_f'] = target_color_temp
        ref['sat_f'] = target_sat
        ref['Rf_highlight'] = target_R + 20  # slight highlight bump
        ref['warmth_highlight'] = max(target_color_temp - 5, 0)
        # CRITICAL — symmetry constraints
        ref['Yf_LR_diff'] = 0.0
        ref['R_LR_diff'] = 0.0
        ref['sat_LR_diff'] = 0.0

    ref['_meta'] = {
        'source': str(video_path),
        'frame_index': frame_index,
        'frames_averaged': len(fps),
        'mode': 'hybrid_ideal_face' if hybrid_ideal_face else 'observed',
    }
    return ref


def fingerprint_distance(fp_a, fp_b, weights=None):
    """
    Weighted L2 distance (Rt) between two fingerprints.

    Args:
        fp_a, fp_b: fingerprint dicts
        weights: optional dict {dim: weight}; default uniform per category

    Returns:
        (total_distance, per_dimension_deltas)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    deltas = {}
    sq = 0.0
    for k, w in weights.items():
        if k in fp_a and k in fp_b:
            d = fp_b[k] - fp_a[k]
            deltas[k] = d
            sq += w * d * d
    return float(np.sqrt(sq)), deltas


# Default per-dimension weights — face dimensions weighted higher because the
# perceptual issue is on the face. Asymmetry dimensions are critical (root cause).
DEFAULT_WEIGHTS = {
    # Global luminance — moderate weight
    'Y_mean': 0.5, 'Y_std': 0.3, 'Y_p50': 0.5, 'Y_p99': 0.4, 'Y_p10': 0.3, 'Y_p90': 0.4,
    # Global color — moderate weight
    'R_mean': 0.4, 'G_mean': 0.4, 'B_mean': 0.4,
    'color_temp': 0.6, 'tint': 0.5, 'sat_mean': 0.5,
    # LAB
    'L_mean': 0.5, 'a_mean': 0.6, 'b_mean': 0.6,
    # HSV
    'H_mean': 0.2, 'S_mean': 0.4, 'V_mean': 0.5,
    # Texture
    'edge_density': 0.3, 'patch_variance': 0.2,
    # Face global — high weight
    'Yf_mean': 1.5, 'Yf_p99': 1.0, 'R_face': 1.0, 'B_face': 1.0,
    'color_temp_f': 1.5, 'sat_f': 1.0,
    # Face quadrants — moderate
    'Yf_TL': 0.8, 'Yf_TR': 0.8, 'Yf_BL': 0.8, 'Yf_BR': 0.8,
    # Highlights
    'Rf_highlight': 1.2, 'warmth_highlight': 1.5,
    # Asymmetry — CRITICAL (this is the root cause)
    'Yf_LR_diff': 2.0, 'R_LR_diff': 2.0, 'sat_LR_diff': 1.0,
}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python3 fingerprint.py reference_video.mp4 [output.json]")
        sys.exit(1)

    video = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'reference_fingerprint.json'
    hybrid = '--hybrid' in sys.argv

    print(f"Extracting reference fingerprint from {video}{' (hybrid mode)' if hybrid else ''}...")
    ref = extract_video_reference(video, frame_index='last', n_average=5,
                                    hybrid_ideal_face=hybrid)
    print(f"  Averaged across {ref['_meta']['frames_averaged']} frames")
    print(f"  Has face: {ref['has_face']}")
    print()
    print("=== Fingerprint dimensions ===")
    for k in sorted(ref.keys()):
        if k.startswith('_') or k == 'has_face':
            continue
        print(f"  {k:25s}: {ref[k]:8.2f}")

    with open(out, 'w') as f:
        json.dump(ref, f, indent=2)
    print(f"\nSaved: {out}")
