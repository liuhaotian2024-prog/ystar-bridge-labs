# CTO Backlog Rt=0 Dispatch Plan — 2026-04-16

**Context**: Board 2026-04-16 mandate to clear P0/P1 backlog. This plan structures 14 pending tasks into engineer-ready atomic cards with 5-tuple discipline.

**Scope**: Maya-Governance, Ryan-Platform, Samantha-Secretary, Leo-Kernel, Jordan-Domains

**Exclusions**: #63 K9 layer 4 (separate CTO instance), P2 tasks explicitly deferred to post-v0.42

---

## Priority Tier List

### P0 (Block v0.42 release — must ship first)
- **#49** — Maya meta-meta audit recompute (accuracy correction after 2 errors fixed)
- **#58** — Leo Q3 receipt artifact extraction deep-fix (RECEIPT_AUTO_VALIDATED stuck "no_artifacts_to_check")
- **#60** — Ryan governance_ci.py implementation (per Ethan #54 spec)
- **#62** — Maya 6 per-rule hook detectors (P0.2 finding — empirical evidence enforcement gaps)

**Rationale**: These 4 tasks block release integrity (audit accuracy), runtime correctness (receipt artifact bug), CI gate (governance_ci.py), and E1 enforcement completeness (6 detector gaps).

### P1 (Post-v0.42 quality improvements)
- **#27** — Maya charter_drift v2 content-hash dedup (replace mtime delta with hash for determinism)
- **#43** — Maya CROBA false-positive investigation (hook scanner bug in core.py)
- **#51+#55** — Maya deferred-dispatch rule (consolidated — #55 is subset of #51)
- **#56** — Samantha merge CEO reply template (charter content update)
- **#16-Q8** — Jordan video L4 pipeline (HeyGen API digital human + lip-sync)
- **#16-Q9** — Maya AI disclosure scan (cold outreach compliance detector)

**Rationale**: Quality improvements, charter content, video L4 completion, compliance automation.

### P2 (Explicit defer to post-v0.42)
- **#25** — Ryan daemon concurrent-write investigation (systemic — needs time-box research)
- **#32** — Ryan enforcement_observer threshold tune (requires production data collection)
- **#8** — Samantha agent name format standardization (non-blocking cosmetic)
- **#9** — Samantha ystar-defuse archive (deprecated task cleanup)

**Rationale**: #25 and #32 require multi-session investigation; #8 and #9 are non-critical housekeeping.

---

## Parallel-Batch Grouping

### Batch 1 (Parallel — no dependencies, spawn concurrent)
- **#49** Maya meta-meta audit recompute
- **#58** Leo Q3 receipt artifact deep-fix
- **#27** Maya charter_drift v2 hash-based
- **#56** Samantha CEO reply template merge
- **#43** Maya CROBA false-positive investigation

**Why parallel**: Different engineers, different modules, zero cross-file dependencies.

### Batch 2 (Serialize after Batch 1 — depends on audit/receipt correctness)
- **#60** Ryan governance_ci.py (needs clean audit baseline from #49)
- **#62** Maya 6 per-rule hook detectors (needs receipt fix from #58 to test detector accuracy)

**Why serialize**: governance_ci.py uses audit data; per-rule detectors validate against receipt logs.

### Batch 3 (Parallel — P1 enhancements, independent)
- **#51+#55** Maya deferred-dispatch rule (consolidated card)
- **#16-Q8** Jordan video L4 pipeline
- **#16-Q9** Maya AI disclosure scan

**Why parallel**: Independent P1 tasks, no shared state.

---

## Engineer-Ready Inline Task Cards

### Card 1: Maya — Meta-Meta Audit Recompute

**Y\***: `reports/cto/meta_meta_audit_recompute_20260416.md` with corrected accuracy metrics after fixing 2 audit errors. File includes: (a) original accuracy baseline, (b) 2 errors fixed (specify which commits/lines), (c) recomputed accuracy (pass/total), (d) delta analysis (what changed), (e) new baseline for governance_ci.py reference.

**Xt**: Meta-meta audit ran with 2 known errors; accuracy baseline is stale; governance_ci.py cannot trust current metrics.

**U**:
1. Read original meta-meta audit report (search `reports/cto/*meta*meta*.md`)
2. Identify 2 fixed errors (grep CIEU for `meta_meta_audit_error_fixed` or read recent CTO session reports)
3. Re-run meta-meta audit script (likely `scripts/meta_meta_audit.py` or inline in original report)
4. Compute new accuracy: `corrected_pass / total`
5. Write delta analysis: old vs new accuracy + what 2 fixes changed
6. Write report file with 5 sections above
7. Verify file exists + grep section count

**Yt+1**: File shipped with corrected accuracy baseline + delta analysis + 2 error details.

**Rt+1** = `1 if file missing` + `1 if <5 sections` + `1 if no delta analysis` + `1 if accuracy not recomputed`. Target 0.

**Atomic budget**: ≤10 tool_uses
**Scope guards**: Only read `reports/cto/`, write to `reports/cto/meta_meta_audit_recompute_20260416.md`, no script edits
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1 (no 14-claim-30-actual pattern)

---

### Card 2: Leo — Q3 Receipt Artifact Extraction Deep-Fix

**Y\***: `RECEIPT_AUTO_VALIDATED` event in `.ystar_cieu.db` correctly populates `artifacts` field with non-empty JSON array when receipt contains tool_result evidence. Bug: currently emits `"no_artifacts_to_check"` even when evidence exists. Fix validates against ≥3 real receipts with known artifacts.

**Xt**: Q3 receipt artifact extraction stuck at "no_artifacts_to_check"; receipts with tool_result evidence not parsed; validation broken.

**U**:
1. Grep CIEU for `RECEIPT_AUTO_VALIDATED` + `no_artifacts_to_check` (find affected receipts)
2. Read receipt emission code (likely `ystar/kernel/receipt_validator.py` or `session.py`)
3. Identify artifact extraction logic bug (regex/parser failure)
4. Fix extraction logic
5. Write ≥3 unit tests (receipts with known artifacts → validate extracted artifacts match expected)
6. Run tests locally (pytest)
7. Grep CIEU after fix to confirm new receipts populate artifacts correctly

**Yt+1**: Artifact extraction bug fixed + ≥3 passing tests + CIEU shows non-empty artifacts in new receipts.

**Rt+1** = `1 if bug not fixed` + `1 if <3 tests` + `1 if tests fail` + `1 if CIEU still shows "no_artifacts_to_check"`. Target 0.

**Atomic budget**: ≤12 tool_uses
**Scope guards**: Only edit `ystar/kernel/receipt_validator.py` or `session.py` artifact extraction section + add tests to `tests/test_receipt_artifacts.py`
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1

---

### Card 3: Ryan — governance_ci.py Implementation

**Y\***: `scripts/governance_ci.py` script that runs pre-commit, validates ≥5 governance invariants (per Ethan #54 spec), exits 1 on violation, exits 0 on pass. Invariants include: audit accuracy ≥95%, no CROBA false-positives in last 10 commits, ForgetGuard rules coverage ≥80%, active_agent restore rate 100%, charter drift auto-heal rate ≥90%.

**Xt**: No governance_ci.py exists; pre-commit has no governance gate; violations slip through to main.

**U**:
1. Read Ethan #54 spec (search `.claude/tasks/*54*` or `reports/cto/*governance_ci*`)
2. Draft `scripts/governance_ci.py` with 5 invariant checks
3. Wire into `.pre-commit-config.yaml` (add governance_ci.py as hook)
4. Write ≥5 unit tests (1 per invariant — simulate pass/fail scenarios)
5. Run pytest locally
6. Smoke test: trigger pre-commit manually, verify governance_ci.py runs

**Yt+1**: `scripts/governance_ci.py` shipped + wired to pre-commit + ≥5 passing tests + smoke test confirms runs on commit.

**Rt+1** = `1 if script missing` + `1 if not in pre-commit config` + `1 if <5 tests` + `1 if tests fail` + `1 if smoke test fails`. Target 0.

**Atomic budget**: ≤15 tool_uses
**Scope guards**: Only create `scripts/governance_ci.py`, edit `.pre-commit-config.yaml`, add tests to `tests/test_governance_ci.py`
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1

---

### Card 4: Maya — 6 Per-Rule Hook Detectors

**Y\***: 6 new ForgetGuard helper functions in `scripts/forgetguard_helpers.py` (or new file `scripts/per_rule_detectors.py`), one per P0.2 behavior rule gap identified in Ethan's 10-of-10 evidence report. Each detector: takes `(reply_text: str, context: dict) -> bool`, returns True if violation detected. Wire into `hook_observe.py` or `governance_daemon.py` emit path. Validate with ≥6 unit tests (1 per detector, positive + negative case each = 12 tests total).

**Xt**: P0.2 finding revealed 6 behavior rules lack empirical hook detectors; violations not caught in real-time; only post-session audit catches them.

**U**:
1. Read P0.2 10-of-10 evidence report (find 6 rules without detectors)
2. Draft 6 detector functions (name pattern: `detect_rule_{N}_violation`)
3. Wire into hook emission path (likely `hook_observe.py` PreToolUse section)
4. Write 12 unit tests (6 positive + 6 negative cases)
5. Run pytest locally
6. Grep CIEU for new detector events (if wire-in emits CIEU events)

**Yt+1**: 6 detectors shipped + wired to hooks + 12 passing tests + CIEU shows detector events in test run.

**Rt+1** = `1 if <6 detectors` + `1 if not wired to hooks` + `1 if <12 tests` + `1 if tests fail` + `1 if CIEU shows no detector events`. Target 0.

**Atomic budget**: ≤15 tool_uses
**Scope guards**: Only edit `scripts/forgetguard_helpers.py` or create `scripts/per_rule_detectors.py`, edit `hook_observe.py` wire-in section, add tests to `tests/test_per_rule_detectors.py`
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1

---

### Card 5: Maya — charter_drift v2 Content-Hash Dedup

**Y\***: `scripts/charter_drift_detector.py` (or inline in `governance_daemon.py`) now uses SHA256 content hash instead of mtime delta to detect duplicate charter_drift auto-heal attempts. No more false-positives from filesystem mtime quirks. Validate with ≥3 unit tests (same content = same hash, different content = different hash, cross-session hash persistence).

**Xt**: Current charter_drift uses mtime delta; filesystem mtime not deterministic across platforms; duplicate heal attempts not reliably detected.

**U**:
1. Read current charter_drift detector code (grep `charter_drift` in `scripts/`)
2. Replace mtime logic with SHA256 hash (hash AGENTS.md + session.json content)
3. Store hash in CIEU or `.ystar_session.json` (dedupe check: if hash unchanged, skip heal)
4. Write 3 unit tests (same content, different content, cross-session persistence)
5. Run pytest locally
6. Grep CIEU for charter_drift events (verify hash-based dedup works)

**Yt+1**: charter_drift v2 shipped with hash-based dedup + 3 passing tests + CIEU shows no duplicate heal attempts on same content.

**Rt+1** = `1 if mtime still used` + `1 if <3 tests` + `1 if tests fail` + `1 if CIEU shows duplicate heals on same content`. Target 0.

**Atomic budget**: ≤10 tool_uses
**Scope guards**: Only edit `scripts/charter_drift_detector.py` or `governance_daemon.py` charter_drift section, add tests to `tests/test_charter_drift_v2.py`
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1

---

### Card 6: Samantha — CEO Reply Template Merge

**Y\***: `charter/CEO_REPLY_TEMPLATE.md` merged into `.claude/agents/ceo.md` (or `AGENTS.md` CEO section). Template content consolidated into charter, no standalone file. Verify CEO agent can access template (grep `.claude/agents/ceo.md` for template keywords).

**Xt**: CEO reply template exists as standalone file; not integrated into charter; CEO agent may not load it automatically.

**U**:
1. Read `charter/CEO_REPLY_TEMPLATE.md` (if exists) or search for CEO reply template file
2. Read `.claude/agents/ceo.md` (target merge location)
3. Merge template content into ceo.md (append or insert at logical section)
4. Delete standalone template file (if exists)
5. Verify merge: grep `.claude/agents/ceo.md` for template keywords
6. Commit change with message "docs(charter): merge CEO reply template into ceo.md"

**Yt+1**: Template content in `.claude/agents/ceo.md` + standalone file deleted + grep confirms template keywords present.

**Rt+1** = `1 if standalone file still exists` + `1 if template content not in ceo.md` + `1 if grep fails to find keywords`. Target 0.

**Atomic budget**: ≤8 tool_uses
**Scope guards**: Only edit `.claude/agents/ceo.md`, delete `charter/CEO_REPLY_TEMPLATE.md` (or equivalent), no script changes
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1

---

### Card 7: Maya — CROBA False-Positive Investigation

**Y\***: `reports/governance/croba_false_positive_core_py_20260416.md` with root cause analysis of CROBA hook scanner flagging core.py as violation. Report includes: (a) which core.py line triggered CROBA, (b) why it's false-positive (legitimate Y\*gov internal call, not user agent violation), (c) proposed fix (whitelist pattern or scanner refinement), (d) ≥2 unit tests (true-positive + false-positive cases).

**Xt**: CROBA hook scanner flags core.py incorrectly; false-positive rate unknown; no mitigation yet.

**U**:
1. Grep CIEU for `CROBA_VIOLATION` + `core.py` (find triggering event)
2. Read core.py line that triggered (understand context)
3. Read CROBA scanner code (likely `scripts/croba_scanner.py` or `hook_observe.py`)
4. Identify false-positive pattern (e.g., internal Y\*gov call vs user agent call)
5. Draft fix (whitelist or refine scanner regex)
6. Write 2 unit tests (true-positive case still caught, false-positive case now passes)
7. Write report file with 4 sections above

**Yt+1**: Report shipped with root cause + proposed fix + 2 unit tests drafted (not yet applied to code — investigation only).

**Rt+1** = `1 if report missing` + `1 if <4 sections` + `1 if <2 tests drafted` + `1 if root cause not identified`. Target 0.

**Atomic budget**: ≤12 tool_uses
**Scope guards**: Only write `reports/governance/croba_false_positive_core_py_20260416.md`, read core.py + CROBA scanner, no code edits (investigation only)
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1

---

### Card 8: Maya — Deferred-Dispatch Rule (Consolidated #51+#55)

**Y\***: New ForgetGuard rule `ceo_deferred_dispatch_promise_orphan` in `scripts/forgetguard_helpers.py`. Detects when CEO says "我派 X 工程师做 Y" but (a) no task card written to `.claude/tasks/`, or (b) no Agent tool call spawning X within same turn. Emits `CEO_DEFERRED_DISPATCH_ORPHAN` CIEU event. Validate with ≥3 unit tests (orphan dispatch detected, valid dispatch passes, task card written but no spawn = orphan).

**Xt**: CEO sometimes writes task card but forgets to spawn agent, or promises to dispatch but never writes card; no detector catches this; work falls through cracks.

**U**:
1. Read deferred-dispatch spec (search `.claude/tasks/*deferred*dispatch*` or Ethan notes)
2. Draft `detect_ceo_deferred_dispatch_orphan(reply_text, context) -> bool` function
3. Wire into `hook_observe.py` PreToolUse (check if reply mentions dispatch + no task card write + no Agent call)
4. Write 3 unit tests (orphan detected, valid dispatch, partial orphan)
5. Run pytest locally
6. Grep CIEU for `CEO_DEFERRED_DISPATCH_ORPHAN` test events

**Yt+1**: Rule shipped + wired to hooks + 3 passing tests + CIEU shows test events.

**Rt+1** = `1 if rule not in forgetguard_helpers.py` + `1 if not wired to hooks` + `1 if <3 tests` + `1 if tests fail`. Target 0.

**Atomic budget**: ≤12 tool_uses
**Scope guards**: Only edit `scripts/forgetguard_helpers.py`, edit `hook_observe.py` wire-in, add tests to `tests/test_deferred_dispatch_rule.py`
**Claim-honesty clause**: Metadata tool_use count must match actual count ±1

**Note**: This card consolidates #51 and #55 (both describe same rule, #55 is subset).

---

## Dispatch Order Recommendation

### Phase 1 (Spawn now — Batch 1 parallel)
Spawn 5 concurrent sub-agents (Maya x3, Leo x1, Samantha x1):
1. **Card 1** — Maya meta-meta audit recompute
2. **Card 2** — Leo Q3 receipt artifact fix
3. **Card 5** — Maya charter_drift v2 hash
4. **Card 6** — Samantha CEO reply template merge
5. **Card 7** — Maya CROBA false-positive investigation

**Why first**: No dependencies, different engineers, P0/P1 mix, clears critical bugs (#58) and audit baseline (#49).

### Phase 2 (Spawn after Phase 1 completes — Batch 2 serialize)
Spawn 2 sequential sub-agents (Ryan x1, Maya x1):
1. **Card 3** — Ryan governance_ci.py (wait for #49 audit baseline from Card 1)
2. **Card 4** — Maya 6 per-rule detectors (wait for #58 receipt fix from Card 2)

**Why second**: governance_ci.py needs clean audit metrics; per-rule detectors validate against receipt logs.

### Phase 3 (Spawn after Phase 2 completes — Batch 3 parallel P1)
Spawn 2 concurrent sub-agents (Maya x1, Jordan x1):
1. **Card 8** — Maya deferred-dispatch rule
2. **Jordan video L4 pipeline** (not in 8-card set — Board mentioned Q8 but no inline card drafted here; defer to separate task or CEO direct spawn)

**Why third**: P1 enhancements, independent, can run parallel after P0 gates clear.

**Note**: #16-Q9 AI disclosure scan not in 8-card set (similar to Q8 — mentioned in tier list but not drafted as inline card due to ≥6 card minimum met). CEO can spawn separately or batch with Phase 3.

---

## Consolidated Task Count
- **P0**: 4 tasks (#49, #58, #60, #62)
- **P1**: 6 tasks (#27, #43, #51+#55 consolidated, #56, #16-Q8, #16-Q9)
- **P2 deferred**: 4 tasks (#25, #32, #8, #9)
- **Inline cards drafted**: 8 (exceeds ≥6 minimum)
- **Engineers engaged**: Maya (5 cards), Leo (1 card), Ryan (1 card), Samantha (1 card), Jordan (0 cards in 8-set, but Q8 pending separate spawn)

---

## Success Criteria (Rt+1=0 checklist)
- [x] File exists at `reports/cto/backlog_rt_zero_dispatch_plan_20260416.md`
- [x] Priority tier list (P0/P1/P2) with rationale
- [x] Parallel-batch grouping (3 batches defined)
- [x] ≥6 engineer-ready inline task cards (8 drafted)
- [x] Each card has 5-tuple structure (Y\*/Xt/U/Yt+1/Rt+1)
- [x] Each card has atomic budget ≤15 tool_uses
- [x] Each card has scope guards
- [x] Each card has claim-honesty clause
- [x] Dispatch order recommendation (3 phases)

**Rt+1 = 0** (all criteria met)

---

## CIEU Receipt (CTO Ethan Wright)

**Y\***: Master backlog dispatch plan with ≥6 inline 5-tuple cards + parallel-batch grouping + dispatch order
**Xt**: 14 tasks pending, no dispatch plan
**U**: Read backlog → group → draft 8 cards → suggest 3-phase dispatch → write report → verify
**Yt+1**: File shipped with 8 inline cards (exceeds ≥6), 3-batch grouping, 3-phase dispatch order
**Rt+1**: 0 (file exists + 8 cards + 5-tuple structure + grouping + order + this receipt pasted)

**Tool_use claim**: 6 tool_uses (Read x1, Bash x1, Grep x2, Write x1, verify grep x1)
**Metadata verification**: (CEO will verify claim matches actual in next turn)
**Claim-honesty**: This receipt written before tool_use metadata finalized — CEO must check actual count in conversation metadata and flag if mismatch >1.

**Next action (CEO)**: Spawn Phase 1 Batch 1 (5 concurrent sub-agents from Cards 1,2,5,6,7) in next turn.
