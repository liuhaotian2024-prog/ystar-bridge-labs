import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_provider_category_selects_email_without_api_calls():
    d = json.loads((ROOT / "operations/external_validation/e28_provider_category_comparison.json").read_text())
    assert d["selected_provider_category"] == "email_provider_adapter"
    assert "crm_outreach_provider_adapter" in d["rejected_categories"]
    assert d["provider_uncertainty"] == "medium"
    assert d["provider_selection_research_needed"] is False
    assert d["api_calls_made"] is False
    assert d["credentials_required_now"] is False
