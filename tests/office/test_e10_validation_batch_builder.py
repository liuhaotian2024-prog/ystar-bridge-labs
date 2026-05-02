from office.mission_command.e10_autonomous_target_discovery import load_or_run_e10_target_discovery
from office.mission_command.e10_shortest_revenue_path_scorer import rank_e10_shortest_revenue_paths
from office.mission_command.e10_target_candidate_registry import build_e10_target_candidate_registry
from office.mission_command.e10_validation_batch_builder import build_e10_validation_batches


def _batches():
    candidates = build_e10_target_candidate_registry(load_or_run_e10_target_discovery()["sources"])
    scores = rank_e10_shortest_revenue_paths(candidates)
    return build_e10_validation_batches(candidates, scores)


def test_validation_batch_builder_creates_at_least_3_batches():
    assert len(_batches()) >= 3


def test_recommended_batch_has_shortest_path_reason():
    batch = _batches()[0]
    assert batch.batch_id == "batch_ai_ops_agency_governance_layer"
    assert "shortest" in batch.why_this_is_shortest_path.lower()
    assert batch.owner_approval_required
