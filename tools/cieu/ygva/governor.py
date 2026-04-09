#!/usr/bin/env python3
"""
YGVA Phase 3 — Per-Frame Governance Loop with Counterfactual Planning

Core innovation: instead of applying per-frame heuristic corrections (which
cause flicker because corrections are noisy across frames), we:

  1. Define a single REFERENCE fingerprint (the convergence target)
  2. Calibrate a CAUSAL MODEL of how interventions move fingerprints
  3. Per frame: solve for the optimal intervention that minimizes Rt
  4. Apply TEMPORAL CONSTRAINT: bound parameter change vs prev frame
     (this is the "delegation monotonicity" rule from Y*gov — child
     correction must be a strict subset of parent allowed range)
  5. Apply intervention; record CIEU; verify Rt decreased

Result: temporally smooth corrections → no flicker → consistent appearance
that converges toward the reference state.

This is a Pearl Level 3 application:
  - Observation: current frame fingerprint
  - Causal model: B (calibrated structural equations)
  - Counterfactual query: "if I had applied params=p, what would Rt be?"
  - Action selection: pick p that minimizes E[Rt | do(params=p)]
  - Temporal smoothing: enforce monotonicity wrt prev intervention
"""
import cv2
import numpy as np
import json
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from fingerprint import (
    build_face_mask, extract_fingerprint, fingerprint_distance,
    DEFAULT_WEIGHTS,
)
from intervention import (
    INTERVENTION_NAMES, INTERVENTION_SPEC, default_params, clip_params,
    apply_intervention, predict_fingerprint_delta,
)


def make_local_reference(baseline_fp, global_palette=None):
    """
    Build a per-frame reference that fixes face defects, preserves the
    frame's content where appropriate, and ANCHORS global brightness/color
    to the segA reference (so the solver can't drift overall exposure).

    Strategy:
      - Asymmetry dims (Yf_LR_diff, R_LR_diff, sat_LR_diff) → 0
      - Face quadrants (Yf_TL/TR/BL/BR) → face mean (uniform)
      - Highlight warmth → small positive value
      - Y_mean, L_mean, V_mean → anchored to segA reference (BRIGHTNESS LOCK)
      - color_temp → anchored to segA reference
      - Yf_p99 → not constrained (was causing right_scale < 1 compromise)
      - All other dims → keep baseline

    Args:
        baseline_fp: current frame fingerprint
        global_palette: segA reference for global anchoring

    Returns:
        local_reference dict
    """
    ref = dict(baseline_fp)
    if not baseline_fp.get('has_face'):
        return ref

    yf_mean = baseline_fp.get('Yf_mean', 100)

    # Symmetry constraints — the actual defect we're fixing
    ref['Yf_LR_diff'] = 0.0
    ref['R_LR_diff'] = 0.0
    ref['sat_LR_diff'] = 0.0

    # Uniform face quadrants
    ref['Yf_TL'] = yf_mean
    ref['Yf_TR'] = yf_mean
    ref['Yf_BL'] = yf_mean
    ref['Yf_BR'] = yf_mean

    # Highlight warmth → reduce orange cast
    if baseline_fp.get('warmth_highlight', 0) > 10:
        ref['warmth_highlight'] = 5.0

    # BRIGHTNESS LOCK — anchor to segA so solver can't drift global exposure
    if global_palette is not None:
        ref['Y_mean'] = global_palette.get('Y_mean', baseline_fp.get('Y_mean'))
        ref['L_mean'] = global_palette.get('L_mean', baseline_fp.get('L_mean'))
        ref['V_mean'] = global_palette.get('V_mean', baseline_fp.get('V_mean'))
        ref['Y_p50'] = global_palette.get('Y_p50', baseline_fp.get('Y_p50'))
        ref['color_temp'] = global_palette.get('color_temp', baseline_fp.get('color_temp'))
        # Face brightness anchor — but only pull moderately (face is closeup detail)
        seg_a_y = global_palette.get('Y_mean', 100)
        # Set face mean target between current and segA Y_mean
        ref['Yf_mean'] = (yf_mean + seg_a_y) / 2

    return ref


def make_governance_bounds():
    """
    Tighter bounds for governance mode — prevents solver from using
    extreme global color shifts as compensation for face-region defects.

    Lessons learned (DNA):
      - dG > 5 produces "诡异绿光" / weird green tint → bound to ±3
      - face_warm_desat > 0.5 makes face look greyish-dead → bound to 0.4
      - global_gamma outside [0.9, 1.1] visible exposure shift → tighten
      - left_dim/right_dim < 0.8 produces "dark cloud patch" → 0.85 floor
    """
    return {
        # Tighter global to prevent overall brightness drift
        'global_gain':       {'min': 0.97, 'max': 1.03},
        'global_gamma':      {'min': 0.95, 'max': 1.05},
        'dR':                {'min': -4.0, 'max': 4.0},
        'dG':                {'min': -2.0, 'max': 2.0},
        'dB':                {'min': -4.0, 'max': 4.0},
        'sat_scale':         {'min': 0.92, 'max': 1.08},
        # Bipolar — left can dim down hard, right can lift up to 2x
        'left_scale':        {'min': 0.50, 'max': 1.05},
        'right_scale':       {'min': 0.95, 'max': 2.00},
        'highlight_rolloff': {'min': 0.0, 'max': 0.5},
        'face_warm_desat':   {'min': 0.0, 'max': 0.35},
        'right_warm_add':    {'min': 0.0, 'max': 10.0},
    }


def clip_to_governance(params, gov_bounds):
    out = {}
    for k, v in params.items():
        b = gov_bounds.get(k, {'min': INTERVENTION_SPEC[k]['min'],
                                 'max': INTERVENTION_SPEC[k]['max']})
        out[k] = float(np.clip(v, b['min'], b['max']))
    return out


def make_focused_weights():
    """
    Weights focused on three priorities (in order):
      1. Symmetry defect fixing (root cause)
      2. Brightness lock to segA (so we don't drift globally)
      3. Face mean alignment

    DNA: removed Yf_p99 from weights — it was causing right_scale<1 compromise
    when solver had to choose between symmetry and highlight compression.
    """
    return {
        # === Brightness lock — STRONG (Board complaint: too bright) ===
        'Y_mean':  2.0,
        'L_mean':  2.0,
        'V_mean':  1.5,
        'Y_p50':   1.5,
        # === Symmetry (CRITICAL — root cause) ===
        'Yf_LR_diff': 5.0,
        'R_LR_diff':  3.0,
        'sat_LR_diff': 1.0,
        # === Face quadrants — bumped to break Yf_TR/BR vs Yf_p99 deadlock ===
        'Yf_TL': 1.5, 'Yf_TR': 3.0, 'Yf_BL': 1.5, 'Yf_BR': 3.0,
        # === Face mean — anchor to segA-aligned value ===
        'Yf_mean': 2.0,
        # === Color anchoring ===
        'color_temp':   1.0,
        'color_temp_f': 0.5,
        'warmth_highlight': 1.5,
        # === Saturation lock to prevent solver from desaturating ===
        'sat_mean': 0.8,
        'sat_f':    0.5,
        # NOTE: Yf_p99 deliberately excluded — was blocking right lift
    }


def solve_optimal_params(baseline_fp, reference_fp, model, weights=None,
                          ridge=0.05):
    """
    Weighted least-squares solution for the optimal intervention parameters.

    Minimize: sum_i w_i * (target_delta_i - B_i · param_delta)^2 + ridge * ||param_delta||^2

    Args:
        baseline_fp: current frame's fingerprint (dict)
        reference_fp: target fingerprint (dict)
        model: causal model from calibrate_causal_model()
        weights: per-dim weights (defaults to DEFAULT_WEIGHTS)
        ridge: regularization to keep parameter changes small

    Returns:
        params dict (matches INTERVENTION_NAMES)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    fp_dims = [d for d in model['B'].keys()
               if d in baseline_fp and d in reference_fp]

    K = len(INTERVENTION_NAMES)
    n = len(fp_dims)

    # Build B matrix (n × K) and target vector y (n)
    B = np.zeros((n, K))
    y = np.zeros(n)
    w = np.zeros(n)
    for i, dim in enumerate(fp_dims):
        coeffs = model['B'][dim]
        for j, name in enumerate(INTERVENTION_NAMES):
            B[i, j] = coeffs.get(name, 0.0)
        y[i] = reference_fp[dim] - baseline_fp[dim]  # desired delta
        w[i] = weights.get(dim, 0.5)

    # Weighted least squares: minimize ||W^0.5 (y - B @ p)||^2 + ridge * ||p||^2
    sqW = np.diag(np.sqrt(w))
    Bw = sqW @ B
    yw = sqW @ y

    # Normal equations with ridge regularization
    BtB = Bw.T @ Bw + ridge * np.eye(K)
    Bty = Bw.T @ yw

    try:
        delta_p = np.linalg.solve(BtB, Bty)
    except np.linalg.LinAlgError:
        delta_p = np.zeros(K)

    # Convert delta_p (relative to defaults) → absolute params
    defaults = default_params()
    params = {}
    for j, name in enumerate(INTERVENTION_NAMES):
        params[name] = defaults[name] + float(delta_p[j])

    return clip_params(params)


def iterative_counterfactual_solve(baseline_fp, target_fp, model,
                                      gov_bounds, weights,
                                      max_iter=8, damping=0.5,
                                      tol_frac=0.05, ridge=0.05,
                                      record_trace=False):
    """
    Pearl Level 3 iterative counterfactual planner.

    Combines passive + active CIEU:
      PASSIVE: observe baseline_fp from real frame (no intervention applied)
      ACTIVE: iterative refinement loop in counterfactual space:
              1. Compute current Rt
              2. Solve for incremental Δu via linear least squares
              3. Compose with running u (with damping)
              4. PREDICT resulting fp via causal model (no real apply)
              5. Verify predicted Rt decreased; else stop
              6. Update state and iterate

    The key innovation: search happens entirely in counterfactual space using
    the causal model as a simulator. The actual frame is only modified ONCE
    at the end, with the converged composite u. This avoids:
      - Compounding artifacts from repeated apply-measure cycles
      - Slow per-iteration disk I/O
      - Pixel saturation from successive operations

    Args:
        baseline_fp:  observed fingerprint (passive CIEU output)
        target_fp:    convergence target (local reference)
        model:        causal model (B coefficients)
        gov_bounds:   governance constraints on u
        weights:      per-dim weights for Rt computation
        max_iter:     max iterations (typically converges in 3-5)
        damping:      step damping factor (0.5 = take half-steps)
        tol_frac:     stop when Rt < tol_frac * initial Rt
        ridge:        ridge for inner solver

    Returns:
        (final_u, trace) where trace is list of per-iteration Rt values.
    """
    initial_Rt, _ = fingerprint_distance(target_fp, baseline_fp, weights)
    tol = max(initial_Rt * tol_frac, 1.0)

    u = default_params()
    current_fp = dict(baseline_fp)
    best_u = dict(u)
    best_Rt = initial_Rt

    trace = []
    if record_trace:
        trace.append({'iter': 0, 'Rt': initial_Rt, 'u': dict(u)})

    for it in range(1, max_iter + 1):
        Rt, _ = fingerprint_distance(target_fp, current_fp, weights)
        if Rt < tol:
            break

        # Solve for an incremental u that reduces residual
        # The solver returns absolute u that would minimize Rt for current_fp
        delta_u_solution = solve_optimal_params(
            current_fp, target_fp, model, weights=weights, ridge=ridge
        )
        # Compose: u_new = u + damping * (delta_u_solution - default)
        defaults = default_params()
        new_u = {}
        for k in u:
            step = delta_u_solution[k] - defaults[k]
            new_u[k] = u[k] + damping * step
        new_u = clip_to_governance(new_u, gov_bounds)

        # Counterfactual prediction: what fp would this u produce?
        predicted_fp = predict_fingerprint_delta(model, baseline_fp, new_u)
        new_Rt, _ = fingerprint_distance(target_fp, predicted_fp, weights)

        if record_trace:
            trace.append({'iter': it, 'Rt': new_Rt, 'u': dict(new_u)})

        # Active CIEU decision: commit only if Rt improved
        if new_Rt >= Rt - 0.01:
            # No improvement — try smaller step (halve damping)
            if damping > 0.05:
                damping = damping * 0.5
                continue
            else:
                break  # converged

        u = new_u
        current_fp = predicted_fp

        if new_Rt < best_Rt:
            best_u = dict(u)
            best_Rt = new_Rt

    return best_u, trace


def temporal_smooth_params(new_params, prev_params, max_change_frac=0.15):
    """
    Bound rate of parameter change vs previous frame.

    This is the core anti-flicker mechanism: each parameter can change at most
    `max_change_frac` of its allowed range per frame. Equivalent to a low-pass
    filter on intervention parameters across the time axis.

    Y*gov analogy: the child intervention's allowed scope at frame t must be
    within the parent intervention's scope at frame t-1, expanded by a small
    monotonicity-preserving epsilon.

    Args:
        new_params: solver output for current frame
        prev_params: applied params for previous frame (or None)
        max_change_frac: max fractional change per frame (0.15 = 15% of range)

    Returns:
        smoothed params dict
    """
    if prev_params is None:
        return new_params

    out = {}
    for name, target in new_params.items():
        prev = prev_params[name]
        spec = INTERVENTION_SPEC[name]
        max_step = (spec['max'] - spec['min']) * max_change_frac
        delta = target - prev
        # Clip delta to ±max_step
        delta_clipped = float(np.clip(delta, -max_step, max_step))
        out[name] = prev + delta_clipped

    return clip_params(out)


def governance_loop(input_video, output_video, reference_fp, model,
                     weights=None, max_change_frac=0.15, ridge=0.05,
                     verbose=True, use_local_reference=True):
    """
    Apply YGVA governance loop to a video.

    For each frame:
      1. Extract fingerprint
      2. Solve optimal intervention via least-squares against reference
      3. Apply temporal smoothness constraint vs prev params
      4. Apply intervention to frame
      5. Re-extract fingerprint, compute Rt before/after
      6. Log to CIEU records

    Returns:
        list of per-frame CIEU records
    """
    import mediapipe as mp

    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if verbose:
        print(f"Input: {os.path.basename(input_video)}")
        print(f"Video: {w}x{h} @ {fps:.1f}fps, {n} frames")
        print(f"Reference: {reference_fp.get('_meta', {}).get('source', 'unknown')}")
        print(f"Causal model: {len(model['B'])} fp dims × {len(INTERVENTION_NAMES)} interventions")

    # Tracking-mode face mesh + last_mask fallback (matches calibrate)
    fm = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.3, min_tracking_confidence=0.3
    )

    # Pre-scan: find the first usable mask for fallback
    if verbose:
        print("  Pre-scanning for first face mask (fallback)...")
    first_mask = None
    for _ in range(min(60, n)):
        ret, frame = cap.read()
        if not ret: break
        m, has = build_face_mask(frame, fm)
        if has:
            first_mask = m
            break
    cap.release()
    cap = cv2.VideoCapture(input_video)

    tmpdir = tempfile.mkdtemp()
    cieu_records = []
    prev_params = None
    last_mask = first_mask
    last_idx = -10
    rt_before_total = 0.0
    rt_after_total = 0.0
    frame_idx = 0

    if weights is None:
        weights = make_focused_weights()
    gov_bounds = make_governance_bounds()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_mask, has_face = build_face_mask(frame, fm)
        if has_face:
            last_mask = face_mask
            last_idx = frame_idx
        elif last_mask is not None:
            face_mask = last_mask  # fallback

        baseline_fp = extract_fingerprint(frame, face_mask=face_mask)

        # Per-frame target: fix face defects but preserve content
        if use_local_reference:
            target_fp = make_local_reference(baseline_fp, global_palette=reference_fp)
        else:
            target_fp = reference_fp

        rt_before, _ = fingerprint_distance(target_fp, baseline_fp, weights)

        # ACTIVE CIEU: iterative counterfactual planner
        # Search happens in counterfactual space using causal model as
        # simulator — no real-frame trial-and-error.
        opt_params, cf_trace = iterative_counterfactual_solve(
            baseline_fp, target_fp, model,
            gov_bounds=gov_bounds, weights=weights,
            max_iter=8, damping=0.5, tol_frac=0.05, ridge=ridge,
            record_trace=False,
        )
        # Temporal smoothness — bounds rate of change vs prev frame
        # (the anti-flicker mechanism)
        applied_params = temporal_smooth_params(
            opt_params, prev_params, max_change_frac=max_change_frac
        )
        applied_params = clip_to_governance(applied_params, gov_bounds)

        # Apply intervention
        modified = apply_intervention(frame, face_mask, applied_params)

        # Final unsharp mask — recover edge detail lost in HSV roundtrips
        # and gaussian blends. Mild sigma to avoid halo artifacts.
        blurred = cv2.GaussianBlur(modified, (0, 0), sigmaX=1.2)
        modified = cv2.addWeighted(modified, 1.4, blurred, -0.4, 0)

        # Verify
        modified_fp = extract_fingerprint(modified, face_mask=face_mask)
        rt_after, _ = fingerprint_distance(target_fp, modified_fp, weights)

        # CIEU record
        cieu_records.append({
            'frame': frame_idx,
            'has_face': has_face,
            'rt_before': rt_before,
            'rt_after': rt_after,
            'rt_delta': rt_after - rt_before,
            'opt_params': opt_params,
            'applied_params': applied_params,
        })
        rt_before_total += rt_before
        rt_after_total += rt_after

        # Save frame
        cv2.imwrite(os.path.join(tmpdir, f'f_{frame_idx:05d}.png'), modified)

        prev_params = applied_params
        frame_idx += 1

        if verbose and frame_idx % 50 == 0:
            avg_before = rt_before_total / frame_idx
            avg_after = rt_after_total / frame_idx
            print(f"  {frame_idx}/{n}: avg Rt {avg_before:.2f} → {avg_after:.2f} "
                  f"(↓{(1 - avg_after/avg_before)*100:.0f}%)", flush=True)

    cap.release()
    fm.close()

    if verbose:
        avg_before = rt_before_total / max(frame_idx, 1)
        avg_after = rt_after_total / max(frame_idx, 1)
        print(f"\n=== Governance summary ===")
        print(f"  Frames: {frame_idx}")
        print(f"  Avg Rt before: {avg_before:.2f}")
        print(f"  Avg Rt after:  {avg_after:.2f}")
        print(f"  Reduction:     {(1 - avg_after/avg_before)*100:.0f}%")

    # Re-encode with audio
    if verbose:
        print(f"\nRe-encoding with audio...")
    cmd = [
        'ffmpeg', '-y',
        '-framerate', f'{fps}',
        '-i', os.path.join(tmpdir, 'f_%05d.png'),
        '-i', input_video,
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-r', f'{fps}',
        '-c:a', 'copy',
        output_video
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"FFmpeg error: {r.stderr.decode()[-500:]}")
        shutil.rmtree(tmpdir)
        return cieu_records

    shutil.rmtree(tmpdir)
    if verbose:
        print(f"Saved: {output_video}")

    return cieu_records


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print(__doc__)
        print("Usage: python3 governor.py input.mp4 output.mp4 reference.json model.json [cieu.json]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2]
    ref_path = sys.argv[3]
    model_path = sys.argv[4]
    cieu_out = sys.argv[5] if len(sys.argv) > 5 else None

    with open(ref_path) as f:
        reference_fp = json.load(f)
    with open(model_path) as f:
        model = json.load(f)

    records = governance_loop(inp, out, reference_fp, model)

    if cieu_out:
        with open(cieu_out, 'w') as f:
            json.dump({
                'input': inp,
                'output': out,
                'reference': ref_path,
                'model': model_path,
                'records': records,
            }, f, indent=2)
        print(f"CIEU records: {cieu_out}")
