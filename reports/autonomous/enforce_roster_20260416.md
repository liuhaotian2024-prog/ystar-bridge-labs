# Enforce Roster — 2026-04-16 (Full Inventory for K9 Monitor)

**Mandate**: Board 2026-04-16 — "把这几轮需要进 enforce 的名录给 K9，包括 CEO 自己"
**K9 Monitor target**: `Y-star-gov/ystar/governance/k9_routing_subscriber.py` extends to track each item below for cascading enforce status

---

## CEO-self Enforce Items (CEO 自身 discipline)

| # | Mechanism | Status | Live Verification |
|---|---|---|---|
| C-1 | Iron Rule 0 — No choice questions to Board | ✅ LIVE | hook_stop_reply_scan + BOARD_CHOICE_QUESTION_DRIFT CIEU |
| C-2 | Iron Rule 0.5 — Atomic Dispatch ≤1 deliverable | ✅ LIVE | governance/sub_agent_atomic_dispatch.md doctrine |
| C-3 | Iron Rule 1.5 — L-tag in status reports | ⚠️ warn-only | `missing_l_tag` ForgetGuard rule (#41) |
| C-4 | CEO Engineering Boundary — only ./reports/ writable | ✅ deny | ForgetGuard `ceo_engineering_boundary` (CROBA hook live) |
| C-5 | CEO Dispatch Self-Check 3-question | ⚠️ warn 48h | `ceo_dispatch_missing_self_check` (Maya Q1) |
| C-6 | CEO Mid-Stream Check-in | ✅ LIVE | `ceo_no_midstream_checkin` (Y-gov W25 R6) |
| C-7 | Coord_audit summary Rt+1 closure check | ✅ LIVE warn | `coordinator_summary_rt_audit` (Maya #33) |
| C-8 | Coord_reply 5-tuple structure | ✅ LIVE warn → deny 2026-04-18 | `coordinator_reply_missing_5tuple` (Maya #46 + Ryan #47 wire) |
| C-9 | Wave_scope undeclared | ✅ LIVE | `wave_scope_undeclared` (Maya batch) |
| C-10 | CEO ecosystem-view (EDM required) | ⏳ rule spec | `ceo_design_ecosystem_blind` (Ethan #74 → Maya pending) |
| C-11 | CEO no deferred-dispatch promise | ⏳ rule spec | `ceo_deferred_dispatch_promise_orphan` (Maya CZL-77 in flight) |
| C-12 | Methodology no hardcoded cadence | ⏳ rule spec | `methodology_hardcoded_cadence` (pending Maya impl) |
| C-13 | CEO via CTO routing for T2/T3 | ⏳ MEMORY only | `feedback_dispatch_via_cto` (need rule per tier-routing v1) |

## Sub-agent Enforce Items (engineer / C-suite discipline)

| # | Mechanism | Status |
|---|---|---|
| S-1 | tool_uses claim/metadata mismatch | ✅ LIVE warn → deny 2026-04-18 (Maya E1 #21) |
| S-2 | Subagent unauthorized git ops | ✅ LIVE warn (Maya forensic per Ryan d2852174 incident) |
| S-3 | Subagent no choice question to CEO | ⏳ MEMORY only (need rule) |
| S-4 | Hallucinated receipt (Rt+1=0 fake) | ✅ LIVE via auto_validate Path.exists check |
| S-5 | Receipt no 5-tuple structure | ⏳ Gate 2 partial (validator deep-parse Maya #45) |
| S-6 | Charter drift mid-session | ✅ LIVE (Maya I1 #23) |
| S-7 | Sub-agent commit accumulator > 5 writes | ✅ LIVE (Y-gov W21 batch) |
| S-8 | CEO direct dispatch tier audit | ✅ LIVE (CEO_DIRECT_DISPATCH_TIER1 emit + sync log) |

## Architecture-Layer Enforce Items (system mechanisms真 LIVE post-PYTHONPATH-fix)

| # | Mechanism | Status |
|---|---|---|
| A-1 | CZL Protocol v1 Gate 1 (validate_dispatch) | ✅ LIVE (Ryan #40) |
| A-2 | CZL Protocol v1 Gate 2 (validate_receipt + auto_validate) | ✅ LIVE (Leo #34 + Ryan #44) |
| A-3 | K9 event-driven trigger (PostToolUse hook → routing) | ✅ LIVE 137+ events (Ethan #52) |
| A-4 | K9 routing chain end-to-end (subscriber + 6 handlers + cascade) | ✅ LIVE (Ethan #63, 5 POST + 4 CLAIM + 2 COMPLETE) |
| A-5 | Sync layer (active_dispatch_log + boot inject CTO awareness) | ✅ LIVE (Ryan #71) |
| A-6 | Dispatch board (滴滴 T1 atomic) | ✅ LIVE (Ryan #72) |
| A-7 | RT_MEASUREMENT auto-emit on receipt | ✅ LIVE (Leo #34) |
| A-8 | Real-time archival CZL duty (Samantha) | ✅ charter LIVE / runtime ⏳ Ryan trigger #14 |
| A-9 | Cron schedule (10 entries) | ✅ Board installed + cron line 22 octal fix Ryan #70 |
| A-10 | K9-RT Sentinel cron 5-min | ⏳ wrapper ready but Board cron entry NOT installed |

## Pending Spec → Impl

| # | Spec | Impl owner | Status |
|---|---|---|---|
| SP-1 | Tier-routing v1 (T1/T2/T3) | Maya rule + Ryan classifier | spec only |
| SP-2 | CTO role v2 + dispatch board | implemented A-6 | partial |
| SP-3 | Skill-trust hybrid (#72) | Phase 2-3 35 atomics queued | spec + retroactive audit |
| SP-4 | Onboarding gauntlet (#73) | Maya/Ryan/Samantha 3 cards | spec |
| SP-5 | Ecosystem checklist (#74) | Maya rule impl C-10 | spec |
| SP-6 | Methodology v1 (#75) | Maya 8-rule mapping derivation | spec |
| SP-7 | External framework research (#76) | engineers self-build | in flight |
| SP-8 | governance_ci.py | Ryan | pending |
| SP-9 | Phase 2-3 remediation (35 atomics) | Maya + Ryan | pending |
| SP-10 | 6 per-rule hook detectors | Ryan CZL-78 | in flight |

---

## K9 Monitor Extension Mandate

`Y-star-gov/ystar/governance/k9_routing_subscriber.py` should monitor each of above (C-* / S-* / A-* / SP-*) and emit cascade event when:
- Item status changes (e.g., "spec only" → "impl shipped" → "live verified" → "auto-promoted to deny")
- Dry_run expiry (2026-04-18 batch) — emit `RULE_DRY_RUN_EXPIRED` per rule
- Live fire delta = 0 over expected window — emit `ENFORCE_HOLLOW_WIRE` (Maya/Ryan investigate)
- Spec → impl gap aging > 5 sessions — emit `SPEC_IMPL_GAP_STALE`

K9 dashboard / monitor: `governance/enforce_status_dashboard.md` auto-updated by K9 subscriber on cascade events.

---

**Total enforce items**: 41 (13 CEO + 8 Sub-agent + 10 Architecture + 10 Pending Spec→Impl)
**LIVE真 verified**: ~22 (54%)
**Spec only / impl pending**: ~19 (46%)

Board mandate: drive % LIVE真 → 100% via parallel batch + K9 monitor cascade.
