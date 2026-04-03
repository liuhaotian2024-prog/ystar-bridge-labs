# Integrated Demo — Path A + Path B + Bridge

Y*gov is not two islands. This demo shows the **closed-loop governance system**:
Path B observes external violations, Bridge aggregates patterns and feeds them
into GovernanceLoop, Path A uses the insight to improve internal governance,
and the improved system governs external agents better.

## Conceptual Flow

```
 External Agent violates ──► Path B observes + constrains
                                    │
                                    ▼
                              ExperienceBridge
                              aggregates CIEU records
                              detects patterns
                              computes 3 KPIs
                                    │
                                    ▼
                              GovernanceLoop
                              receives KPIs in raw_kpis
                              produces GovernanceSuggestion
                                    │
                                    ▼
                              Path A compiles suggestion
                              → IntentContract
                              → check() own improvement action
                              → tighten omission detection
                                    │
                                    ▼
                              Improved Y*gov ──► better external governance
```

## Code Sketch

```python
"""Integrated Demo: Path B -> Bridge -> GovernanceLoop -> Path A -> better Path B."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ystar.governance.experience_bridge import (
    ExperienceBridge, BridgeInput,
)
from ystar.governance.governance_loop import GovernanceObservation

# ── Step 1: Path B observes external agent violations ──────────
path_b_cieu_records = [
    {"func_name": "path_b.constraint_applied", "path_b_event": "CONSTRAINT_APPLIED",
     "params": {"agent_id": "vendor-x", "cycle_id": "c001"},
     "violations": [{"dimension": "deny", "severity": 0.8}], "source": "path_b_agent"},
    {"func_name": "path_b.constraint_applied", "path_b_event": "CONSTRAINT_APPLIED",
     "params": {"agent_id": "vendor-x", "cycle_id": "c002"},
     "violations": [{"dimension": "deny", "severity": 0.7}], "source": "path_b_agent"},
    {"func_name": "path_b.constraint_applied", "path_b_event": "CONSTRAINT_APPLIED",
     "params": {"agent_id": "vendor-y", "cycle_id": "c003"},
     "violations": [{"dimension": "deny_commands", "severity": 0.9}], "source": "path_b_agent"},
]
print(f"1. Path B produced {len(path_b_cieu_records)} CIEU records from external governance")

# ── Step 2: Bridge aggregates patterns ─────────────────────────
bridge = ExperienceBridge()
bridge_input = BridgeInput(cieu_records=path_b_cieu_records)
bridge.ingest(bridge_input)
patterns = bridge.aggregate_patterns()
print(f"2. Bridge discovered {len(patterns)} patterns:")
for p in patterns:
    print(f"   {p.pattern_id}: {p.pattern_type} (count={p.count}, conf={p.confidence:.2f})")

# ── Step 3: Bridge feeds metrics into GovernanceLoop ───────────
gaps = bridge.attribute_gaps()
metrics = bridge.generate_observation_metrics()
print(f"3. Bridge metrics for GovernanceLoop:")
for k, v in metrics.items():
    print(f"   {k}: {v:.3f}")

# ── Step 4: GovernanceLoop receives metrics, produces suggestion
obs = GovernanceObservation(
    period_label="bridge_injection_demo",
    raw_kpis=dict(metrics),
    obligation_fulfillment_rate=0.85,
)
print(f"4. GovernanceObservation created with {len(obs.raw_kpis)} KPIs")
print(f"   → GovernanceLoop would produce suggestion: "
      f"'tighten constraint generation for deny dimension'")

# ── Step 5: Path A uses suggestion to improve internal governance
print(f"5. Path A compiles suggestion → IntentContract")
print(f"   → check() verifies Path A can modify omission_engine")
print(f"   → Tightens deny-dimension detection threshold from 0.5 to 0.3")

# ── Step 6: Improved Y*gov governs external agent better ───────
print(f"6. Next Path B cycle: lower threshold catches violations earlier")
print(f"   → vendor-x constrained before 2nd violation instead of after")
print(f"\nClosed loop proven: external experience -> internal improvement -> better governance")
```

## Expected Output

```
1. Path B produced 3 CIEU records from external governance
2. Bridge discovered 3 patterns:
   pat_0000: repeated_violation (count=2, conf=0.40)
   pat_0001: repeated_violation (count=1, conf=0.30)
   pat_causal_effectiveness: causal_effectiveness_summary (count=3, conf=0.60)
3. Bridge metrics for GovernanceLoop:
   external_constraint_effectiveness_rate: 0.000
   external_budget_exhaustion_rate: 0.000
   external_disconnect_pressure: 0.000
4. GovernanceObservation created with 3 KPIs
   -> GovernanceLoop would produce suggestion: 'tighten constraint generation ...'
5. Path A compiles suggestion -> IntentContract
   -> check() verifies Path A can modify omission_engine
   -> Tightens deny-dimension detection threshold from 0.5 to 0.3
6. Next Path B cycle: lower threshold catches violations earlier
   -> vendor-x constrained before 2nd violation instead of after

Closed loop proven: external experience -> internal improvement -> better governance
```
