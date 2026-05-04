import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_decisions_justify_every_new_wheel():
    d = json.loads((ROOT / "operations/external_validation/e27_reuse_wrap_extend_build_decision.json").read_text())
    assert d["all_new_wheels_have_justification"] is True
    decisions = {row["capability"]: row["decision"] for row in d["decisions"]}
    assert decisions["live-test configuration profile"] == "build_missing"
    assert decisions["persistent idempotency test profile"] == "extend_existing"
    assert decisions["production live receipt boundary"] == "wrap_existing"
