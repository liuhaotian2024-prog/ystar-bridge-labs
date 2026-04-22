# CTO Ruling: Board-Facing Honesty Guardrails Engineering Spec

Audience: Ryan-Platform (implementer), CEO Aiden (accountability), Board (Haotian Liu)
Research basis: `reports/ceo/principle_board_facing_honesty_constitutional_2026_04_22.md` (CEO constitutional-level principle, Board 2026-04-22)
Synthesis: 4 guardrails transformed into pytest-verifiable engineering specs with detection patterns, hook integration points, and acceptance criteria
Purpose: Provide Ryan-Platform with unambiguous implementation specs for G-1 through G-4

---

## CZL-159 Header

- **Y***: 4 guardrails LIVE as hook enforcement, preventing CEO unsubstantiated claims to Board
- **Xt**: Principle document drafted by CEO, 0 guardrails implemented, 0 hooks active
- **U**: [spec 4 guardrails] -> [post 4 dispatch cards] -> [register 4 omission obligations]
- **Yt+1**: Ryan has 4 concrete specs, 4 P0 dispatch cards, 4 tracked obligations with 7-day deadlines
- **Rt+1**: 0 when all 4 specs are pytest-green and hooks are active in `.claude/settings.json`

---

## Formal Definitions

Let C be the set of all CEO reply tokens to Board. Let K be the keyword set:
```
K = {closed, done, shipped, ship了, 完成, 达成, 压到, 降到, 处理, "从.*到.*"}
```
Let A(c) be the artifact-reference predicate: true iff the same paragraph as claim c contains at least one of:
- git commit hash (regex `[0-9a-f]{7,40}`)
- file path + line (regex `[\w/.-]+:\d+` or absolute path)
- pytest output (regex `passed|failed|error`)
- grep count (regex `\d+ match`)
- CIEU event id (regex `CIEU[_-]\w+`)
- dispatch_board state ref (regex `CZL-\w+`)

G-1 requires: forall c in C, if c contains any k in K, then A(c) must hold.

## Mathematical Model

False-positive cost F_p (legitimate claim blocked) vs false-negative cost F_n (unsubstantiated claim passes). Board directive is clear: F_n >> F_p. Therefore detection threshold is set LOW (any keyword match triggers check) with non-blocking warn (not deny) to balance.

---

## G-1: Board-Facing Claim x Artifact Reference

### Input Spec
- **Hook type**: Stop (post-reply scan)
- **Hook file**: `scripts/hook_stop_board_claim_verify.py`
- **Trigger condition**: Active agent is `ceo` AND reply text contains any keyword from set K
- **Keyword detection regex**:
  ```python
  CLAIM_KEYWORDS_RE = re.compile(
      r'\b(closed|done|shipped|ship了|完成|达成|压到|降到|处理)\b'
      r'|从\s*\d+\s*(到|变|降)\s*\d+',
      re.IGNORECASE
  )
  ```

### Detection Pattern
For each paragraph (split by `\n\n`) containing a keyword match, check for artifact reference:
```python
ARTIFACT_REF_RE = re.compile(
    r'[0-9a-f]{7,40}'          # git commit hash
    r'|[\w/.:-]+\.(?:py|md|json|yaml|sh)(?::\d+)?'  # file path
    r'|\d+\s+passed'           # pytest result
    r'|\d+\s+match'            # grep count
    r'|CIEU[_-]\w+'            # CIEU event
    r'|CZL-\w+'                # dispatch board ref
    r'|dispatch_board\.json'   # explicit board ref
)
```

### Action
1. If paragraph has keyword but no artifact ref:
   - Emit CIEU event `CEO_UNSUBSTANTIATED_CLAIM` with `{"claim_text": <paragraph>, "keyword_matched": <keyword>}`
   - Return `{"decision": "warn", "reason": "G-1: claim without artifact reference"}`
   - Write to `scripts/.g1_pending_claims.json`: list of unsubstantiated claims from this reply
2. On next `UserPromptSubmit` hook, if `.g1_pending_claims.json` is non-empty:
   - Inject into system prompt: `"[G-1] 上轮 {N} 条无实证声明必补证据: {claim_list}"`
   - Clear `.g1_pending_claims.json` after injection

### Test Scenario
```python
# Scenario 1: Claim with artifact -> PASS (no warn)
reply = "处理了 5 条 (commit abc1234)"
# Scenario 2: Claim without artifact -> WARN + CIEU event
reply = "从 93 压到 5 了"
# Scenario 3: No claim keyword -> PASS (no check)
reply = "architecture looks good"
# Scenario 4: Multiple paragraphs, mixed -> warn only on violating paragraphs
reply = "处理了 5 条 (commit abc1234)\n\n完成了搬家"
# Scenario 5: Chinese numerals in "从X到Y" pattern
reply = "从93变5了，全部搞定"
```

### Acceptance Pytest
```
test name: test_g1_claim_with_artifact_passes
test name: test_g1_claim_without_artifact_warns
test name: test_g1_no_claim_keyword_passes
test name: test_g1_mixed_paragraphs_partial_warn
test name: test_g1_cieu_event_emitted_on_violation
test name: test_g1_next_prompt_inject_pending_claims
```

### Files in Scope
- `scripts/hook_stop_board_claim_verify.py` (NEW)
- `scripts/.g1_pending_claims.json` (runtime state, NEW)
- `scripts/hook_user_prompt_g1_inject.py` (NEW, UserPromptSubmit hook)
- `.claude/settings.json` (register hooks)

---

## G-2: CIEU Audit Log for CEO -> Board Claims

### Input Spec
- **Hook type**: Stop (same hook as G-1, additional emit path)
- **Hook file**: `scripts/hook_stop_board_claim_verify.py` (shared with G-1)
- **Trigger condition**: Same keyword detection as G-1
- **Action is unconditional**: every claim gets logged regardless of whether artifact ref exists

### Detection Pattern
Same `CLAIM_KEYWORDS_RE` as G-1. This guardrail does not block -- it records.

### Action
1. For every paragraph containing a keyword match, emit CIEU event:
   ```
   event_type: CEO_CLAIM_TO_BOARD
   payload: {
     "claim_text": <paragraph text, max 500 chars>,
     "artifact_refs_found": [<list of matched refs>],
     "g1_passed": true/false,
     "timestamp": <ISO8601>,
     "session_id": <from .ystar_session.json>
   }
   ```
2. Events accumulate in `.ystar_cieu.db` (main CIEU store)
3. Samantha weekly scan (separate scope, not Ryan's deliverable) queries:
   ```sql
   SELECT * FROM cieu_events
   WHERE event_type = 'CEO_CLAIM_TO_BOARD'
   AND timestamp > strftime('%s','now','-7 days')
   ORDER BY timestamp DESC
   ```

### Test Scenario
```python
# Scenario 1: Claim with artifact -> CIEU event emitted with g1_passed=true
# Scenario 2: Claim without artifact -> CIEU event emitted with g1_passed=false
# Scenario 3: 3 claims in one reply -> 3 separate CIEU events
# Scenario 4: No claim keywords -> 0 CIEU events of this type
```

### Acceptance Pytest
```
test name: test_g2_cieu_event_emitted_for_substantiated_claim
test name: test_g2_cieu_event_emitted_for_unsubstantiated_claim
test name: test_g2_multiple_claims_multiple_events
test name: test_g2_no_claim_no_event
test name: test_g2_event_payload_structure_valid
```

### Files in Scope
- `scripts/hook_stop_board_claim_verify.py` (shared with G-1)
- `.ystar_cieu.db` (existing, write path)

---

## G-3: Board Directive -> CEO Tracked Entity Auto-Registration

### Input Spec
- **Hook type**: UserPromptSubmit (fires on every Board message before CEO processes it)
- **Hook file**: `scripts/hook_user_prompt_board_directive_register.py` (NEW)
- **Trigger condition**: Message originates from Board (detected by: active agent is `ceo` AND prompt is from human user)
- **Directive detection regex**:
  ```python
  # Imperative sentence + action noun heuristic
  DIRECTIVE_RE = re.compile(
      r'(?:^|\n)\s*'
      r'(?:'
      r'(?:把|让|给我|必须|确保|修|做|搬|装|跑|写|删|停|升级|检查|完成|搞定|拿|弄)'  # Chinese imperatives
      r'|(?:fix|do|make|ensure|run|write|install|check|complete|stop|upgrade|move)'  # English imperatives
      r')'
      r'.{5,200}',  # followed by substantive content (5-200 chars)
      re.IGNORECASE | re.MULTILINE
  )
  ```

### Detection Pattern
1. Split Board prompt into sentences (by newline or Chinese period)
2. For each sentence matching `DIRECTIVE_RE`:
   - Extract directive text (first 200 chars)
   - Generate entity_id: `board_directive_{timestamp_hex}`
3. Skip if sentence is clearly a question (ends with `?` or `？`) or is a comment (starts with `#`)

### Action
1. For each detected directive, call `register_obligation_programmatic()`:
   ```python
   register_obligation_programmatic(
       db_path=str(OMISSION_DB),
       entity_id=f"board_directive_{ts_hex}",
       owner="ceo",
       rule_id="board_directive_auto",
       rule_name="Board directive auto-tracked",
       description=f"Board directive: {directive_text[:200]}",
       due_secs=86400,  # 24h hard deadline
       severity="high",
       obligation_type="required_acknowledgement_omission",
       required_event="ceo_directive_close",
       initiator="board",
       directive_ref=f"board_directive_{ts_hex}",
   )
   ```
2. CEO closes by emitting one of:
   - `ceo_directive_close` with `acknowledgement` / `decline` / `blocker_report` payload
3. If 24h passes without close event, existing `hook_omission_enforce_pretool.py` will deny CEO tool calls

### Test Scenario
```python
# Scenario 1: "修所有问题" -> 1 obligation registered, owner=ceo, deadline=24h
# Scenario 2: "搬家进行到底" -> 1 obligation registered
# Scenario 3: "你觉得怎么样？" -> 0 obligations (question, not directive)
# Scenario 4: 5 directives in one prompt -> 5 separate obligations
# Scenario 5: Obligation not closed in 24h -> hook_omission_enforce denies next tool call
```

### Acceptance Pytest
```
test name: test_g3_imperative_detected_as_directive
test name: test_g3_question_not_detected_as_directive
test name: test_g3_obligation_registered_in_omission_db
test name: test_g3_obligation_has_24h_deadline
test name: test_g3_multiple_directives_multiple_obligations
test name: test_g3_close_event_resolves_obligation
```

### Files in Scope
- `scripts/hook_user_prompt_board_directive_register.py` (NEW)
- `.ystar_cieu_omission.db` (existing, write path)
- `.claude/settings.json` (register hook)

---

## G-4: Reply Pre-Write Verification Inject

### Input Spec
- **Hook type**: PreToolUse (fires before Write tool)
- **Hook file**: `scripts/hook_pretool_board_report_verify.py` (NEW)
- **Trigger condition**: Tool is `Write` AND `file_path` matches:
  ```python
  BOARD_REPORT_PATH_RE = re.compile(
      r'reports/ceo/.*(?:board|morning|status|weekly|brief)',
      re.IGNORECASE
  )
  ```

### Detection Pattern
Pure path-based pattern match. No content scanning. Non-blocking.

### Action
1. If path matches, return:
   ```json
   {
     "decision": "warn",
     "reason": "[G-4] This file path suggests a Board-facing report. Before writing claims, run verification queries to generate artifact references. Suggested: `git log --oneline -5`, `python3 scripts/dispatch_board.py status`, `python3 scripts/omission_status.py`."
   }
   ```
2. Emit CIEU event `CEO_BOARD_REPORT_VERIFY_NUDGE` with `{"file_path": <path>}`
3. No blocking. Claude Code surfaces the warn as a cognitive pause.

### Test Scenario
```python
# Scenario 1: Write to "reports/ceo/morning_board_brief.md" -> warn injected
# Scenario 2: Write to "reports/ceo/status_20260422.md" -> warn injected
# Scenario 3: Write to "reports/cto/ruling_xyz.md" -> no warn (not ceo board path)
# Scenario 4: Write to "reports/ceo/internal_notes.md" -> no warn (no board/morning/status keyword)
# Scenario 5: Tool is Read (not Write) -> no trigger
```

### Acceptance Pytest
```
test name: test_g4_board_report_path_triggers_warn
test name: test_g4_status_report_path_triggers_warn
test name: test_g4_non_ceo_path_no_warn
test name: test_g4_non_board_keyword_path_no_warn
test name: test_g4_non_write_tool_no_trigger
test name: test_g4_cieu_event_emitted
```

### Files in Scope
- `scripts/hook_pretool_board_report_verify.py` (NEW)
- `.claude/settings.json` (register hook)

---

## Implementation Sequence (Ryan's discretion, recommendation only)

1. G-1 + G-2 together (shared hook file, biggest impact)
2. G-4 (simplest, pure path match)
3. G-3 (most complex, requires omission engine integration)

## Cross-Cutting Concerns

- All 4 hooks must handle `ImportError` for CIEU helpers gracefully (log + continue, never crash)
- All hooks must check active agent == `ceo` before firing (skip for CTO/engineer sessions)
- Settings.json registration: each hook needs an entry in `hooks[]` array with correct `event` type
- Test fixtures: use `tmp_path` for DB isolation, `monkeypatch` for active agent identity

## Ruling Decision Log

| Decision Point | Resolution | Rationale |
|---|---|---|
| G-1 block vs warn | warn (not deny) | Principle doc says "warn + CIEU event", not block. Blocking CEO reply would break session flow. |
| G-1 paragraph vs sentence granularity | paragraph (`\n\n` split) | Artifact ref may be in same paragraph but different sentence; paragraph is natural grouping. |
| G-3 directive detection false positive rate | Accept 20% FP | Better to over-register (CEO can close quickly) than miss a directive. Board explicitly wants tracking. |
| G-3 deadline | 24h fixed | Principle doc specifies 24h. No variable deadline needed. |
| G-4 blocking behavior | Non-blocking warn | Principle doc explicitly says "非阻断但加 cognitive pause". |
| Shared vs separate hook files for G-1/G-2 | Shared | Same trigger, same regex, same iteration. Separate files = duplicate code. |
