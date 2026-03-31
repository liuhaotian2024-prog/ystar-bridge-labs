# Path B Demo — External Agent Governance

Y*gov governs external agents using the same architectural pattern as Path A.
This demo shows the full Path B cycle: observation, constraint generation,
budget tracking, compliance verification, and escalation.

Path B is the **commercial entry point** -- most users want to govern external
agents first. Path A (self-governance) strengthens Path B over time via the Bridge.

## Copy-Paste Demo

```python
"""Path B Demo: Y*gov governs an external agent."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ystar.kernel.dimensions import IntentContract
from ystar.kernel.engine import check, Violation
from ystar.path_b.path_b_agent import (
    ExternalObservation,
    ConstraintBudget,
    ExternalGovernanceAction,
    observation_to_constraint,
)

agent_id = "ext-agent-vendor-x"

# ── Step 1: Observe a violating external agent ─────────────────
violation = Violation(
    dimension="deny", field="command",
    message="Agent executed banned command: rm -rf /data",
    actual="rm -rf /data", constraint="deny=['rm -rf']", severity=0.9,
)
observation = ExternalObservation(
    agent_id=agent_id,
    action_type="command_exec",
    params={"command": "rm -rf /data", "target": "/data"},
    violations=[violation],
)
print(f"1. Observed violation: agent={agent_id}")
print(f"   action={observation.action_type}, severity={observation.severity_score()}")

# ── Step 2: observation_to_constraint() generates constraint ───
budget = ConstraintBudget(agent_id=agent_id)
constraint = observation_to_constraint(
    observation=observation,
    violation_history=[observation],
    budget=budget,
    confidence_threshold=0.65,
)
print(f"2. Generated constraint: {constraint.name}")
print(f"   deny={constraint.deny}, deny_commands={constraint.deny_commands}")

# ── Step 3: ConstraintBudget tracks authority ──────────────────
print(f"3. Budget after constraint: {budget.current_budget:.2f} "
      f"(consumed={budget.consumed_total:.2f})")
print(f"   Can tighten further: {budget.can_tighten()}")

# ── Step 4: apply_constraint + verify_compliance ───────────────
# Simulate: apply constraint, then check the agent's next action
next_action_good = check(
    params={"path": "reports/summary.txt"},
    result=None,
    contract=constraint,
)
print(f"4a. Agent compliant action: passed={next_action_good.passed}")

next_action_bad = check(
    params={"command": "rm -rf /data", "path": "/data"},
    result=None,
    contract=constraint,
)
print(f"4b. Agent re-violation: passed={next_action_bad.passed}")
for v in next_action_bad.violations:
    print(f"    BLOCKED: {v.dimension} — {v.message}")

# ── Step 5: Repeated violation → escalation ────────────────────
print(f"\n5. Escalation ladder for repeat offender:")
escalation_steps = [
    ("warn",       ExternalGovernanceAction.APPLY_CONSTRAINT),
    ("downgrade",  ExternalGovernanceAction.DOWNGRADE_CONTRACT),
    ("freeze",     ExternalGovernanceAction.FREEZE_SESSION),
    ("disconnect", ExternalGovernanceAction.DISCONNECT_AGENT),
]
for step_name, action in escalation_steps:
    print(f"   Step: {step_name:12s} -> action={action.value}")

# ── Step 6: ExternalGovernanceAction enum in action ────────────
print(f"\n6. All Path B governance actions:")
for action in ExternalGovernanceAction:
    print(f"   {action.value}")

# ── Step 7: CIEU records for external governance ───────────────
cieu_records = [
    {"event": "OBSERVATION", "agent": agent_id,
     "violation": "rm -rf /data", "severity": 0.9},
    {"event": "CONSTRAINT_APPLIED", "agent": agent_id,
     "constraint": constraint.name, "budget_remaining": budget.current_budget},
    {"event": "COMPLIANCE_CHECK", "agent": agent_id,
     "compliant_action": True, "action": "read_file"},
    {"event": "VIOLATION_REPEATED", "agent": agent_id,
     "action": "rm -rf /data", "escalation": "warn"},
    {"event": "ESCALATION_COMPLETE", "agent": agent_id,
     "steps": ["warn", "downgrade", "freeze", "disconnect"]},
]
print(f"\n7. CIEU audit trail ({len(cieu_records)} records):")
for r in cieu_records:
    print(f"   [{r['event']}] agent={r['agent']}")

print("\nPath B complete: external agent governed with same check() engine as Path A.")
print("Bridge feeds these patterns back to Path A for continuous improvement.")
```

## Expected Output

```
1. Observed violation: agent=ext-agent-vendor-x
   action=command_exec, severity=0.9
2. Generated constraint: path_b:external:ext-ag:xxxxxx
   deny=['rm -rf /data'], deny_commands=[]
3. Budget after constraint: 0.91 (consumed=0.10)
   Can tighten further: True
4a. Agent compliant action: passed=True
4b. Agent re-violation: passed=False
    BLOCKED: deny — 'rm -rf /data' is not allowed in command

5. Escalation ladder for repeat offender:
   Step: warn         -> action=apply_constraint
   Step: downgrade    -> action=downgrade_contract
   Step: freeze       -> action=freeze_session
   Step: disconnect   -> action=disconnect_agent

6. All Path B governance actions:
   apply_constraint
   verify_compliance
   downgrade_contract
   freeze_session
   disconnect_agent
   require_human_review

7. CIEU audit trail (5 records):
   [OBSERVATION] agent=ext-agent-vendor-x
   [CONSTRAINT_APPLIED] agent=ext-agent-vendor-x
   [COMPLIANCE_CHECK] agent=ext-agent-vendor-x
   [VIOLATION_REPEATED] agent=ext-agent-vendor-x
   [ESCALATION_COMPLETE] agent=ext-agent-vendor-x

Path B complete: external agent governed with same check() engine as Path A.
Bridge feeds these patterns back to Path A for continuous improvement.
```
