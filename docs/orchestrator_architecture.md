# Y*video — Long Video Orchestrator Architecture

**Date**: 2026-04-09
**Status**: Design draft for Board review
**Author**: CTO Ethan (Mac mini overnight session)

## Executive Summary

Y*video is a **long-video generation orchestrator** that uses open-source video generation models as commodity primitives, while contributing the **missing piece**: cross-segment consistency governance.

**Thesis**: Open-source video generation has reached parity with closed-source (Sora, Kling, Pika, Veo). The remaining moat is **temporal/cross-segment consistency**, which Y*video provides via the YGVCC framework.

## The Problem

Current state of generative video (April 2026):
- Sora, Kling, Pika, Veo: closed-source SaaS, expensive, gated
- CogVideoX (Apache 2.0), Mochi-1 (Apache 2.0), HunyuanVideo (Apache 2.0), LTX-Video (OpenRAIL): SOTA-level open source
- **Common failure mode**: All of them lose consistency over multi-segment generation

When you generate a 60-second video as 6 × 10-second segments:
- Character drift (face changes, hair/skin shifts)
- Environment drift (lighting changes between cuts)
- Color drift (saturation/temperature shifts)
- Detail drift (sharpness varies)
- Style drift (slightly different aesthetic)

**Nobody solves this in open source.** That's the gap.

## The Architecture

```
                       ┌──────────────────────────┐
                       │   Y*video Orchestrator   │
                       │   (our IP)               │
                       └────────────┬─────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ↓                     ↓                     ↓
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │ Generation Layer │  │ YGVCC Layer      │  │ Output Layer     │
    │ (open source)    │  │ (our innovation) │  │ (FFmpeg)         │
    │                  │  │                  │  │                  │
    │ • LTX-Video      │  │ • physical_align │  │ • H.264 encode   │
    │ • CogVideoX      │  │ • face symmetry  │  │ • audio mux      │
    │ • Mochi-1        │  │ • iterative      │  │ • seamless concat│
    │ • HunyuanVideo   │  │   counterfactual │  │                  │
    │ • SVD            │  │ • temporal       │  │                  │
    │                  │  │   monotonicity   │  │                  │
    │ I2V continuation │  │ • CIEU audit     │  │                  │
    └──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Core Workflow: Long Video Continuation

```python
def generate_long_video(seed_video, storyboard_segments):
    """
    Generate a long video from a seed using continuation + YGVCC consistency.

    Args:
        seed_video: starting clip (e.g., stage 1A walking)
        storyboard_segments: list of (prompt, duration_seconds) tuples

    Returns:
        long_video.mp4 with cross-segment consistency
    """
    # Build reference state from seed
    reference_fingerprint = extract_fingerprint(seed_video)
    reference_last_frame = get_last_frame(seed_video)

    output_segments = [seed_video]

    for i, (prompt, duration) in enumerate(storyboard_segments):
        # Use last frame of previous segment as continuation seed
        seed_frame = get_last_frame(output_segments[-1])

        # Generate next segment with image-to-video model
        raw_segment = ltx_video_generate(
            seed_image=seed_frame,
            prompt=prompt,
            duration=duration,
        )

        # Apply YGVCC physical alignment to fix Kling-style degradation
        physically_aligned = physical_align_pipeline(
            raw_segment, reference_frame=reference_last_frame
        )

        # Apply face symmetry governance if face visible
        face_governed = inter_segment_governance(
            prev=output_segments[-1],
            next=physically_aligned,
        )

        # Verify Rt convergence
        rt = compute_rt(face_governed, reference_fingerprint)
        if rt > tolerance:
            log_warning(f"Segment {i}: Rt {rt} > tolerance")

        # Append to output
        output_segments.append(face_governed)

        # Update reference (use rolling average to allow gradual drift)
        reference_fingerprint = update_reference(reference_fingerprint, face_governed)

    return concat_segments(output_segments)
```

## Component Selection (decided)

### Generation Layer

| Model | License | M4 24GB Compatible | Selected |
|---|---|---|---|
| **LTX-Video 0.9.7-distilled** | OpenRAIL-M | ✅ Confirmed | ⭐ Primary |
| CogVideoX-2B | Apache 2.0 | ✅ via diffusers MPS | Backup |
| AnimateDiff | Apache 2.0 | ⚠ memory crashes reported | Skip |
| Mochi-1 | Apache 2.0 | ❌ too large (10B params) | Skip |
| HunyuanVideo | Apache 2.0 | ❌ GPU only | Skip |
| Stable Video Diffusion | Stability (commercial restricted) | ✅ | License issue |

### YGVCC Layer

Already built in `tools/cieu/ygva/`:
- `fingerprint.py` (35-dim per-frame extractor)
- `intervention.py` (11-param library + causal calibration)
- `governor.py` (iterative counterfactual + inter_segment)
- `physical_align.py` (4 classical CV tools, no ML)

### Output Layer

FFmpeg + libx264 (system standard).

## What's New vs Existing Work

| Capability | Sora/Kling | Open source | **Y*video** |
|---|---|---|---|
| Text-to-video | ✅ | ✅ (CogVideoX, Mochi) | Uses open source |
| Image-to-video | ✅ | ✅ (LTX-Video, SVD) | Uses open source |
| **Cross-segment consistency** | ❌ | ❌ | ✅ **YGVCC** |
| **Audit trail (SHA-256)** | ❌ | ❌ | ✅ via Y*gov cieu_store |
| **Counterfactual planning** | ❌ | ❌ | ✅ Pearl L3 active CIEU |
| Local Mac M4 deployment | ❌ | Partial | ✅ |

## Why This Wins

1. **Generation is commodity** — open source has caught up. No moat there.
2. **Consistency is the gap** — nobody else does it well at the cross-segment level.
3. **Y*gov framework** — we already have the governance primitives. Pearl L3, structural equations, CIEU chain. Wrap them with video adapters.
4. **MIT-friendly stack** — entire pipeline is MIT/Apache compatible, can be open-sourced.

## Migration Plan

**Tonight (overnight session)**:
- ✅ Mission 1: physical_align + 3-segment governance demo
- 🚧 Mission 2: LTX-Video hello-world on M4

**Tomorrow**:
- Test LTX-Video on Mac M4 with stage1A seed
- If working: generate 6-segment continuation following TL-008 storyboard
- Apply YGVCC at each segment boundary
- Compare consistency with raw Kling output

**Next week**:
- Refactor `tools/cieu/ygva/` → `ystar-video/` standalone repo
- Open source as MIT
- Write arXiv paper draft
- HN/Twitter launch

## Open Questions for Board

1. Should ystar-video be MIT or AGPL? (affects how others can use it)
2. Once ystar-video is shipped, should we offer a hosted SaaS version too?
3. Do we want to integrate with external generation APIs (Replicate, fal.ai) as fallback for users without M4?

These can be answered after first working demo.
