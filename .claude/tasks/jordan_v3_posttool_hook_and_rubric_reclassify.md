---
title: "V3 Jordan: PostToolUse Hook for feedback->yaml + Layered Translation Rubric Reclassify"
engineer: eng-domains (Jordan Lee)
priority: P0
atomic_id: CZL-CEO-RULES-REGISTRY-V3-JORDAN
parent: CZL-CEO-RULES-REGISTRY-V3-EXISTING-ASSETS-FIRST
date: 2026-04-22
estimated_tu: 15
m_triangle: M-2a (commission auto-propose) + M-2b (rule classification rigor)
---

## BOOT 4-step (MANDATORY -- run before any business tool)

```bash
cat /Users/haotianliu/.openclaw/workspace/ystar-company/.czl_subgoals.json
cd /Users/haotianliu/.openclaw/workspace/ystar-company && git log -10 --oneline
python3 scripts/precheck_existing.py "CZL-CEO-RULES-REGISTRY-V3-JORDAN" 2>&1 | tail -10
sqlite3 .ystar_cieu.db "SELECT count(*) FROM cieu_events WHERE created_at >= strftime('%s','now','-1 hour')"
```

## Context (self-contained -- no session history required)

CEO spec: `reports/ceo/governance/CEO_RULES_REGISTRY_AUDIT.md` Section 10.3 (G3, last-mile automation) + Section 9.1 (Layered Translation Method rubric).

Board 2026-04-22 directive: close 4 governance gaps. This card covers two pieces:

1. **G3 last-mile wire**: PostToolUse hook that fires whenever `memory/feedback_*.md` is written, triggering Maya's `wisdom_to_yaml_proposer.py` to auto-generate a candidate yaml entry in `governance/proposed_rules/`. This closes the loop: new Board feedback -> automatic yaml proposal -> CTO review.

2. **Section 3c SOFT reclassification**: Apply the Layered Translation Method 6-criteria rubric (timing / observability / determinacy / judgment-load / reversibility / evidence-clarity) from arxiv 2604.05229 to the 12 SOFT rules in Section 3c, and produce a scored classification deciding which are truly SOFT (advisory-only) vs which should be reclassified to COMMISSION or OMISSION.

### Existing Assets (DO NOT rebuild)

1. **`scripts/wisdom_to_yaml_proposer.py`**: Maya is building this (her V3 task). Your hook calls it IF it exists, produces a helpful skip message if not yet available.
2. **`scripts/hook_stop_reply_scan.py`** (14KB): Example PostToolUse hook -- use as structural template (hook function signature, CIEU emit pattern, error handling).
3. **`scripts/hook_subagent_output_scan.py`**: Another PostToolUse hook example.
4. **`scripts/hook_ceo_pre_output.py`**: PreToolUse hook example.
5. **`governance/forget_guard_rules.yaml`**: Target registry for reclassified rules.
6. **CEO spec Section 3c**: The 12 SOFT rules to reclassify (listed below for reference).

### Section 3c SOFT Rules (from CEO spec -- your reclassification input)

| # | memory rule | CEO initial classification |
|---|---|---|
| 1 | feedback_cmo_12layer_rt_loop | CMO-specific process |
| 2 | feedback_cto_subagent_cannot_async_orchestrate | architectural lesson |
| 3 | feedback_daemon_cache_workaround | workaround note |
| 4 | feedback_self_heal_via_daemon_window | recovery pattern |
| 5 | feedback_team_enforce_asymmetry | diagnostic knowledge |
| 6 | feedback_testing_is_ceo_scope | scope clarification |
| 7 | feedback_scenario_c_is_real_usp | sales positioning |
| 8 | feedback_cto_owns_technical_modeling | role clarification |
| 9 | feedback_boot_no_pipe | operator discipline (Board, not agent) |
| 10 | feedback_close_stub_trigger | moved to 3a (commission) |
| 11 | feedback_rt1_0_lesson_production_mode_writes_to_real_m | merged with 3b item |
| 12 | feedback_rt1_0_lesson_default_is_production | operating mode awareness |

Note: Items 10 and 11 were already reclassified by CEO. Your rubric applies to the remaining 10 (items 1-9, 12).

## Task 1: PostToolUse Hook on Write memory/feedback_*.md (~10 tu)

### Goal

When any agent Writes a file matching `memory/feedback_*.md`, automatically trigger the wisdom-to-yaml pipeline so that new Board feedback immediately produces a candidate governance rule.

### Deliverable: `scripts/hook_posttool_feedback_to_yaml.py`

**Hook function signature** (must match Claude Code PostToolUse protocol):

```python
def hook_posttool_feedback_to_yaml(tool_name: str, tool_input: dict, tool_result: dict) -> dict:
    """
    PostToolUse hook: fires after Write tool completes.
    If file_path matches memory/feedback_*.md, triggers yaml proposal generation.
    """
```

**Logic**:

1. Check: `tool_name == "Write"` and `tool_input.get("file_path", "")` matches `memory/feedback_*.md` pattern
2. If match: check if `scripts/wisdom_to_yaml_proposer.py` exists
   - If exists: subprocess call `python3 scripts/wisdom_to_yaml_proposer.py --input {file_path}`
   - If not exists: log `[SKIP] wisdom_to_yaml_proposer.py not yet available (Maya V3 pending)` and return clean
3. Emit CIEU event `FEEDBACK_TO_YAML_HOOK_FIRED` with payload: `{file_path, proposer_available, result}`
4. Return `{"status": "ok"}` -- this hook is advisory (never blocks Write)

**Error handling**:
- If proposer subprocess fails, catch and log, do NOT crash the hook
- If CIEU emit fails, log and continue (hook must be resilient)

**Registration**: The hook must be importable. Write a brief comment at top explaining how to register in hooks.json (but do NOT modify hooks.json yourself -- CTO does that).

### Steps

1. Read `scripts/hook_stop_reply_scan.py` -- understand the hook function signature pattern
2. Read `scripts/hook_subagent_output_scan.py` -- understand CIEU emit pattern from hooks
3. Write `scripts/hook_posttool_feedback_to_yaml.py` with the logic above
4. Write `tests/hooks/test_posttool_feedback_to_yaml.py`:
   - Test 1: tool_name="Write", file_path="memory/feedback_test_new.md" -> hook fires, CIEU event emitted
   - Test 2: tool_name="Write", file_path="src/some_code.py" -> hook does NOT fire (path filter works)
   - Test 3: tool_name="Read" -> hook does NOT fire (tool filter works)
   - Test 4: proposer not available -> hook logs skip, returns ok (no crash)

### Acceptance Criteria

- [ ] `scripts/hook_posttool_feedback_to_yaml.py` exists
- [ ] Hook function signature matches PostToolUse protocol
- [ ] Path filter correctly matches `memory/feedback_*.md` only
- [ ] Gracefully handles missing proposer (Maya dependency)
- [ ] `python3 -m pytest tests/hooks/test_posttool_feedback_to_yaml.py -v` all pass
- [ ] CIEU event `FEEDBACK_TO_YAML_HOOK_FIRED` emitted on match

## Task 2: Layered Translation 6-Criteria Rubric Reclassify (~5 tu)

### Goal

Apply the 6-criteria rubric from arxiv 2604.05229 (Layered Translation Method, Table I) to the 10 remaining SOFT rules and produce a scored classification.

### The 6 Criteria (from paper)

| Criterion | What It Measures | Score Range |
|---|---|---|
| **Timing** | Can the rule be checked BEFORE action (pretool) or only AFTER (posttool/audit)? | pretool=3, posttool=2, audit-only=1 |
| **Observability** | Can violation be detected from tool_calls + reply text alone? | fully=3, partial=2, requires-judgment=1 |
| **Determinacy** | Is violation detection deterministic (regex/logic) or requires LLM judgment? | deterministic=3, heuristic=2, llm-judge=1 |
| **Judgment-load** | How much context does the detector need? | single-reply=3, multi-turn=2, full-session=1 |
| **Reversibility** | If rule fires incorrectly, is the damage reversible? | info-only=3, warn-reversible=2, deny-irreversible=1 |
| **Evidence-clarity** | How clear is the violation evidence to a human reviewer? | self-evident=3, needs-explanation=2, ambiguous=1 |

**Scoring**:
- Total 13-18: COMMISSION candidate (hard enforce, runtime deny)
- Total 9-12: OMISSION candidate (deadline/required-action, warn+escalate)
- Total 6-8: ADVISORY (info-only, weekly review)

### Deliverable: `reports/governance/soft_rule_rubric_reclassification.md`

Write a markdown table with:

```markdown
| Rule | Timing | Obs | Det | Judg | Rev | Evid | Total | Reclassification |
|---|---|---|---|---|---|---|---|---|
| feedback_cmo_12layer_rt_loop | 1 | 1 | 1 | 1 | 3 | 1 | 8 | ADVISORY |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
```

### Steps

1. Read each of the 10 feedback files from `memory/feedback_*.md` (items 1-9, 12 from the table above)
2. For each, score all 6 criteria with a 1-sentence justification per score
3. Sum scores and assign reclassification bucket
4. If any rule scores 13+, note it as "UPGRADE CANDIDATE: should be COMMISSION, not SOFT" in the output
5. If any rule scores 9-12, note it as "UPGRADE CANDIDATE: should be OMISSION, not SOFT"

### Acceptance Criteria

- [ ] `reports/governance/soft_rule_rubric_reclassification.md` exists
- [ ] All 10 remaining SOFT rules scored across all 6 criteria
- [ ] Each score has a 1-sentence justification
- [ ] Reclassification bucket assigned per scoring threshold
- [ ] Any upgrade candidates explicitly flagged

## Livefire Verification (MANDATORY)

### Livefire -- PostToolUse Hook
```bash
# Create a test feedback file to trigger the hook
python3 -c "
from scripts.hook_posttool_feedback_to_yaml import hook_posttool_feedback_to_yaml
result = hook_posttool_feedback_to_yaml(
    'Write',
    {'file_path': '/Users/haotianliu/.openclaw/workspace/ystar-company/memory/feedback_test_xxx.md'},
    {'status': 'ok'}
)
print('Hook result:', result)
"
# Verify CIEU event
sqlite3 .ystar_cieu.db "SELECT count(*) FROM cieu_events WHERE event_type='FEEDBACK_TO_YAML_HOOK_FIRED' AND created_at >= strftime('%s','now','-300')"
# Expect: >= 1
```

### Livefire -- Rubric Output
```bash
# Verify rubric file exists and has content
wc -l reports/governance/soft_rule_rubric_reclassification.md
# Expect: >= 15 lines (header + 10 rules + justifications)
grep -c "UPGRADE CANDIDATE" reports/governance/soft_rule_rubric_reclassification.md
# Shows how many rules are recommended for upgrade (0 is valid if none qualify)
```

## 5-Tuple Receipt Template (fill and return to CEO)

```
- Y*: PostToolUse hook LIVE + rubric reclassification complete
- Xt: [describe starting state]
- U: [list exact tool_uses honestly]
- Yt+1: [end state + file paths]
- Rt+1: [honest gap -- 0 if truly done]
```

## Hard Constraints

- **NO git commit / push / add / reset** -- only Write/Edit, CEO handles git
- **NO choice questions** -- decide and execute, report "I chose X because Y"
- **NO defer language** -- no "later/next session/will do"
- **NO self-claims without tool evidence** -- narrative_coherence_detector is LIVE
- **Files in scope**: `scripts/hook_posttool_feedback_to_yaml.py` (new), `tests/hooks/test_posttool_feedback_to_yaml.py` (new), `reports/governance/soft_rule_rubric_reclassification.md` (new)
- **Files NOT in scope**: anything else. Do NOT modify hooks.json, forget_guard_rules.yaml, or any existing hook scripts.
