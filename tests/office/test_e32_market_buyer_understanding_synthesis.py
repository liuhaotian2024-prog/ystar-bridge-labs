import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_market_synthesis_preserves_evidence_boundaries():
    data = json.loads((ROOT / "operations/external_validation/e32_market_buyer_understanding_synthesis.json").read_text())
    assert data["buyer_pain_cluster_count"] >= 7
    assert data["competitor_alternative_category_count"] >= 7
    assert data["pricing_proxy_count"] >= 5
    assert "market_gaps_y_star_cannot_address_yet" in data
