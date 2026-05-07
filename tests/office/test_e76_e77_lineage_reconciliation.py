import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_phase_a_records_prior_public_read_lineage():
    lineage = _load("operations/external_validation/e76_e77_prior_public_read_lineage_map.json")
    reconciliation = _load("operations/external_validation/e76_e77_public_read_lineage_reconciliation.json")

    assert lineage["existing_public_read_lineage_found"] is True
    assert lineage["lineage_count"] >= 6
    milestone_ids = {row["prior_milestone_id"] for row in lineage["rows"]}
    assert {"E59", "E61", "E67", "E68"}.issubset(milestone_ids)
    assert reconciliation["wrong_narrative_is_false"] is True
    assert reconciliation["prior_public_read_non_contact_work_exists"] is True


def test_lineage_rows_are_bounded_as_public_proxy_not_validation():
    lineage = _load("operations/external_validation/e76_e77_prior_public_read_lineage_map.json")

    for row in lineage["rows"]:
        assert row["contact_or_outreach_occurred"] is False
        assert "customer" not in row["no_overclaim_status"] or "not_customer" in row["no_overclaim_status"]
        assert row["post_E73_L3_gated"] is False

