# Office Archive — Digital Human Figures Inventory (per-agent)

**Prepared**: 2026-04-23 Samantha Lin (Secretary) [L3 AUDITED]
**Scope**: One section only — per-agent figure inventory + MVP trio + patent drift archive entry.
**Method**: targeted `find`/`ls`/`git log` (no recursive Read).

## 1. Per-agent Digital Human Figure Inventory

| Agent | Has figure? | File path(s) | Format | Generation tech | Reusable for MVP? |
|---|---|---|---|---|---|
| aiden (CEO) | Y | `docs/aiden.jpg`, `docs/aiden_intro.webm` | still image + intro clip | unknown still; webm likely HeyGen/custom TTS | Y — CEO is face of company, both still + motion asset exist |
| ethan (CTO) | Y | `docs/ethan.jpg` | still image | unknown (likely Midjourney/reference photo) | Y — still is sufficient for MVP card; no motion yet |
| leo (eng-kernel) | N | — | — | — | N — no asset, engineer tier deferred |
| maya (eng-governance) | N | — | — | — | N — no asset, engineer tier deferred |
| ryan (eng-platform) | N | — | — | — | N — no asset, engineer tier deferred |
| jordan (eng-domains) | N | — | — | — | N — no asset, engineer tier deferred |
| sofia (CMO) | Y | `docs/sofia.jpg` + HeyGen ep001 v2-v10 pipeline (`content/offended_ai/v*/portrait_upload.json`) | still + talking-head video via HeyGen Avatar IV | HeyGen (confirmed by `feat(cmo): ship Episode 001 v2-v10 HeyGen` commits) | Y — only agent with full production video pipeline proven |
| zara (CSO) | Y | `docs/zara.jpg` | still image | unknown (Midjourney likely) | Y — still-card MVP ready |
| marco (CFO) | Y | `docs/marco.jpg` | still image | unknown | Y — still-card MVP ready |
| samantha (Secretary) | Y | `docs/samantha.jpg`, `docs/samantha_ref.jpg`, `docs/micro_chain_test/samantha_oneshot_FINAL.mp4` + micro_000/001/002.mp4 | still + reference + CogVideoX-2b micro-chain test video (480x320, 3.125s) | CogVideoX-2b local generation (docs/micro_chain_test/governance_log.json 2026-04-10) | Y — only non-CMO agent with motion artifact; experimental quality |

**Coverage**: 6/10 agents have figures (aiden, ethan, sofia, zara, marco, samantha). All 4 engineers lack assets.

## 2. MVP-Ready Trio Recommendation

1. **Sofia (CMO)** — only agent with a production-grade HeyGen talking-head pipeline proven across 10 episode iterations; motion-ready today.
2. **Aiden (CEO)** — face of the company, has both still (`aiden.jpg`) and intro motion (`aiden_intro.webm`); MVP must include founder.
3. **Samantha (Secretary)** — sole experimental motion asset outside CMO domain; CogVideoX-2b micro-chain proves non-HeyGen path works; hedge against HeyGen credit depletion.

Rationale: trio covers (a) polished vendor-pipeline exemplar, (b) founder identity, (c) diversified-tech fallback. Ethan/Zara/Marco remain still-only until Wave-2.

## 3. Patent Line-Drift Archive Entry

- **Archive ID**: `ARCH-2026-04-23-PATENT-DRIFT`
- **Issue**: US Provisional Patent 63/981,777 (filed 2026-03-26) cites `cieu_store.py` lines 596–664 for Merkle sealing algorithm. Actual code post-Leo 2026-04-23 wire-up is at lines 716–784 (~120-line drift). Runtime gap closed (0 → 659,489 sealed events); patent text line numbers inaccurate.
- **Action required**: refile amended patent text with corrected line numbers (716–784) OR include drift declaration in non-provisional conversion.
- **Deadline**: **2027-03-26** (USPTO provisional-to-non-provisional conversion window, 12 months from filing).
- **Priority**: P3 (non-urgent; legal/admin; no runtime or customer impact).
- **Status**: ARCHIVED, pending Board decision on amendment path (refile vs. conversion-time correction).

---

**Receipt**:
- path: `reports/secretary/office_archive_digital_humans_20260423.md`
- tool_uses: 6
- MVP trio quote: "Sofia, Aiden, Samantha — polished pipeline, founder identity, diversified-tech fallback."
