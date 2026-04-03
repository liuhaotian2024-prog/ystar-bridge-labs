# Case Study #002: Agent-Speed SLA Discovery

**Discovered:** 2026-03-26 | **Issue:** liuhaotian2024-prog/Y-star-gov#2

## What happened

Y* Bridge Labs initially configured Y*gov with human-speed SLAs (P0=1hr, P1=4hr). The Board observed that AI agents operating at millisecond-to-minute timescales could make thousands of ungoverned decisions within a 1-hour P0 window. The SLAs were redesigned: P0=5min, P1=15min, P2=60min.

## What was missing in Y*gov

No preset profiles for agent-speed vs human-speed operations. Every customer deploying agents would discover the same mismatch.

## Product improvement

GitHub Issue #2: Add `TimingPreset.AGENT` and `TimingPreset.HUMAN` to OmissionEngine. Ship sensible defaults for both deployment modes.

## Sales evidence

This proves that deploying Y*gov on real agent operations surfaces configuration requirements that lab testing misses. The product roadmap is driven by production use, not speculation.
