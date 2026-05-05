import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_frontier_strategy_selects_black_box_mvp_without_live_or_fake_signal():
    selection = json.loads((ROOT / "operations/external_validation/e32_shock_level_mvp_selection.json").read_text())
    run = json.loads((ROOT / "operations/external_validation/e32_frontier_research_run.json").read_text())
    czl = json.loads((ROOT / "operations/external_validation/e32_czl_closure.json").read_text())
    assert selection["selected_mvp"] == "mvp_agent_action_black_box"
    assert selection["candidates_generated"] >= 5
    assert "mvp_no_fake_agent_evidence_pack" in selection["backup_mvps"]
    assert run["research_status"] == "executed"
    assert run["source_count"] == 12
    assert run["receipt_count"] == 12
    assert czl["customer_contact_occurred"] is False
    assert czl["published_externally"] is False
    assert czl["production_live_receipt_count"] == 0
    assert czl["fake_evidence_created"] is False
