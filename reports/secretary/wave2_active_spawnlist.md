---
Audience: CEO (Aiden) — primary, will consume this as a spawn checklist in next turn. Secondary: CTO (Ethan) for pre-flight ruling on ordering; Wave-2 engineers (Leo/Maya/Ryan) as target receivers.
Research basis: dispatch_board_archive_20260424.md Section D STILL-RELEVANT classification; MEMORY feedback keys [工程任务派白板不直 spawn / CTO subagent cannot async orchestrate / Sub-agent dispatch must explicitly prohibit git ops / Dispatch negative-constraint regex trap]; current session Wave-1.5 work stream (Leo PPID marker) to avoid collision.
Synthesis: 9 items remain executable today but white-board subscriber is structurally broken (can't Agent-spawn). CEO must direct-spawn each via the Agent tool in-turn. Spawn prompts below are pre-scoped with (a) positive-allowlist scope (not negative "NO" regex — per regex-trap memory), (b) explicit "no git commit/push/add" scope guard, (c) 5-tuple receipt requirement, (d) tool_uses self-count + MANDATORY breakdown, (e) ordering by upstream dependency so downstream items don't re-block.
Purpose: Enable CEO to Agent-spawn 9 items without re-deriving prompts. Each entry below is a copy-paste-ready spawn block. Ordering is Wave-2a (structural unblocks first) → Wave-2b (M-2 closure) → Wave-2c (honesty + schema).
---

# Wave-2 Active Spawn List — 9 items from dispatch_board triage 2026-04-24

**Secretary**: Samantha Lin
**Maturity Tag**: [L3] ready-to-spawn list; each entry's M-axis tag noted per item
**Source**: `reports/secretary/dispatch_board_archive_20260424.md` Section D
**Spawn channel**: CEO Agent tool (NOT dispatch_board.py post) until white-board subscriber structural fix lands

---

## Wave-2a — Upstream unblocks (spawn FIRST, parallel OK)

### 2a.1 INC-2026-04-23-ITEM-5 — CZL Gate 1 Import Family Audit (P0, eng-kernel Leo)
**M-tag**: M-2a structural import resolution (blocker for multiple downstream)
**Budget**: 20 tool_uses
**Agent target**: Leo-Chen (eng-kernel)
**Spawn prompt**:
> P0 INC-2026-04-23-ITEM-5. CZL Gate 1 transitive import family audit for `ystar.governance.identity_detector` + `ystar.governance.forget_guard` ModuleNotFoundError. Ref: `reports/inc-20260423-task-cards.md` Item 5.
>
> Actions: (1) grep live refs; (2) detect stale egg-info; (3) rm stale; (4) `pip install -e .` rebuild at `/Users/haotianliu/.openclaw/workspace/Y-star-gov/`; (5) 3 smoke imports verify; (6) write receipt to `reports/kernel_import_audit_20260423.md`.
>
> Scope (allowlist): Y-star-gov/ystar/, Y-star-gov/*.egg-info, reports/kernel_import_audit_20260423.md, scripts/ for smoke-test execution.
> Scope guard: no git commit, no git push, no git add. Budget 20 tool_uses. Report 5-tuple receipt (Y*/Xt/U/Yt+1/Rt+1) with MANDATORY tool_uses self-count + breakdown {bash/read/edit/write/grep/glob/agent}.

### 2a.2 INC-2026-04-23-ITEM-3 — forget_guard None.startswith 1-line fix (P0, eng-governance Maya)
**M-tag**: M-2a commission-path hardening
**Budget**: 8 tool_uses
**Agent target**: Maya-Patel (eng-governance)
**Spawn prompt**:
> P0 INC-2026-04-23-ITEM-3. FORGET_GUARD None.startswith 1-line fix. Ref: `reports/inc-20260423-task-cards.md` Item 3 + `reports/incidents/2026-04-23-hook-fail-closed-deadlock.md`. Also fixes Item 4 RuntimeError spam (downstream cascade).
>
> Actions: (1) locate None.startswith line in `scripts/forget_guard.py`; (2) add `is not None` guard; (3) run `scripts/tests/test_forget_guard*` to verify regression clean; (4) receipt.
>
> Scope (allowlist): scripts/forget_guard.py, scripts/tests/test_forget_guard*.
> Scope guard: no git commit, no git push, no git add. Budget 8 tool_uses. 5-tuple receipt with tool_uses self-count + breakdown.

### 2a.3 INC-2026-04-23-ITEM-7 — hook tmp/bak cleanup + chmod verify (P1, eng-kernel Leo)
**M-tag**: M-1 workspace hygiene (session stability)
**Budget**: 5 tool_uses
**Agent target**: Ryan-Park (eng-platform) per prompt
**Spawn prompt**:
> P1 INC-2026-04-23-ITEM-7. Hook tmp/bak cleanup + hook_wrapper.py chmod +x verify.
>
> Actions: (1) `find scripts/ -name '*.tmp' -o -name '*.bak' -mtime +1 -delete`; (2) `ls -la scripts/hook_wrapper.py` verify +x; (3) if not +x then `chmod +x`; (4) write brief report to `reports/platform_hook_cleanup_20260423.md`.
>
> Scope (allowlist): scripts/ tmp+bak cleanup, scripts/hook_wrapper.py chmod, reports/platform_hook_cleanup_20260423.md.
> Scope guard: no git commit, no git push, no git add. Budget 5 tool_uses. 5-tuple receipt with tool_uses self-count + breakdown.

### 2a.4 INC-2026-04-23-ITEM-1 — commit Board sed fix line 80 False-and (P1, eng-platform Ryan)
**M-tag**: M-1 incident fix commit
**Budget**: 5 tool_uses
**Agent target**: Ryan-Park (eng-platform)
**Note**: this ONE item explicitly permits git commit per its prompt (single file, no push). Secretary flags: CEO should confirm before spawn.
**Spawn prompt** (only if CEO confirms commit authorization):
> P1 INC-2026-04-23-ITEM-1. Commit Board sed fix at `scripts/hook_wrapper.py` line 80 (`False and` gate) + inline comment referencing incident doc `reports/incidents/2026-04-23-hook-fail-closed-deadlock.md` + Iron Rule 0 doc.
>
> Actions: (1) verify sed fix present at line 80; (2) add inline comment; (3) single-line git commit msg to avoid hook regex false-positive.
>
> Scope (allowlist): scripts/hook_wrapper.py only.
> Scope guard: commit OK this item, no git push. Budget 5 tool_uses. 5-tuple receipt with tool_uses self-count + breakdown.

---

## Wave-2b — M-2 closure (spawn AFTER 2a.1 + 2a.2 land; serial preferred)

### 2b.1 CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST (P0, eng-governance Maya + multi-engineer)
**M-tag**: M-2 full registry unification (supersedes V1+V2)
**Budget**: 125 tool_uses total (Maya 55 / Leo 25 / Ryan 30 / Jordan 15)
**Agent target**: first spawn Maya-Patel (drives wave-by-wave), Maya then coordinates sub-spawns
**Spawn prompt**:
> P0 CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST (SUPERSEDES V1+V2). Read `reports/ceo/governance/CEO_RULES_REGISTRY_AUDIT.md` Section 10. Board catch: 4 gap we already built main in 2026-04 (AMENDMENT-015 Layer 3.1/3.4 detectors + Maya EXP-6 wisdom_extractor_v2 + auto_codify meta-rule + behavior_gov_engine 4 unified handlers + k9_silent_fire_audit + unified_compliance_audit). True delta 125 tu not 285.
>
> Wave split (Section 9.5 revised): Maya 55 (wire wisdom→yaml propose + 7-哲学/M-三角 binding to detectors); Leo 25 (omission_unification 对称 + Petri scenario daemon); Ryan 30 (6h cron commission+omission unification + yaml mutation harness); Jordan 15 (PostToolUse hook on memory/feedback Write + Layered Translation rubric reclassify).
>
> Priority: G2+G4 binding 同 wave 先, G1 omission_unification + G3 propose pipeline 第二 wave. Each new wire MUST: (1) symbolic enforce path; (2) livefire deliberate-violation CIEU 0→1; (3) cron entry.
>
> Scope (allowlist): reports/ceo/governance/CEO_RULES_REGISTRY_AUDIT.md (read), governance/forget_guard_rules.yaml, scripts/behavior_gov_rules.yaml, scripts/board_shell_omission_unification.py, scripts/launchd/*.plist, governance/proposed_rules/.
> Scope guard: no git commit, no git push, no git add. RT+1=0 only when `board_shell_full_registry_unification` + memory_to_yaml roundtrip + constitutional_judge bypass test ALL PASS.
> 5-tuple receipt with wave-by-wave artifacts + livefire commands + tool_uses self-count + breakdown.

### 2b.2 CZL-OMISSION-UNIFY-LIVEFIRE (P0, eng-governance Leo/Maya)
**M-tag**: M-2b symmetric validation of M-2a commission unification
**Budget**: implicit from prompt (~40 tool_uses)
**Agent target**: Leo-Chen (eng-kernel) or Maya-Patel
**Spawn prompt**:
> P0 CZL-OMISSION-UNIFY-LIVEFIRE. M-2b symmetric verification of M-2a commission unification (just PASS). Build `scripts/board_shell_omission_unification.py` mirroring `scripts/board_shell_commission_unification.py` 4-step pattern:
> (A) audit tracked-entity registry — schema unified, ≥50 entities tracked, idempotent re-run;
> (B) verify omission_rules.py covers ≥50 omission patterns (parallel to 52 commission rules);
> (C) confirm omission scheduler is event-driven (CIEU delta trigger) not pure cron polling — reframe any pure-polling rules;
> (D) LIVE-FIRE: create deliberately overdue tracked entity → omission_engine MUST emit P0 alarm + CIEU record within 60s.
> Script MUST print `=== OVERALL: PASS ===` on success.
>
> Scope (allowlist): scripts/board_shell_omission_unification.py (new file).
> Scope guard: no git commit, no git push, no git add. Budget ~40 tool_uses. 5-tuple receipt with tool_uses self-count + breakdown.

---

## Wave-2c — Honesty guardrails + schema (spawn parallel after 2b lands)

### 2c.1 CZL-BOARD-HONESTY-G1 (+ G2 integrated) (P0, eng-platform Ryan)
**M-tag**: M-2a Board-facing commission guardrail + M-2b audit log
**Budget**: implicit (~20 tool_uses; includes G2 as feature per dupe merge)
**Agent target**: Ryan-Park (eng-platform)
**Spawn prompt**:
> P0 CZL-BOARD-HONESTY-G1 + G2 (integrated). Implement Stop hook scanning CEO replies for claim keywords (closed / done / shipped / 完成 / 达成 / 压到 / 降到 / 处理 / 从X到Y) and checking same paragraph for artifact reference (commit hash / file path / pytest output / CIEU event id).
>
> G-1: if missing → emit `CEO_UNSUBSTANTIATED_CLAIM` CIEU + warn + write pending claims to `.g1_pending_claims.json`; UserPromptSubmit hook injects reminder on next turn.
> G-2 (integrated, not separate spawn): unconditionally emit `CEO_CLAIM_TO_BOARD` CIEU for every keyword-matched paragraph, payload `{claim_text, artifact_refs_found, g1_passed, timestamp, session_id}`.
>
> Reference: `reports/cto/ruling_board_facing_honesty_guardrails_2026_04_22.md` G-1 for 6 pytest names + G-2 for 5 pytest names (total 11 tests).
>
> Scope (allowlist): scripts/hook_stop_board_claim_verify.py, scripts/.g1_pending_claims.json, scripts/hook_user_prompt_g1_inject.py, .claude/settings.json, scripts/tests/ for new tests.
> Scope guard: no git commit, no git push, no git add. 5-tuple receipt with tool_uses self-count + breakdown.

### 2c.2 CZL-WAVE-5-RECEIPT-STRUCTURED-SCHEMA (P1, eng-kernel Leo)
**M-tag**: M-2a structured-receipt parser (unblocks Wave-5 closure loop)
**Budget**: 15 tool_uses
**Agent target**: Leo-Chen (eng-kernel)
**Note**: CEO originally flagged "延 Wave-2". Keep on list but only spawn after 2a + 2b + 2c.1 land OR CEO explicitly green-lights in parallel.
**Spawn prompt**:
> P1 CZL-WAVE-5-RECEIPT-STRUCTURED-SCHEMA. Wave-5 真治理闭环 — 老大 2026-04-22 catch language mismatch (engineer receipt 自然语言 vs 治理层机器语言, regex parse lossy). Solution: structured receipt YAML frontmatter schema + parser, NL → structured 翻译断点处加 structured 入口.
>
> Sub-tasks (~15 tool_uses):
> 1. Update `governance/sub_agent_boot_prompt_template.md` MANDATORY section: receipt 必含 YAML frontmatter (`---` block), fields: `receipt_schema_version: 1.0`, `tool_uses_claimed: int`, `tool_breakdown: {bash, read, edit, write, grep, glob, agent}`, `m_functor: str`, `rt_plus_1: int`, `artifacts: list[str]`, `eight_module_activation: dict`.
> 2. Upgrade `Y-star-gov/ystar/adapters/hooks/stop_hook.py` `auto_validate_subagent_receipt`: parse YAML frontmatter via `yaml.safe_load`; cross-check `tool_uses_claimed` vs `metadata.usage.tool_uses` (drift > 30% → emit `E1_RECEIPT_REJECTED` + system-reminder XML inject); missing frontmatter → `RECEIPT_MISSING_STRUCTURED_HEADER` warn (7d baseline); reuse `_format_correction_xml` mechanism.
> 3. Add `forget_guard_rules.yaml` rule `receipt_missing_structured_frontmatter` (warn after 7d → deny upgrade per Wave-N+1).
> 4. Test: `Y-star-gov/tests/adapters/hooks/test_structured_receipt_schema.py` — PASS case (frontmatter 真有 + drift < 10%) + FAIL case (frontmatter 缺 / drift > 30%).
> 5. Livefire: emit fake receipt with `tool_uses_claimed=5` vs declared metadata 50 → `E1_RECEIPT_REJECTED` CIEU 真 emit.
>
> Scope (allowlist): Y-star-gov/ystar/adapters/hooks/stop_hook.py, Y-star-gov/ystar/kernel/czl_protocol.py, governance/sub_agent_boot_prompt_template.md, governance/forget_guard_rules.yaml, Y-star-gov/tests/adapters/hooks/test_structured_receipt_schema.py (new).
> Scope guard: no git commit, no git push, no git add. Budget 15 tool_uses. 5-tuple receipt with MANDATORY tool_uses self-count + breakdown (你自己 first-victim 用 new YAML frontmatter format demo).

### 2c.3 INC-2026-04-23-ITEM-6 — K9 Rescue Daemon v1 ship (P0, eng-platform Ryan)
**M-tag**: M-1 survivability (physical-isolation rescue) + M-2a zero-gov-import hardcoded-whitelist
**Budget**: 40 tool_uses
**Agent target**: Ryan-Park (eng-platform)
**Note**: Large scope (40 tu), requires CTO pre-ruling on 5 design principles. Spawn AFTER 2a.1 (import audit) lands — otherwise same import failures haunt rescue daemon.
**Spawn prompt**:
> P0 INC-2026-04-23-ITEM-6. K9 Rescue Daemon v1 ship with 5 design principles: (1) physical-isolation from main governance stack; (2) launchd-managed; (3) zero-gov-import (`no import ystar.*`); (4) hardcoded whitelist R-001 through R-007; (5) FIFO-single-direction + Merkle-audit.
>
> Reference: `reports/inc-20260423-task-cards.md` Item 6 + `reports/ceo/iron_rule_incident_response_3channel_20260423.md`. Test: pytest unit + integration.
>
> Scope (allowlist): scripts/k9_rescue_daemon.py (new), scripts/k9_rescue_actions.py (new), scripts/com.ystar.k9rescue.plist (new), scripts/tests/test_k9_rescue* (new).
> Scope guard: no `import ystar.*`. no git commit, no git push, no git add. Budget 40 tool_uses. 5-tuple receipt with tool_uses self-count + breakdown.

---

## Spawn Ordering Summary

1. **Wave-2a (parallel OK)**: 2a.1 Leo import audit (P0) + 2a.2 Maya forget_guard 1-line (P0) + 2a.3 hook cleanup (P1) + 2a.4 Ryan commit (P1, needs CEO git-commit authorization)
2. **Wave-2b (serial, after 2a.1 + 2a.2)**: 2b.1 Maya V3 registry → 2b.2 omission livefire
3. **Wave-2c (parallel after 2b)**: 2c.1 Ryan honesty G1+G2 || 2c.2 Leo structured schema (optional) || 2c.3 Ryan K9 rescue daemon

---

## CEO Checklist (for next turn)

- [ ] Read this file top-to-bottom (already done by triage)
- [ ] Spawn 2a.1 + 2a.2 + 2a.3 in parallel (3 Agent tool calls same turn)
- [ ] Decide on 2a.4 git-commit authorization (single file, no push)
- [ ] Wait for 2a.1 + 2a.2 receipts, verify ls/pytest PASS empirically (not trust self-report)
- [ ] Spawn 2b.1 Maya
- [ ] After 2b.1 first-wave artifacts land, spawn 2b.2
- [ ] Spawn 2c.1 + 2c.3 in parallel (2c.2 optional, defer if CEO wants)
- [ ] All receipts empirically verified → dispatch_board.json white-board emptied of ghosts

---

## Forbidden patterns (reminder)

- DO NOT repost these items on dispatch_board.py (subscriber broken)
- DO NOT use negative constraints in spawn prompts ("NO touch foo.md") — RULE-CHARTER-001 regex trap; use positive allowlist
- DO NOT trust engineer self-report RT+1=0; CEO must `ls` / `wc` / `pytest` verify artifact exists
- DO NOT present choice questions to Board; CEO picks + executes
