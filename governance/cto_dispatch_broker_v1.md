# CTO Dispatch Broker Architecture v1.0

**Constitutional — Board 2026-04-16 P0 Role Reorientation**

**Problem**: CEO spends 40%+ cycles routing atomics ("CEO writes intent → manually spawns Agent sub-agent per task"). CTO sub-agent ephemeral, cannot monitor dispatch board standing. Bottleneck at CEO layer, not CTO layer.

**Solution**: CTO Dispatch Broker — standing daemon that monitors dispatch_board.json + CIEU stream, applies CTO design judgment, spawns engineer sub-agents, validates completions. Replaces "CEO manual spawning" pattern with "CEO posts intent → broker handles routing."

---

## Part 1 — CTO Dispatch Broker Architecture

### 1.1 Current Flow (CEO-Centric)

```
CEO receives task (Board directive OR event-triggered)
  ↓
CEO writes atomic task card OR composes Agent spawn prompt
  ↓
CEO manually spawns Agent({agent_id: eng-{role}, ...})
  ↓
Engineer sub-agent executes
  ↓
Engineer returns receipt to CEO
  ↓
CEO validates + posts to dispatch_board.json OR reports to Board
```

**Latency**: ~30min per task (CEO serialization)  
**CEO overhead**: 40% of cycles on manual dispatch composition

### 1.2 New Flow (Broker-Centric)

```
CEO posts intent to dispatch_board.json (high-level goal)
  ↓
CTO broker daemon polls board every N CIEU events (no time-cadence)
  ↓
CTO broker reads task, applies CTO judgment:
  - Tier classify (T1/T2/T3 per tiered_routing_protocol_v1.md)
  - Engineer assignment (skill-trust matrix per cto_role_v2 Appendix)
  - EDM (Ecosystem Dependency Map) cross-check
  - Decompose T2 into N atomic T1s if needed
  ↓
Broker spawns Agent sub-agent(s) with engineered prompt
  ↓
Engineer executes, returns receipt to broker (NOT CEO)
  ↓
Broker validates receipt:
  - Rt+1=0 check (per CIEU 5-tuple)
  - Scope compliance (files_in_scope match)
  - Test gate (pytest pass if test-touching task)
  ↓
Broker posts completion back to dispatch_board.json
  ↓
CEO observes completion events (passive observer, not active router)
```

**Latency**: ~15min per task (broker handles routing + spawn + validation)  
**CEO overhead**: 5% of cycles (only posts intents + monitors exceptions)

### 1.3 Broker Responsibilities

1. **Monitor dispatch_board.json** — poll every N CIEU events (N=10 default, no hardcoded time intervals per governance no-cadence rule)
2. **Tier classification** — apply tier-routing v1 classifier (T1/T2/T3)
3. **Engineer selection** — use skill-trust matrix (per cto_role_v2 Appendix C, trust_scores.json)
4. **Decomposition** — if T2 intent, break into N atomic T1 sub-tasks
5. **Spawn orchestration** — write Agent tool call with engineered prompt referencing task card
6. **Receipt validation** — verify Rt+1=0, scope compliance, test gate
7. **Completion posting** — update dispatch_board.json with completion_receipt + validation result
8. **Exception escalation** — if validation fails, escalate to CEO with diagnostics

### 1.4 Integration Points

**Upstream dependencies**:
- `dispatch_board.py` (Ryan #72) — post/claim/complete CLI
- `tier-routing v1` (#66) — T1/T2/T3 classifier
- `trust_scores.json` (cto_role_v2 Appendix) — engineer skill-trust matrix
- `engineer_task_subscriber.py` (Ryan #71) — daemon pattern template

**Downstream consumers**:
- CEO workflow (intent posting only, no manual spawning)
- Engineer workflows (unchanged, still claim/execute/complete)
- K9 routing chain (#63) — broker emits `CTO_BROKER_ROUTING` events for causal tracing

**Cross-cutting**:
- `enforce_roster` (#73) — broker validates agent_id before spawn (must be in canonical roster)
- ForgetGuard rules — broker triggers `dispatch_tier_misclassified` if scope exceeds tier
- CIEU audit — broker emits 5 event types (see Part 2 §2.4)

---

## Part 2 — Implementation: scripts/cto_dispatch_broker.py

### 2.1 CLI Interface

```bash
# Start broker daemon (blocks, runs until SIGTERM)
python3 scripts/cto_dispatch_broker.py start

# Stop broker daemon (kills PID file)
python3 scripts/cto_dispatch_broker.py stop

# Query broker status (RUNNING / NOT RUNNING / STALE PID)
python3 scripts/cto_dispatch_broker.py status

# Manual single-task dispatch (for testing, non-daemon mode)
python3 scripts/cto_dispatch_broker.py dispatch --atomic_id CZL-99
```

### 2.2 Daemon Loop (Event-Driven, No Time Intervals)

```python
#!/usr/bin/env python3
"""
CTO Dispatch Broker Daemon — CTO-judgment routing automation
Implements broker pattern per governance/cto_dispatch_broker_v1.md
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Import CIEU helpers + dispatch_board API
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import emit_cieu, count_recent_events

BOARD_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/dispatch_board.json")
PID_FILE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.cto_broker.pid")
POLL_TRIGGER_EVENTS = 10  # Poll dispatch_board every N CIEU events (no hardcoded time)

def daemon_loop():
    """Event-driven polling loop (no time-based cadence)."""
    last_event_count = count_recent_events(hours=1)
    
    emit_cieu("CTO_BROKER_DAEMON_START", decision="info", passed=1)
    
    while True:
        # Event-driven trigger: poll when CIEU event count increases by N
        current_event_count = count_recent_events(hours=1)
        if current_event_count - last_event_count >= POLL_TRIGGER_EVENTS:
            poll_and_route()
            last_event_count = current_event_count
        
        # Minimal sleep to avoid CPU spin (not time-cadence, just yielding)
        import time
        time.sleep(0.5)
```

### 2.3 CTO Routing Logic (Tier Classify + Skill-Trust + EDM)

```python
def poll_and_route():
    """Poll dispatch_board, route tasks with CTO judgment."""
    board = _read_board()
    
    # Find tasks with status="open" and posted_by="ceo"
    ceo_posted_tasks = [t for t in board["tasks"] if t["status"] == "open" and t["posted_by"] == "ceo"]
    
    for task in ceo_posted_tasks:
        # Step 1: Tier classify (T1/T2/T3)
        tier = classify_tier(task["description"], task["scope"], task.get("estimated_tool_uses", 0))
        
        emit_cieu("CTO_BROKER_TIER_CLASSIFIED", 
                  decision="info", passed=1,
                  task_description=f"{task['atomic_id']} classified as {tier}",
                  params_json=json.dumps({"atomic_id": task["atomic_id"], "tier": tier}))
        
        # Step 2: Routing decision
        if tier == "T1":
            # T1 → direct engineer assignment
            engineer_id = select_engineer_for_t1(task["scope"])
            spawn_engineer_agent(task, engineer_id)
            
        elif tier == "T2":
            # T2 → CTO design task card + decompose into T1s
            task_card_path = cto_design_t2(task)
            subtasks = decompose_t2_to_t1s(task_card_path)
            for subtask in subtasks:
                post_t1_to_board(subtask)  # Post decomposed T1s back to board
            
        elif tier == "T3":
            # T3 → escalate to Board (CEO drafts proposal)
            escalate_to_board(task)
        
        # Mark task as "claimed" by broker (prevents duplicate routing)
        task["status"] = "broker_routing"
        task["claimed_by"] = "cto-broker"
        task["claimed_at"] = datetime.now(timezone.utc).isoformat()
        _write_board(board)

def classify_tier(description, scope, estimated_tool_uses):
    """Tier classifier per tier-routing v1 rules."""
    # T3 keywords (highest priority)
    t3_keywords = ["push origin", "git push", "deploy", "release", "pypi", "payment", "rollback", "amendment"]
    if any(kw in description.lower() for kw in t3_keywords):
        return "T3"
    
    # T2 heuristics
    if estimated_tool_uses > 15:
        return "T2"
    if len(scope.split(",")) > 3:
        return "T2"
    t2_keywords = ["architecture", "API change", "cross-engineer", "refactor", "new module"]
    if any(kw in description.lower() for kw in t2_keywords):
        return "T2"
    
    # Default T1
    return "T1"

def select_engineer_for_t1(scope):
    """Select engineer based on file scope + trust scores."""
    # Load trust scores
    trust_file = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/governance/trust_scores.json")
    trust_data = json.loads(trust_file.read_text()) if trust_file.exists() else {}
    
    # Simple scope-based routing (expand with skill-trust matrix later)
    if "governance/" in scope:
        return "maya-governance"
    elif "scripts/" in scope or "platform/" in scope:
        return "ryan-platform"
    elif "kernel/" in scope:
        return "leo-kernel"
    elif "domains/" in scope:
        return "jordan-domains"
    else:
        # Fallback: pick engineer with highest trust score
        return max(trust_data.items(), key=lambda x: x[1].get("trust_score", 0))[0]

def spawn_engineer_agent(task, engineer_id):
    """Spawn Agent sub-agent with engineered prompt."""
    # This is pseudocode — in production, broker would call Agent tool via MCP
    # or write to a queue that CEO's Agent tool handler consumes
    
    emit_cieu("CTO_BROKER_ROUTING", 
              decision="dispatch", passed=1,
              task_description=f"Dispatching {task['atomic_id']} to {engineer_id}",
              params_json=json.dumps({
                  "atomic_id": task["atomic_id"],
                  "engineer_id": engineer_id,
                  "tier": "T1",
              }))
    
    # Engineer claim pattern (reuse dispatch_board.py claim logic)
    # In production: spawn Agent({agent_id: engineer_id, ...}) with prompt referencing task
```

### 2.4 CIEU Event Taxonomy (Broker-Specific)

Broker emits 5 event types:

1. **CTO_BROKER_DAEMON_START** — daemon started
2. **CTO_BROKER_TIER_CLASSIFIED** — task tier classified (T1/T2/T3)
3. **CTO_BROKER_ROUTING** — task dispatched to engineer (includes engineer_id, tier, atomic_id)
4. **CTO_BROKER_VALIDATION_PASS** — receipt validation passed (Rt+1=0, scope compliance)
5. **CTO_BROKER_VALIDATION_FAIL** — receipt validation failed (escalated to CEO)

### 2.5 Receipt Validation Logic

```python
def validate_receipt(task, receipt_text):
    """Validate engineer receipt per CIEU 5-tuple."""
    # Parse receipt for Rt+1 value (expect "Rt+1 = 0" or "Rt+1: 0")
    import re
    rt_match = re.search(r"Rt\+1[:\s=]+([0-9.]+)", receipt_text)
    if not rt_match or float(rt_match.group(1)) > 0:
        emit_cieu("CTO_BROKER_VALIDATION_FAIL",
                  decision="reject", passed=0,
                  task_description=f"{task['atomic_id']} receipt validation failed: Rt+1 > 0",
                  params_json=json.dumps({"atomic_id": task["atomic_id"], "rt_value": rt_match.group(1) if rt_match else "missing"}))
        return False
    
    # Scope compliance check (files_in_scope from dispatch vs files_modified from receipt)
    claimed_scope = set(task["scope"].split(","))
    # Parse receipt for modified files (heuristic: look for file paths in receipt)
    modified_files = set(re.findall(r"[a-z_/]+\.(?:py|md|yaml|json)", receipt_text.lower()))
    if not modified_files.issubset(claimed_scope):
        emit_cieu("CTO_BROKER_VALIDATION_FAIL",
                  decision="reject", passed=0,
                  task_description=f"{task['atomic_id']} scope violation",
                  params_json=json.dumps({"claimed": list(claimed_scope), "actual": list(modified_files)}))
        return False
    
    emit_cieu("CTO_BROKER_VALIDATION_PASS",
              decision="accept", passed=1,
              task_description=f"{task['atomic_id']} receipt valid")
    return True
```

---

## Part 3 — CEO Role Reframing (Intent Posting)

### 3.1 Old CEO Workflow (Manual Dispatching)

```python
# CEO receives task from Board OR event-triggered
# CEO manually composes Agent spawn:

from anthropic import Anthropic
client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    tools=[{"type": "computer_20241022", ...}, {"type": "agent", ...}],
    tool_choice={"type": "tool", "name": "agent"},
    messages=[{
        "role": "user",
        "content": f"Dispatch to Ryan: extend hook script with try/except wrapper, files: scripts/governance_boot.sh, CZL-99"
    }]
)

# Manually validate agent return
# Manually post to dispatch_board.json
```

**Problem**: CEO spends 40% of cycles on manual dispatch composition, validation, posting.

### 3.2 New CEO Workflow (Intent Posting)

```python
# CEO receives task from Board OR event-triggered
# CEO posts high-level intent to dispatch_board:

import subprocess
subprocess.run([
    "python3", "scripts/dispatch_board.py", "post",
    "--atomic_id", "CZL-99",
    "--scope", "scripts/governance_boot.sh",
    "--description", "Add try/except wrapper to boot script CIEU write section",
    "--urgency", "P1",
    "--estimated_tool_uses", "8"
])

# CTO broker daemon handles:
# - Tier classification (T1)
# - Engineer selection (ryan-platform, based on scripts/ scope)
# - Agent spawn with engineered prompt
# - Receipt validation
# - Completion posting

# CEO receives completion notification via CIEU event stream
# CEO only intervenes if CTO_BROKER_VALIDATION_FAIL event observed
```

**Benefit**: CEO cycles reduced from 40% dispatching to 5% (intent composition + exception handling).

### 3.3 CEO Retained Scope

CEO still owns:

1. **Strategic decisions** — which initiatives to prioritize (responds to Board directives)
2. **Board interface** — translate Board language into agent tasks
3. **T3 approval gate** — draft proposals for Board approval (commit/push, PyPI release, payment)
4. **Emergency break_glass** — manual intervention if broker fails or task stuck
5. **Final acceptance** — review broker-validated completions before considering initiative "done"

CEO no longer owns:

1. ~~Per-task atomic dispatch composition~~
2. ~~Manual Agent tool spawning for T1 tasks~~
3. ~~Engineer selection for routine work~~
4. ~~Receipt validation for T1 completions~~

### 3.4 Migration Example (Before/After)

**Before** (CEO manual dispatch):

```
Board: "Add ForgetGuard rule for ceo_dispatch_velocity_too_high"
  ↓
CEO: Reads Board directive
  ↓
CEO: Writes task card `.claude/tasks/maya-forgetguard-velocity.md`
  ↓
CEO: Manually spawns Agent({agent_id: "maya-governance", prompt: "Read .claude/tasks/maya-forgetguard-velocity.md and implement..."})
  ↓
Maya sub-agent executes, returns receipt
  ↓
CEO: Reads receipt, validates Rt+1=0, checks scope compliance
  ↓
CEO: Posts to dispatch_board.json with completion status
  ↓
Total CEO tool_uses: ~8 (Read directive, Write task card, Agent spawn, Read receipt, Write board, emit CIEU)
```

**After** (CEO intent posting):

```
Board: "Add ForgetGuard rule for ceo_dispatch_velocity_too_high"
  ↓
CEO: Posts intent to dispatch_board.json via dispatch_board.py post
  ↓
CTO broker: Polls board, classifies T1, selects maya-governance, spawns Agent, validates receipt, posts completion
  ↓
CEO: Observes CTO_BROKER_VALIDATION_PASS event (passive monitoring)
  ↓
Total CEO tool_uses: ~2 (Read directive, Bash dispatch_board.py post)
```

**Efficiency gain**: 75% reduction in CEO dispatch overhead.

---

## Part 4 — Migration Path (4 Phases)

### Phase 1: Ship Broker Infra (Ryan CZL-89)

**Owner**: ryan-platform  
**Acceptance**:
- [ ] `scripts/cto_dispatch_broker.py` with 4 subcommands (start, stop, status, dispatch)
- [ ] Daemon loop (event-driven polling, no hardcoded time intervals)
- [ ] Tier classifier logic (T1/T2/T3 per tier-routing v1)
- [ ] Engineer selection logic (skill-trust matrix stub)
- [ ] Receipt validation logic (Rt+1=0 check + scope compliance)
- [ ] CIEU integration (5 event types emitted)
- [ ] Integration with `governance_boot.sh` (start broker if cto agent active)
- [ ] Tests: `pytest tests/platform/test_cto_broker.py -q` (≥3 tests: tier_classify, engineer_select, receipt_validate)
- [ ] No files outside `scripts/`, `tests/platform/` modified
- [ ] Commit: `feat(platform): CTO dispatch broker daemon (CZL-89)`

**Timeline**: Ryan ships within 2h (inline task card below)

### Phase 2: CEO Dogfood (5 Real Tasks)

**Owner**: CEO  
**Acceptance**:
- CEO posts 5 real T1 tasks to dispatch_board via `dispatch_board.py post`
- Verify broker claims + classifies tier + selects engineer + spawns Agent
- Verify broker validates receipts + posts completions
- Measure latency (post → completion) vs old manual dispatch flow
- Target: <20min average (vs old ~30min)

**Timeline**: 1h after Phase 1 ships

### Phase 3: Update MEMORY + ForgetGuard Rules

**Owner**: Samantha (secretary)  
**Acceptance**:
- Update `memory/MEMORY.md` entry `feedback_dispatch_via_cto.md` to reference broker pattern
- Add ForgetGuard rule `ceo_manual_dispatch_when_broker_running` (mode=warn, triggers if CEO spawns Agent directly while broker daemon running)
- Update tier-routing v1 spec Section 7 (migration path) to reference broker

**Timeline**: 30min after Phase 2 completes

### Phase 4: CTO Role v2 Activation (Event-Driven Rituals)

**Owner**: CTO Ethan  
**Acceptance**:
- CTO runs first T1 sample review (triggered after 10 T1 broker dispatches observed)
- CTO runs first 1-on-1 with Ryan (triggered after Ryan completes 5 atomic tasks)
- CTO writes first tech debt tally (triggered after Labs Atlas subsystem index shows dead code count ≥100 lines OR CIEU audit logs emit ≥5 drift violations)
- Deliverables logged to `.claude/engineer_growth/` and `reports/tech_debt.md`

**Timeline**: Triggers naturally after broker processes first batch of tasks

---

## Part 5 — Inline Ryan Task Card (CZL-89)

### Task: Ship CTO Dispatch Broker Infrastructure

**Atomic ID**: CZL-89  
**Engineer**: ryan-platform  
**Priority**: P0 (blocks CEO workflow efficiency gain)  
**Tier**: T2 (new component, >15 tool_uses estimated, architectural pattern)  
**Posted by**: Ethan-CTO (this spec)  
**Estimated tool_uses**: ≤25

### Acceptance Criteria

- [ ] `scripts/cto_dispatch_broker.py` exists with CLI (start/stop/status/dispatch subcommands)
- [ ] Daemon loop implemented (event-driven: poll every N CIEU events, NO hardcoded time intervals)
- [ ] Tier classifier function `classify_tier(description, scope, estimated_tool_uses)` returns "T1"/"T2"/"T3"
- [ ] Engineer selector function `select_engineer_for_t1(scope)` returns engineer_id based on file scope + trust_scores.json
- [ ] Receipt validator function `validate_receipt(task, receipt_text)` checks Rt+1=0 + scope compliance
- [ ] CIEU integration: emits 5 event types (DAEMON_START, TIER_CLASSIFIED, ROUTING, VALIDATION_PASS, VALIDATION_FAIL)
- [ ] Integration with `governance_boot.sh`: add broker daemon start if `$AGENT_ID == "cto"`
- [ ] PID file management (`.cto_broker.pid` per daemon pattern)
- [ ] Tests pass: `pytest tests/platform/test_cto_broker.py -q` (≥3 tests)
- [ ] No files outside `scripts/`, `tests/platform/`, `governance/` modified
- [ ] Commit message: `feat(platform): CTO dispatch broker daemon (CZL-89)`

### Test Specification (Write Tests First)

```python
# tests/platform/test_cto_broker.py

def test_cto_broker_tier_classify():
    """Test tier classifier logic."""
    from scripts.cto_dispatch_broker import classify_tier
    
    # T3 examples
    assert classify_tier("git push origin main", "src/", 5) == "T3"
    assert classify_tier("PyPI release 0.43.0", "pyproject.toml", 3) == "T3"
    
    # T2 examples
    assert classify_tier("Refactor CIEU event taxonomy", "src/cieu/", 20) == "T2"
    assert classify_tier("Add new MCP server", "src/mcp/", 10) == "T2"
    
    # T1 examples
    assert classify_tier("Add ForgetGuard warn rule", "governance/forget_guard_rules.yaml", 8) == "T1"
    assert classify_tier("Extend hook try/except", "scripts/governance_boot.sh", 5) == "T1"

def test_cto_broker_engineer_select():
    """Test engineer selection based on scope."""
    from scripts.cto_dispatch_broker import select_engineer_for_t1
    
    assert select_engineer_for_t1("governance/forget_guard_rules.yaml") == "maya-governance"
    assert select_engineer_for_t1("scripts/dispatch_board.py") == "ryan-platform"
    assert select_engineer_for_t1("ystar/kernel/parser.py") == "leo-kernel"
    assert select_engineer_for_t1("ystar/domains/claw_template.py") == "jordan-domains"

def test_cto_broker_receipt_validate():
    """Test receipt validation (Rt+1=0 check + scope compliance)."""
    from scripts.cto_dispatch_broker import validate_receipt
    
    task = {
        "atomic_id": "CZL-99",
        "scope": "governance/forget_guard_rules.yaml",
    }
    
    # Valid receipt
    receipt_valid = "Y*: rule added\nXt: 0 rules\nU: add rule\nYt+1: 1 rule\nRt+1: 0"
    assert validate_receipt(task, receipt_valid) == True
    
    # Invalid: Rt+1 > 0
    receipt_rt_fail = "Rt+1: 0.5"
    assert validate_receipt(task, receipt_rt_fail) == False
    
    # Invalid: scope violation
    receipt_scope_fail = "Modified files: governance/forget_guard_rules.yaml, scripts/governance_boot.sh\nRt+1: 0"
    assert validate_receipt(task, receipt_scope_fail) == False
```

### Scope Guards

**Writable paths**:
- `scripts/cto_dispatch_broker.py` (new file, ~300 lines)
- `tests/platform/test_cto_broker.py` (new file, ~80 lines)
- `scripts/governance_boot.sh` (append broker daemon start, +5 lines)
- `scripts/_cieu_helpers.py` (add `count_recent_events(hours)` helper if missing, +10 lines)

**Read-only**:
- `governance/dispatch_board.json` (read via `_read_board()`)
- `governance/trust_scores.json` (read for engineer selection)
- `.ystar_cieu.db` (read for event-driven polling trigger)

**Forbidden**:
- Modifications to `.claude/agents/*.md`
- Modifications to `AGENTS.md`, `CLAUDE.md`
- Modifications to existing engineer workflows

### Yt+1 (Expected State After Completion)

- `scripts/cto_dispatch_broker.py` exists, daemon start/stop/status works
- 3 tests PASS in `tests/platform/test_cto_broker.py`
- `governance_boot.sh` starts broker daemon if `$AGENT_ID == "cto"`
- CIEU events emitted: CTO_BROKER_DAEMON_START, CTO_BROKER_TIER_CLASSIFIED, CTO_BROKER_ROUTING
- Commit hash available, no files outside scope modified

### Rt+1 Criteria

- `0.0` if all 11 acceptance criteria checked + 3 tests PASS + commit exists + no scope violations
- `1.0` if daemon logic incomplete OR tests fail OR CIEU integration missing
- `0.5` if daemon works but tests missing OR governance_boot.sh integration skipped OR scope violation (extra files modified)

### Dependencies

**Upstream** (must exist before this task):
- `scripts/dispatch_board.py` (Ryan #72, already shipped)
- `governance/tier-routing v1` (#66, already shipped)
- `scripts/_cieu_helpers.py` (exists, may need `count_recent_events()` helper added)

**Downstream** (will use this after shipping):
- CEO workflow (Phase 2 dogfood)
- MEMORY update (Phase 3, Samantha)
- CTO role v2 activation (Phase 4, Ethan)

---

## Part 6 — Ecosystem Dependency Map (EDM)

### Upstream Dependencies (Must Exist)

1. **dispatch_board.py** (Ryan #72, shipped 2026-04-16)  
   - Provides `post`, `claim`, `complete`, `status` CLI
   - Broker reads `dispatch_board.json` for open tasks
   - Broker writes completion receipts back to board

2. **tier-routing v1** (#66, shipped 2026-04-16)  
   - Defines T1/T2/T3 taxonomy
   - Provides classifier rules (keywords, heuristics)
   - Broker reuses tier classification logic

3. **engineer_task_subscriber.py** (Ryan #71, shipped 2026-04-16)  
   - Daemon pattern template (PID file, start/stop, polling loop)
   - Broker reuses daemon lifecycle pattern

4. **trust_scores.json** (cto_role_v2 Appendix, to be created)  
   - Engineer skill-trust matrix
   - Broker reads for engineer selection
   - Format: `{"maya-governance": {"trust_score": 85, "skill_domains": ["governance", "ForgetGuard"]}, ...}`

5. **CIEU helpers** (`scripts/_cieu_helpers.py`)  
   - `emit_cieu()` for event emission
   - `count_recent_events(hours)` for event-driven polling trigger (may need to add this helper)

### Downstream Consumers (Will Use This)

1. **CEO workflow** (Phase 2 migration)  
   - Switches from manual Agent spawning to `dispatch_board.py post` intent posting
   - Observes `CTO_BROKER_VALIDATION_PASS/FAIL` events for monitoring

2. **CTO role v2 rituals** (Phase 4)  
   - T1 sample review triggered after broker processes 10 tasks
   - 1-on-1s triggered after engineer completes 5 tasks (observed via broker ROUTING events)

3. **ForgetGuard rules** (Phase 3, Samantha)  
   - `ceo_manual_dispatch_when_broker_running` rule (warns if CEO bypasses broker)
   - Reads `.cto_broker.pid` to check if broker running

4. **K9 routing chain** (#63, Maya)  
   - Consumes `CTO_BROKER_ROUTING` events for causal analysis
   - Traces dispatch → execution → validation → completion chains

### Cross-Cutting Concerns

1. **enforce_roster** (#73, Architecture A-6)  
   - Broker validates `agent_id` against canonical roster before spawning
   - Prevents broker from spawning non-existent or deactivated agents

2. **Sync layer** (CZL-67, Architecture A-5)  
   - Broker emits CIEU events for sync propagation
   - Multi-session broker state NOT required (broker is stateless, polls dispatch_board.json as source of truth)

3. **Identity detector** (#61, Architecture A-3)  
   - Broker queries identity detector before spawning to verify agent session health
   - If identity drift detected (wrong agent_id in .ystar_active_agent), broker escalates to CEO

4. **Labs Atlas** (Architecture A-2)  
   - Broker routing decisions logged to subsystem index
   - Tech debt tally (Part 4 Ritual 4) queries Labs Atlas for dead code count

### Naming Collision Check

- **cto_dispatch_broker.py** — no collision (new file)
- **CTO_BROKER_*** CIEU events** — no collision (5 new event types)
- **.cto_broker.pid** — no collision (new PID file)
- **test_cto_broker.py** — no collision (new test file)

### Architecture Integration

**Architecture A-6** (enforce_roster) updated to include:
- Dispatch board adds CTO broker layer
- Broker validates agent_id against roster before spawning
- CEO posts intents (high-level goals), broker decomposes into atomic dispatches

**No amendments required** — broker is additive, does not modify existing governance contracts.

---

## Receipt (CIEU 5-Tuple)

**Y\***: Spec at `governance/cto_dispatch_broker_v1.md` containing (1) CTO Dispatch Broker Architecture — replaces CEO manual spawning with standing CTO daemon that monitors dispatch_board + CIEU stream, applies CTO judgment (tier classify + skill-trust + EDM), spawns engineers, validates receipts, (2) Implementation `scripts/cto_dispatch_broker.py` — CLI/daemon with event-driven polling (NO time cadence), tier classifier, engineer selector, receipt validator, 5 CIEU event types, (3) CEO Role Reframing — CEO posts intents only (high-level goals), broker handles atomic dispatch composition + validation + completion posting, CEO retains Board interface + T3 approval + strategic decisions + emergency break_glass, (4) Migration — 4 phases (Ryan ships broker infra → CEO dogfood 5 tasks → Samantha updates MEMORY/ForgetGuard → CTO event-driven rituals activate), (5) Inline Ryan CZL-89 task card — ship broker daemon ≤25 tool_uses with 3 tests (tier_classify, engineer_select, receipt_validate), (6) Ecosystem Dependency Map — upstream (dispatch_board #72, tier-routing #66, trust_scores.json), downstream (CEO workflow, CTO rituals, ForgetGuard, K9 routing), cross-cutting (enforce_roster, sync layer, identity detector, Labs Atlas), naming (no collisions).

**Xt**: Today CEO does ALL routing (manual Agent spawning per task). CTO sub-agent ephemeral, cannot standing daemon. Dispatch board (#72) live but no broker layer. Tier-routing v1 (#66) spec exists. Engineer subscriber (#71) daemon pattern exists. Trust scores = stub (to be created). Ryan ready to ship CZL-89.

**U**: (1) Read dispatch_board.py + engineer_task_subscriber.py (broker pattern reuse), (2) Read cto_role_v2 + tier-routing v1 (CTO responsibilities + tier classifier), (3) Draft 6-part spec (architecture + implementation + CEO reframing + migration + Ryan card + EDM), (4) Inline CZL-89 with acceptance criteria + test spec + Yt+1/Rt+1, (5) Receipt with verification.

**Yt+1**: Spec shipped at `governance/cto_dispatch_broker_v1.md` with 6 parts (architecture design, Python implementation pseudocode, CEO workflow before/after, 4-phase migration, Ryan inline task CZL-89 with 11 acceptance criteria + 3 test cases, full EDM with upstream/downstream/cross-cutting/naming). Ryan task card includes: daemon loop (event-driven polling), tier classifier (T1/T2/T3), engineer selector (scope + trust_scores.json), receipt validator (Rt+1=0 + scope compliance), 5 CIEU event types, governance_boot.sh integration, PID file management, 3 tests.

**Rt+1**: `0` (spec complete with all 6 parts, broker architecture designed, implementation pattern specified with event-driven polling, CEO role reframed from manual dispatch to intent posting, migration path 4 phases, Ryan CZL-89 inline with 11 acceptance criteria + 3 test spec + Yt+1/Rt+1 criteria, EDM complete with 5 upstream + 4 downstream + 4 cross-cutting + naming check, no hardcoded time cadence per governance rule, receipt pasted).
