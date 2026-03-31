# Y*gov Integration Quick-Start

Three paths depending on what you need. Most users start with Path B.
Y*gov is a dual-track system: Path B governs external agents, Path A governs
Y*gov itself, and the Bridge connects them into a closed feedback loop.

---

## Path B Quick-Start — "I have external agents I want to govern"

This is the most common starting point. You have LLM agents, tool-using bots,
or third-party integrations and you want to control what they can do.

```bash
pip install ystar
```

Create `AGENTS.md` with your rules:

```markdown
# External Agent Rules
- DENY commands: rm -rf, sudo, eval, exec
- DENY paths: /etc, /root, /production, ~/.ssh
- ONLY domains: api.mycompany.com, storage.mycompany.com
```

Set up and verify:

```bash
ystar setup          # compiles AGENTS.md -> IntentContract
ystar hook-install   # installs pre-execution check hook
ystar doctor         # verifies wiring
```

See your first DENY in action:

```python
from ystar.kernel.engine import check
from ystar.kernel.dimensions import IntentContract

contract = IntentContract(
    name="vendor-agent-policy",
    deny=["/etc", "/root"],
    deny_commands=["rm -rf", "sudo"],
    only_domains=["api.mycompany.com"],
)

result = check(
    params={"command": "sudo rm -rf /", "path": "/etc/passwd"},
    result=None,
    contract=contract,
)
print(f"Passed: {result.passed}")  # False
for v in result.violations:
    print(f"  DENIED: {v.dimension} - {v.message}")
```

**What just happened:** Y*gov compiled your natural-language rules into a
machine-checkable IntentContract, then blocked the agent's dangerous action
before it executed. Every check is logged to CIEU for audit.

---

## Path A Quick-Start — "I want my governance system to govern itself"

For researchers and advanced users. Path A makes Y*gov eat its own dog food:
the same check() engine that governs external agents also governs Y*gov's
own self-improvement actions.

```python
from ystar.kernel.dimensions import IntentContract
from ystar.kernel.engine import check

# GovernanceLoop produces a suggestion to tighten omission detection
# Path A compiles it into a contract that governs the improvement action
meta_contract = IntentContract(
    name="path_a:meta_agent:tighten_omission",
    deny=["/etc", "/root", "/production"],
    deny_commands=["rm -rf", "sudo", "exec("],
    only_paths=["ystar/governance/omission_engine.py"],
)

# Path A checks its OWN action against the contract
result = check(
    params={"path": "ystar/governance/omission_engine.py", "value": 0.3},
    result=None,
    contract=meta_contract,
)
print(f"Self-governance check: {result.passed}")  # True — allowed

# But Path A cannot escape its bounds
escape = check(
    params={"path": "/etc/shadow"},
    result=None,
    contract=meta_contract,
)
print(f"Escape attempt: {escape.passed}")  # False — blocked
```

**What just happened:** Path A tried to improve Y*gov's omission detection
and was allowed. When it tried to access /etc/shadow, it was blocked by its
own governance contract. The governors are governed.

---

## Full-Stack Quick-Start — "I want the complete dual-track system"

Combines Path B (external governance) + Path A (self-governance) + Bridge
(feedback loop). This is the full Y*gov architecture.

```python
from ystar.kernel.dimensions import IntentContract
from ystar.kernel.engine import check
from ystar.path_b.path_b_agent import (
    ExternalObservation, ConstraintBudget, observation_to_constraint,
)
from ystar.kernel.engine import Violation
from ystar.governance.experience_bridge import ExperienceBridge, BridgeInput

# 1. Path B: govern an external agent
violation = Violation(
    dimension="deny", field="cmd", message="banned command",
    actual="sudo rm -rf /", constraint="deny", severity=0.9,
)
obs = ExternalObservation(
    agent_id="vendor-x", action_type="command_exec",
    params={"command": "sudo rm -rf /"}, violations=[violation],
)
budget = ConstraintBudget(agent_id="vendor-x")
constraint = observation_to_constraint(obs, [obs], budget, 0.65)
print(f"Path B constraint: {constraint.name}")

# 2. Bridge: aggregate Path B experience
bridge = ExperienceBridge()
bridge.ingest(BridgeInput(cieu_records=[
    {"func_name": "path_b.constraint_applied",
     "path_b_event": "CONSTRAINT_APPLIED",
     "params": {"agent_id": "vendor-x"},
     "violations": [{"dim": "deny"}], "source": "path_b_agent"},
]))
bridge.aggregate_patterns()
bridge.attribute_gaps()
metrics = bridge.generate_observation_metrics()
print(f"Bridge metrics: {metrics}")

# 3. Path A: use metrics to improve internal governance
meta_contract = IntentContract(
    name="path_a:improve_deny_detection",
    deny=["/etc"], deny_commands=["sudo"],
    only_paths=["ystar/governance/omission_engine.py"],
)
result = check(
    params={"path": "ystar/governance/omission_engine.py", "value": 0.3},
    result=None,
    contract=meta_contract,
)
print(f"Path A self-improvement: passed={result.passed}")
print("Feedback loop: Path B experience -> Bridge -> Path A -> better Path B")
```

**What just happened:** Path B caught an external agent violation and
generated a constraint. The Bridge aggregated that experience into metrics.
Path A used those metrics to tighten its own detection. Next cycle, Path B
catches violations earlier. That is the closed-loop dual-track system.
