# Proposal: ObligationTrigger Framework
## Board Directive #015 Response

**Author:** CEO Agent
**Date:** 2026-03-26
**Status:** PENDING BOARD APPROVAL
**Priority:** P0 - Most important architectural upgrade in Y*gov history

---

## Executive Summary

Y*gov currently governs only the tool-call layer: when an agent executes a tool, `check()` intercepts and validates. But an entire class of behavior escapes governance: **consequent obligations** - things agents SHOULD do but DON'T. This proposal introduces the **ObligationTrigger** framework to automatically create follow-up obligations when certain tool calls occur, enabling the OmissionEngine to track and enforce behaviors that currently escape detection.

---

## Problem Statement

### The Governance Gap

Today's Y*gov architecture has a fundamental blind spot:

```
Current Y*gov Governance Model:
================================

  Agent calls tool ---> check() intercepts ---> ALLOW/DENY ---> CIEU record
       |                      |                      |
       v                      v                      v
   [GOVERNED]            [GOVERNED]             [GOVERNED]

  Agent SHOULD do X ---> ??? ---> ??? ---> ???
       |                  |        |        |
       v                  v        v        v
   [UNGOVERNED]      [UNGOVERNED] [UNGOVERNED] [UNGOVERNED]
```

### Real Evidence from Y* Bridge Labs Operations

**CASE: CMO Bootstrap Omission (2026-03-26)**
- CMO completed 19 `web_search` calls
- CMO wrote a 2,847-word article
- CMO did NOT update `knowledge/cmo/` with new findings
- CMO did NOT log to `knowledge/bootstrap_log.md`
- **Y*gov had no mechanism to detect this, intercept it, or record it**

This is not a CMO-specific failure. It is a **systemic governance gap**.

### Complete Inventory of Ungoverned Consequent Obligations

From analysis of AGENTS.md and current operations, the following obligation types exist but are completely ungoverned:

| Trigger Event | Required Follow-Up | Target Agent | Currently Enforced? |
|---------------|-------------------|--------------|---------------------|
| `web_search` call | Update `knowledge/[role]/` | Calling agent | NO |
| `WebSearch` call | Update `knowledge/[role]/` | Calling agent | NO |
| Session completion | Run `track_burn.py` | CFO | NO |
| Knowledge gap detected | Bootstrap within 30 min | Detecting agent | NO |
| Task completion | Update `bootstrap_log.md` | Completing agent | NO |
| Bug fix completed | Update `cto_fix_log.md` | CTO | NO |
| Subagent task complete | Report to orchestrator | Subagent | NO |
| Content creation complete | Update article pipeline | CMO | NO |
| CIEU deny event | Log for case analysis | Any agent | NO |
| User conversation | Document in `sales/feedback/` | CSO | NO |
| P0 bug assigned | Fix within 5 minutes | CTO | SOFT (SLA only) |
| Cross-agent conflict | Resolve within 10 min | CEO | SOFT (SLA only) |
| Expenditure occurs | Log within 24 hours | CFO | SOFT (SLA only) |
| GitHub Issue created | Triage within 15 min | CTO | SOFT (SLA only) |

**Key insight:** The "SOFT (SLA only)" items exist as text in AGENTS.md but have no enforcement mechanism. They are aspirational, not operational.

### Root Cause Analysis

The OmissionEngine (`omission_engine.py`) already has sophisticated machinery for:
- Tracking obligations with deadlines
- Detecting violations when deadlines pass
- Escalating through SOFT_OVERDUE -> HARD_OVERDUE stages
- Recording violations to CIEU

**What's missing:** A mechanism to **automatically create obligations** when certain tool calls occur.

Currently, obligations are only created when:
1. Explicit governance events are injected via `ingest_event()`
2. Domain packs register rules that trigger on governance event types (like `ENTITY_CREATED`)

But tool calls (like `web_search`, `Write`, session end) do not automatically generate governance events that trigger obligation creation.

---

## Proposed Solution: ObligationTrigger Framework

### Core Concept

**ObligationTrigger** bridges the gap between tool-call-layer governance and obligation-layer governance.

```
New Y*gov Governance Model with ObligationTrigger:
===================================================

  Agent calls tool ---> check() intercepts ---> ALLOW/DENY ---> CIEU record
       |                      |                      |              |
       v                      v                      v              v
   [GOVERNED]            [GOVERNED]             [GOVERNED]     [GOVERNED]
                              |
                              v
                   ObligationTrigger.match(tool_call)
                              |
                              v (if matches)
                   Create ObligationRecord
                              |
                              v
                   OmissionEngine.track(obligation)
                              |
                              v (if deadline passes)
                   OmissionViolation ---> CIEU record
                              |
                              v
                   InterventionEngine.gate() ---> DENY future actions
```

### ObligationTrigger Definition

```python
@dataclass
class ObligationTrigger:
    """
    Defines when a tool call creates a follow-up obligation.

    When an agent calls a tool matching trigger_pattern,
    the system automatically creates an obligation that must be
    fulfilled within deadline_seconds by producing the required_event.
    """

    # Unique identifier
    trigger_id:           str

    # Matching criteria
    trigger_tool_pattern: str          # regex pattern for tool_name (e.g., "web_search|WebSearch")
    trigger_param_filter: dict = None  # optional param conditions (e.g., {"agent_role": "CMO"})

    # Obligation specification
    obligation_type:      str          # e.g., "knowledge_update_required"
    description:          str          # human-readable description
    target_agent:         str          # "caller" | "CFO" | specific agent | "orchestrator"

    # Timing
    deadline_seconds:     int          # how long they have to fulfill
    grace_period_secs:    float = 0.0  # soft grace before violation
    hard_overdue_secs:    float = 0.0  # when to block all unrelated actions

    # Severity escalation
    initial_severity:     str = "SOFT" # SOFT | HARD
    escalate_to_hard:     bool = True  # auto-escalate after deadline
    escalate_to_actor:    str = None   # who gets notified on escalation

    # Verification
    fulfillment_event:    str          # what event type fulfills this obligation
    verification_method:  str = None   # "file_modified" | "event_received" | "custom"
    verification_target:  str = None   # e.g., "knowledge/{role}/" for file_modified

    # Control
    enabled:              bool = True
    deduplicate:          bool = True  # don't create if same obligation pending
    deny_closure_on_open: bool = False # block session close if unfulfilled
```

### Integration Point: Hook Adapter

The hook adapter (`hook.py`) is the natural integration point. After `check()` returns ALLOW:

```python
def check_hook(hook_payload, policy, agent_id=None):
    # ... existing check logic ...

    if result.allowed:
        # NEW: Check if this tool call triggers any obligations
        triggers = match_obligation_triggers(tool_name, tool_input, who)
        for trigger in triggers:
            create_triggered_obligation(trigger, who, session_id)

    return _result_to_response(result)


def match_obligation_triggers(tool_name: str, tool_input: dict, agent_id: str) -> List[ObligationTrigger]:
    """
    Match tool call against registered ObligationTriggers.
    Returns all triggers that match this tool call.
    """
    triggers = get_trigger_registry().all_enabled()
    matches = []

    for trigger in triggers:
        # Check tool name pattern
        if not re.match(trigger.trigger_tool_pattern, tool_name, re.IGNORECASE):
            continue

        # Check param filter if specified
        if trigger.trigger_param_filter:
            if not _params_match_filter(tool_input, trigger.trigger_param_filter):
                continue

        # Check target agent
        if trigger.target_agent == "caller":
            pass  # always matches
        elif trigger.target_agent != agent_id:
            continue

        matches.append(trigger)

    return matches


def create_triggered_obligation(trigger: ObligationTrigger, agent_id: str, session_id: str):
    """
    Create an ObligationRecord from an ObligationTrigger.
    Inject into OmissionEngine for tracking.
    """
    adapter = get_omission_adapter()
    if adapter is None:
        return

    # Determine target actor
    target = agent_id if trigger.target_agent == "caller" else trigger.target_agent

    # Create governance event to trigger obligation
    from ystar.governance.omission_models import GovernanceEvent, GEventType

    ev = GovernanceEvent(
        event_id    = f"trigger:{trigger.trigger_id}:{uuid.uuid4().hex[:8]}",
        event_type  = f"tool_trigger:{trigger.trigger_id}",
        entity_id   = session_id,
        actor_id    = target,
        ts          = time.time(),
        payload     = {
            "trigger_id":     trigger.trigger_id,
            "obligation_type": trigger.obligation_type,
            "deadline_secs":  trigger.deadline_seconds,
            "fulfillment":    trigger.fulfillment_event,
        },
    )

    adapter.engine.ingest_event(ev)
```

### TriggerRegistry: Configuration and Management

```python
class TriggerRegistry:
    """
    Global registry for ObligationTriggers.
    Loaded from AGENTS.md or separate trigger config.
    """

    def __init__(self):
        self._triggers: Dict[str, ObligationTrigger] = {}

    def register(self, trigger: ObligationTrigger) -> None:
        self._triggers[trigger.trigger_id] = trigger

    def all_enabled(self) -> List[ObligationTrigger]:
        return [t for t in self._triggers.values() if t.enabled]

    def triggers_for_tool(self, tool_name: str) -> List[ObligationTrigger]:
        return [
            t for t in self.all_enabled()
            if re.match(t.trigger_tool_pattern, tool_name, re.IGNORECASE)
        ]

    @classmethod
    def from_agents_md(cls, agents_md_path: str) -> "TriggerRegistry":
        """
        Parse AGENTS.md and extract trigger definitions.

        Expected format in AGENTS.md:

        ## Obligation Triggers

        | Trigger | Tool Pattern | Obligation | Target | Deadline | Fulfillment |
        |---------|--------------|------------|--------|----------|-------------|
        | web_search_knowledge | web_search|WebSearch | knowledge_update | caller | 1800s | file_write:knowledge/ |
        """
        # Implementation details...
```

---

## Trigger Catalog

### Complete set of triggers for Y* Bridge Labs operations:

---

### Trigger 1: Knowledge Update After Research

```yaml
trigger_id:           "research_knowledge_update"
trigger_tool_pattern: "web_search|WebSearch|WebFetch"
trigger_param_filter: null
obligation_type:      "knowledge_update_required"
description:          "After web research, update knowledge/[role]/ with findings"
target_agent:         "caller"
deadline_seconds:     1800    # 30 minutes (matches AGENTS.md bootstrap obligation)
grace_period_secs:    180     # 3 minute soft grace
hard_overdue_secs:    3600    # 1 hour before blocking
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "file_write"
verification_method:  "file_modified"
verification_target:  "knowledge/{agent_role}/"
enabled:              true
deduplicate:          true
deny_closure_on_open: false
```

**Rationale:** This directly addresses the CMO case. After any web search, the agent has 30 minutes to write findings to their knowledge directory.

---

### Trigger 2: Token Recording After Session

```yaml
trigger_id:           "session_token_recording"
trigger_tool_pattern: "session_end|TaskComplete|task_closed"
trigger_param_filter: null
obligation_type:      "token_recording_required"
description:          "After session completion, CFO must run track_burn.py"
target_agent:         "CFO"
deadline_seconds:     600     # 10 minutes (from AGENTS.md CFO obligations)
grace_period_secs:    60      # 1 minute soft grace
hard_overdue_secs:    600     # Immediate block after deadline
initial_severity:     "HARD"  # Non-negotiable per AGENTS.md
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "bash_exec"
verification_method:  "command_contains"
verification_target:  "track_burn.py"
enabled:              true
deduplicate:          true
deny_closure_on_open: true    # Cannot close session without recording
```

**Rationale:** This makes CFO token recording machine-enforced rather than dependent on CFO initiative.

---

### Trigger 3: Bootstrap Log After Task Completion

```yaml
trigger_id:           "bootstrap_log_update"
trigger_tool_pattern: "Write|Edit"
trigger_param_filter:
  file_path_contains: "knowledge/"
obligation_type:      "bootstrap_log_required"
description:          "After writing to knowledge/, update bootstrap_log.md"
target_agent:         "caller"
deadline_seconds:     300     # 5 minutes
grace_period_secs:    60
hard_overdue_secs:    600
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    null    # No escalation, just violation record
fulfillment_event:    "file_write"
verification_method:  "file_modified"
verification_target:  "knowledge/bootstrap_log.md"
enabled:              true
deduplicate:          true
deny_closure_on_open: false
```

**Rationale:** Ensures bootstrap_log.md stays up to date with all knowledge updates.

---

### Trigger 4: Fix Log After Bug Fix

```yaml
trigger_id:           "cto_fix_log_update"
trigger_tool_pattern: "Write|Edit"
trigger_param_filter:
  file_path_contains: "ystar/"
  agent_role:         "CTO"
obligation_type:      "fix_log_required"
description:          "After code changes in ystar/, update cto_fix_log.md"
target_agent:         "CTO"
deadline_seconds:     300     # 5 minutes
grace_period_secs:    60
hard_overdue_secs:    600
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "file_write"
verification_method:  "file_modified"
verification_target:  "reports/cto_fix_log.md"
enabled:              true
deduplicate:          true
deny_closure_on_open: false
```

**Rationale:** Ensures all CTO fixes are documented for audit and knowledge transfer.

---

### Trigger 5: Subagent Report to Orchestrator

```yaml
trigger_id:           "subagent_completion_report"
trigger_tool_pattern: "task_complete|result_ready"
trigger_param_filter:
  is_subagent:        true
obligation_type:      "orchestrator_report_required"
description:          "Subagent must report completion to orchestrator"
target_agent:         "caller"
deadline_seconds:     120     # 2 minutes
grace_period_secs:    30
hard_overdue_secs:    300
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    "orchestrator"
fulfillment_event:    "upstream_notify"
verification_method:  "event_received"
verification_target:  null
enabled:              true
deduplicate:          true
deny_closure_on_open: true    # Subagent cannot close without reporting
```

**Rationale:** Prevents orphaned subagent work that never surfaces to orchestrator.

---

### Trigger 6: User Conversation Documentation

```yaml
trigger_id:           "user_conversation_doc"
trigger_tool_pattern: "WebFetch|web_search|external_api"
trigger_param_filter:
  agent_role:         "CSO"
  url_contains:       ["linkedin", "twitter", "email", "slack", "discord"]
obligation_type:      "conversation_documentation_required"
description:          "CSO must document user conversations within 24 hours"
target_agent:         "CSO"
deadline_seconds:     86400   # 24 hours (from AGENTS.md)
grace_period_secs:    3600    # 1 hour
hard_overdue_secs:    172800  # 48 hours
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "file_write"
verification_method:  "file_modified"
verification_target:  "sales/feedback/"
enabled:              true
deduplicate:          false   # Each conversation needs documentation
deny_closure_on_open: false
```

**Rationale:** Ensures no user feedback is lost.

---

### Trigger 7: Case Documentation After Failure

```yaml
trigger_id:           "failure_case_documentation"
trigger_tool_pattern: ".*"    # Any tool
trigger_param_filter:
  cieu_decision:      "DENY"
obligation_type:      "case_documentation_required"
description:          "After CIEU deny, document in knowledge/cases/"
target_agent:         "caller"
deadline_seconds:     3600    # 1 hour
grace_period_secs:    600
hard_overdue_secs:    7200
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "file_write"
verification_method:  "file_modified"
verification_target:  "knowledge/cases/"
enabled:              true
deduplicate:          true
deny_closure_on_open: false
```

**Rationale:** Builds case accumulation protocol automatically.

---

### Trigger 8: GitHub Issue Triage

```yaml
trigger_id:           "github_issue_triage"
trigger_tool_pattern: "mcp__github_create_issue|github_issue_created"
trigger_param_filter: null
obligation_type:      "issue_triage_required"
description:          "CTO must triage new GitHub Issues within 15 minutes"
target_agent:         "CTO"
deadline_seconds:     900     # 15 minutes (from AGENTS.md)
grace_period_secs:    120
hard_overdue_secs:    1800
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "github_issue_labeled"
verification_method:  "event_received"
verification_target:  null
enabled:              true
deduplicate:          true
deny_closure_on_open: false
```

**Rationale:** Ensures GitHub Issues are triaged promptly per AGENTS.md SLAs.

---

### Trigger 9: Content Accuracy Review

```yaml
trigger_id:           "content_accuracy_review"
trigger_tool_pattern: "Write|Edit"
trigger_param_filter:
  agent_role:         "CMO"
  file_path_contains: ["content/", "marketing/"]
obligation_type:      "cto_review_required"
description:          "CMO content must be reviewed by CTO before publish"
target_agent:         "CTO"
deadline_seconds:     7200    # 2 hours
grace_period_secs:    600
hard_overdue_secs:    14400
initial_severity:     "SOFT"
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "review_complete"
verification_method:  "event_received"
verification_target:  null
enabled:              true
deduplicate:          true
deny_closure_on_open: false
```

**Rationale:** Implements "Content must be technically accurate (CTO reviews before publish)" from AGENTS.md.

---

### Trigger 10: P0 Bug Fix Obligation

```yaml
trigger_id:           "p0_bug_fix"
trigger_tool_pattern: "github_issue_labeled|blocker_detected"
trigger_param_filter:
  priority:           "P0"
  label_contains:     ["P0", "critical", "production-broken"]
obligation_type:      "p0_fix_required"
description:          "P0 bugs must be fixed within 5 minutes"
target_agent:         "CTO"
deadline_seconds:     300     # 5 minutes (from AGENTS.md)
grace_period_secs:    30
hard_overdue_secs:    300     # Immediate hard overdue
initial_severity:     "HARD"  # Start at HARD for P0
escalate_to_hard:     true
escalate_to_actor:    "CEO"
fulfillment_event:    "bug_fix_merged"
verification_method:  "event_received"
verification_target:  null
enabled:              true
deduplicate:          true
deny_closure_on_open: true    # Cannot do other work with P0 pending
```

**Rationale:** Machine-enforces AGENTS.md Operating Principle #6: "P0 blockers block everything."

---

## Implementation Scope

### 1. Y*gov Core Changes (`ystar/` source)

#### New Files:
```
ystar/
  governance/
    obligation_trigger.py      # ObligationTrigger dataclass
    trigger_registry.py        # TriggerRegistry management
    trigger_matcher.py         # Match tool calls to triggers
```

#### Modified Files:
```
ystar/
  adapters/
    hook.py                    # Add trigger matching after check()
  governance/
    omission_engine.py         # Add trigger-specific event handling
    omission_rules.py          # Add tool-trigger rule type
  domains/
    openclaw/
      accountability_pack.py   # Add trigger configurations
```

#### Key Integration Points:

**hook.py changes:**
```python
def check_hook(hook_payload, policy, agent_id=None):
    # ... existing check logic ...
    result = policy.check(who, tool_name, **params)

    if result.allowed:
        # NEW: Trigger obligation creation
        _process_obligation_triggers(tool_name, params, who, session_id)

    return _result_to_response(result)


def _process_obligation_triggers(tool_name, params, agent_id, session_id):
    """Check for and create any triggered obligations."""
    from ystar.governance.trigger_registry import get_trigger_registry
    from ystar.governance.trigger_matcher import match_triggers

    registry = get_trigger_registry()
    if registry is None:
        return

    triggers = match_triggers(registry, tool_name, params, agent_id)
    for trigger in triggers:
        _create_obligation_from_trigger(trigger, agent_id, session_id, params)
```

**omission_engine.py changes:**
```python
# Add new event type handling in _trigger_obligations
def _trigger_obligations(self, ev: GovernanceEvent) -> List[ObligationRecord]:
    # ... existing code ...

    # NEW: Handle tool-trigger events
    if ev.event_type.startswith("tool_trigger:"):
        trigger_id = ev.event_type.split(":")[1]
        return self._create_triggered_obligation(ev, trigger_id)
```

**omission_rules.py changes:**
```python
# Add dynamic rule creation from triggers
class RuleRegistry:
    def register_trigger_rule(self, trigger: "ObligationTrigger") -> None:
        """Create an OmissionRule from an ObligationTrigger."""
        rule = OmissionRule(
            rule_id              = f"trigger_{trigger.trigger_id}",
            name                 = trigger.description,
            description          = trigger.description,
            trigger_event_types  = [f"tool_trigger:{trigger.trigger_id}"],
            actor_selector       = _select_trigger_target(trigger),
            obligation_type      = trigger.obligation_type,
            required_event_types = [trigger.fulfillment_event],
            due_within_secs      = trigger.deadline_seconds,
            grace_period_secs    = trigger.grace_period_secs,
            hard_overdue_secs    = trigger.hard_overdue_secs,
            severity             = Severity.MEDIUM if trigger.initial_severity == "SOFT" else Severity.HIGH,
        )
        self.register(rule)
```

### 2. AGENTS.md Changes

Add new section for trigger definitions:

```markdown
## Obligation Triggers (Y*gov Enforced)

The following triggers automatically create obligations when tool calls occur:

| ID | Tool Pattern | Obligation | Target | Deadline | Fulfillment |
|----|--------------|------------|--------|----------|-------------|
| research_knowledge_update | web_search, WebSearch | knowledge_update | caller | 30m | file:knowledge/{role}/ |
| session_token_recording | session_end | token_recording | CFO | 10m | cmd:track_burn.py |
| bootstrap_log_update | Write(knowledge/) | bootstrap_log | caller | 5m | file:bootstrap_log.md |
| cto_fix_log_update | Write(ystar/) | fix_log | CTO | 5m | file:cto_fix_log.md |
| subagent_completion_report | task_complete | orchestrator_report | caller | 2m | event:upstream_notify |
| user_conversation_doc | external_api | conversation_doc | CSO | 24h | file:sales/feedback/ |
| failure_case_documentation | CIEU:DENY | case_doc | caller | 1h | file:knowledge/cases/ |
| github_issue_triage | github_issue_created | issue_triage | CTO | 15m | event:issue_labeled |
| content_accuracy_review | Write(content/) | cto_review | CTO | 2h | event:review_complete |
| p0_bug_fix | P0 labeled | p0_fix | CTO | 5m | event:bug_fix_merged |

These triggers are machine-enforced. Violations are recorded to CIEU.
```

### 3. Agent Definition Files (`.claude/agents/`)

Each agent needs awareness of their obligations:

```markdown
# Add to each agent definition

## Your Triggered Obligations

When you perform certain actions, Y*gov automatically creates obligations you must fulfill:

- After `web_search`: Update `knowledge/{your_role}/` within 30 minutes
- After writing to `knowledge/`: Update `bootstrap_log.md` within 5 minutes
- [Agent-specific obligations from trigger catalog]

If you fail to fulfill these obligations:
1. SOFT warning after deadline
2. HARD violation after 2x deadline (may block unrelated work)
3. Recorded to CIEU for audit
```

### 4. Configuration Location Options

**Option A: In AGENTS.md (Recommended)**
- Pros: Single source of truth, human-readable, version controlled
- Cons: Requires AGENTS.md parser changes

**Option B: Separate YAML file**
- Pros: Clean separation, easier to parse
- Cons: Two files to maintain, risk of drift

**Option C: In .ystar_session.json**
- Pros: Runtime configuration, per-session customization
- Cons: Transient, not auditable

**Recommendation:** Option A with Option B fallback. Triggers defined in AGENTS.md are authoritative; a `.ystar_triggers.yaml` file can provide defaults when AGENTS.md doesn't specify.

---

## Backward Compatibility

### Zero-Breaking-Change Guarantee

1. **Opt-in by default:** Triggers are only active if explicitly configured
2. **No triggers = no change:** Systems without trigger definitions work exactly as before
3. **Graceful degradation:** If trigger subsystem fails, `check()` still works
4. **Existing obligations preserved:** Current OmissionRule definitions continue to work

### Migration Path

**Phase 1: Soft Introduction**
- Add trigger framework as optional feature
- No triggers registered by default
- Document feature in release notes

**Phase 2: Default Triggers for Y* Bridge Labs**
- Enable all 10 triggers in AGENTS.md
- Monitor for false positives
- Tune deadlines based on real usage

**Phase 3: Domain Pack Integration**
- Add `apply_triggers()` to accountability packs
- Provide trigger templates for common patterns
- Enable per-deployment customization

### Version Strategy

```
v0.42.0: Add ObligationTrigger infrastructure (no default triggers)
v0.43.0: Add TriggerRegistry and hook integration
v0.44.0: Add 10 standard triggers for Y* Bridge Labs
v0.45.0: Stabilize and document for general use
```

---

## Risks

### Risk 1: False Positive Overload
**Description:** Triggers fire too often, creating obligation noise
**Mitigation:**
- Start with long deadlines, tighten gradually
- Deduplicate same-type obligations
- Provide per-agent disable controls

### Risk 2: Deadline Misconfiguration
**Description:** Unrealistic deadlines cause constant violations
**Mitigation:**
- Use AGENTS.md SLAs as baseline
- Require Board approval for deadlines < 5 minutes
- Log deadline statistics for tuning

### Risk 3: Verification Brittleness
**Description:** File modification checks fail due to path variations
**Mitigation:**
- Use glob patterns, not exact paths
- Support multiple verification methods
- Fall back to manual fulfillment events

### Risk 4: Performance Impact
**Description:** Trigger matching on every tool call adds latency
**Mitigation:**
- Pre-compile regex patterns
- Use tool-name index for fast filtering
- Cache trigger registry

### Risk 5: Circular Trigger Chains
**Description:** Trigger A creates obligation B which triggers C which triggers A
**Mitigation:**
- Track trigger chain depth
- Hard limit: 3 levels of nested triggers
- Warn on circular definitions

---

## Recommended Implementation Order

### Sprint 1 (Week 1): Foundation
1. Create `ObligationTrigger` dataclass
2. Create `TriggerRegistry` class
3. Add `trigger_matcher.py` with basic pattern matching
4. Unit tests for all new components

### Sprint 2 (Week 2): Integration
5. Modify `hook.py` to call trigger matcher
6. Connect triggers to `OmissionEngine`
7. Add fulfillment verification methods
8. Integration tests with mock tool calls

### Sprint 3 (Week 3): Y* Bridge Labs Deployment
9. Define all 10 triggers in AGENTS.md
10. Deploy to Y* Bridge Labs operations
11. Monitor for first 48 hours
12. Tune deadlines based on real data

### Sprint 4 (Week 4): Stabilization
13. Fix issues from production usage
14. Document trigger authoring guide
15. Add trigger metrics to `ystar report`
16. Prepare for general release

---

## Estimated Effort

| Component | Estimated Hours | Assignee |
|-----------|-----------------|----------|
| ObligationTrigger dataclass | 2h | CTO |
| TriggerRegistry | 4h | CTO |
| trigger_matcher.py | 6h | CTO |
| hook.py integration | 4h | CTO |
| OmissionEngine changes | 4h | CTO |
| Verification methods | 8h | CTO |
| AGENTS.md parser changes | 6h | CTO |
| 10 trigger definitions | 4h | CEO/CTO |
| Unit tests | 8h | CTO |
| Integration tests | 8h | CTO |
| Documentation | 4h | CMO |
| **Total** | **58h** | - |

**Timeline:** 2-3 weeks of CTO focus time

---

## Board Decision Required

Before CTO begins implementation, the Board must approve:

### 1. Architectural Approval
- [ ] Approve the ObligationTrigger framework design
- [ ] Approve integration point (hook.py after check())
- [ ] Approve trigger configuration location (AGENTS.md)

### 2. Specific Trigger Approval
- [ ] Approve all 10 triggers in the catalog
- [ ] Approve deadline values for each trigger
- [ ] Approve severity levels (SOFT vs HARD start)

### 3. Resource Allocation
- [ ] Approve CTO time allocation (~58h over 2-3 weeks)
- [ ] Approve P0 priority for this work
- [ ] Defer other CTO work during implementation

### 4. Rollout Strategy
- [ ] Approve phased rollout (soft introduction first)
- [ ] Approve Y* Bridge Labs as first deployment
- [ ] Approve monitoring period before general release

---

## Conclusion

The ObligationTrigger framework closes the most significant governance gap in Y*gov: consequent obligations. By automatically creating trackable obligations when certain tool calls occur, we can finally govern not just what agents DO, but what they SHOULD do afterward.

This is not a nice-to-have feature. The CMO case (19 web_searches, 0 knowledge updates) demonstrates that without this framework, a significant class of agent behaviors remains completely ungoverned.

**Recommendation:** Approve this proposal and authorize CTO to begin Sprint 1 immediately.

---

**Submitted by:** CEO Agent
**Date:** 2026-03-26
**Status:** AWAITING BOARD DECISION
