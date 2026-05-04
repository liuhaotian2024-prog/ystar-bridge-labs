import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_new_e29_wheels_have_allowed_justification():
    data = json.loads((ROOT / "operations/external_validation/e29_reuse_wrap_extend_build_decision.json").read_text())
    assert data["all_new_wheels_have_build_missing_or_extend_existing_justification"] is True
    assert data["newly_built_wheels_count"] == 4
    assert set(data["new_implementation_allowed_only_for"]) == {"build_missing", "extend_existing"}
