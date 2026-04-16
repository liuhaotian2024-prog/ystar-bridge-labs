# Reply Scan Detector Methodology v1

**Authority**: Maya Patel (eng-governance) per CEO dispatch CZL-113  
**Upstream**: Maya CZL-111 forensic + Ethan #75 CEO Operating Methodology  
**Downstream**: Ryan CZL-112 coordinator_reply_missing_5tuple import fix  
**Purpose**: Define WHEN replies must be 5-tuple structured, WHEN optional, and HOW to detect each case — prevent regex over-fire (false positives on "好的") and under-fire (misses prose dispatches)

---

## Section 1: Trigger Taxonomy — When 5-Tuple IS Required

A reply **IS a dispatch/receipt** requiring CIEU 5-tuple structure if it contains **ANY** of the following:

### 1.1 Action Verbs to Sub-Agent
Keywords indicating task delegation or execution coordination:
- **Chinese**: 派, 调起, 执行, 启动, spawn, 分配, 命令, 指示, 让 [agent] 做
- **English**: dispatch, spawn, executing, now running, delegating to, routing to, calling [Agent tool], activating

**Pattern**: `(派|调起|执行|启动|spawn|分配|命令|指示|让\s+\w+\s+做|dispatch|executing|now running|delegating to|routing to|calling|activating)`

**Example** (MUST be 5-tuple):
> "NOW 派 Ryan CZL-112 修复 import 路径"

### 1.2 Artifact Landing Report
Keywords indicating work product delivered:
- **File paths**: Absolute paths (e.g., `/Users/.../file.md`, `governance/spec.yaml`)
- **Commit hashes**: 7-8 char hex (e.g., `commit a1b2c3d`, `dedf11d7`)
- **Status markers**: shipped, landed, closed, Rt+1=0, Rt+1=N, L0-L5 maturity tags
- **Metrics**: `N/M tests PASS`, `X violations detected`, `Y% coverage`

**Pattern**: `(shipped|landed|closed|Rt\+1\s*=\s*\d|L[0-5]\s+(SHIPPED|VALIDATED|TESTED)|commit\s+[a-f0-9]{7,}|/Users/\S+\.md|\d+/\d+ tests PASS|\d+%)`

**Example** (MUST be 5-tuple):
> "Maya CZL-111 forensic shipped (L3 VALIDATED), commit f00e91ac, 20/20 deliverables verified, Rt+1=1 (test file pending)."

### 1.3 State-Change to Project
Keywords indicating campaign/milestone/blocker transitions:
- **Campaign progress**: Wave N closed, Subgoal W{N} complete, Campaign v{N} launched
- **Task lifecycle**: Task #{N} assigned/blocked/resolved, P0/P1/P2 escalation
- **System state**: Daemon recycled, enforcement LIVE, hook promoted warn→deny

**Pattern**: `(Wave\s+\w+\s+closed|Subgoal\s+W\d+|Campaign\s+v\d+|Task\s+#\d+|P[0-2]\s+escalation|Daemon\s+recycled|enforcement\s+LIVE|hook\s+promoted|模式\s+切换|状态\s+变更)`

**Example** (MUST be 5-tuple):
> "Campaign v6 W1-W2 closed (Rt+1=0), W3 in flight (Ryan CZL-102 running)."

### 1.4 Direct Response to Board ASK
Board query patterns requiring structured answer:
- **Status queries**: 状态/进度/结果如何, what's status, did X work, show progress
- **Metric queries**: 多少/几个/百分比, how many, count, percentage
- **Decision queries**: 决定/选择, which option, what's the call, recommendation

**Pattern**: `(?i)(状态|进度|结果|status|progress|多少|几个|how many|count|percentage|决定|选择|recommendation|which option|what's the call)`

**Context**: Appears in Board's **previous** message (not CEO's reply) — requires lookback.

**Example** (Board asks "W11 状态?", CEO reply MUST be 5-tuple):
> Board: "W11 Agent Capability Monitor 进度?"  
> CEO: [must structure with Y\*/Xt/U/Yt+1/Rt+1]

---

## Section 2: Exemption Taxonomy — When 5-Tuple IS Optional

A reply **IS conversational** (5-tuple optional) if it satisfies **ALL** of:

### 2.1 No Action Verbs
- Does NOT contain any §1.1 action verbs (派/dispatch/spawn/executing...)
- Does NOT contain any §1.2 artifact markers (file paths, commit hashes, maturity tags)
- Does NOT contain any §1.3 state-change keywords

### 2.2 No Artifact References
- No file paths (absolute or relative)
- No commit hashes, git refs, branch names
- No line numbers, function names, code snippets
- No tool output paste (pytest/ls/wc/git diff)

### 2.3 No Metric Numbers
- No counts (e.g., "3/5 tasks", "12 violations")
- No percentages (e.g., "87% FP rate")
- No scores (e.g., "trust=0.7", "Rt+1=2")
- **Exception**: Session/conversation IDs (e.g., "session f3b750b8") allowed

### 2.4 Reply Length <50 Chars OR Pure Greeting/Ack
Short acknowledgments exempt from 5-tuple requirement:
- **Chinese**: 好的, 收到, 明白, 了解, 是的, 对, 懂, OK
- **English**: yes, ok, got it, understood, roger, ack, will do, on it

**Pattern**: `^(好的|收到|明白|了解|是的|对|懂|OK|yes|ok|got it|understood|roger|ack|will do|on it)[。!！.]*$`

**Length check**: `len(reply.strip()) < 50`

### 2.5 Direct Clarifying Question to Board
Reply **only** asks for confirmation/clarification, contains NO action claims:
- **Chinese**: 我理解为 X 对吗？, 您是指 Y？, 确认一下 Z？
- **English**: Do you mean X?, Just to confirm Y?, Clarifying: Z?

**Pattern**: `(我理解为|您是指|确认一下|Do you mean|Just to confirm|Clarifying)[^。!！.?？]*[?？]$`

**Example** (5-tuple optional):
> "我理解为：W11 需要优先级提到 P0 对吗？"

---

## Section 3: 5-Tuple Format Spec — Strictness Levels

### 3.1 Strict Mode (Recommended for CEO→Board replies)
**Requirements**:
- All 5 labels present: `**Y\***`, `**Xt**`, `**U**`, `**Yt+1**`, `**Rt+1**`
- Labels appear **in order** (not shuffled)
- Each label followed by content (not empty sections)
- Labels use exact markdown bold syntax: `**Label**:` or `**Label**` on own line

**Regex**:
```python
strict_pattern = r"""
\*\*Y\\\*\*\*\s*:?\s+.+?         # Y* with content
\*\*Xt\*\*\s*:?\s+.+?           # Xt with content
\*\*U\*\*\s*:?\s+.+?            # U with content
\*\*Yt\+1\*\*\s*:?\s+.+?        # Yt+1 with content
\*\*Rt\+1\*\*\s*:?\s+.+?        # Rt+1 with content
"""
```

**Why Strict for CEO**: Board is dispatch sender, CEO reply is receipt — highest accountability tier per Iron Rule 0. Board's anger 2026-04-16 stemmed from CEO prose summaries with 0 5-tuple structure across 20-hour session. Strict mode prevents recurrence.

### 3.2 Lenient Mode (Acceptable for sub-agent receipts)
**Requirements**:
- **≥3 of 5** labels present (allows omission of 2 sections if not applicable)
- Labels may be abbreviated: `Y*`, `U`, `Rt` (without markdown bold)
- Order flexible (e.g., Rt+1 before Yt+1 allowed)
- Content under each label required

**Regex**:
```python
lenient_pattern = r"""
(?=.*\b(Y\*|Y\\\*))             # Has Y* somewhere
(?=.*\b(Xt|X_t))                # Has Xt somewhere
(?=.*\b(U|Actions?))            # Has U somewhere
"""  # Match if ≥3 labels found (simplified)
```

**Use case**: Sub-agent atomic receipts where context is tightly scoped (e.g., "write file X") — full 5-tuple overhead may be verbose. Lenient allows flexibility while maintaining core structure.

### 3.3 Permissive Mode (For engineer chitchat — NOT recommended for production)
**Requirements**:
- 5-tuple **semantic content** present without literal labels
- Must detect: mission statement + before-state + action list + after-state + gap measurement
- Requires NLP heuristic or GPT-based classification

**Example** (permissive accepts):
> "Task: fix import. Current: broken path. Steps: grep, edit, test. Result: all green. Gap: none."

**Why NOT recommended**: Ambiguous, requires LLM call per reply (expensive + latency), no empirical validation. Use Strict or Lenient instead.

**Detection algorithm pseudocode**:
```python
def is_permissive_5tuple(reply: str) -> bool:
    # Calls GPT-4 mini with prompt:
    # "Does this text contain: (1) goal, (2) initial state, (3) actions, (4) final state, (5) gap? Yes/No"
    # Return GPT answer == "Yes"
    # WARNING: Not empirical, not recommended for production enforcement
```

---

## Section 4: Detection Algorithm Pseudocode

### 4.1 Main Dispatcher: `is_dispatch_receipt(reply_text) -> bool`

```python
def is_dispatch_receipt(reply_text: str, board_previous_msg: str = "") -> bool:
    """
    Determine if reply requires 5-tuple structure.
    
    Args:
        reply_text: CEO/coordinator reply message
        board_previous_msg: Board's previous message (for §1.4 context)
    
    Returns:
        True if reply is dispatch/receipt (must be 5-tuple), False if conversational
    """
    import re
    
    # §2 Exemption checks (ALL must pass to exempt)
    if _is_exempt_conversational(reply_text):
        return False  # Conversational, 5-tuple optional
    
    # §1 Trigger checks (ANY passes → must be 5-tuple)
    if _has_action_verbs(reply_text):
        return True
    if _has_artifact_landing(reply_text):
        return True
    if _has_state_change(reply_text):
        return True
    if _is_response_to_board_ask(reply_text, board_previous_msg):
        return True
    
    # Default: if >200 chars and no exemption, treat as dispatch (conservative)
    return len(reply_text.strip()) > 200


def _is_exempt_conversational(text: str) -> bool:
    """§2 exemption taxonomy — all conditions must be True to exempt."""
    # §2.1-2.3: No action verbs, artifacts, metrics
    if re.search(r'(派|调起|执行|启动|spawn|dispatch|shipped|landed|commit\s+[a-f0-9]{7}|/Users/\S+\.\w+|\d+/\d+|L[0-5]\s+SHIPPED)', text, re.IGNORECASE):
        return False
    
    # §2.4: Short ack OR greeting pattern
    if len(text.strip()) < 50 or re.match(r'^(好的|收到|明白|了解|是的|对|懂|OK|yes|ok|got it|understood|roger|ack|will do|on it)[。!！.]*$', text.strip(), re.IGNORECASE):
        return True
    
    # §2.5: Clarifying question
    if re.search(r'(我理解为|您是指|确认一下|Do you mean|Just to confirm|Clarifying)[^。!！.?？]*[?？]$', text, re.IGNORECASE):
        return True
    
    return False


def _has_action_verbs(text: str) -> bool:
    """§1.1 trigger: dispatch/execution verbs."""
    pattern = r'(派|调起|执行|启动|spawn|分配|命令|指示|让\s+\w+\s+做|dispatch|executing|now running|delegating to|routing to|calling|activating)'
    return re.search(pattern, text, re.IGNORECASE) is not None


def _has_artifact_landing(text: str) -> bool:
    """§1.2 trigger: file paths, commit hashes, maturity tags."""
    pattern = r'(shipped|landed|closed|Rt\+1\s*=\s*\d|L[0-5]\s+(SHIPPED|VALIDATED|TESTED)|commit\s+[a-f0-9]{7,}|/Users/\S+\.md|\d+/\d+\s+tests?\s+PASS|\d+%)'
    return re.search(pattern, text, re.IGNORECASE) is not None


def _has_state_change(text: str) -> bool:
    """§1.3 trigger: campaign/milestone/system state transitions."""
    pattern = r'(Wave\s+\w+\s+closed|Subgoal\s+W\d+|Campaign\s+v\d+|Task\s+#\d+|P[0-2]\s+escalation|Daemon\s+recycled|enforcement\s+LIVE|hook\s+promoted|模式\s+切换|状态\s+变更)'
    return re.search(pattern, text, re.IGNORECASE) is not None


def _is_response_to_board_ask(reply: str, board_msg: str) -> bool:
    """§1.4 trigger: Board asked status/metric/decision question."""
    if not board_msg:
        return False  # No context, can't determine
    
    ask_pattern = r'(状态|进度|结果|status|progress|多少|几个|how many|count|percentage|决定|选择|recommendation|which option|what\'s the call)'
    return re.search(ask_pattern, board_msg, re.IGNORECASE) is not None
```

### 4.2 Validator: `validate_5tuple(reply_text, strictness) -> (passed, missing_labels)`

```python
def validate_5tuple(reply_text: str, strictness: str = "strict") -> tuple[bool, list[str]]:
    """
    Validate if reply contains 5-tuple structure.
    
    Args:
        reply_text: CEO/coordinator reply message
        strictness: "strict" | "lenient" | "permissive"
    
    Returns:
        (passed: bool, missing_labels: list[str])
        - passed: True if 5-tuple valid per strictness level
        - missing_labels: ["Y*", "Xt", ...] if any required labels absent
    """
    import re
    
    if strictness == "strict":
        required_labels = ["Y\\*", "Xt", "U", "Yt\\+1", "Rt\\+1"]
        missing = []
        for label in required_labels:
            pattern = rf'\*\*{label}\*\*\s*:?\s+\S+'  # Bold label + content
            if not re.search(pattern, reply_text):
                missing.append(label.replace("\\", ""))
        return (len(missing) == 0, missing)
    
    elif strictness == "lenient":
        # ≥3 of 5 labels required (abbreviated ok)
        labels_found = 0
        for label in ["Y\\*", "Xt", "\\bU\\b", "Yt\\+1", "Rt\\+1"]:
            if re.search(rf'({label}|{label.lower()})', reply_text, re.IGNORECASE):
                labels_found += 1
        passed = labels_found >= 3
        missing = [] if passed else [f"<3 labels found ({labels_found}/5)"]
        return (passed, missing)
    
    elif strictness == "permissive":
        # Semantic content check (NLP required, not implemented here)
        # Placeholder: always pass (NOT recommended for production)
        return (True, [])
    
    else:
        raise ValueError(f"Unknown strictness: {strictness}")
```

---

## Section 5: Test Corpus — 10 Labeled Historical/Synthetic Examples

### Positive Cases (MUST fire — 5-tuple required)

#### P1: Action verb dispatch
**Text**:
> "收到老大。NOW 派 Ryan CZL-112 修复 coordinator_reply_missing_5tuple import 路径，≤8 tool_uses，禁 git commit。"

**Label**: DISPATCH (§1.1 action verb "派")  
**Expected**: `is_dispatch_receipt() == True`

#### P2: Artifact landing with commit hash
**Text**:
> "Maya CZL-111 forensic shipped (L3 VALIDATED), commit f00e91ac, 20/20 deliverables verified, Rt+1=1 (test file pending)."

**Label**: RECEIPT (§1.2 artifact markers: shipped, commit hash, Rt+1=N, maturity tag)  
**Expected**: `is_dispatch_receipt() == True`

#### P3: State-change to campaign
**Text**:
> "Campaign v6 W1-W2 closed (Rt+1=0), W3 in flight (Ryan CZL-102 running), 总进度 2/10。"

**Label**: PROJECT_STATE (§1.3 state-change: Wave closed, Subgoal)  
**Expected**: `is_dispatch_receipt() == True`

#### P4: Response to Board status query
**Board msg**: "W11 Agent Capability Monitor 状态?"  
**CEO reply**:
> "W11 Ryan CZL-108 进行中，statusline 已 wire 4 信号，测试 pending。"

**Label**: BOARD_ASK (§1.4 Board query contains "状态")  
**Expected**: `is_dispatch_receipt() == True` (given board_previous_msg context)

#### P5: Multiple triggers (action + artifact + metric)
**Text**:
> "NOW 执行 Leo CZL-115 跨工程师协作测试：governance/cross_team_test_v1.py shipped (87 lines), 5/5 tests PASS, commit a1b2c3d。"

**Label**: MULTI_TRIGGER (§1.1 "执行", §1.2 file path + tests + commit)  
**Expected**: `is_dispatch_receipt() == True`

---

### Negative Cases (MUST NOT fire — 5-tuple optional)

#### N1: Short acknowledgment
**Text**:
> "好的，收到。"

**Label**: ACK (§2.4 short greeting, length=6 chars <50)  
**Expected**: `is_dispatch_receipt() == False`

#### N2: Clarifying question
**Text**:
> "我理解为：W11 需要优先级提到 P0 对吗？"

**Label**: CLARIFYING_QUESTION (§2.5 pattern match)  
**Expected**: `is_dispatch_receipt() == False`

#### N3: Pure greeting (English)
**Text**:
> "Got it, on it."

**Label**: ACK_ENGLISH (§2.4 greeting pattern)  
**Expected**: `is_dispatch_receipt() == False`

#### N4: Conversational chitchat (no triggers)
**Text**:
> "明白，这个思路很清楚，我同意这个判断。"

**Label**: CONVERSATIONAL (§2.1-2.3 no action/artifact/metric, §2.4 length >50 but no triggers)  
**Expected**: `is_dispatch_receipt() == False`

#### N5: Session ID mention (metric exception)
**Text**:
> "这个 session f3b750b8 里确实没有五元组回复，我检讨。"

**Label**: CONVERSATIONAL (§2.3 metric exception: session ID allowed, no other triggers)  
**Expected**: `is_dispatch_receipt() == False`

---

## Section 6: Integration Directive for Ryan CZL-112

**Downstream consumer**: Ryan Park (eng-platform), Task CZL-112 `coordinator_reply_missing_5tuple` import fix

**Integration steps**:

### 6.1 Import Methodology Module
Ryan should import this spec's detection functions into `ystar/governance/reply_scan_detector.py`:

```python
# ystar/governance/reply_scan_detector.py
"""
Reply Scan Detector — WHEN replies must be 5-tuple structured.

Canonical spec: governance/reply_scan_detector_methodology_v1.md (Maya CZL-113)
"""

def is_dispatch_receipt(reply_text: str, board_previous_msg: str = "") -> bool:
    """§4.1 main dispatcher — see methodology spec."""
    # [Copy pseudocode from §4.1]
    ...

def validate_5tuple(reply_text: str, strictness: str = "strict") -> tuple[bool, list[str]]:
    """§4.2 validator — see methodology spec."""
    # [Copy pseudocode from §4.2]
    ...
```

### 6.2 Wire to ForgetGuard Rule
Update `governance/forget_guard_rules.yaml` rule `coordinator_reply_missing_5tuple`:

```yaml
id: coordinator_reply_missing_5tuple
validation:
  - type: python_validator
    module: "ystar.governance.reply_scan_detector"
    function: "is_dispatch_receipt"
    args: ["text", "board_previous_msg"]  # Pass Board's last msg for §1.4 context
    expect_true: true
  - type: python_validator
    module: "ystar.governance.reply_scan_detector"
    function: "validate_5tuple"
    args: ["text", "strict"]  # Strict mode for CEO→Board
    expect_passed: true
```

### 6.3 Configure Strictness Per Agent Role
```python
# ystar/governance/reply_scan_detector.py

STRICTNESS_MAP = {
    "ceo": "strict",       # CEO→Board must be strict (highest accountability)
    "cto": "strict",       # CTO→CEO also strict (coordination tier)
    "eng-*": "lenient",    # Engineers→CTO lenient (atomic context)
    "default": "lenient"   # Sub-agents default lenient
}

def get_strictness(agent_id: str) -> str:
    """Return strictness level for agent_id."""
    if agent_id.startswith("eng-"):
        return STRICTNESS_MAP["eng-*"]
    return STRICTNESS_MAP.get(agent_id, STRICTNESS_MAP["default"])
```

### 6.4 Test Calibration
Ryan should run 10-item test corpus (§5) against `is_dispatch_receipt()` and `validate_5tuple()`:

```bash
pytest tests/platform/test_reply_scan_detector.py::test_positive_cases -v
pytest tests/platform/test_reply_scan_detector.py::test_negative_cases -v
```

Expected: 5/5 positive cases fire, 5/5 negative cases exempt (0 false positives, 0 false negatives).

### 6.5 Regex Tuning
If test corpus fails (e.g., P4 doesn't fire because board_previous_msg not passed), Ryan should:
1. Review §1-2 taxonomy
2. Adjust pattern in §4 pseudocode (NOT §1-2 spec — keep spec stable)
3. Re-run tests until 10/10 pass
4. Document tuning rationale in test file docstring

**Threshold**: ≥9/10 test cases must pass before merging. If <9/10, escalate to Maya for taxonomy refinement (potential false positive/negative in spec).

---

## Appendix A: Empirical Verification Checklist

After shipping this spec, Maya (eng-governance) must verify:

- [ ] File `governance/reply_scan_detector_methodology_v1.md` exists
- [ ] `wc -l` output: ≥800 words (estimated ~1100 lines markdown)
- [ ] 6 sections present: §1 Trigger Taxonomy, §2 Exemption Taxonomy, §3 Format Spec, §4 Detection Algorithm, §5 Test Corpus, §6 Integration Directive
- [ ] §5 contains 10 labeled examples (5 positive P1-P5, 5 negative N1-N5)
- [ ] §6 contains Ryan integration directive with 5 subsections (6.1-6.5)
- [ ] Tool_uses claim matches metadata exactly (no over/under claim per E1 rule)
- [ ] Receipt is 5-tuple structured (Y\*/Xt/U/Yt+1/Rt+1 labels present)
- [ ] Receipt ≤200 words (Board overwhelm threshold per MEMORY `user_overwhelm_threshold.md`)

**Bash verification paste**:
```bash
ls -la governance/reply_scan_detector_methodology_v1.md
wc -l governance/reply_scan_detector_methodology_v1.md
grep -c "^## Section [1-6]:" governance/reply_scan_detector_methodology_v1.md  # Expect 6
grep -c "^#### [PN][1-5]:" governance/reply_scan_detector_methodology_v1.md  # Expect 10
grep -c "^### 6\.[1-5]" governance/reply_scan_detector_methodology_v1.md     # Expect 5
```

---

**Version**: v1.0  
**Author**: Maya Patel (eng-governance)  
**Date**: 2026-04-16  
**Task**: CZL-113 P1 atomic  
**Upstream**: Maya CZL-111 forensic + Ethan #75 CEO Operating Methodology  
**Downstream**: Ryan CZL-112 coordinator_reply_missing_5tuple import fix

Co-Authored-By: Maya Patel (Y* Bridge Labs, eng-governance)
