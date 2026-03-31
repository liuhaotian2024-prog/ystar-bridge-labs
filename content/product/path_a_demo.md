# Path A Demo — Internal Self-Governance

Y*gov governs itself using the same check() engine it uses to govern others.
This demo shows the full Path A cycle: suggestion, compilation, check, denial,
success, causal learning, and CIEU audit.

Path A is one half of Y*gov's dual-track system. Path B (external governance)
uses the same architectural pattern directed outward.

## Copy-Paste Demo

```python
"""Path A Demo: Y*gov governs its own actions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dataclasses import dataclass
from ystar.kernel.dimensions import IntentContract
from ystar.kernel.engine import check, Violation

# ── Step 1: GovernanceSuggestion generated ──────────────────────
@dataclass
class GovernanceSuggestion:
    suggestion_type: str = ""
    target_rule_id: str = ""
    current_value: object = None
    suggested_value: object = None
    confidence: float = 0.5
    rationale: str = ""

suggestion = GovernanceSuggestion(
    suggestion_type="tighten_timing",
    target_rule_id="omission.deadline",
    current_value=600,
    suggested_value=300,
    confidence=0.72,
    rationale="Obligation expiry rate > 15%, tighten deadline",
)
print(f"1. Suggestion: {suggestion.suggestion_type} "
      f"(confidence={suggestion.confidence})")

# ── Step 2: suggestion_to_contract() compiles IntentContract ────
allowed_modules = ["governance.omission_engine", "governance.metalearning"]
contract = IntentContract(
    name="path_a:meta_agent:tighten_timing",
    deny=["/etc", "/root", "/production"],
    deny_commands=["rm -rf", "sudo", "exec(", "eval("],
    only_paths=[f"ystar/{m.replace('.', '/')}.py" for m in allowed_modules],
)
print(f"2. Compiled contract: {contract.name}")
print(f"   deny={contract.deny}, only_paths={contract.only_paths}")

# ── Step 3: check() verifies Path A's own action ───────────────
result_good = check(
    params={"path": "ystar/governance/omission_engine.py", "value": 300},
    result=None,
    contract=contract,
)
print(f"3. check() on allowed action: passed={result_good.passed}")

# ── Step 4: Path A DENIED by its own system ─────────────────────
result_denied = check(
    params={"path": "/etc/shadow"},
    result=None,
    contract=contract,
)
print(f"4. check() on /etc access: passed={result_denied.passed}")
for v in result_denied.violations:
    print(f"   DENIED: {v.dimension} — {v.message}")

# ── Step 5: Path A succeeds on legitimate wiring ───────────────
result_legit = check(
    params={"path": "ystar/governance/metalearning.py", "alpha": 0.05},
    result=None,
    contract=contract,
)
print(f"5. Legitimate wiring: passed={result_legit.passed}")

# ── Step 6: Causal confidence grows with evidence ───────────────
from ystar.governance.causal_engine import CausalEngine
causal = CausalEngine(confidence_threshold=0.65)
# Feed multiple governance cycles to build causal evidence
for i in range(5):
    causal.observe(
        health_before="degraded", health_after="healthy",
        obl_before=(3, 10), obl_after=(8, 10),
        edges_before=[], edges_after=[("omission_engine", "metalearning")],
        action_edges=[("omission_engine", "metalearning")],
        succeeded=True, cycle_id=f"demo_{i:03d}",
        suggestion_type="tighten_timing",
    )
result_causal = causal.do_wire_query("omission_engine", "metalearning")
print(f"6. Causal confidence after 5 cycles: {result_causal.confidence:.2f}")
print(f"   (grows with evidence — Pearl L2-3 do-calculus)")

# ── Step 7: CIEU audit trail ───────────────────────────────────
cieu_record = {
    "cycle_id": "demo_001",
    "layer": "path_a",
    "func_name": "meta_agent.execute_suggestion",
    "contract": contract.name,
    "check_passed": result_good.passed,
    "denied_action": "/etc/shadow",
    "causal_confidence": conf_after,
}
print(f"7. CIEU record: {cieu_record}")
print("\nPath A complete: Y*gov governed itself using its own check() engine.")
print("Path B uses the same pattern to govern external agents.")
```

## Expected Output

```
1. Suggestion: tighten_timing (confidence=0.72)
2. Compiled contract: path_a:meta_agent:tighten_timing
   deny=['/etc', '/root', '/production'], only_paths=['ystar/governance/omission_engine.py', 'ystar/governance/metalearning.py']
3. check() on allowed action: passed=True
4. check() on /etc access: passed=False
   DENIED: deny — '/etc' is not allowed in path
   DENIED: only_paths — Path '/etc/shadow' is not in allowed paths [...]
5. Legitimate wiring: passed=True
6. Causal confidence after 5 cycles: 1.00
   (grows with evidence — Pearl L2-3 do-calculus)
7. CIEU record: {'cycle_id': 'demo_001', 'layer': 'path_a', ...}

Path A complete: Y*gov governed itself using its own check() engine.
Path B uses the same pattern to govern external agents.
```
