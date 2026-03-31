# "Who Governs the Governors?" -- Path A Live Demo

Path A is Y*gov's internal meta-governance agent. It receives governance
suggestions, compiles them into IntentContracts, and then **its own actions
are checked by the same engine it enforces on others**. This demo shows
the full cycle: suggestion, contract compilation, denial, success, and
causal confidence evolution.

## Copy-Paste Demo (requires: `pip install ystar-gov`)

```python
"""Path A Demo: the governor governs itself."""
import time, uuid
from ystar.kernel.dimensions import IntentContract
from ystar.kernel.engine import check, CheckResult
from ystar.governance.governance_loop import GovernanceSuggestion
from ystar.governance.causal_engine import CausalEngine, CausalState, CausalObservation
from ystar.governance.cieu_store import CIEUStore
from ystar.path_a.meta_agent import suggestion_to_contract

# ── Step 1: Governance Loop produces a suggestion ──────────────────
suggestion = GovernanceSuggestion(
    suggestion_type="tighten_rule",
    target_rule_id="omission.scan_interval",
    suggested_value=30,
    confidence=0.72,
    observation_ref="obs_demo_001",
)
print(f"1. Suggestion received: {suggestion.suggestion_type}")
print(f"   Target: {suggestion.target_rule_id} -> {suggestion.suggested_value}")

# ── Step 2: Compile suggestion into IntentContract ─────────────────
contract = suggestion_to_contract(
    suggestion,
    allowed_modules=["omission_engine", "scanner"],
    deadline_secs=300.0,
)
print(f"\n2. Contract compiled: {contract.name}")
print(f"   Denied paths: {contract.deny}")
print(f"   Denied cmds:  {contract.deny_commands[:3]}...")

# ── Step 3-4: Path A's OWN action is checked -- and DENIED ────────
# Path A tries to write to /etc (forbidden even for the governor)
bad_result: CheckResult = check(contract, {"file_path": "/etc/shadow"})
print(f"\n3. Path A attempts /etc/shadow:")
print(f"   Result: {bad_result.summary()}")
print(f"   Passed: {bad_result.passed}")
for v in bad_result.violations:
    print(f"   Violation: [{v.dimension}] {v.message}")

# ── Step 5: Path A succeeds on a legitimate action ────────────────
good_result: CheckResult = check(contract, {"file_path": "module:omission_engine"})
print(f"\n4. Path A attempts module:omission_engine:")
print(f"   Result: {good_result.summary()}")
print(f"   Passed: {good_result.passed}")

# ── Step 6: CIEU records the full audit trail ─────────────────────
store = CIEUStore(":memory:")
session_id = f"demo_{uuid.uuid4().hex[:8]}"

for label, result, target in [
    ("denied",  bad_result,  "/etc/shadow"),
    ("allowed", good_result, "module:omission_engine"),
]:
    store.write_dict({
        "event_id":    str(uuid.uuid4()),
        "session_id":  session_id,
        "agent_id":    "path_a_agent",
        "event_type":  "meta_governance_check",
        "decision":    "deny" if not result.passed else "allow",
        "passed":      result.passed,
        "violations":  [v.to_dict() for v in result.violations],
        "file_path":   target,
        "contract_hash": contract.hash,
        "human_initiator": "governance_loop",
        "lineage_path": ["governance_loop", "path_a_agent"],
    })

stats = store.stats(session_id=session_id)
print(f"\n5. CIEU audit trail ({stats['total']} records):")
print(f"   Decisions: {stats['by_decision']}")
print(f"   Deny rate: {stats['deny_rate']}")

# ── Step 7: Causal confidence evolves 0.64 -> 0.84 ────────────────
engine = CausalEngine()

state_before = CausalState(
    wired_edges=[], health="degraded",
    obl_fulfilled=2, obl_total=5, suggestion_type="tighten_rule",
)
state_after = CausalState(
    wired_edges=[("scanner", "omission_engine")], health="stable",
    obl_fulfilled=4, obl_total=5, suggestion_type="tighten_rule",
)

# Feed three observations to build causal history
for i in range(3):
    engine.observe(CausalObservation(
        state_before=state_before, state_after=state_after,
        action_taken=f"wire_edge_{i}", cycle_id=f"cycle_{i}",
    ))

conf_before = engine.causal_confidence(state_before)
conf_after  = engine.causal_confidence(state_after)
print(f"\n6. Causal confidence (Pearl L2 do-calculus):")
print(f"   Before intervention: {conf_before:.2f}")
print(f"   After intervention:  {conf_after:.2f}")
print(f"   Delta:               +{conf_after - conf_before:.2f}")
```

## Expected Output

```
1. Suggestion received: tighten_rule
   Target: omission.scan_interval -> 30

2. Contract compiled: path_a:tighten_rule:XXXXXX
   Denied paths: ['/etc', '/root', '~/.clawdbot', '/production']
   Denied cmds:  ['rm -rf', 'sudo', 'exec(']...

3. Path A attempts /etc/shadow:
   Result: VIOLATION: Path '/etc/shadow' is under denied path '/etc'
   Passed: False
   Violation: [deny] Path '/etc/shadow' is under denied path '/etc'

4. Path A attempts module:omission_engine:
   Result: PASS
   Passed: True

5. CIEU audit trail (2 records):
   Decisions: {'deny': 1, 'allow': 1}
   Deny rate: 0.5

6. Causal confidence (Pearl L2 do-calculus):
   Before intervention: 0.64
   After intervention:  0.84
   Delta:               +0.20
```

## What Just Happened

1. The governance loop detected a health issue and generated a suggestion.
2. Path A compiled that suggestion into a **machine-enforceable contract**.
3. Path A tried to touch `/etc/shadow` -- **denied by its own contract**.
   The governor cannot exempt itself from the rules.
4. Path A performed a legitimate module wiring -- **allowed**.
5. Both events were recorded in the CIEU audit trail with full lineage.
6. The causal engine computed confidence using Pearl Level 2 do-calculus,
   showing that the intervention genuinely improved system health.
