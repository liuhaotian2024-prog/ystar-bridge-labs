import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_reuse_decision_justifies_new_commercial_wheels_only():
    d = json.loads((ROOT / "operations/external_validation/e28_reuse_wrap_extend_build_decision.json").read_text())
    assert d["all_new_wheels_have_justification"] is True
    assert d["gov_mcp_modification_needed"] is False
    decisions = {row["capability"]: row["decision"] for row in d["decisions"]}
    assert decisions["production live configuration decision gate"] == "build_missing"
    assert decisions["live-readiness validator update"] == "reuse_existing"
