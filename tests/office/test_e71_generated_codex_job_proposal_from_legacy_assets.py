import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e71_generated_codex_job_proposal_comes_from_top_legacy_score():
    proposal = json.loads((ROOT / "operations/external_validation/e71_generated_codex_job_proposal_from_legacy_assets.json").read_text())
    scorecards = json.loads((ROOT / "operations/external_validation/e71_legacy_asset_scorecards.json").read_text())
    assert proposal["generated_from_legacy_asset_scoring"] is True
    assert proposal["source_legacy_asset_cluster"] == scorecards["top_cluster"]
    assert proposal["source_legacy_asset_cluster"] == "k9_cieu_hash_chain_spec_cluster"
    assert proposal["proposed_milestone_id"] == "E72_integrate_K9_CIEU_hash_chain_context_into_CIEU_audit_module"
    assert proposal["owner_approval_status"] == "pending_owner_decision"
    assert proposal["external_action_allowed"] is False

