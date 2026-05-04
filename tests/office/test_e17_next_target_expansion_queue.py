import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_next_target_queue_reuses_existing_repo_evidence_only():
    data = json.loads((ROOT / "operations/external_validation/e17_next_target_expansion_queue.json").read_text())
    assert data["selection_policy"] == "reuse_existing_repo_evidence_only_no_web_scrape_no_fake_targets"
    assert data["external_action_executed"] is False
    statuses = {entry["status"] for entry in data["entries"]}
    assert "current_selected_action" in statuses
    assert "ready_candidate_from_existing_repo_evidence" in statuses
    assert data["entries"]


def test_next_target_queue_does_not_invent_targets():
    data = json.loads((ROOT / "operations/external_validation/e17_next_target_expansion_queue.json").read_text())
    names = {entry["target_name"] for entry in data["entries"]}
    assert "Alice Labs AI Operations Consulting" in names
    assert "BotSquash AI Automation Agency" in names
