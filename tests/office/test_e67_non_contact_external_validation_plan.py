import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e67_plan_attempts_ev1_ev4_for_core_routes_without_contact():
    data = json.loads((ROOT / "operations/external_validation/e67_non_contact_external_validation_plan.json").read_text())
    assert data["source_count_planned"] >= 24
    for ev in [
        "EV1_public_market_language",
        "EV2_competitor_or_adjacent_product_presence",
        "EV3_public_pricing_or_packaging_evidence",
        "EV4_public_demand_or_behavior_proxy",
    ]:
        assert ev in data["EV_levels_attempted"]
    assert data["rules"]["no_contact_scraping"] is True
    assert data["rules"]["no_human_identification"] is True

