# CZL Unified Communication Protocol v1.0

**Constitutional, Board 2026-04-16, fixes Ethan#CZL-1 hallucination root cause**

## Purpose

This protocol defines the **envelope, validator gates, and migration path** for CIEU 5-tuple sub-agent dispatch and receipt under the **CZL framework** (CEO-Zone-Layer). It extends `ystar.kernel.rt_measurement.py` RT_MEASUREMENT v1.0 schema from machine-logged CIEU events to **human-readable structured prompts and receipts** between CEO/CTO and sub-agents.

**Why this exists:**
- Ethan#CZL-1 returned a 14-second zero-tool hallucination claiming `Rt+1=0` and shipped spec. **Gate 2 did not exist** to empirically validate.
- Prior TaskList items (e.g., W5.1, W22.1, W29.3) lack 5-tuple structure → sub-agents can't bootstrap from them.
- This protocol is the **compiler** from legacy task text → executable sub-agent dispatch.

---

## 1. CZLMessageEnvelope Schema

All CEO/CTO ↔ sub-agent communication uses this envelope (extends RT_MEASUREMENT v1.0):

```python
from typing import Literal, TypedDict
from datetime import datetime

class CZLMessageEnvelope(TypedDict):
    # --- Core RT_MEASUREMENT v1.0 fields ---
    schema_version: str  # "1.0"
    task_id: str         # Unique ID (e.g., "ceo_task_42", "W5.1_eng-kernel")
    y_star: str          # Ideal contract (verifiable predicate)
    x_t: str             # Pre-state (measured via tool_use, NOT impression)
    u: list[str]         # Actions to execute (numbered, concrete tool calls)
    y_t_plus_1: str      # Post-state (predicted, verifiable by CEO/CTO)
    rt_value: float      # Target (dispatch) or actual (receipt); 0.0 = closure
    
    # --- CZL Communication Extensions ---
    message_type: Literal["dispatch", "receipt"]
    sender: str          # "ceo", "cto", "eng-kernel", etc. (canonical agent ID)
    recipient: str       # Same format as sender
    dispatch_timestamp: str  # ISO8601 UTC when dispatch was sent
    parent_task_id: str | None  # If this is a sub-task, link to parent
    
    # --- Three-Dimensional Role Tags (K9 3D Audit) ---
    role_tags: dict[str, str]  # {"producer": "ceo", "executor": "eng-kernel", "governed": "eng-kernel"}
```

**Embedding in prompts:**
- CEO/CTO dispatch prompts MUST contain a `=== CIEU 5-tuple dispatch ===` section with all fields except `message_type: "receipt"`.
- Sub-agent receipts MUST mirror the same fields, replacing predictions with actuals, and set `message_type: "receipt"`.

**Auto-fill fallback:**
- If a CEO prompt lacks explicit 5-tuple structure, the **auto-fill parser** (§5) extracts best-effort fields and flags low-confidence sections.

---

## 2. Gate 1 — Dispatch Pre-Validator

**Purpose:** CEO/CTO validation BEFORE sub-agent spawn. Blocks launch if critical fields are missing.

### Specification

```python
def validate_dispatch(prompt: str) -> list[str]:
    """
    Validate CEO/CTO dispatch prompt against CZL envelope requirements.
    
    Args:
        prompt: Full sub-agent dispatch prompt text
    
    Returns:
        List of missing sections (empty = valid, can launch)
    
    Rejection conditions:
        - Missing Y* (ideal contract)
        - Missing Xt (pre-state) OR Xt contains "印象" / "should be" (not measured)
        - Missing U (actions list)
        - U contains ">15 tool_uses estimate" (violates atomic dispatch)
        - Missing Yt+1 (post-state verifiability clause)
        - Missing rt_value target (must be "Rt+1 target = 0.0" or explicit gap threshold)
        - Missing recipient field (which engineer/agent?)
        - Missing task_id
    """
```

**Implementation notes:**
- Pattern match for `=== CIEU 5-tuple dispatch ===` header or extract sections via regex.
- Xt validation: reject if contains "应该" / "印象" / "大概" / "估计" (Chinese speculation markers) or "should", "probably", "likely" (English equivalents) → force actual tool_use measurement.
- U validation: reject if summed tool_use estimate >15 (atomic dispatch violation per `sub_agent_atomic_dispatch.md`).

**Integration point:**
- CEO/CTO must call this validator **before** `Agent` tool spawn.
- If `validate_dispatch()` returns non-empty list, CEO/CTO must fix prompt and re-validate.

---

## 3. Gate 2 — Receipt Post-Validator (EMPIRICAL VERIFICATION)

**Purpose:** CEO/CTO validation AFTER sub-agent return. **Rejects hallucinated success claims** by verifying artifacts on disk, not just parsing receipt text.

### Specification

```python
from pathlib import Path

def validate_receipt(
    receipt: str,
    artifacts_expected: list[Path],
    tests_expected: dict[str, int] | None = None,
) -> tuple[bool, float]:
    """
    Empirically validate sub-agent receipt against declared Yt+1.
    
    Args:
        receipt: Sub-agent's CIEU 5-tuple receipt text
        artifacts_expected: Paths to files/dirs that MUST exist if Rt+1=0
        tests_expected: Optional test pass counts {"pytest": 6, "mypy": 0}
    
    Returns:
        (is_valid, actual_rt_plus_1) where:
            is_valid = all artifacts exist AND tests pass AND receipt rt_value ≤ gap
            actual_rt_plus_1 = empirical gap (0.0 = closure, >0 = incomplete)
    
    Validation steps:
        1. Parse receipt for claimed rt_value
        2. Check EVERY path in artifacts_expected with Path.exists()
        3. If tests_expected given, extract test output from receipt and verify counts
        4. Check receipt contains bash verification output (wc -l, ls -la, pytest -q, etc.)
        5. Compute actual_rt_plus_1:
            - +1.0 for each missing artifact
            - +1.0 if test output not found in receipt
            - +0.5 if claimed rt_value differs from empirical gap
        6. is_valid = (actual_rt_plus_1 == 0.0)
    """
```

**Rejection patterns (actual_rt_plus_1 > 0):**
- File claimed written but `ls -la <path>` not in receipt → +1.0 gap
- Tests claimed pass but no `pytest -q` output in receipt → +1.0 gap
- Receipt says `Rt+1=0` but artifact missing → hallucination, +1.0 gap
- Receipt contains "我已完成" / "done" but tool_uses metadata shows 0 tool calls → instant reject, +5.0 gap

**Integration point:**
- CEO/CTO must call this validator **immediately after** sub-agent returns.
- If `is_valid == False`, CEO re-dispatches with corrected prompt OR escalates to Board.

**Critical design note:**
This validator is why Ethan#CZL-1's hallucination would have been caught. It would have failed on:
- `artifacts_expected = [Path("governance/czl_unified_communication_protocol_v1.md")]`
- `Path.exists()` → False
- `actual_rt_plus_1 = 1.0`
- CEO would have re-dispatched instead of reporting false success.

---

## 4. Empirical Verification Requirement (Non-Negotiable)

**Constitutional Constraint:**
NO receipt is considered valid unless it contains **pasted bash output** proving artifacts exist.

Required bash commands in EVERY receipt (sub-agent must run and paste output):
```bash
# For file writes:
ls -la <path_to_file>
wc -l <path_to_file>

# For code changes:
git diff --stat
git log -1 --oneline

# For tests:
pytest -q <test_file>  # Paste full output, not summary
```

**Why this is non-negotiable:**
- LLM agents can hallucinate completion without executing tools (Ethan#CZL-1 proof).
- Bash output is cryptographically hard to fake (requires actual tool execution).
- CEO/CTO Gate 2 validator greps for these outputs; absence → auto-reject.

---

## 5. Auto-Fill Parser Specification

**Purpose:** Extract 5-tuple fields from legacy TaskList items or free-text CEO prompts that lack explicit structure.

### Specification

```python
def parse_legacy_task_to_envelope(
    task_text: str,
    task_id: str,
    recipient: str,
) -> tuple[CZLMessageEnvelope, list[str]]:
    """
    Best-effort parser for legacy tasks → CZL envelope.
    
    Args:
        task_text: Raw task description (e.g., from .claude/tasks/ or TaskList)
        task_id: Assigned ID (e.g., "W5.1")
        recipient: Target agent ("eng-kernel", "eng-governance", etc.)
    
    Returns:
        (envelope, low_confidence_fields) where:
            envelope = CZLMessageEnvelope with auto-filled fields
            low_confidence_fields = list of field names that need human review
    
    Parsing strategy:
        Y*: Extract from "Acceptance Criteria" / "Success Condition" section
            If missing → use task title + " completed with tests passing"
        Xt: Extract from "Context" / "Current State" section
            If missing → flag as low-confidence, fill with "Not measured (legacy task)"
        U: Extract numbered list from task body
            If missing → infer from Files in Scope + task type (write/test/refactor)
        Yt+1: Mirror Y* with "verified by" clause
        rt_value: Default to 0.0 target
        role_tags: Auto-fill {"producer": "ceo", "executor": recipient, "governed": recipient}
    
    Low-confidence triggers:
        - No "Acceptance Criteria" section → flag Y*
        - No "Context" section → flag Xt
        - No numbered action list → flag U
        - Task description <50 chars → flag entire envelope
    """
```

**Integration point:**
- CEO runs this parser on legacy TaskList items (§7 migration table) before dispatching.
- Output includes `low_confidence_fields` → CEO reviews and manually corrects before Gate 1.

---

## 6. Inline Task Cards (Appendices)

### Appendix A — Leo Chen (eng-kernel) Task Card

**Task ID:** `W22.2_eng-kernel_czl_parser_lib`  
**Priority:** P1  
**Depends on:** This spec landed

**CIEU 5-tuple:**

**Y\*:** Python module `ystar/kernel/czl_parser.py` exists with 3 functions:
1. `validate_dispatch(prompt: str) -> list[str]` — returns empty list for valid dispatch
2. `validate_receipt(receipt: str, artifacts: list[Path], tests: dict | None) -> tuple[bool, float]` — returns `(True, 0.0)` for valid closure
3. `parse_legacy_task(task_text: str, task_id: str, recipient: str) -> tuple[CZLMessageEnvelope, list[str]]`

Test coverage ≥80%. Passes `pytest ystar/tests/kernel/test_czl_parser.py -q` with 6/6 tests green.

**Xt:** No `czl_parser.py` exists. `rt_measurement.py` (117 lines) provides RT_MEASUREMENT schema but no validation logic.

**U:**
1. Read this spec (`governance/czl_unified_communication_protocol_v1.md`)
2. Read `ystar/kernel/rt_measurement.py` for schema reference
3. Write `ystar/kernel/czl_parser.py` with 3 functions (§2, §3, §5 pseudocode)
4. Write `ystar/tests/kernel/test_czl_parser.py` with:
   - `test_validate_dispatch_missing_fields()` — rejects incomplete prompts
   - `test_validate_dispatch_xt_speculation()` — rejects "印象" in Xt
   - `test_validate_receipt_missing_artifact()` — catches hallucination
   - `test_validate_receipt_no_bash_output()` — rejects missing verification
   - `test_parse_legacy_task_full()` — extracts all fields from well-formed legacy task
   - `test_parse_legacy_task_minimal()` — flags low-confidence on sparse input
5. Run `pytest ystar/tests/kernel/test_czl_parser.py -q`, paste output
6. Run `wc -l ystar/kernel/czl_parser.py`, paste output
7. Commit: `git commit -m "feat(kernel): CZL parser lib — Gate 1/2 validators + legacy parser [W22.2]"`

**Yt+1:** File exists, 6/6 tests pass, receipt contains bash output of pytest + wc.

**Rt+1 target:** 0.0 (clean closure)

**Role tags:** `{"producer": "cto", "executor": "eng-kernel", "governed": "eng-kernel"}`

---

### Appendix B — Maya Patel (eng-governance) Task Card

**Task ID:** `W22.3_eng-governance_czl_forgetguard_rules`  
**Priority:** P1  
**Depends on:** Leo's parser lib (W22.2) landed

**CIEU 5-tuple:**

**Y\*:** File `ystar/governance/forgetguard_rules/czl_envelope_rules.py` exists with 2 ForgetGuard rules:
1. `dispatch_missing_cieu_5tuple` — triggers if CEO/CTO Agent tool prompt lacks `=== CIEU 5-tuple dispatch ===` header (action: warn first 2 times, then deny)
2. `receipt_no_bash_verification` — triggers if sub-agent receipt (detected via "message_type: receipt" or final reply) lacks bash output patterns (`ls -la`, `wc -l`, `pytest`, `git diff`) (action: deny + emit CIEU `HALLUCINATED_RECEIPT`)

Tests pass: `pytest ystar/tests/governance/test_czl_forgetguard.py -q` 4/4 green.

**Xt:** No CZL-specific ForgetGuard rules exist. Existing rules in `ystar/governance/forgetguard_rules/*.py` cover choice questions, multi-task dispatch, boot state reads.

**U:**
1. Read `governance/czl_unified_communication_protocol_v1.md` (this spec) for Gate 1/2 requirements
2. Read `ystar/governance/forgetguard_rules/choice_question_to_board.py` as pattern reference
3. Write `ystar/governance/forgetguard_rules/czl_envelope_rules.py` with 2 rules
4. Write `ystar/tests/governance/test_czl_forgetguard.py` with:
   - `test_dispatch_missing_5tuple_warn()` — first violation → warn
   - `test_dispatch_missing_5tuple_deny()` — 3rd violation → deny
   - `test_receipt_no_bash_verification_deny()` — missing `ls -la` → deny
   - `test_receipt_with_bash_verification_pass()` — valid receipt → pass
5. Register rules in `ystar/governance/forgetguard_engine.py` rule loader
6. Run `pytest ystar/tests/governance/test_czl_forgetguard.py -q`, paste output
7. Commit: `git commit -m "feat(governance): CZL envelope ForgetGuard rules [W22.3]"`

**Yt+1:** File exists, rules registered, 4/4 tests pass, receipt contains pytest output.

**Rt+1 target:** 0.0

**Role tags:** `{"producer": "cto", "executor": "eng-governance", "governed": "eng-governance"}`

---

### Appendix C — Ryan Park (eng-platform) Task Card

**Task ID:** `W22.4_eng-platform_czl_stop_hook`  
**Priority:** P2  
**Depends on:** Maya's ForgetGuard rules (W22.3) landed

**CIEU 5-tuple:**

**Y\*:** File `ystar/adapters/claudecode/stop_hook_czl.py` exists with function:
```python
def czl_stop_hook(reply_text: str, metadata: dict) -> tuple[bool, str]:
    """
    Stop hook that scans CEO/CTO replies for CZL protocol violations.
    Returns (should_block, reason) where should_block=True blocks reply.
    """
```

Scans for:
1. Agent tool dispatch without `=== CIEU 5-tuple dispatch ===` header → block + emit `DISPATCH_NO_5TUPLE`
2. Receipt acceptance without bash verification paste → block + emit `RECEIPT_NO_VERIFICATION`

Hook registered in `hooks.json`. Tests pass: `pytest ystar/tests/adapters/claudecode/test_stop_hook_czl.py -q` 3/3 green.

**Xt:** No CZL-specific stop hook exists. Existing stop hooks in `ystar/adapters/claudecode/hooks/` cover choice questions, multi-task dispatch.

**U:**
1. Read `governance/czl_unified_communication_protocol_v1.md` (this spec)
2. Read `ystar/adapters/claudecode/hooks/stop_hook_choice_question.py` as pattern
3. Write `ystar/adapters/claudecode/stop_hook_czl.py` with `czl_stop_hook()` function
4. Write `ystar/tests/adapters/claudecode/test_stop_hook_czl.py` with:
   - `test_dispatch_no_5tuple_block()` — blocks invalid dispatch
   - `test_receipt_no_verification_block()` — blocks hallucinated receipt
   - `test_valid_dispatch_pass()` — allows well-formed dispatch
5. Register hook in `hooks.json` (add to `stop_hooks` list)
6. Run `pytest ystar/tests/adapters/claudecode/test_stop_hook_czl.py -q`, paste output
7. Commit: `git commit -m "feat(platform): CZL Stop hook — block invalid dispatch/receipt [W22.4]"`

**Yt+1:** File exists, hook registered, 3/3 tests pass, receipt contains pytest output.

**Rt+1 target:** 0.0

**Role tags:** `{"producer": "cto", "executor": "eng-platform", "governed": "eng-platform"}`

---

## 7. Backlog Migration Table

All legacy TaskList items must be migrated to CZL envelope format before dispatch. Table maps TaskList ID → 5-tuple template.

| TaskList ID | Title | Recipient | Y\* (Acceptance Criteria) | Xt (Pre-State) | U (Actions, ≤15 tool_uses) | Priority | Migration Notes |
|-------------|-------|-----------|---------------------------|----------------|----------------------------|----------|-----------------|
| **W5.1** | K9 RT Fuse | eng-kernel | `ystar/kernel/rt_measurement.py` exists, 6/6 tests pass, no violations | No RT emit module in kernel | 1. Read K9Audit causal_analyzer.py<br>2. Write rt_measurement.py<br>3. Write test_rt_measurement.py<br>4. pytest -q<br>5. commit | P0 | **COMPLETED** (commit d89f2a1c). Migrate to envelope for reference only. |
| **W7** | CIEU Path B Demo | eng-governance | `path_b/demo_cieu_injection.py` runs without error, emits 3+ CIEU events to DB | Path B stub exists, no CIEU integration | 1. Read path_b/ structure<br>2. Import emit_cieu from kernel<br>3. Add CIEU calls to decision points<br>4. Run demo, verify DB writes<br>5. commit | P1 | Requires W5.1 landed. Xt must measure current CIEU event count in path_b/ (likely 0). |
| **W8** | 3D Audit Role Tags | eng-kernel | All `emit_cieu()` calls include `role_tags` param, K9 causal analyzer can parse 3D roles | Current emit_cieu() has no role_tags field | 1. Read K9Audit auditor.py<br>2. Update emit_cieu() signature<br>3. Update all callsites in kernel/<br>4. Add role_tags to CIEU schema<br>5. pytest kernel/ -q<br>6. commit | P1 | Xt should grep current emit_cieu callsites and count how many lack role_tags. |
| **W9** | GOV MCP SSE Stream | eng-platform | GOV MCP server streams CIEU events via SSE to localhost:7922/events, client demo script receives events | Current GOV MCP has no SSE endpoint | 1. Read gov-mcp/ server.py<br>2. Add /events SSE route<br>3. Tail CIEU DB for new events<br>4. Write client demo script<br>5. Run server + client, verify stream<br>6. commit | P2 | Xt must check if gov-mcp/ already has any SSE code (possible from prior work). |
| **W11** | Kernel CI Pipeline | eng-platform | `.github/workflows/kernel_tests.yml` exists, runs 86 tests on every push to main, badge in README green | No CI workflow for kernel tests | 1. Read .github/workflows/ existing patterns<br>2. Write kernel_tests.yml<br>3. Add pytest + mypy steps<br>4. Push to feature branch<br>5. Verify CI runs on GitHub<br>6. PR to main | P2 | Xt should count current workflows in .github/workflows/ and check if any run pytest. |
| **W12** | K9 Causal Chain Linker | eng-kernel | `ystar/kernel/causal_chain.py` exists, links RT_MEASUREMENT to prior CIEU events via task_id, tests pass | No causal linking in kernel, K9Audit has causal_analyzer.py (read-only reference) | 1. Read K9Audit causal_analyzer.py<br>2. Design task_id parent linkage<br>3. Write causal_chain.py<br>4. Write test_causal_chain.py<br>5. pytest -q<br>6. commit | P1 | DO NOT copy K9Audit code (AGPL). Extract patterns only. Xt must note license boundary. |
| **W13** | ForgetGuard Omission Detector | eng-governance | `ystar/governance/omission_detector.py` exists, scans CIEU DB for missing expected events, emits OMISSION_DETECTED | No omission detection in governance layer | 1. Read governance/omission_engine.py design<br>2. Write omission_detector.py<br>3. Write test_omission_detector.py<br>4. pytest -q<br>5. commit | P1 | Xt should check if omission_engine.py already has detector logic (may be partial). |
| **W14** | Scenario C Demo Script | eng-domains | `ystar/domains/demo_scenario_c.py` runs end-to-end, catches CROBA injection, emits INTERVENTION_TRIGGERED | No Scenario C demo exists, only Scenario A/B stubs | 1. Read products/ystar-gov/scenarios.md<br>2. Write demo_scenario_c.py (CROBA inject + catch)<br>3. Write test_scenario_c.py<br>4. Run demo, verify CIEU<br>5. commit | P1 | Xt must verify if scenario_a/b demos exist and measure their CIEU event counts. |

**Migration Protocol:**
1. CEO/CTO reads legacy TaskList item
2. Runs `parse_legacy_task_to_envelope()` (§5 auto-fill parser) → get envelope + low-confidence fields
3. Manually reviews and corrects low-confidence fields (especially Xt — must measure, not guess)
4. Runs `validate_dispatch()` (§2 Gate 1) → if fails, fix and re-validate
5. Dispatches sub-agent with corrected envelope
6. On receipt, runs `validate_receipt()` (§3 Gate 2) → if fails, re-dispatch or escalate

---

## 8. Adoption Roadmap

**Phase 1 (W22 — This Week):**
- Leo ships parser lib (W22.2)
- Maya ships ForgetGuard rules (W22.3)
- Ryan ships Stop hook (W22.4)
- **Gate 1/2 validators are live and enforced**

**Phase 2 (W23-W24):**
- CEO/CTO migrate all TaskList items (W7-W14) to CZL envelope format
- Sub-agents begin using envelope in receipts
- Collect metrics: dispatch rejection rate, receipt hallucination rate

**Phase 3 (W25+):**
- Auto-calculate Rt+1 in kernel (Phase 2 from `rt_measurement.py` docstring)
- Causal chain linking (W12)
- Real-time SSE stream for Rt>0 alerts (W9)

**Success Metrics:**
- Week 1: 0 hallucinated receipts pass Gate 2 (baseline: 1 failure today, Ethan#CZL-1)
- Week 2: 100% of dispatches include explicit 5-tuple (baseline: ~30% today)
- Week 4: Average sub-agent Rt+1 gap <0.2 (baseline: unknown, no measurement)

---

## 9. References

**Authoritative Sources:**
- `ystar/kernel/rt_measurement.py` — RT_MEASUREMENT v1.0 schema (117 lines, commit d89f2a1c)
- `governance/sub_agent_atomic_dispatch.md` — 1 dispatch = 1 deliverable rule
- `governance/sub_agent_boot_prompt_template.md` — Boot context requirements
- `knowledge/shared/unified_work_protocol_20260415.md` — CIEU 5-tuple definition, Rt+1=0 closure criteria

**Related Work:**
- K9Audit `k9log/causal_analyzer.py` — Causal chain analysis (read-only, AGPL license boundary)
- K9Audit `k9log/auditor.py` — Static analysis patterns (read-only)
- TaskList legacy items (W5-W14) — Pre-CZL task format, requires migration

**Version History:**
- v1.0 (2026-04-16): Initial specification, fixes Ethan#CZL-1 hallucination failure

---

**END OF SPECIFICATION**

Co-Authored-By: Ethan Wright (CTO) + Leo Chen (Kernel spec review) + Maya Patel (Governance spec review) + Ryan Park (Platform spec review)
