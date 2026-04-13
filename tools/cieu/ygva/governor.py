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
    mirror_face_reference, DEFAULT_WEIGHTS,
)
from intervention import (
    INTERVENTION_NAMES, INTERVENTION_SPEC, default_params, clip_params,
    apply_intervention, predict_fingerprint_delta,
)
from physical_align import physical_align_pipeline, compute_reference_stats


def make_mirror_local_reference(baseline_fp, mirror_fp, global_palette=None,
                                  lift_cap=0.15):
    """
    Per-frame reference using MIRROR REFERENCE (Phase 2 upgrade).

    The mirror reference fingerprint gives us PHYSICALLY VALID quadrant values
    derived from the actual frame — no external data needed.

    Strategy:
      - Symmetry dims → 0 (Yf_LR_diff, R_LR_diff, sat_LR_diff)
      - Quadrants → mirror reference's value, BUT capped at baseline*lift_cap
        to prevent over-brightening
      - Yf_mean → midpoint between baseline and mirror (gentle lift)
      - Global palette dims → segA anchor (Y_mean, L_mean, V_mean, color_temp)
      - All other dims → keep baseline
    """
    ref = dict(baseline_fp)
    if not baseline_fp.get('has_face'):
        return ref

    yf_baseline = baseline_fp.get('Yf_mean', 100)
    cap_max = yf_baseline * (1 + lift_cap)  # max allowed face brightness

    # Symmetry constraints
    ref['Yf_LR_diff'] = 0.0
    ref['R_LR_diff'] = 0.0
    ref['sat_LR_diff'] = 0.0

    if mirror_fp is not None and mirror_fp.get('has_face'):
        # Use mirror's quadrant values, capped
        ref['Yf_TL'] = min(mirror_fp.get('Yf_TL', yf_baseline), cap_max)
        ref['Yf_TR'] = min(mirror_fp.get('Yf_TR', yf_baseline), cap_max)
        ref['Yf_BL'] = min(mirror_fp.get('Yf_BL', yf_baseline), cap_max)
        ref['Yf_BR'] = min(mirror_fp.get('Yf_BR', yf_baseline), cap_max)
        # Yf_mean: midpoint between baseline and capped mirror mean
        target_yf_mean = (mirror_fp.get('Yf_mean', yf_baseline) + yf_baseline) / 2
        ref['Yf_mean'] = min(target_yf_mean, cap_max)
        # Use mirror's other face stats (they're physically valid)
        if 'sat_f' in mirror_fp:
            ref['sat_f'] = mirror_fp['sat_f']
        if 'color_temp_f' in mirror_fp:
            ref['color_temp_f'] = mirror_fp['color_temp_f']
        if 'warmth_highlight' in mirror_fp:
            ref['warmth_highlight'] = mirror_fp['warmth_highlight']
    else:
        # Fallback: uniform quadrants at baseline mean
        ref['Yf_TL'] = yf_baseline
        ref['Yf_TR'] = yf_baseline
        ref['Yf_BL'] = yf_baseline
        ref['Yf_BR'] = yf_baseline
        if baseline_fp.get('warmth_highlight', 0) > 10:
            ref['warmth_highlight'] = 5.0

    # Anchor global brightness/color to segA
    if global_palette is not None:
        ref['Y_mean'] = global_palette.get('Y_mean', baseline_fp.get('Y_mean'))
        ref['L_mean'] = global_palette.get('L_mean', baseline_fp.get('L_mean'))
        ref['V_mean'] = global_palette.get('V_mean', baseline_fp.get('V_mean'))
        ref['Y_p50'] = global_palette.get('Y_p50', baseline_fp.get('Y_p50'))
        ref['color_temp'] = global_palette.get('color_temp', baseline_fp.get('color_temp'))

    return ref


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
        # === Global params: ESSENTIALLY FROZEN ===
        'global_gain':       {'min': 0.99, 'max': 1.01},
        'global_gamma':      {'min': 0.99, 'max': 1.01},
        'dR':                {'min': -1.0, 'max': 1.0},
        'dG':                {'min': -0.5, 'max': 0.5},
        'dB':                {'min': -1.0, 'max': 1.0},
        'sat_scale':         {'min': 0.96, 'max': 1.04},
        # === Face-region params: GENTLE (DNA #011) ===
        # Old aggressive bounds (left 0.5, right 2.0) caused "dilution"
        # because the GaussianBlur'd face mask bleeds operations into hair/
        # neck/background. Tighter bounds = subtler corrections = no halo.
        'left_scale':        {'min': 0.80, 'max': 1.05},
        'right_scale':       {'min': 0.95, 'max': 1.25},
        'highlight_rolloff': {'min': 0.0, 'max': 0.4},
        'face_warm_desat':   {'min': 0.0, 'max': 0.20},
        'right_warm_add':    {'min': 0.0, 'max': 6.0},
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
      1. Brightness/color anchor to segA — UPGRADED to STRONG
         (DNA: in v1 inter-segment, solver drifted Y/L/G/B/color_temp
          while satisfying symmetry. Anchor must dominate.)
      2. Symmetry defect fixing
      3. Face mean alignment
    """
    return {
        # === Brightness/color anchor — STRONG (must dominate solver) ===
        'Y_mean':     4.0,
        'L_mean':     4.0,
        'V_mean':     3.0,
        'Y_p50':      2.5,
        'color_temp': 3.0,
        'sat_mean':   2.0,
        'R_mean':     1.5,
        'G_mean':     1.5,
        'B_mean':     1.5,
        # === Symmetry ===
        'Yf_LR_diff': 5.0,
        'R_LR_diff':  3.0,
        'sat_LR_diff': 1.0,
        # === Face quadrants ===
        'Yf_TL': 1.5, 'Yf_TR': 3.0, 'Yf_BL': 1.5, 'Yf_BR': 3.0,
        # === Face anchors ===
        'Yf_mean': 2.0,
        'color_temp_f': 0.5,
        'warmth_highlight': 1.5,
        'sat_f': 0.5,
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

    # === NEW: Compute physical alignment reference from prev segment ===
    if verbose:
        print(f"  Computing physical alignment reference from prev segment...")
    phys_ref_stats = compute_reference_stats(prev_segment_path, n_samples=20)
    phys_ref_frame = phys_ref_stats.get('representative_frame')
    if phys_ref_frame is not None and verbose:
        print(f"  Physical reference frame: {phys_ref_frame.shape}")

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


def inter_segment_governance(prev_segment_path, next_segment_path,
                                output_path, model, global_palette=None,
                                cieu_out=None, max_change_frac=0.10,
                                ridge=0.05, verbose=True):
    """
    Cross-segment YGVCC entry point — Phase 2.

    Treats `next_segment` as a sequence that should converge to:
      1. The MIRROR-derived ideal symmetric face (per-frame, mirror reference)
      2. The PREVIOUS segment's global palette (color/lighting consistency)
      3. The PREVIOUS segment's last frame's fingerprint (boundary smoothness)

    Three convergence forces:
      a) Face symmetry: mirror reference per frame → Yf_LR_diff → 0
      b) Global palette anchoring: Y_mean/L_mean/V_mean/color_temp → segA values
      c) Cross-segment boundary: first N frames of next_segment treated specially
         with extra weight on matching prev_segment's last frame

    Args:
        prev_segment_path: e.g. segA video (provides anchor)
        next_segment_path: e.g. segB video (gets governed)
        output_path: where to write governed next_segment
        model: causal model (calibrated on next_segment via intervention.py)
        global_palette: optional pre-computed segA fingerprint dict (else extracted)
        cieu_out: optional path to CIEU JSON
    """
    import mediapipe as mp

    if verbose:
        print(f"=== YGVCC inter-segment governance ===")
        print(f"  Previous segment: {os.path.basename(prev_segment_path)}")
        print(f"  Next segment:     {os.path.basename(next_segment_path)}")
        print(f"  Output:           {os.path.basename(output_path)}")

    # 1. Build / use global palette from prev_segment (anchor)
    if global_palette is None:
        if verbose: print(f"  Extracting palette from {os.path.basename(prev_segment_path)}...")
        from fingerprint import extract_video_reference
        global_palette = extract_video_reference(
            prev_segment_path, frame_index='last', n_average=15,
            hybrid_ideal_face=True
        )
    if verbose:
        print(f"  Anchor: Y_mean={global_palette.get('Y_mean'):.1f}, "
              f"color_temp={global_palette.get('color_temp'):.1f}, "
              f"sat={global_palette.get('sat_mean'):.1f}")

    # 2. Extract prev_segment's last 10 frames fingerprint (for boundary smoothing)
    if verbose: print(f"  Extracting prev_segment last 10 frames for boundary anchor...")
    fm_static = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1,
        refine_landmarks=False, min_detection_confidence=0.1,
    )
    prev_cap = cv2.VideoCapture(prev_segment_path)
    prev_n = int(prev_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    boundary_fps = []
    for idx in range(max(0, prev_n - 10), prev_n):
        prev_cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, f = prev_cap.read()
        if not ret: continue
        m, has = build_face_mask(f, fm_static)
        boundary_fps.append(extract_fingerprint(f, face_mask=m if has else None))
    prev_cap.release()
    fm_static.close()
    boundary_anchor = None
    if boundary_fps:
        boundary_anchor = {
            k: float(np.mean([fp[k] for fp in boundary_fps]))
            for k in boundary_fps[0]
            if k != 'has_face' and isinstance(boundary_fps[0][k], (int, float))
        }
        if verbose:
            print(f"  Boundary anchor: Y_mean={boundary_anchor.get('Y_mean'):.1f}")

    # 3. Open next_segment and run governance loop with mirror references
    cap = cv2.VideoCapture(next_segment_path)
    fps_v = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if verbose:
        print(f"  Next segment: {w}x{h} @ {fps_v:.1f}fps, {n} frames")

    fm = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1, refine_landmarks=False,
        min_detection_confidence=0.3, min_tracking_confidence=0.3,
    )

    # Pre-scan: first usable mask (fallback)
    first_mask = None
    for _ in range(min(60, n)):
        ret, frame = cap.read()
        if not ret: break
        m, has = build_face_mask(frame, fm)
        if has:
            first_mask = m
            break
    cap.release()
    cap = cv2.VideoCapture(next_segment_path)

    # === Compute physical alignment reference frame from prev segment ===
    # Use LAST REAL non-black frame (DNA #014: median composite has wrong stats)
    phys_ref_frame = None
    prev_cap = cv2.VideoCapture(prev_segment_path)
    prev_n_frames = int(prev_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for back in range(2, 20):
        idx = prev_n_frames - back
        if idx < 0: break
        prev_cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, f = prev_cap.read()
        if ret and float(f.mean()) > 30:
            phys_ref_frame = f
            if verbose:
                print(f"  Physical alignment ref: prev frame {idx}, Y={float(f.mean()):.0f}")
            break
    prev_cap.release()

    tmpdir = tempfile.mkdtemp()
    cieu_records = []
    prev_params = None
    last_mask = first_mask
    weights = make_focused_weights()
    gov_bounds = make_governance_bounds()
    rt_before_total = 0.0
    rt_after_total = 0.0
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret: break

        face_mask, has_face = build_face_mask(frame, fm)
        if has_face:
            last_mask = face_mask
        elif last_mask is not None:
            face_mask = last_mask

        # === PHYSICAL ALIGNMENT (BEFORE fingerprint — the frame itself is modified) ===
        # This is the "physical level forced alignment" that fixes:
        # - Y_p10 (shadow lifting from Kling) via histogram + tone curve
        # - Y_p99 (highlight clipping) via histogram
        # - sat_mean (saturation drift) via histogram + color transfer
        # - color_temp (color shift) via Reinhard LAB transfer
        if phys_ref_frame is not None:
            frame = physical_align_pipeline(
                frame, phys_ref_frame,
                histogram_strength=0.7,
                detail_strength=0.0,  # DISABLED: median ref too soft, causes edge loss
                black_crush=0.5,
                highlight_compress=0.3,
                midtone_contrast=0.15,
                color_transfer_strength=0.4,
            )

        baseline_fp = extract_fingerprint(frame, face_mask=face_mask)

        # === KEY: build target via mirror reference ===
        _, mirror_fp = mirror_face_reference(frame, face_mask)
        target_fp = make_mirror_local_reference(
            baseline_fp, mirror_fp, global_palette=global_palette
        )

        # Boundary smoothing: first 10 frames of next_segment must align
        # to prev_segment's last frame anchor with strong weight
        boundary_weight_boost = 0.0
        if boundary_anchor is not None and frame_idx < 10:
            boundary_weight_boost = (10 - frame_idx) / 10.0  # 1.0 → 0.0
            # Pull a few key dims toward boundary
            for k in ['Y_mean', 'L_mean', 'V_mean', 'color_temp', 'sat_mean']:
                if k in boundary_anchor and k in target_fp:
                    target_fp[k] = (target_fp[k] * (1 - boundary_weight_boost)
                                     + boundary_anchor[k] * boundary_weight_boost)

        rt_before, _ = fingerprint_distance(target_fp, baseline_fp, weights)

        # Active CIEU iterative counterfactual solve
        opt_params, _ = iterative_counterfactual_solve(
            baseline_fp, target_fp, model,
            gov_bounds=gov_bounds, weights=weights,
            max_iter=10, damping=0.5, tol_frac=0.05, ridge=ridge,
        )
        applied_params = temporal_smooth_params(
            opt_params, prev_params, max_change_frac=max_change_frac
        )
        applied_params = clip_to_governance(applied_params, gov_bounds)

        # OPTIMIZATION: skip intervention if all params are at defaults
        # (no-face frames or frames where solver returned identity)
        defaults = default_params()
        is_noop = all(
            abs(applied_params[k] - defaults[k]) < 0.005
            for k in applied_params
        )
        if is_noop:
            modified = frame  # PASS-THROUGH — no float math, no PNG round-trip artifacts
        else:
            modified = apply_intervention(frame, face_mask, applied_params)
        # NOTE: removed unsharp mask — it was over-sharpening (+40%) and
        # introducing artificial high-frequency noise on no-face frames

        modified_fp = extract_fingerprint(modified, face_mask=face_mask)
        rt_after, _ = fingerprint_distance(target_fp, modified_fp, weights)

        cieu_records.append({
            'frame': frame_idx,
            'has_face': has_face,
            'rt_before': rt_before,
            'rt_after': rt_after,
            'rt_delta': rt_after - rt_before,
            'opt_params': opt_params,
            'applied_params': applied_params,
            'mirror_used': mirror_fp is not None,
            'boundary_weight': boundary_weight_boost,
        })
        rt_before_total += rt_before
        rt_after_total += rt_after

        cv2.imwrite(os.path.join(tmpdir, f'f_{frame_idx:05d}.png'), modified)
        prev_params = applied_params
        frame_idx += 1

        if verbose and frame_idx % 30 == 0:
            avg_b = rt_before_total / frame_idx
            avg_a = rt_after_total / frame_idx
            print(f"  {frame_idx}/{n}: avg Rt {avg_b:.1f} → {avg_a:.1f} "
                  f"(↓{(1-avg_a/avg_b)*100:.0f}%)", flush=True)

    cap.release()
    fm.close()

    if verbose:
        avg_b = rt_before_total / max(frame_idx, 1)
        avg_a = rt_after_total / max(frame_idx, 1)
        print(f"\n=== Governance summary ===")
        print(f"  Frames: {frame_idx}")
        print(f"  Avg Rt before: {avg_b:.2f}")
        print(f"  Avg Rt after:  {avg_a:.2f}")
        print(f"  Reduction:     {(1-avg_a/avg_b)*100:.0f}%")

    # Re-encode with audio — use PRECISE framerate so video duration ==
    # audio duration exactly (avoids 47ms av_sync mismatch from -c:a copy)
    if verbose: print(f"\nRe-encoding with audio (precise framerate)...")
    # Probe input audio duration
    try:
        audio_dur_s = subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=duration',
            '-of', 'default=nw=1:nk=1', next_segment_path
        ], stderr=subprocess.DEVNULL).decode().strip()
        audio_dur = float(audio_dur_s) if audio_dur_s else (frame_idx / fps_v)
    except Exception:
        audio_dur = frame_idx / fps_v

    # Compute precise fps so n_frames * (1/precise_fps) = audio_dur
    precise_fps = frame_idx / audio_dur
    if verbose:
        print(f"  audio_dur={audio_dur:.4f}s, frames={frame_idx}, "
              f"precise_fps={precise_fps:.4f} (orig={fps_v:.4f})")

    cmd = [
        'ffmpeg', '-y', '-framerate', f'{precise_fps}',
        '-i', os.path.join(tmpdir, 'f_%05d.png'),
        '-i', next_segment_path,
        '-map', '0:v', '-map', '1:a?',
        # CRF=12 + veryslow preset for high-quality encoding (was crf=18 slow)
        # DNA: crf=18 caused visible "dilution" — 38% sharpness loss on
        # no-face passthrough frames. crf=12 makes the loss imperceptible.
        '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '12',
        '-pix_fmt', 'yuv420p',
        '-r', f'{precise_fps}', '-c:a', 'copy', output_path
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(f"FFmpeg error: {r.stderr.decode()[-500:]}")
    shutil.rmtree(tmpdir)
    if verbose: print(f"Saved: {output_path}")

    if cieu_out:
        with open(cieu_out, 'w') as f:
            json.dump({
                'mode': 'inter_segment',
                'prev': prev_segment_path,
                'next': next_segment_path,
                'output': output_path,
                'global_palette': global_palette,
                'boundary_anchor': boundary_anchor,
                'records': cieu_records,
            }, f, indent=2, default=str)
        if verbose: print(f"CIEU records: {cieu_out}")

    return cieu_records


if __name__ == '__main__':
    # Two modes:
    # (1) Single segment governance (existing):
    #     python3 governor.py input.mp4 output.mp4 reference.json model.json [cieu.json]
    # (2) Inter-segment governance (NEW Phase 2):
    #     python3 governor.py --inter prev.mp4 next.mp4 output.mp4 model.json [cieu.json]

    if len(sys.argv) >= 6 and sys.argv[1] == '--inter':
        prev = sys.argv[2]
        nxt  = sys.argv[3]
        out  = sys.argv[4]
        model_path = sys.argv[5]
        cieu_out = sys.argv[6] if len(sys.argv) > 6 else None

        with open(model_path) as f:
            model = json.load(f)

        inter_segment_governance(
            prev_segment_path=prev,
            next_segment_path=nxt,
            output_path=out,
            model=model,
            cieu_out=cieu_out,
        )
        sys.exit(0)

    if len(sys.argv) < 5:
        print(__doc__)
        print("Usage: python3 governor.py input.mp4 output.mp4 reference.json model.json [cieu.json]")
        print("       python3 governor.py --inter prev.mp4 next.mp4 output.mp4 model.json [cieu.json]")
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
