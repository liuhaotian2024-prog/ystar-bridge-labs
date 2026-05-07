import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e68_legal_caution_policy_prohibits_compliance_and_readiness_claims():
    data = json.loads((ROOT / "operations/external_validation/e68_cieu_no_overclaim_legal_caution_policy.json").read_text())
    assert "CIEU ensures EU AI Act compliance" in data["prohibited_claims"]
    assert "CIEU is medically certified" in data["prohibited_claims"]
    assert "CIEU is suitable for live energy dispatch" in data["prohibited_claims"]
    assert data["legal_advice_disclaimer_required"] is True

