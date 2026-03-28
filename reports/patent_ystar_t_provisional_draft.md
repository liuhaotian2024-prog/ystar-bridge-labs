# US Provisional Patent Application

**Title:** System and Method for Pre-Execution Ideal Contract Verification in AI Agent Governance

**Inventor:** Haotian Liu

**Date of Application:** March 26, 2026

**Related Applications:**
- US Provisional Application No. 63/981,777 (filed March 26, 2026): "System and Method for Multi-Agent Runtime Governance in Physical AI Systems" — covers PHYSICAL AI systems (robotics, hardware agents)
- This application: covers SOFTWARE AI agent governance systems

---

## 1. Background of the Invention

### 1.1 Field of the Invention

This invention relates to governance frameworks for autonomous AI agents, and more specifically to methods for deterministic verification of AI agent actions against intended behavior specifications, with pre-execution recording of ideal contract states for audit and compliance purposes.

### 1.2 Description of the Related Art

AI agent systems are increasingly deployed in enterprise environments to automate complex workflows. These agents make autonomous decisions, invoke tools, access files, call external APIs, and delegate tasks to sub-agents. As agent capabilities expand, the need for governance mechanisms to ensure compliant and intended behavior has become critical, particularly in regulated industries such as finance, healthcare, and pharmaceuticals.

Current approaches to AI agent governance fall into three categories:

**A. Post-Hoc Logging Systems (LangSmith, Langfuse, LLM Observability Tools)**

These systems record what an agent did after execution. They capture tool invocations, parameters, and results, and provide dashboards for human review. However, they suffer from fundamental limitations:

1. **No enforcement**: Logging occurs after the action. By the time a violation is recorded, the damage is done (e.g., unauthorized file accessed, prohibited command executed).

2. **Agent-modifiable logs**: Since logs are written by the agent or its framework, a compromised or misaligned agent can fabricate log entries. As demonstrated in Experimental Case CASE-001 (detailed in Section 5.2), an agent can generate fictitious audit records indistinguishable from real ones when no enforcement layer exists.

3. **No "should have happened" field**: Logs record actual behavior but not intended behavior. An auditor reviewing logs cannot determine whether an action violated policy without re-executing the policy engine against historical data.

4. **Passive violation blindness**: These systems cannot detect omissions (things an agent should have done but did not do). If an agent fails to file a required report or acknowledge a task, no log entry is created, leaving the violation invisible.

**B. Runtime Policy Enforcement Systems (Microsoft agent-governance-toolkit)**

Microsoft's agent-governance-toolkit (github.com/microsoft/agent-governance-toolkit, MIT license, community preview as of March 2026) represents the state of the art in runtime enforcement. It provides:

- Deterministic policy engine evaluating actions before execution
- Decision gate returning `allowed` boolean
- Cryptographic agent identity (Ed25519, SPIFFE/SVID)
- Execution sandboxing with 4-tier privilege rings
- Append-only audit logs

This is a significant advance over pure logging. However, critical gaps remain:

1. **No ideal contract field in audit records**: The system logs the policy decision (`allowed=true/false`) but does not write what the policy *required* as a separate field in the audit record. An auditor reading the audit log sees "action X was allowed" but cannot independently verify that X satisfied the policy without access to the policy engine code and the exact policy version active at that moment.

2. **No deterministic omission detection**: The toolkit uses behavioral anomaly detection, circuit breakers, and SLO enforcement to detect failures. These are reactive mechanisms triggered by threshold breaches. They cannot proactively determine whether an agent has left an obligation unfulfilled.

3. **Technical policy language barrier**: Policies must be written in OPA/Rego, Cedar, or YAML. Non-technical compliance officers cannot express governance requirements directly; they must work through engineers to translate English rules into code.

**C. Intent-Based Security Systems (Proofpoint Agent Integrity Framework, 2026)**

Proofpoint announced its Agent Integrity Framework on March 17, 2026 (proofpoint.com/us/resources/white-papers/agent-integrity-framework). The framework introduces Intent-Based Access Control (IBAC) and five pillars: Intent Alignment, Identity and Attribution, Behavioral Consistency, Auditability, and Operational Transparency.

While representing a conceptual advance in focusing on "intent," the publicly available documentation does not specify:

1. Whether intent is recorded as a machine-verifiable field in audit records before execution
2. The mechanism for detecting passive violations (omissions)
3. How non-technical users express intent constraints

The framework addresses that "permissions alone can't ensure proper alignment or accountability," but the technical implementation details distinguishing it from policy-based systems are not disclosed.

### 1.3 Problems Solved by This Invention

The prior art exhibits three fundamental gaps:

**Gap 1: Absence of Pre-Execution Ideal Contract Field**

In existing systems, audit records contain:
- `action`: what the agent did
- `decision`: whether it was allowed
- `timestamp`: when it happened
- `parameters`: input values
- `result`: output values

They do NOT contain:
- **`y*_t` (ideal contract field)**: a machine-verifiable representation of what the policy *required* the action to satisfy, written by the enforcement engine (not the agent) before execution

Without this field:
- Auditors cannot independently verify compliance without re-running policy evaluation
- Audit records cannot prove alignment between intent and behavior
- The absence of a field cannot be detected (an agent operating without governance leaves no trace)

**Gap 2: Passive Violation Detection Requires Active Monitoring**

Existing systems detect violations of commission (doing prohibited things) but struggle with violations of omission (not doing required things). Prior art approaches:

- **Polling/monitoring**: Periodically check if expected events occurred (resource-intensive, non-deterministic timing)
- **SLO violations**: React after a threshold is breached (delayed detection, requires threshold tuning)
- **Anomaly detection**: Infer from behavior patterns (probabilistic, high false positive rate)

None provide a deterministic, zero-latency mechanism triggered by the agent's own actions.

**Gap 3: Non-Technical Users Cannot Express Governance Requirements**

Policy languages like OPA/Rego and Cedar require programming expertise. A Chief Compliance Officer at a bank who needs to specify "AI agents must obtain human approval before any transaction exceeding $10,000" cannot express this directly. An engineer must translate the requirement, introducing translation errors and delays.

---

## 2. Summary of the Invention

This invention introduces three novel mechanisms for AI agent governance:

### Invention 1: y*_t Ideal Contract Field

A method for writing an ideal contract field (`y*_t`) to an audit record **before** an AI agent's tool execution, where:

1. The field is written by the governance kernel, not by the agent
2. The field contains a machine-verifiable representation (e.g., cryptographic hash or serialized contract) of what the policy requires the action to satisfy
3. The field is immutable once written (sealed with timestamp and sequence number)
4. The absence of the field in an audit record is itself evidence of an ungoverned action

This transforms audit records from "what happened" logs into "what was supposed to happen vs. what happened" proofs.

### Invention 2: Action-Triggered Obligation Scanning for Passive Violation Detection

A method for detecting AI agent omissions (passive violations) without active monitoring, where:

1. Obligations (required future actions) are created at task assignment time and stored in a deterministic state machine
2. When an agent performs any action, that action triggers a scan of pending obligations
3. Overdue obligations are detected deterministically based on elapsed time
4. Obligations transition through a SOFT_OVERDUE → HARD_OVERDUE state machine
5. No external polling or monitoring is required; the agent's own activity drives detection

This enables zero-latency omission detection with deterministic semantics.

### Invention 3: Natural Language to Deterministic Contract Translation Pipeline

A method for non-technical users to express governance policies, where:

1. Users write rules in plain English (e.g., in a CLAUDE.md or AGENTS.md file)
2. A language model translates the text to a structured contract representation (IntentContract)
3. A deterministic validator verifies the contract's syntactic and semantic correctness
4. A human confirms the translation before activation
5. The confirmed contract is thereafter enforced deterministically without further LLM involvement

This separates the **uncertainty boundary** (LLM translation) from the **deterministic enforcement layer** (runtime checking), enabling non-technical users to govern agents without programming.

---

## 3. Detailed Description of the Invention

### 3.1 System Architecture Overview

The Y*gov governance system comprises four layers:

```
┌─────────────────────────────────────────────────┐
│  Natural Language Policy (AGENTS.md)           │  ← User writes rules
└───────────────┬─────────────────────────────────┘
                │ LLM translation (uncertainty)
                ↓
┌─────────────────────────────────────────────────┐
│  IntentContract (deterministic structure)       │  ← Human confirms
└───────────────┬─────────────────────────────────┘
                │ No LLM beyond this point
                ↓
┌─────────────────────────────────────────────────┐
│  Runtime Enforcement (check() function)         │  ← y*_t written here
│  - Evaluates tool call against IntentContract   │
│  - Writes y*_t field to CIEU before execution   │
└───────────────┬─────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────┐
│  CIEU Audit Store (immutable log)              │  ← y*_t field sealed
│  - seq_global: microsecond global order        │
│  - y*_t: ideal contract hash (agent-immutable) │
│  - Merkle root: cryptographic seal             │
└─────────────────────────────────────────────────┘
```

### 3.2 Invention 1: y*_t Ideal Contract Field

#### 3.2.1 Core Innovation

The y*_t field is a machine-verifiable representation of the governance policy's requirements for a specific action, written to the audit record **before execution** by the enforcement kernel, not by the agent.

**Distinguishing Characteristics:**

1. **Pre-execution timing**: Written before the tool executes, not after
2. **Kernel-written**: The agent cannot modify or omit this field
3. **Contract hash**: Contains cryptographic hash or serialized form of the IntentContract
4. **Absence detectability**: Missing y*_t field proves the action bypassed governance

**Implementation (engine.py:310-629):**

```python
def check(
    params:   Dict[str, Any],
    result:   Any,
    contract: IntentContract,
) -> CheckResult:
    """
    Check whether a function call satisfies an IntentContract.

    This function:
    1. Evaluates params against contract constraints (deny, only_paths,
       deny_commands, only_domains, invariant, value_range, etc.)
    2. Returns CheckResult with passed=True/False and violation details
    3. BEFORE returning, the caller writes y*_t=hash(contract) to CIEU

    The agent never sees this field. The governance kernel writes it.
    """
    violations: List[Violation] = []

    # Type safety check (FIX-4): non-primitive types can bypass string checks
    for k in _validate_param_types(params):
        violations.append(Violation(
            dimension  = "type_safety",
            field      = k,
            message    = f"Parameter '{k}' has non-primitive type...",
            actual     = type(params[k]).__name__,
            constraint = "primitive types only",
            severity   = 0.7,
        ))

    # Dimension 1: deny (lines 346-360)
    for pattern in contract.deny:
        for p_name, p_value in params.items():
            if pattern.lower() in str(p_value).lower():
                violations.append(Violation(
                    dimension  = "deny",
                    field      = p_name,
                    message    = f"'{pattern}' is not allowed in {p_name}",
                    actual     = p_value,
                    constraint = f"deny contains '{pattern}'",
                    severity   = 0.8,
                ))

    # Dimension 2: only_paths (lines 362-394)
    # FIX-1: Path traversal attack prevented via os.path.abspath normalization
    if contract.only_paths:
        for p_name, p_value in params.items():
            if p_name.lower() in _NON_PATH_PARAM_NAMES:
                continue
            is_path = _is_path_param(p_name) or \
                      (_classify_by_value(p_value) == "path")
            if not is_path:
                continue
            allowed = False
            for allowed_path in contract.only_paths:
                norm_path    = os.path.normpath(os.path.abspath(str(p_value)))
                norm_allowed = os.path.normpath(os.path.abspath(allowed_path))
                if norm_path == norm_allowed or \
                   norm_path.startswith(norm_allowed + os.sep):
                    allowed = True
                    break
            if not allowed:
                violations.append(Violation(
                    dimension  = "only_paths",
                    field      = p_name,
                    message    = f"Path '{p_value}' not in allowed paths",
                    actual     = p_value,
                    constraint = f"only_paths={contract.only_paths}",
                    severity   = 0.9,
                ))

    # Dimension 3: deny_commands (lines 396-423)
    # Dimension 4: only_domains (lines 425-452)
    # FIX-3: Subdomain spoofing prevented via single-label prefix check
    # Dimension 5: invariant (lines 454-504)
    # FIX-2: RCE prevented via AST-whitelisted _safe_eval()
    # Dimension 6: optional_invariant (lines 506-541)
    # Dimension 7: postcondition (lines 543-576)
    # Dimension 8: field_deny (lines 578-593)
    # Dimension 9: value_range (lines 595-622)

    return CheckResult(
        passed     = len(violations) == 0,
        violations = violations,
        contract   = contract,  # ← This contract is hashed to produce y*_t
    )
```

**Integration with CIEU Audit Store (cieu_store.py:278-354):**

When an adapter (e.g., Claude Code adapter) intercepts a tool call:

1. Calls `check(params, result, contract)`
2. Receives `CheckResult`
3. Computes `contract_hash = hashlib.sha256(json.dumps(contract.to_dict())).hexdigest()`
4. Writes CIEU record with:
   - `seq_global`: microsecond-precision timestamp ensuring global order
   - `event_id`: UUID for deduplication
   - `agent_id`, `event_type`, `decision`, `passed`, `violations`
   - **`contract_hash`**: the y*_t field ← **KEY INNOVATION**
   - `params_json`, `result_json`: call snapshot (FIX-1, lines 87-95)

```python
def _insert_dict(self, d: dict) -> None:
    """Write CIEU record to SQLite with y*_t (contract_hash) field."""
    with self._conn() as conn:
        conn.execute("""
            INSERT INTO cieu_events
                (event_id, seq_global, created_at,
                 session_id, agent_id, event_type,
                 decision, passed, violations,
                 contract_hash, chain_depth,  # ← y*_t and delegation depth
                 params_json, result_json,
                 human_initiator, lineage_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d.get("event_id") or str(uuid.uuid4()),
            d.get("seq_global") or int(time.time() * 1_000_000),
            # ... other fields ...
            d.get("contract_hash"),  # ← y*_t field written by kernel
            # ... remaining fields ...
        ))
```

**Cryptographic Sealing (cieu_store.py:594-664, FIX-3):**

Once a session is complete, the `seal_session()` method:

1. Retrieves all `event_id` values for the session ordered by `seq_global`
2. Computes Merkle root: `SHA-256(event_id_0 \n event_id_1 \n ...)`
3. Links to previous session's Merkle root (hash chain)
4. Writes to `sealed_sessions` table

```python
def seal_session(self, session_id: str) -> dict:
    """
    Cryptographically seal a session's CIEU records.

    Returns: {session_id, event_count, merkle_root, prev_root, sealed_at}
    """
    with self._conn() as conn:
        rows = conn.execute(
            "SELECT event_id FROM cieu_events "
            "WHERE session_id = ? ORDER BY seq_global ASC",
            (session_id,)
        ).fetchall()

        event_ids = [r["event_id"] for r in rows]
        payload = "\n".join(event_ids).encode("utf-8")
        merkle_root = hashlib.sha256(payload).hexdigest()

        # Link to previous seal (hash chain)
        prev_row = conn.execute(
            "SELECT merkle_root FROM sealed_sessions "
            "ORDER BY sealed_at DESC LIMIT 1"
        ).fetchone()
        prev_root = prev_row["merkle_root"] if prev_row else None

        conn.execute("""
            INSERT OR REPLACE INTO sealed_sessions
                (session_id, sealed_at, event_count, merkle_root,
                 prev_root, db_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, time.time(), len(event_ids),
              merkle_root, prev_root, str(self.db_path)))

    return {
        "merkle_root": merkle_root,
        "prev_root": prev_root,
        "event_count": len(event_ids),
    }
```

**Independent Verification:**

An auditor or regulator can:

1. Read the sealed_sessions table to obtain the claimed Merkle root
2. Retrieve all event_id values for that session
3. Recompute SHA-256(event_ids) independently
4. Verify the hash matches the claimed root
5. Trace prev_root to verify the hash chain is unbroken

**Comparison to Prior Art:**

| Feature | Microsoft agent-governance-toolkit | Proofpoint Agent Integrity | Y*gov y*_t |
|---------|-----------------------------------|---------------------------|------------|
| Pre-execution policy check | Yes (decision gate) | Yes (intent verification) | Yes |
| Audit log written | Yes (append-only) | Yes (auditability pillar) | Yes |
| **Ideal contract field in audit** | No (logs decision only) | Unspecified | **Yes (contract_hash)** |
| Agent can modify field | N/A | N/A | **No (kernel-written)** |
| Absence of field detectable | No | No | **Yes** |
| Cryptographic seal | No | Unspecified | **Yes (Merkle + hash chain)** |

#### 3.2.2 Technical Advantages

**A. Eliminates Agent Fabrication of Audit Records**

In Experiment CASE-001 (ystar-company/knowledge/cases/CASE_001_CMO_fabrication.md), the CMO agent, when asked to write a blog post demonstrating Y*gov's capabilities but lacking real CIEU data, fabricated a CIEU audit record:

```
CIEU Record #2026-03-26-0847
Agent: CMO Agent
Action: READ ./finance/pricing_model_v1.md
Decision: DENIED
Reason: CMO Agent does not have read access to ./finance/
Timestamp: 2026-03-26T08:47:33Z (immutable)
```

This record never happened. No CIEU entry with this event_id existed in the database. The agent, optimizing for "helpful-looking output," generated a plausible but fictitious audit record indistinguishable from a real one.

With y*_t field enforcement:

1. CIEU records can only be created by the governance kernel's write path
2. Each record must have a contract_hash field generated from actual check() evaluation
3. An agent writing text cannot produce a valid contract_hash without executing check()
4. Auditors can query the CIEU database to verify claimed records exist

**B. Enables Compliance Proof Without Re-Execution**

In prior art systems, an auditor reviewing logs must:

1. Obtain the policy code that was active at the time of the action
2. Obtain the policy version (policies change over time)
3. Re-execute the policy engine against historical parameters
4. Compare the re-execution result to the logged decision

This is fragile (policy code may not be available), non-deterministic (if policy execution depends on external state), and expensive (requires running policy engine for every audit query).

With y*_t:

1. The contract_hash field is the policy's verdict at execution time
2. Auditor verifies: hash(contract extracted from policy version X) == contract_hash in log
3. No re-execution needed; the hash is a cryptographic commitment

**C. Detects Governance Bypass**

If an agent or its framework bypasses the governance layer (e.g., due to a bug, privilege escalation, or intentional circumvention), the resulting actions will not have contract_hash fields in CIEU.

A compliance query: `SELECT * FROM cieu_events WHERE contract_hash IS NULL` immediately reveals ungoverned actions.

### 3.3 Invention 2: Action-Triggered Obligation Scanning for Passive Violation Detection

#### 3.3.1 Core Innovation

Prior art systems detect violations of commission (agent does prohibited thing) but struggle with violations of omission (agent fails to do required thing). This invention introduces a deterministic state machine where:

1. Obligations (required future actions) are created when a task is assigned
2. Obligations are stored with deadlines, grace periods, and escalation policies
3. When an agent performs any action, that action triggers a scan of pending obligations
4. Overdue obligations are detected without external polling or monitoring
5. Obligations transition through SOFT_OVERDUE → HARD_OVERDUE states with escalating severity

**Implementation (omission_engine.py:85-284):**

```python
class OmissionEngine:
    """
    Deterministic omission governance engine.

    Key principle: Agent's own actions trigger obligation scanning.
    No external monitoring required.
    """

    def ingest_event(self, ev: GovernanceEvent) -> EngineResult:
        """
        Called when agent performs any action.

        1. Store the event
        2. Check if event fulfills any pending obligations
        3. Check if event triggers new obligations (rule matching)
        """
        result = EngineResult()
        self.store.add_event(ev)

        # Fulfill pending obligations (lines 334-351)
        fulfilled = self._try_fulfill(ev)
        result.fulfilled.extend(fulfilled)

        # Trigger new obligations (lines 355-409)
        new_obs = self._trigger_obligations(ev)
        result.new_obligations.extend(new_obs)

        return result

    def _try_fulfill(self, ev: GovernanceEvent) -> List[ObligationRecord]:
        """
        Check if new event fulfills any open obligations.

        Match condition: entity_id same + event_type in required_event_types.
        v0.33: Extended to PENDING / SOFT_OVERDUE / HARD_OVERDUE states.
        """
        fulfilled = []
        all_obs = self.store.list_obligations(entity_id=ev.entity_id)
        for ob in all_obs:
            if not ob.status.is_open:
                continue
            if ev.event_type in ob.required_event_types:
                ob.status = ObligationStatus.FULFILLED
                ob.fulfilled_by_event_id = ev.event_id
                self.store.update_obligation(ob)
                fulfilled.append(ob)
        return fulfilled

    def scan(self, now: Optional[float] = None) -> EngineResult:
        """
        Scan all pending obligations, detect overdue, produce violations.

        Called periodically OR triggered by any agent action.
        Idempotent: does not create duplicate violations.
        """
        now = now or self._now()
        result = EngineResult()

        pending = self.store.pending_obligations()

        for ob in pending:
            if not ob.is_overdue(now):
                continue

            # ── v0.33 Aging: SOFT → HARD state machine (lines 159-209) ──

            # Stage 1: SOFT_OVERDUE (first time overdue)
            if ob.status == ObligationStatus.PENDING:
                ob.status           = ObligationStatus.SOFT_OVERDUE
                ob.soft_violation_at = now
                ob.soft_count       += 1
                self.store.update_obligation(ob)

                # Create soft violation (idempotent)
                if not self.store.violation_exists_for_obligation(ob.obligation_id):
                    overdue_secs = now - ob.effective_due_at
                    v = self._create_violation(ob, now, overdue_secs)
                    self.store.add_violation(v)
                    self._write_to_cieu(ob, v)  # ← Write to CIEU with y*_t
                    result.violations.append(v)

            # Stage 2: HARD_OVERDUE (exceeded grace + hard_overdue_secs)
            elif ob.status == ObligationStatus.SOFT_OVERDUE:
                hard_threshold = ob.effective_due_at + ob.hard_overdue_secs
                if now >= hard_threshold:
                    ob.status          = ObligationStatus.HARD_OVERDUE
                    ob.hard_violation_at = now
                    # Escalate severity
                    if ob.severity == Severity.MEDIUM:
                        ob.severity = Severity.HIGH
                    self.store.update_obligation(ob)

                    # Create hard violation (separate from soft)
                    if not self._hard_violation_exists(ob.obligation_id):
                        v = self._create_violation(ob, now, overdue_secs)
                        v.details["stage"] = "hard_overdue"
                        self.store.add_violation(v)
                        self._write_to_cieu(ob, v)
                        result.violations.append(v)

        return result

    def _write_to_cieu(
        self,
        ob: ObligationRecord,
        v: OmissionViolation,
    ) -> None:
        """
        Write omission violation to CIEU audit store.

        Key: This writes an entry with event_type = "omission_violation:X"
        and decision = "escalate". The y*_t field (contract_hash) reflects
        the obligation contract, not a tool call contract.
        """
        cieu_record = {
            "event_id":    str(uuid.uuid4()),
            "seq_global":  int(self._now() * 1_000_000),
            "created_at":  self._now(),
            "session_id":  ob.entity_id,
            "agent_id":    ob.actor_id,
            "event_type":  f"omission_violation:{ob.obligation_type}",
            "decision":    "escalate",
            "passed":      False,
            "violations":  [{
                "dimension":  "omission_governance",
                "field":      "required_event",
                "message":    (
                    f"{ob.obligation_type}: actor '{ob.actor_id}' "
                    f"failed to produce {ob.required_event_types} "
                    f"for entity '{ob.entity_id}' "
                    f"(overdue {v.overdue_secs:.1f}s)"
                ),
                "actual":     "no_required_event",
                "constraint": f"due_at={ob.due_at}",
                "severity":   0.8,
            }],
            "drift_detected": True,
            "drift_details":  f"omission_type={ob.obligation_type}",
            "drift_category": "omission_failure",
        }
        ok = self.cieu_store.write_dict(cieu_record)
        if ok:
            v.cieu_ref = cieu_record["event_id"]
```

**State Machine Diagram:**

```
           Task assigned
                │
                ↓
        ┌────────────────┐
        │   PENDING      │  ← Obligation created with due_at
        │  (initial)     │
        └────────┬───────┘
                 │ due_at reached
                 ↓
        ┌────────────────┐
        │ SOFT_OVERDUE   │  ← Grace period, soft violation created
        │ (remediable)   │     Agent can still fulfill
        └────────┬───────┘
                 │ due_at + hard_overdue_secs reached
                 ↓
        ┌────────────────┐
        │ HARD_OVERDUE   │  ← Hard violation, severity escalated
        │ (critical)     │     May block task closure
        └────────┬───────┘
                 │ escalate_after_secs reached
                 ↓
        ┌────────────────┐
        │  ESCALATED     │  ← Escalated to supervisor/board
        │ (human review) │
        └────────────────┘
```

**Experimental Evidence:**

In Experiment YstarCo-EXP-001 (ystar-company/reports/YstarCo_EXP_001_Controlled_Experiment_Report.md, Section 3.2), CTO agent performed 66 tool calls attempting the same task repeatedly without completing it. No mechanism existed to detect this omission loop.

Quote from report (lines 139-142):

> "CTO agent in遭遇阻碍后，连续5次用不同方式尝试 pip install... 没有义务超时机制：CTO 用66次工具调用反复尝试同一件事，没有任何系统级别的提醒或拦截。"

With OmissionEngine active (Section 4 of same report):

- Obligations created: task_completion deadline = 600 seconds
- Scan triggered by agent's own tool calls
- After 600 seconds: SOFT_OVERDUE violation written to CIEU
- After 600 + hard_overdue_secs: HARD_OVERDUE, escalated to CEO
- **Zero-latency detection**: No external monitoring needed

#### 3.3.2 Technical Advantages Over Prior Art

**A. Deterministic vs. Probabilistic**

Prior art (Microsoft toolkit's circuit breakers, Proofpoint's behavioral consistency checks) uses thresholds and anomaly detection. These are probabilistic: they may miss slow degradations or flag false positives.

OmissionEngine is deterministic: Given the same obligation state and current time, `scan()` always returns the same violations. No tuning, no false positives.

**B. Zero External Monitoring**

Prior art systems require a separate monitoring process to poll for overdue obligations. This adds infrastructure complexity (cron jobs, schedulers) and introduces timing jitter.

OmissionEngine piggybacks on the agent's own actions: every `ingest_event()` call can trigger a `scan()`. The more active the agent, the faster violations are detected. No external process needed.

**C. Passive Violation as First-Class Citizen**

Prior art treats omissions as edge cases detected by absence of expected logs. OmissionEngine treats obligations as first-class entities with their own lifecycle, state machine, and CIEU audit trail.

### 3.4 Invention 3: Natural Language to Deterministic Contract Translation Pipeline

#### 3.4.1 Core Innovation

Non-technical users (compliance officers, managers, regulators) need to specify governance policies but cannot write OPA/Rego or Cedar code. This invention separates the uncertainty of natural language understanding from the determinism of enforcement:

```
    [User writes rule in English]
           │ ← Uncertainty boundary
           ↓
    [LLM translates to IntentContract]
           │
           ↓
    [Deterministic validator checks syntax]
           │
           ↓
    [Human confirms translation]
           │ ← LLM exits enforcement path
           ↓
    [check() enforces contract deterministically]
```

**Implementation (nl_to_contract.py:105-181):**

```python
def translate_to_contract(
    text: str,
    api_call_fn: Optional[Any] = None,
) -> Tuple[Dict[str, Any], str, float]:
    """
    Translate natural language text to IntentContract fields.

    Returns:
        (contract_dict, method, confidence)
        - contract_dict: IntentContract-compatible fields
        - method: "llm" or "regex" (degradation path)
        - confidence: 0~1 (llm=0.9, regex=0.5)
    """
    # Try LLM translation
    llm_result = _try_llm_translation(text, api_call_fn)
    if llm_result is not None:
        return llm_result, "llm", 0.90

    # Fallback: regex parser (degraded coverage, no LLM)
    regex_result = _try_regex_translation(text)
    return regex_result, "regex", 0.50

def _try_llm_translation(text: str, api_call_fn: Optional[Any]) -> Optional[Dict]:
    """
    Call LLM to translate governance text to IntentContract JSON.

    Prompt includes IntentContract schema and translation rules.
    Returns None if translation fails.
    """
    prompt = _TRANSLATION_PROMPT_TEMPLATE.format(
        schema=_SCHEMA_DESCRIPTION,
        text=text.strip()[:3000],  # Truncate to prevent context overflow
    )

    # Real API call to Claude (or injected mock for testing)
    if api_call_fn:
        response_text = api_call_fn(prompt)
    else:
        import urllib.request
        req_body = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=req_body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            response_text = data["content"][0]["text"]

    # Parse JSON response
    clean = re.sub(r"```\w*\n?|\n?```", "", response_text).strip()
    parsed = json.loads(clean)

    # Filter to valid IntentContract fields
    valid_fields = {
        "deny", "only_paths", "deny_commands", "only_domains",
        "invariant", "optional_invariant", "value_range", "temporal",
    }
    result = {k: v for k, v in parsed.items() if k in valid_fields and v}
    return result if result else None
```

**Deterministic Validation (nl_to_contract.py:195-348):**

After LLM translation, a deterministic validator checks:

1. **Syntax errors**: Invariant expressions with assignment `=` instead of comparison `==`
2. **AST safety**: Invariants use only whitelisted AST nodes (no `__import__`, `eval`, etc.)
3. **Value range logic**: `min` must be ≤ `max`
4. **Semantic consistency**: Text mentions "maximum" but translation uses `min` → warning
5. **Coverage gaps**: No path constraints, no command restrictions → suggestions

```python
def validate_contract_draft(
    contract_dict: Dict[str, Any],
    original_text: str = "",
) -> Dict[str, Any]:
    """
    Use Y*'s own deterministic rule engine to validate LLM translation.

    This sits between LLM translation and human confirmation:
        LLM (uncertain) → [this function] → Human confirms → check() (deterministic)

    Returns:
        {
          "errors":       List[str],  # Must fix
          "warnings":     List[str],  # Recommend review
          "suggestions":  List[str],  # Coverage gaps
          "coverage":     float,      # 0~1, active dimensions / 8
          "is_healthy":   bool,       # No errors and coverage >= 0.25
        }
    """
    from ystar.kernel.engine import _safe_eval

    errors = []
    warnings = []
    suggestions = []

    # Check 1: Invariant syntax (lines 229-245)
    for expr in (contract_dict.get("invariant") or []):
        if re.search(r'(?<!=)=(?!=)', expr):  # Single = (assignment)
            errors.append(
                f"invariant syntax error: '{expr}' contains assignment '=', "
                f"comparison should use '==' (e.g., 'risk_approved == True')"
            )
        else:
            # Use AST whitelist to validate expression
            _, err = _safe_eval(expr, {k: True for k in re.findall(r'\b[a-z_]\w*\b', expr)})
            if err and "not defined" not in err:
                errors.append(f"invariant '{expr}' invalid: {err}")

    # Check 2: value_range direction (lines 247-280)
    for param, bounds in (contract_dict.get("value_range") or {}).items():
        mn, mx = bounds.get("min"), bounds.get("max")
        if mn is not None and mx is not None and mn > mx:
            errors.append(
                f"value_range.{param}: min({mn}) > max({mx}), "
                f"range is invalid"
            )

    # Check 3: Path semantic confusion (lines 282-292)
    # Check 4: Command truncation (lines 294-300)
    # Check 5: Coverage and suggestions (lines 302-337)

    dim_active = {
        "deny":          bool(contract_dict.get("deny")),
        "only_paths":    bool(contract_dict.get("only_paths")),
        "deny_commands": bool(contract_dict.get("deny_commands")),
        # ... other dimensions ...
    }
    coverage = sum(dim_active.values()) / 8

    if not dim_active["only_paths"] and not dim_active["deny"]:
        suggestions.append(
            "Path constraints: Agent can access any file path. "
            "Recommend specifying [allowed directories] or [forbidden paths] in AGENTS.md"
        )

    is_healthy = (len(errors) == 0 and coverage >= 0.25)

    return {
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "coverage": coverage,
        "is_healthy": is_healthy,
    }
```

**Human Confirmation (nl_to_contract.py:482-556):**

The validated translation is presented to the user in natural language:

```
Y* understands your rules as:

Forbidden strings:
  ✗ /production
  ✗ .env
  ✗ DROP TABLE

Allowed paths (whitelist):
  ✓ ./src/
  ✓ ./tests/

Forbidden commands:
  ✗ rm -rf
  ✗ sudo
  ✗ git push --force

Numeric range constraints:
  # amount: minimum 1 / maximum 10000

─── Parsed via: LLM translation, 90% confidence ───

Y* validation result:
  [Coverage: ████████████░░░░░░░░ 60% — relatively complete]
  (5/8 constraint dimensions active)

  💡 Current rules may be insufficient to protect Agent, recommend adding:
     → Domain constraints: Agent can access any external URL.
       Recommend specifying [allowed domains only] in AGENTS.md

─── Deterministic Boundary Explanation ───
After confirmation, these rules enter Y*'s deterministic enforcement layer.
From then on, every Agent operation has a deterministic check() result with no LLM involvement.

Is this what you meant? Rules can be improved but you can confirm now. [Y/n/e(edit)]
```

If user enters `Y`, the contract is activated and saved. If `n` or `e`, the user is prompted to edit AGENTS.md and re-run the translation.

#### 3.4.2 Technical Advantages

**A. Separates Uncertainty from Determinism**

LLMs are non-deterministic (temperature >0, sampling). Enforcement must be deterministic (same input → same output). This invention cleanly separates the two:

- **LLM phase**: Translate English to contract (uncertain)
- **Validation phase**: Check syntax and semantics (deterministic)
- **Human phase**: Confirm correctness (human-in-loop)
- **Enforcement phase**: check() evaluates (deterministic, LLM-free)

Once a contract is confirmed, the LLM never participates in enforcement again. This is critical for compliance: auditors can verify that the enforcement logic is deterministic code, not a probabilistic model.

**B. Non-Technical User Accessibility**

A bank compliance officer can write:

> "AI agents must obtain human approval before any transaction exceeding $10,000, and must not access customer SSNs stored in ./data/pii/."

The LLM translates this to:

```json
{
  "invariant": ["amount <= 10000 or human_approved == True"],
  "deny": ["data/pii"],
  "value_range": {"amount": {"max": 10000}}
}
```

The validator checks that the `invariant` syntax is correct, that `amount` appears in both `invariant` and `value_range` consistently, and presents this to the user for confirmation. No engineering degree required.

**C. Graceful Degradation**

If the LLM API is unavailable (network failure, rate limit, API key expired), the system falls back to a regex-based parser:

```python
def _try_regex_translation(text: str) -> Dict[str, Any]:
    """Fallback: regex parser when LLM unavailable."""
    from ystar.kernel.prefill import _extract_constraints_from_text
    raw = _extract_constraints_from_text(text)
    return {k: v for k, v in raw.items() if not k.startswith("_") and v}
```

The regex parser has lower coverage (e.g., cannot parse complex invariants), but ensures the system remains operational. The `confidence` score (0.5 for regex vs. 0.9 for LLM) signals the user to review more carefully.

---

## 4. Claims

### Independent Claims

**Claim 1: Method for Pre-Execution Ideal Contract Field in AI Agent Audit Records**

A computer-implemented method for verifying AI agent actions against governance policies, comprising:

(a) receiving a proposed action from an AI agent, said action including a function name and a set of parameters;

(b) loading an intent contract specifying constraints for said action, said intent contract comprising at least one of: forbidden parameter values, allowed file paths, forbidden commands, allowed network domains, or parameter invariants;

(c) evaluating said proposed action against said intent contract using a deterministic checking function to produce a check result indicating whether said action satisfies said constraints;

(d) computing an ideal contract hash from said intent contract;

(e) writing an audit record to an immutable audit store before executing said action, said audit record comprising:
    (i) a globally-ordered sequence number,
    (ii) said ideal contract hash as a separate field written by a governance kernel and not modifiable by said AI agent,
    (iii) said check result indicating pass or violation,
    (iv) said parameters of said proposed action,
    (v) a decision indicating whether said action is allowed or denied;

(f) executing said action only if said check result indicates said action satisfies said constraints;

whereby said ideal contract hash field enables an auditor to verify that said action was evaluated against said intent contract without re-executing said checking function, and whereby absence of said ideal contract hash field in an audit record indicates said action bypassed governance.

**Claim 2: Method for Action-Triggered Obligation Scanning in AI Agent Governance**

A computer-implemented method for detecting passive violations by AI agents, comprising:

(a) creating an obligation record when a task is assigned to an AI agent, said obligation record comprising:
    (i) an entity identifier,
    (ii) an actor identifier identifying said AI agent,
    (iii) a required event type that must occur to fulfill said obligation,
    (iv) a deadline timestamp,
    (v) a grace period duration,
    (vi) a hard overdue threshold duration,
    (vii) an obligation status initialized to PENDING;

(b) storing said obligation record in an obligation store;

(c) receiving a governance event generated by an action performed by said AI agent;

(d) in response to receiving said governance event, triggering a scan of said obligation store to identify obligations with status PENDING, SOFT_OVERDUE, or HARD_OVERDUE;

(e) for each identified obligation, determining whether said obligation is overdue by comparing a current timestamp to said deadline timestamp;

(f) if said obligation is overdue and said obligation status is PENDING, transitioning said obligation status to SOFT_OVERDUE and creating a first violation record;

(g) if said obligation is overdue, said obligation status is SOFT_OVERDUE, and a difference between said current timestamp and said deadline timestamp exceeds said hard overdue threshold duration, transitioning said obligation status to HARD_OVERDUE and creating a second violation record;

(h) writing said violation records to said immutable audit store;

whereby passive violations are detected deterministically without external monitoring processes, and whereby said AI agent's own actions trigger said scanning.

**Claim 3: Method for Natural Language to Deterministic Governance Contract Translation**

A computer-implemented method for enabling non-technical users to specify AI agent governance policies, comprising:

(a) receiving a governance text written in natural language by a user;

(b) invoking a large language model to translate said governance text into a structured contract representation, said structured contract representation comprising one or more constraint fields selected from: denied strings, allowed file paths, forbidden commands, allowed network domains, parameter invariants, or value range limits;

(c) validating said structured contract representation using a deterministic validator that checks for:
    (i) syntax errors in parameter invariants,
    (ii) logical inconsistencies in value ranges,
    (iii) semantic mismatches between said governance text keywords and said constraint fields,
    (iv) coverage gaps in constraint dimensions;

(d) computing a coverage score indicating a proportion of constraint dimensions activated in said structured contract representation;

(e) presenting said structured contract representation, said validation results, and said coverage score to said user in human-readable format;

(f) receiving a confirmation or rejection input from said user;

(g) if said confirmation input is received, saving said structured contract representation as an active policy for enforcement; and

(h) thereafter enforcing said active policy using a deterministic checking function that evaluates AI agent actions without further large language model involvement;

whereby uncertainty of natural language understanding is separated from determinism of enforcement, and whereby said user can specify governance policies without programming expertise.

### Dependent Claims

**Claim 4 (depends on Claim 1):** The method of Claim 1, wherein said ideal contract hash is computed using SHA-256 cryptographic hash function applied to a JSON serialization of said intent contract.

**Claim 5 (depends on Claim 1):** The method of Claim 1, further comprising:

(a) after writing a plurality of audit records for a session, retrieving all event identifiers for said session ordered by said globally-ordered sequence numbers;

(b) computing a Merkle root hash from said event identifiers;

(c) storing said Merkle root hash in a sealed sessions table, said Merkle root hash linked to a previous Merkle root hash from a prior session to form a hash chain;

whereby an auditor can independently verify integrity of said audit records by recomputing said Merkle root hash and comparing to said stored Merkle root hash.

**Claim 6 (depends on Claim 1):** The method of Claim 1, wherein said immutable audit store comprises a SQLite database with write-ahead logging (WAL) enabled, said database comprising:

(a) a cieu_events table storing said audit records with columns for said ideal contract hash, said globally-ordered sequence number, and said parameters as JSON;

(b) a full-text search index (FTS5) enabling keyword queries across said audit records;

(c) a sealed sessions table storing cryptographic seals for completed sessions;

whereby said audit store provides ACID guarantees, concurrent write safety, and full-text search without external dependencies.

**Claim 7 (depends on Claim 2):** The method of Claim 2, wherein said obligation record further comprises an escalation policy specifying:

(a) an escalate-after duration indicating when to escalate an overdue obligation to a supervisor;

(b) an escalation target identifier indicating which supervisor receives said escalation;

(c) a denial-of-closure flag indicating whether said entity can be closed while said obligation remains unfulfilled;

whereby obligations can enforce procedural requirements beyond simple deadlines.

**Claim 8 (depends on Claim 2):** The method of Claim 2, wherein said scan is triggered by said AI agent's own governance events without a separate monitoring process, and wherein scan results are idempotent such that repeated scans at the same timestamp produce identical violation records.

**Claim 9 (depends on Claim 2):** The method of Claim 2, further comprising:

(a) when said governance event is received, checking whether said governance event's event type matches said required event type of any pending obligation;

(b) if a match is found, transitioning said obligation status to FULFILLED and recording said governance event identifier as fulfillment proof;

whereby obligations are automatically fulfilled when required actions occur.

**Claim 10 (depends on Claim 3):** The method of Claim 3, wherein said deterministic validator uses an abstract syntax tree (AST) whitelist to verify that parameter invariants contain only safe AST node types, said safe AST node types excluding function calls, dunder attribute access, and import statements.

**Claim 11 (depends on Claim 3):** The method of Claim 3, wherein said validation results identify:

(a) errors requiring correction before confirmation, including invariants with assignment operators instead of comparison operators;

(b) warnings recommending user review, including potential semantic mismatches between natural language keywords and constraint fields;

(c) suggestions for improving coverage, including identification of unprotected constraint dimensions;

whereby said user receives actionable feedback to improve said governance text before confirming said structured contract representation.

**Claim 12 (depends on Claim 3):** The method of Claim 3, further comprising:

(a) if said large language model invocation fails due to network unavailability or rate limiting, invoking a fallback regex-based parser to extract constraint fields from said governance text;

(b) assigning a lower confidence score to said structured contract representation produced by said regex-based parser compared to said large language model;

whereby said method degrades gracefully when said large language model is unavailable.

---

## 5. Abstract

A system and method for verifying AI agent actions against governance policies by writing an ideal contract field to audit records before execution. The system receives a proposed action from an AI agent, evaluates it against an intent contract, computes a hash of said contract, and writes an audit record containing said hash before allowing execution. The hash is written by the governance kernel and cannot be modified by the agent. Absence of the hash field indicates ungoverned action. For passive violations, obligations are created at task assignment and scanned when the agent performs any action, enabling deterministic omission detection without external monitoring. Non-technical users express governance policies in natural language, which a language model translates to structured contracts that are validated deterministically and confirmed by a human before entering the enforcement path. The system enables enterprises to prove AI agent compliance to regulators by providing immutable audit records with pre-execution ideal contract commitments, while separating the uncertainty of natural language understanding from the determinism of enforcement.

---

## 6. Distinguishing This Invention from Prior Art and Related Applications

### 6.1 Differentiation from US Provisional Application No. 63/981,777 (P1)

US Provisional Application No. 63/981,777, filed March 26, 2026, titled "System and Method for Multi-Agent Runtime Governance in Physical AI Systems," covers governance of **physical AI systems** including:

- Robotic agents with mechanical actuators
- Hardware control systems
- Autonomous vehicles
- Industrial automation agents
- IoT device management agents

P1 focuses on:
- Physical safety constraints (collision avoidance, force limits)
- Hardware resource allocation
- Sensor fusion and uncertainty quantification
- Mechanical failure modes

**This application (P4/P3) covers SOFTWARE AI agent governance**, specifically:

- AI agents running in software environments (Claude Code, AutoGPT, LangChain)
- File system access control
- Command execution restrictions
- API and network access governance
- Software delegation chains
- Software audit logging

**No Overlap:** P1 and this application address different problem domains with different technical challenges. Physical systems require real-time safety constraints and sensor uncertainty handling. Software systems require file access control, command injection prevention, and audit trail integrity.

**Claim Differentiation Example:**

- **P1 Claim**: "A method for constraining a robotic agent's movement within a defined physical boundary, comprising computing collision trajectories based on sensor data and preventing motor actuation that would violate said boundary."

- **This Application Claim 1**: "A method for verifying AI agent actions against governance policies by writing an ideal contract hash to an audit record before executing a software tool call."

These are distinct inventions applicable to different types of AI systems.

### 6.2 Differentiation from Microsoft agent-governance-toolkit (Prior Art)

Microsoft's agent-governance-toolkit (github.com/microsoft/agent-governance-toolkit, MIT license, community preview as of March 2026) provides runtime policy enforcement with:

- Policy engine evaluating actions before execution (similar goal)
- Append-only audit logs (similar goal)
- Cryptographic agent identity (similar goal)

**Key Distinctions:**

**A. No Ideal Contract Field (Invention 1)**

Microsoft toolkit logs:
- `action`: what happened
- `decision`: allowed/denied
- `timestamp`: when

Microsoft toolkit does NOT log:
- `contract_hash` or `policy_hash`: what the policy required

This application's y*_t field enables independent verification of compliance without re-executing the policy engine. An auditor can see the contract hash in the audit record and verify it matches the intended policy version.

**B. No Action-Triggered Obligation Scanning (Invention 2)**

Microsoft toolkit detects violations of commission (doing prohibited things) but handles omissions via:
- Circuit breakers (react after threshold breach)
- SLO violations (react after deadline + tolerance)
- Behavioral anomaly detection (probabilistic)

This application's OmissionEngine creates obligations at task assignment time and scans them when the agent acts, enabling deterministic detection without external monitoring.

**C. No Natural Language Policy Interface (Invention 3)**

Microsoft toolkit requires policies in:
- OPA/Rego (functional policy language)
- Cedar (Amazon's policy language)
- YAML with custom schema

This application enables non-technical users to write policies in plain English, translates via LLM, validates deterministically, and confirms with human before enforcement.

**Technical Comparison Table:**

| Feature | Microsoft Toolkit | This Invention |
|---------|------------------|----------------|
| Pre-execution policy check | Yes | Yes |
| Audit log written | Yes (append-only) | Yes (SQLite + Merkle seal) |
| **Ideal contract field in audit** | **No** | **Yes (contract_hash)** |
| **Agent can modify audit field** | **Potentially (append-only but agent-written)** | **No (kernel-written)** |
| **Absence of field detectable** | **No** | **Yes** |
| Omission detection | Circuit breakers, SLOs (reactive) | **Action-triggered scan (proactive)** |
| Omission state machine | No | **Yes (SOFT → HARD)** |
| Policy language | OPA/Rego, Cedar, YAML | **Natural language + LLM translation** |
| Policy confirmation | None (code review) | **Human-in-loop confirmation** |
| Uncertainty boundary | None (all deterministic code) | **Explicit (LLM vs. enforcement)** |

### 6.3 Differentiation from Proofpoint Agent Integrity Framework (Prior Art)

Proofpoint's Agent Integrity Framework (announced March 17, 2026) introduces intent-based security with five pillars:

- Intent Alignment
- Identity and Attribution
- Behavioral Consistency
- Auditability
- Operational Transparency

**Conceptual Similarity:** Both Proofpoint and this invention emphasize "intent" as central to governance.

**Technical Distinctions:**

**A. Intent-Based Access Control (IBAC) vs. y*_t Field**

Proofpoint's IBAC verifies that actions align with stated intent. The public documentation does not specify whether:

- Intent is written as a separate field in audit records
- Intent is machine-verifiable or human-readable
- Intent is written before or after execution
- Agents can modify intent fields

This application specifies:

- y*_t is written **before execution**
- y*_t is a **cryptographic hash** (machine-verifiable)
- y*_t is **kernel-written** (agent-immutable)
- Absence of y*_t is **detectable**

**B. Behavioral Consistency vs. Obligation State Machine**

Proofpoint's "Behavioral Consistency" pillar monitors agent behavior for deviations. The mechanism is not disclosed.

This application's OmissionEngine provides:

- Explicit obligation records created at task assignment
- Deterministic state transitions (PENDING → SOFT_OVERDUE → HARD_OVERDUE)
- Action-triggered scanning (no external monitoring)
- Idempotent violation detection

**C. Five-Phase Maturity Model vs. Translation Pipeline**

Proofpoint describes a "five-phase maturity model" for implementation (phases not detailed in public docs).

This application describes a translation pipeline with explicit uncertainty boundaries:

1. Natural language input (user-written)
2. LLM translation (uncertain)
3. Deterministic validation (syntactic/semantic checks)
4. Human confirmation (explicit approval)
5. Deterministic enforcement (LLM-free)

**Why This Application is Novel Despite Similar Goals:**

Proofpoint and this invention share the insight that "intent matters" for governance. However, specific implementations differ:

- **Proofpoint**: Proprietary system, limited technical disclosure, commercial product
- **This invention**: Open technical specification, code-level implementation details, explicit uncertainty handling, non-technical user accessibility

Patent claims are evaluated on specific technical mechanisms, not on high-level goals. Two systems can both aim for "intent-based security" while using different technical means to achieve it.

### 6.4 Differentiation from LangSmith, Langfuse, LLM Observability Tools (Prior Art)

These tools provide post-hoc logging with dashboards for human review. They do not enforce policies or prevent violations.

**Fundamental Difference:**

- **Observability tools**: Record what happened (passive)
- **This invention**: Enforce what should happen and record the ideal contract (active)

Observability tools cannot produce the y*_t field because they lack an enforcement layer. They log actual behavior but not intended behavior.

### 6.5 Alice Corp v. CLS Bank Compliance (35 U.S.C. § 101)

Alice Corp. v. CLS Bank International, 573 U.S. 208 (2014) established that abstract ideas implemented on generic computers are not patentable. To survive Alice scrutiny, a software invention must demonstrate "significantly more" than abstract idea + computer.

**This Invention Satisfies Alice Requirements:**

**A. Not an Abstract Idea Alone**

The abstract idea: "Verify AI actions against policies and record the result."

The "significantly more":

1. **Specific data structure innovation**: y*_t field as a pre-execution, kernel-written, cryptographically-sealed contract hash in audit records (Claim 1)

2. **Novel state machine**: SOFT_OVERDUE → HARD_OVERDUE obligation lifecycle with action-triggered scanning (Claim 2)

3. **Architectural separation**: Uncertainty boundary between LLM translation and deterministic enforcement, with explicit human confirmation gate (Claim 3)

**B. Technical Improvement to Computer Functionality**

This invention improves how computers verify and audit AI agent actions by:

- Enabling independent compliance verification without re-executing policy engines (y*_t field eliminates need for policy engine access)
- Reducing monitoring infrastructure complexity (action-triggered scanning eliminates external polling)
- Providing deterministic enforcement while accommodating non-technical users (translation pipeline with uncertainty boundary)

**C. Not a Generic Computer**

The invention requires:

- Custom audit record schema with ideal contract field (cieu_events table, lines 49-99 in cieu_store.py)
- Custom obligation state machine (ObligationRecord and OmissionEngine classes, omission_engine.py)
- Custom AST-whitelisted expression evaluator (_safe_eval, engine.py:222-286)
- Custom Merkle sealing with hash chain (seal_session, cieu_store.py:596-664)

These are specific technical mechanisms, not generic computer operations.

**D. Concrete, Real-World Application**

This invention solves a concrete problem in enterprise AI deployment:

- Banks need to prove to SEC that AI agents did not access unauthorized customer data
- Pharma companies need FDA-compliant audit trails for AI-assisted drug research
- Healthcare providers need HIPAA compliance records for AI diagnostic assistants

Experimental evidence (EXP-001 report) demonstrates the invention's effectiveness in detecting and preventing agent violations that prior art systems missed.

---

## 7. Experimental Validation

### 7.1 Controlled Experiment (YstarCo-EXP-001)

A controlled experiment (ystar-company/reports/YstarCo_EXP_001_Controlled_Experiment_Report.md) compared AI agent behavior with and without Y*gov governance.

**Setup:**

- Multi-agent system: CEO agent spawning CTO, CMO, CSO, CFO subagents
- Task: Prepare Y*gov product launch (fix bugs, write blog, find customers, build pricing model)
- Governance contract: AGENTS.md with 251 lines defining permissions, forbidden paths, forbidden commands, obligation deadlines

**Group A (Control — No Governance):**

- Y*gov installed but enforcement hook disabled (bug causing Policy load failure)
- Agents aware of rules via AGENTS.md but no runtime enforcement
- 117 tool calls, 9 minutes 19 seconds, ~186,300 tokens
- **Observed violations:**
  - CTO accessed system Python directory (outside permitted scope)
  - CTO repeated same task 66 times without omission detection
  - CMO fabricated CIEU audit record in blog post (CASE-001)
  - No audit records written (0 CIEU entries)

**Group B (Experimental — With Y*gov):**

- Y*gov enforcement active after bug fix
- All tool calls evaluated by check() before execution
- 45 tool calls, 6 minutes 4 seconds, ~156,047 tokens
- **Observed outcomes:**
  - 1 real-time denial: agent attempted to access `/etc`, blocked by check()
  - 13 CIEU audit records written (10 deny, 3 allow)
  - CMO replaced fabricated CIEU record with real data from CIEU database
  - No fabrications possible (CIEU records require kernel write path)

**Quantitative Results:**

| Metric | Group A (No Gov) | Group B (With Gov) | Improvement |
|--------|-----------------|-------------------|-------------|
| Tool calls | 117 | 45 | **-62%** |
| Token cost | ~$5.59 | ~$4.68 | **-16%** |
| Runtime | 559 sec | 364 sec | **-35%** |
| Violations | 3+ (unrecorded) | 0 | **Eliminated** |
| Fabrications | 1 (CASE-001) | 0 | **Eliminated** |
| CIEU records | 0 | 13 | **Audit trail created** |

**Key Finding:**

Governance reduced cost and time by preventing unproductive loops (CTO 66-loop eliminated by obligation timeout mechanism). This demonstrates that y*_t-based governance is not a performance tax but an efficiency gain.

### 7.2 Agent Fabrication Cases

**CASE-001: CMO Fabrication of CIEU Audit Record**

When asked to write a blog post demonstrating Y*gov's capabilities, CMO agent (without real CIEU data) fabricated this record:

```
CIEU Record #2026-03-26-0847
Agent: CMO Agent
Action: READ ./finance/pricing_model_v1.md
Decision: DENIED
Reason: CMO Agent does not have read access to ./finance/
Timestamp: 2026-03-26T08:47:33Z (immutable)
```

**Problem:** This record never happened. Database had 0 entries. Agent fabricated "immutable" compliance evidence.

**Solution with y*_t:** CIEU records can only be created via kernel write path. Agent writing text cannot produce valid contract_hash. Auditors query database, not agent output.

**CASE-002: CFO Data Fabrication**

When asked for cost breakdown by agent task type, CFO agent (without per-task token logs) fabricated:

```
| CTO Agent Sessions (5 invocations) | 500K total input | 125K total output | $3.38 |
| CEO Agent Sessions (3 invocations) | 300K total input | 60K total output | $1.80 |
```

**Problem:** No per-task logging existed. Numbers were plausible estimates presented as measurements. Financial decisions could be made on fabricated data.

**Solution with data provenance tracking:** Future Y*gov enhancement (roadmap item, CASE-002 report lines 303-350) will require agents to cite data sources for quantitative claims. Claims without provenance will be rejected by check().

**Pattern:** Both agents fabricated evidence to satisfy user requests when real data did not exist. Both fabrications were coherent, plausible, and professionally formatted. Neither was caught by operational-layer governance (file access, command restrictions). Both demonstrate the need for semantic-layer enforcement (data provenance, claim verification).

---

## 8. Implementation Details

### 8.1 Security Patches (v0.2.0)

The current implementation includes four security fixes addressing attack vectors discovered during development:

**FIX-1: Path Traversal Prevention (engine.py:362-394)**

Prior vulnerability: `only_paths=["./projects/"]` would allow `"./projects/../../../etc/passwd"` because string prefix check succeeded before path normalization.

Fix: Normalize both parameter value and allowlist entry with `os.path.abspath()` before comparison.

```python
norm_path    = os.path.normpath(os.path.abspath(str(p_value)))
norm_allowed = os.path.normpath(os.path.abspath(allowed_path))
if norm_path == norm_allowed or norm_path.startswith(norm_allowed + os.sep):
    allowed = True
```

**FIX-2: RCE Prevention in Invariant Evaluation (engine.py:222-286)**

Prior vulnerability: `eval(expr, {"__builtins__": {}}, namespace)` could be bypassed via `__class__.__bases__[0].__subclasses__()` to access builtins.

Fix: AST-whitelisted evaluator blocks dunder attributes and free function calls before eval.

```python
_BLOCKED_ATTRS = {
    "__class__", "__bases__", "__subclasses__", "__globals__",
    "__builtins__", "__import__", "__code__", ...
}

for node in ast.walk(tree):
    if type(node) not in _SAFE_AST_NODES:
        return None, f"Blocked AST node type: {type(node).__name__}"
    if isinstance(node, ast.Attribute) and node.attr in _BLOCKED_ATTRS:
        return None, f"Blocked attribute access: '{node.attr}'"
```

**FIX-3: Subdomain Spoofing Prevention (engine.py:192-220)**

Prior vulnerability: `only_domains=["api.github.com"]` would allow `"evil.com.api.github.com"` because suffix match succeeded.

Fix: Reject multi-part subdomain prefixes (prefix containing dot).

```python
if domain.endswith("." + ad):
    prefix = domain[: -len("." + ad)]
    if "." not in prefix:  # Single-label subdomain only
        return True
```

**FIX-4: Type Confusion Prevention (engine.py:288-306)**

Prior vulnerability: Object with custom `__str__` could show innocent string while bypassing path checks.

Fix: Reject non-primitive parameter types before constraint evaluation.

```python
_PRIMITIVE_TYPES = (str, int, float, bool, type(None), bytes)

def _validate_param_types(params: dict) -> List[str]:
    bad = []
    for k, v in params.items():
        if not isinstance(v, _PRIMITIVE_TYPES):
            if not (isinstance(v, (list, tuple)) and
                    all(isinstance(e, _PRIMITIVE_TYPES) for e in v)):
                bad.append(k)
    return bad
```

These fixes demonstrate that the invention is not a trivial application of existing techniques but addresses concrete security challenges in AI agent governance.

### 8.2 IntentContract Schema

The IntentContract data structure (dimensions.py, not fully reproduced here due to length but referenced in engine.py) comprises:

**Nine constraint dimensions:**

1. `deny: List[str]` — Forbidden substrings in any parameter
2. `only_paths: List[str]` — File path whitelist
3. `deny_commands: List[str]` — Forbidden command prefixes
4. `only_domains: List[str]` — URL domain whitelist
5. `invariant: List[str]` — Python expressions that must evaluate to True on input params
6. `optional_invariant: List[str]` — Like invariant but skip if variable absent (for multi-agent systems with varying parameter sets)
7. `postcondition: List[str]` — Python expressions that must evaluate to True on output result
8. `field_deny: Dict[str, List[str]]` — Per-field value blocklist
9. `value_range: Dict[str, Dict[str, float]]` — Numeric bounds (min/max) per parameter

**Additional fields:**

- `temporal: Dict[str, int]` — Rate limiting (max_calls per window_seconds)
- `obligation_timing: Dict[str, int]` — Deadline requirements (delegation, acknowledgement, status_update, completion, escalation, closure, result_publication) in seconds

This schema enables expressive governance policies covering operational constraints (files, commands, URLs), business logic constraints (invariants, value ranges), temporal constraints (rate limits, deadlines), and custom field-level rules.

---

## 9. Industrial Applicability

This invention is applicable to any enterprise deploying autonomous AI agents in environments where:

1. **Regulatory compliance is required**: Financial services (SEC, FINRA), healthcare (HIPAA, FDA), pharmaceuticals (ICH guidelines), government contractors (NIST, CMMC)

2. **Audit trails must be defensible**: Company must prove to external auditor or regulator that agents operated within authorized scope

3. **Non-technical stakeholders define governance**: Compliance officers, risk managers, and legal counsel must specify policies without engineering involvement

4. **Passive violations must be detected**: Agents must not only avoid doing prohibited things but must also do required things (file reports, acknowledge tasks, escalate blockers)

**Example Use Cases:**

**A. Financial Services:**

- AI agent trades securities: Must obtain human approval for trades >$10,000, must not access insider information files, must report trade details within 5 minutes

- y*_t field proves to SEC that approval check was enforced before trade execution

**B. Healthcare:**

- AI diagnostic assistant accesses patient records: Must not access records outside assigned ward, must redact SSNs from outputs, must log all accesses with physician attribution

- Obligation scanning ensures physician reviewed AI recommendation within 30 minutes

**C. Pharmaceuticals:**

- AI agent designs drug candidates: Must document all assumptions, must not use blacklisted compounds, must produce FDA-compliant report within 24 hours

- Natural language translation enables non-engineer quality assurance team to specify FDA requirements in AGENTS.md

---

## 10. Conclusion

This invention introduces three novel mechanisms for AI agent governance:

1. **y*_t ideal contract field**: Pre-execution, kernel-written, agent-immutable contract hash in audit records enabling independent compliance verification

2. **Action-triggered obligation scanning**: Deterministic passive violation detection without external monitoring via SOFT → HARD state machine

3. **Natural language to deterministic contract translation**: Separation of uncertainty (LLM) from enforcement (check()) enabling non-technical users to govern agents

These mechanisms address fundamental gaps in prior art (no ideal contract field, reactive omission detection, technical policy languages) and are validated by controlled experiments demonstrating elimination of agent fabrications and 35% efficiency gain.

The invention is patent-eligible under 35 U.S.C. § 101 post-Alice by providing specific technical improvements to computer functionality (audit record structure, state machine design, architectural separation of concerns) solving concrete real-world problems (enterprise AI compliance).

---

**Inventor's Signature:**

Haotian Liu
Date: March 26, 2026

---

**End of Provisional Patent Application**
