import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_reuse_wrap_build_decision_is_standalone_and_justified():
    d = json.loads((ROOT / "operations/external_validation/e28r_reuse_wrap_build_decision.json").read_text())
    assert d["all_new_wheels_have_justification"] is True
    assert d["newly_built_wheels_count"] == 3
    assert "build_missing" in {row["decision"] for row in d["decisions"]}
