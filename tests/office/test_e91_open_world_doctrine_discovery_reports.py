from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "operations/ceo_doctrine_registry"


def _load(name: str):
    return json.loads((REPORT_DIR / name).read_text(encoding="utf-8"))


def test_asset_graph_and_required_reports_exist():
    for name in [
        "e91_asset_graph.json",
        "e91_asset_graph_summary.md",
        "e91_query_expansion_log.json",
        "e91_open_world_same_problem_clusters.json",
        "e91_discovery_coverage_proof.json",
        "e91_canonical_doctrine_registry_spec.json",
    ]:
        assert (REPORT_DIR / name).exists()


def test_query_expansion_has_at_least_four_rounds():
    log = _load("e91_query_expansion_log.json")

    assert log["round_count"] >= 4
    assert log["initial_seeds_treated_as_opening_not_ontology"] is True


def test_coverage_proves_old_and_broad_discovery():
    coverage = _load("e91_discovery_coverage_proof.json")

    assert coverage["total_tracked_files_scanned"] >= 34000
    assert coverage["findings_older_than_E86"] > 0
    assert coverage["findings_from_E65_E80"] > 0
    assert coverage["findings_from_L5_or_L6"] >= 0
    assert coverage["findings_in_Y_star_gov"] > 0
    assert coverage["findings_in_gov_mcp"] > 0


def test_clusters_are_not_fixed_prompt_categories_and_include_unseeded_cluster():
    clusters = _load("e91_open_world_same_problem_clusters.json")
    spec = _load("e91_canonical_doctrine_registry_spec.json")

    assert clusters["cluster_count"] >= 15
    assert clusters["unseeded_clusters"]
    assert spec["prompt_categories_used_as_closed_ontology"] is False
    assert spec["unseeded_doctrines"]
    assert spec["doctrine_count"] == clusters["cluster_count"]


def test_reports_do_not_claim_l5d_or_live_execution():
    status = json.loads(
        (ROOT / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e91_open_world_doctrine_enforcement.json").read_text(
            encoding="utf-8"
        )
    )

    assert status["L5-D"] == "absent_or_not_executed"
    assert status["gov_mcp_live_execution"] is False
    assert status["K9Audit_integrated"] is False
