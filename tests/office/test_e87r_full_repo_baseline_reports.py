from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = ROOT / "operations/baseline/e87r_full_repo_baseline"


def load_json(name: str) -> dict:
    return json.loads((BASELINE_DIR / name).read_text(encoding="utf-8"))


def test_file_manifests_exist_for_all_three_repos():
    expected = {
        "bridge_labs_file_manifest.json": "bridge_labs",
        "Y_star_gov_file_manifest.json": "Y_star_gov",
        "gov_mcp_file_manifest.json": "gov_mcp",
    }
    for filename, repo in expected.items():
        manifest = load_json(filename)
        assert manifest["repo"] == repo
        assert manifest["tracked_file_count"] > 0
        assert len(manifest["tracked_files"]) == manifest["tracked_file_count"]
        assert "counts_by_category" in manifest
        assert "counts_by_extension" in manifest


def test_code_index_exists_and_covers_all_repo_python_files():
    index = load_json("code_index.json")

    assert index["counts"]["total_tracked_files"] >= 34000
    assert index["counts"]["total_python_files"] >= 3000
    assert index["counts"]["total_functions"] >= 10000
    assert index["counts"]["total_classes"] >= 1000
    assert set(index["counts_by_repo"]) == {"bridge_labs", "Y_star_gov", "gov_mcp"}
    assert index["python_symbol_index"]


def test_architecture_vocabulary_l5_gap_and_roadmap_reports_exist():
    for filename in [
        "architecture_evidence_map.json",
        "stable_vocabulary_and_owner_map.json",
        "l5_truth_table.json",
        "final_goal_gap_analysis.json",
        "next_engineering_roadmap.json",
        "baseline_summary.json",
    ]:
        assert (BASELINE_DIR / filename).exists(), filename
        assert load_json(filename)["artifact_id"].startswith("e87r_")


def test_vocabulary_does_not_claim_gov_mcp_is_sole_behavior_center():
    vocab = load_json("stable_vocabulary_and_owner_map.json")
    terms = {item["term"]: item for item in vocab["terms"]}

    assert terms["CEO behavior center"]["canonical_owner"] == "bridge-labs"
    assert terms["execution boundary"]["canonical_owner"] == "gov-mcp"
    assert any("gov-mcp is not the sole behavior center" in item for item in vocab["guardrails"])


def test_cieustore_and_k9audit_boundaries_are_distinguished():
    vocab = load_json("stable_vocabulary_and_owner_map.json")
    terms = {item["term"]: item for item in vocab["terms"]}

    assert terms["CIEU memory / audit store"]["canonical_owner"] == "Y-star-gov"
    assert terms["K9Audit evidence chain"]["canonical_owner"] == "K9Audit"
    assert "no integration write claimed" in load_json("baseline_summary.json")["real_architecture_baseline"]["K9Audit_boundary"]


def test_l5_truth_table_does_not_claim_revenue_loop_complete():
    l5 = load_json("l5_truth_table.json")
    statuses = {item["level"]: item["status"] for item in l5["levels"]}

    assert statuses["L5-A Runtime Foundation"] in {"partial_to_complete_foundation", "partial", "complete"}
    assert statuses["L5-C Controlled External Action"] == "partial_dry_run_only"
    assert statuses["L5-D Revenue/Customer/Payment Loop"] == "absent_or_not_executed"


def test_gov_mcp_live_execution_is_not_claimed():
    architecture = load_json("architecture_evidence_map.json")
    gov_domain = next(item for item in architecture["domains"] if item["domain_id"] == "gov_mcp_execution_boundary")

    assert gov_domain["status"] == "active_dry_run"
    assert any("No live provider execution" in gap for gap in gov_domain["gaps"])


def test_roadmap_uses_major_closure_milestones_not_tiny_tasks():
    roadmap = load_json("next_engineering_roadmap.json")
    milestones = roadmap["milestones"]

    assert len(milestones) == 5
    assert milestones[0]["milestone"].startswith("E87_")
    assert milestones[-1]["milestone"].startswith("E91_")
    for milestone in milestones:
        assert "runtime_chain_to_prove" in milestone
        assert "completion_criteria" in milestone
        assert "what_must_not_be_claimed" in milestone
