import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OPS = ROOT / "operations" / "external_validation"


def test_proposed_manifest_is_not_treated_as_approval():
    manifest = json.loads((OPS / "e10_external_validation_manifest.proposed.json").read_text(encoding="utf-8"))
    assert manifest["proposal_only"] is True
    assert manifest["template_is_approval"] is False
    assert manifest["external_contact_authorized"] is False


def test_proposed_target_seeds_are_not_contact_approved():
    payload = json.loads((OPS / "e10_target_seeds.proposed.json").read_text(encoding="utf-8"))
    assert payload["proposal_only"] is True
    assert payload["contact_authorized"] is False
    assert all(target["owner_approved_for_contact"] is False for target in payload["targets"])
    assert all(target["contact_executed"] is False for target in payload["targets"])
