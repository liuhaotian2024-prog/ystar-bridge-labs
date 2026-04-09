#!/usr/bin/env python3
"""
YGVA Phase 2 — Intervention Library + Causal Calibration

Defines parameterized interventions and calibrates a causal model that
maps `intervention_params → fingerprint_dim_deltas`.

The causal model uses Y*gov's StructuralEquation primitives to learn how
each intervention affects each fingerprint dimension. The CounterfactualEngine
in governor.py then uses this model to predict (without actually applying)
which intervention will best minimize Rt.

Interventions (10 control variables total):
  1. global_gain         : multiplicative on RGB        [0.7, 1.3]
  2. global_gamma        : Y^gamma                       [0.7, 1.4]
  3. dR                  : R additive shift              [-30, 30]
  4. dG                  : G additive shift              [-20, 20]
  5. dB                  : B additive shift              [-20, 30]
  6. sat_scale           : HSV S multiplier              [0.5, 1.5]
  7. left_dim            : multiplier on left half face  [0.6, 1.0]
  8. right_dim           : multiplier on right half face [0.6, 1.0]
  9. highlight_rolloff   : compress face Y > thresh      [0, 1]
 10. face_warm_desat     : neutralize warm in face       [0, 1]
"""
import cv2
import numpy as np
import json
import sys
import os
from pathlib import Path

# Allow import from sibling module
sys.path.insert(0, os.path.dirname(__file__))
from fingerprint import build_face_mask, extract_fingerprint, DEFAULT_WEIGHTS  # noqa


# =====================================================
# Intervention parameter spec
# =====================================================
INTERVENTION_SPEC = {
    'global_gain':       {'default': 1.0, 'min': 0.7, 'max': 1.3, 'step': 0.05},
    'global_gamma':      {'default': 1.0, 'min': 0.7, 'max': 1.4, 'step': 0.05},
    'dR':                {'default': 0.0, 'min':-30.0,'max': 30.0,'step': 5.0},
    'dG':                {'default': 0.0, 'min':-20.0,'max': 20.0,'step': 5.0},
    'dB':                {'default': 0.0, 'min':-20.0,'max': 30.0,'step': 5.0},
    'sat_scale':         {'default': 1.0, 'min': 0.5, 'max': 1.5, 'step': 0.05},
    # Bipolar face-half scalers — can brighten OR dim each side
    'left_scale':        {'default': 1.0, 'min': 0.4, 'max': 1.5, 'step': 0.05},
    'right_scale':       {'default': 1.0, 'min': 0.5, 'max': 2.0, 'step': 0.05},
    'highlight_rolloff': {'default': 0.0, 'min': 0.0, 'max': 1.0, 'step': 0.1},
    'face_warm_desat':   {'default': 0.0, 'min': 0.0, 'max': 1.0, 'step': 0.1},
    # Add warmth to the dark side (compensate noise from amplification)
    'right_warm_add':    {'default': 0.0, 'min': 0.0, 'max': 20.0, 'step': 2.0},
}

INTERVENTION_NAMES = list(INTERVENTION_SPEC.keys())


def default_params():
    return {k: v['default'] for k, v in INTERVENTION_SPEC.items()}


def clip_params(params):
    out = {}
    for k, v in params.items():
        spec = INTERVENTION_SPEC[k]
        out[k] = float(np.clip(v, spec['min'], spec['max']))
    return out


# =====================================================
# Intervention application
# =====================================================
def apply_intervention(frame, face_mask, params):
    """
    Apply a parameterized intervention to a frame.

    Args:
        frame: BGR uint8 (H, W, 3)
        face_mask: uint8 (H, W) — 255 inside face, 0 outside
        params: dict matching INTERVENTION_SPEC

    Returns:
        modified BGR uint8 frame
    """
    bgr = frame.astype(np.float32)
    b, g, r = bgr[:, :, 0].copy(), bgr[:, :, 1].copy(), bgr[:, :, 2].copy()
    h, w = b.shape

    # Soft face mask (smooth edges to avoid hard transitions)
    if face_mask is not None and face_mask.sum() > 0:
        face_norm = cv2.GaussianBlur(face_mask.astype(np.float32) / 255.0,
                                       (61, 61), 18)
    else:
        face_norm = np.zeros_like(b, dtype=np.float32)

    # 1. Global gain (multiplicative on full frame)
    gain = params.get('global_gain', 1.0)
    if gain != 1.0:
        b = b * gain
        g = g * gain
        r = r * gain

    # 2. Global gamma — operate on Y channel for color preservation
    gamma = params.get('global_gamma', 1.0)
    if gamma != 1.0:
        Y = 0.114 * b + 0.587 * g + 0.299 * r
        Y_norm = np.clip(Y / 255.0, 0, 1)
        Y_new = np.power(Y_norm, gamma) * 255.0
        # Scale RGB by Y ratio to preserve color
        ratio = Y_new / np.maximum(Y, 1.0)
        b = b * ratio
        g = g * ratio
        r = r * ratio

    # 3-5. Color shifts (additive)
    dR = params.get('dR', 0.0)
    dG = params.get('dG', 0.0)
    dB = params.get('dB', 0.0)
    if dR != 0: r = r + dR
    if dG != 0: g = g + dG
    if dB != 0: b = b + dB

    # 6. Saturation scale via HSV
    sat = params.get('sat_scale', 1.0)
    if sat != 1.0:
        bgr_now = np.clip(np.stack([b, g, r], axis=2), 0, 255).astype(np.uint8)
        hsv = cv2.cvtColor(bgr_now, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat, 0, 255)
        bgr_new = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8),
                                cv2.COLOR_HSV2BGR).astype(np.float32)
        b, g, r = bgr_new[:, :, 0], bgr_new[:, :, 1], bgr_new[:, :, 2]

    # 7-8. Bipolar spatial scaling on face halves (can brighten OR dim)
    left_scale = params.get('left_scale', params.get('left_dim', 1.0))
    right_scale = params.get('right_scale', params.get('right_dim', 1.0))
    if (left_scale != 1.0 or right_scale != 1.0) and face_norm.sum() > 0:
        # Build smooth left/right gradient masks within face
        rows = np.where(face_mask.sum(1) > 0)[0]
        cols = np.where(face_mask.sum(0) > 0)[0]
        if len(rows) > 0 and len(cols) > 0:
            cx = (cols[0] + cols[-1]) // 2
            x_coords = np.arange(w, dtype=np.float32)
            # Smooth sigmoid transition around cx (use larger sigma for softer blend)
            sigma = max((cols[-1] - cols[0]) * 0.20, 15.0)
            left_weight = 1.0 / (1.0 + np.exp((x_coords - cx) / sigma))  # 1 at left, 0 at right
            right_weight = 1.0 - left_weight
            left_w_2d = np.tile(left_weight, (h, 1)) * face_norm
            right_w_2d = np.tile(right_weight, (h, 1)) * face_norm

            # Scale factor blends — interpolates between 1.0 (outside) and scale (inside)
            l_scale_map = 1.0 + left_w_2d * (left_scale - 1.0)
            r_scale_map = 1.0 + right_w_2d * (right_scale - 1.0)
            scale_map = l_scale_map * r_scale_map

            b = b * scale_map
            g = g * scale_map
            r = r * scale_map

    # 11. Add warmth to the dark side (compensate amplification noise visually)
    right_warm = params.get('right_warm_add', 0.0)
    if right_warm > 0 and face_norm.sum() > 0:
        rows = np.where(face_mask.sum(1) > 0)[0]
        cols = np.where(face_mask.sum(0) > 0)[0]
        if len(rows) > 0 and len(cols) > 0:
            cx = (cols[0] + cols[-1]) // 2
            x_coords = np.arange(w, dtype=np.float32)
            sigma = max((cols[-1] - cols[0]) * 0.20, 15.0)
            right_weight = 1.0 - 1.0 / (1.0 + np.exp((x_coords - cx) / sigma))
            right_w_2d = np.tile(right_weight, (h, 1)) * face_norm
            r = r + right_warm * right_w_2d * 0.7
            g = g + right_warm * right_w_2d * 0.3
            # B unchanged → adds warmth

    # 9. Highlight rolloff inside face (compress Y > thresh, leave Y <= thresh untouched)
    rolloff = params.get('highlight_rolloff', 0.0)
    if rolloff > 0 and face_norm.sum() > 0:
        Y = 0.114 * b + 0.587 * g + 0.299 * r
        thresh = 170.0
        # Only modify pixels above threshold; clamp the rest unchanged
        excess = np.maximum(Y - thresh, 0)
        compressed = excess * (1.0 - rolloff)
        # CRITICAL: pixels below threshold must keep Y unchanged
        new_Y_above = thresh + compressed
        new_Y_full = np.where(Y > thresh, new_Y_above, Y)
        # Blend by face mask softness (outside face: original Y)
        new_Y_blend = Y * (1 - face_norm) + new_Y_full * face_norm
        ratio = new_Y_blend / np.maximum(Y, 1.0)
        b = b * ratio
        g = g * ratio
        r = r * ratio

    # 10. Face warm desaturation (pull R toward (R+G+B)/3 inside face)
    desat = params.get('face_warm_desat', 0.0)
    if desat > 0 and face_norm.sum() > 0:
        gray = (r + g + b) / 3.0
        w_desat = face_norm * desat
        r = r * (1 - w_desat) + gray * w_desat
        g = g * (1 - w_desat * 0.4) + gray * (w_desat * 0.4)
        b = b * (1 - w_desat * 0.2) + gray * (w_desat * 0.2)

    out = np.stack([b, g, r], axis=2)
    return np.clip(out, 0, 255).astype(np.uint8)


# =====================================================
# Causal calibration
# =====================================================
def calibrate_causal_model(video_path, n_samples=8, n_perturbations=25,
                            verbose=True):
    """
    Calibrate a linear structural equation model:
        delta_fp_i = sum_j (B_ij * delta_param_j) + noise_i

    Procedure:
    1. Pre-scan video to find all frames with face detection (use tracking mode
       + last_mask fallback for missed frames)
    2. Sample n_samples frames evenly from face-frame pool
    3. For each frame: apply n_perturbations random param sets, measure fp deltas
    4. Fit OLS regression for each fingerprint dim
    """
    import mediapipe as mp
    cap = cv2.VideoCapture(str(video_path))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Pre-scan: collect (frame_idx, frame, mask) for all face frames using
    # tracking-mode FaceMesh + last_mask fallback (matches face_relight.py)
    fm_track = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.3, min_tracking_confidence=0.3
    )

    if verbose:
        print(f"  Pre-scanning {n_frames} frames for face detection...")
    face_frames = []  # list of (idx, frame_copy, mask)
    last_mask = None
    last_idx = 0
    for idx in range(n_frames):
        ret, frame = cap.read()
        if not ret:
            break
        face_mask, has_face = build_face_mask(frame, fm_track)
        if has_face:
            last_mask = face_mask
            last_idx = idx
            face_frames.append((idx, frame.copy(), face_mask))
        elif last_mask is not None and (idx - last_idx) < 5:
            # Use last mask if recent (within 5 frames)
            face_frames.append((idx, frame.copy(), last_mask))

    cap.release()
    fm_track.close()

    if verbose:
        print(f"  Face frames available: {len(face_frames)}/{n_frames}")

    if len(face_frames) == 0:
        raise RuntimeError("No face frames found in calibration video")

    # Sample n_samples evenly from face_frames pool
    n_use = min(n_samples, len(face_frames))
    sample_idxs = np.linspace(0, len(face_frames) - 1, n_use).astype(int)
    sampled = [face_frames[i] for i in sample_idxs]

    # Collect (param_delta, fp_delta) pairs
    param_deltas = []
    fp_deltas = []

    rng = np.random.default_rng(42)
    n_face_frames = len(sampled)

    for (idx, frame, face_mask) in sampled:
        baseline_fp = extract_fingerprint(frame, face_mask=face_mask)

        for pi in range(n_perturbations):
            params = default_params()
            param_vec = []
            for name in INTERVENTION_NAMES:
                spec = INTERVENTION_SPEC[name]
                half = (spec['max'] - spec['min']) * 0.4
                offset = rng.uniform(-half, half)
                new_val = float(np.clip(spec['default'] + offset,
                                          spec['min'], spec['max']))
                params[name] = new_val
                param_vec.append(new_val - spec['default'])

            modified = apply_intervention(frame, face_mask, params)
            mod_fp = extract_fingerprint(modified, face_mask=face_mask)

            fp_d = {k: mod_fp[k] - baseline_fp[k]
                    for k in baseline_fp
                    if k != 'has_face' and isinstance(baseline_fp[k], (int, float))}
            param_deltas.append(param_vec)
            fp_deltas.append(fp_d)

        if verbose:
            print(f"  frame {idx}: collected {n_perturbations} perturbations")

    if not param_deltas:
        raise RuntimeError("No perturbation data collected")

    P = np.array(param_deltas)  # shape (N, K)
    fp_dims = list(fp_deltas[0].keys())

    # Fit per-dim OLS: y = P @ beta (no intercept since baseline subtracted)
    B = {}
    rmse = {}
    # Add small ridge for stability
    ridge = 1e-3 * np.eye(P.shape[1])
    PtP_inv = np.linalg.inv(P.T @ P + ridge)

    for dim in fp_dims:
        y = np.array([fpd[dim] for fpd in fp_deltas])
        beta = PtP_inv @ P.T @ y
        pred = P @ beta
        residuals = y - pred
        rmse[dim] = float(np.sqrt(np.mean(residuals ** 2)))
        B[dim] = {INTERVENTION_NAMES[i]: float(beta[i])
                  for i in range(len(INTERVENTION_NAMES))}

    return {
        'B': B,
        'rmse': rmse,
        'meta': {
            'source': str(video_path),
            'n_face_frames': n_face_frames,
            'n_perturbations_per_frame': n_perturbations,
            'total_samples': len(param_deltas),
            'fp_dimensions': fp_dims,
            'intervention_names': INTERVENTION_NAMES,
        }
    }


def predict_fingerprint_delta(model, baseline_fp, params, defaults=None):
    """
    Linear prediction: predicted_fp[dim] = baseline_fp[dim] + B[dim] · (params - defaults)
    """
    if defaults is None:
        defaults = default_params()
    delta_p = np.array([params[k] - defaults[k] for k in INTERVENTION_NAMES])
    out = {}
    for dim, coeffs in model['B'].items():
        beta = np.array([coeffs[k] for k in INTERVENTION_NAMES])
        out[dim] = baseline_fp.get(dim, 0.0) + float(beta @ delta_p)
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python3 intervention.py source_video.mp4 [output_model.json]")
        sys.exit(1)

    source = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'intervention_model.json'

    print(f"Calibrating causal model from {source}...")
    print(f"  Sampling 8 frames × 20 perturbations = 160 calibration samples")
    model = calibrate_causal_model(source, n_samples=8, n_perturbations=20)
    print(f"  Total face frames used: {model['meta']['n_face_frames']}")
    print(f"  Total samples: {model['meta']['total_samples']}")
    print()
    print("=== Top causal coefficients (|β| > 1) ===")
    for dim in sorted(model['B'].keys()):
        coeffs = model['B'][dim]
        big = {k: v for k, v in coeffs.items() if abs(v) > 1.0}
        if big:
            print(f"  {dim:20s}: " + ", ".join(f"{k}={v:+.2f}" for k, v in big.items()))

    with open(out, 'w') as f:
        json.dump(model, f, indent=2)
    print(f"\nSaved: {out}")
