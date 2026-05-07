import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_corrected_naming_registry_forbids_false_first_read_narrative():
    registry = json.loads((ROOT / "operations/external_validation/e76_e77_corrected_l3_milestone_naming_registry.json").read_text())

    assert "first external read-only research" in registry["forbidden_naming"]
    assert "first public-read validation" in registry["forbidden_naming"]
    assert "first controlled read-only research in project history" in registry["forbidden_naming"]
    assert "first post-E73 CEO-readiness-gated owner-approved L3 read-only pilot" in registry["correct_naming"]
    assert registry["naming_gate_passed"] is True


def test_reconciliation_uses_corrected_post_e73_narrative():
    reconciliation = json.loads((ROOT / "operations/external_validation/e76_e77_public_read_lineage_reconciliation.json").read_text())

    assert "Historical public-read and non-contact validation already exists" in reconciliation["corrected_narrative"]
    assert "post-E73 CEO-readiness-gated owner-approved L3 read-only pilot" in reconciliation["corrected_narrative"]

