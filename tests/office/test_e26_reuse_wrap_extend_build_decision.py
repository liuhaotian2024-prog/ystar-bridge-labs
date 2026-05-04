import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_reuse_decisions_justify_every_new_wheel():
    d=json.loads((ROOT/"operations/external_validation/e26_reuse_wrap_extend_build_decision.json").read_text())
    assert d["all_new_wheels_have_justification"] is True
    decisions={r["capability"]:r["decision"] for r in d["decisions"]}
    assert decisions["persistent idempotency"]=="extend_existing"
    assert decisions["live receipt boundary"]=="build_missing"
