import json
from pathlib import Path

from office.mission_command.e18_batch_target_selection import E18_TARGET_STATUSES, build_revenue_validation_batch, classify_candidate

ROOT = Path(__file__).resolve().parents[2]


def test_batch_target_selection_classifies_ready_and_blocked_candidates():
    data = json.loads((ROOT / "operations/external_validation/e18_revenue_validation_batch.json").read_text())
    assert data["selection_policy"] == "existing_repo_evidence_only_no_scraping_no_fake_targets"
    assert data["candidate_count"] >= 5
    assert data["ready_for_owner_review_count"] >= 3
    assert data["external_action_executed"] is False
    statuses = {item["status"] for item in data["candidates"]}
    assert statuses <= set(E18_TARGET_STATUSES)
    assert "ready_for_owner_review" in statuses


def test_classify_candidate_never_treats_missing_evidence_as_ready():
    assert classify_candidate({"role": "primary", "target_evidence_basis": [], "missing_fields": []}) == "blocked_missing_source"
    assert classify_candidate({"role": "primary", "target_evidence_basis": ["src"], "missing_fields": ["channel"]}) == "needs_more_evidence"
