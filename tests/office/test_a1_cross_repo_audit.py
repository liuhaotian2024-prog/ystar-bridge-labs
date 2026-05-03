from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "cross_repo"


def test_a1_outputs_exist() -> None:
    expected = [
        "a1_y_star_gov_full_evidence_chain.md",
        "a1_runtime_alignment_matrix.json",
        "a1_canonical_ownership_map.json",
        "a1_backflow_p0_p1_p2_plan.md",
        "a1_duplicate_conflict_register.json",
        "a1_y_star_gov_maturity_scorecard.json",
    ]
    for name in expected:
        assert (REPORTS / name).exists(), name


def test_a1_y_star_gov_full_coverage_categories() -> None:
    report = (REPORTS / "a1_y_star_gov_full_evidence_chain.md").read_text(encoding="utf-8")
    for term in [
        "governance validators",
        "Pre-U packet validation",
        "CIEU / prediction delta / residual",
        "approval records / approval lifecycle",
        "delegation contracts",
        "obligation registration",
        "hook adapters / dry-run contract harness",
        "MCP decision envelope",
        "release preflight",
    ]:
        assert term in report


def test_a1_alignment_matrix_has_required_rows() -> None:
    matrix = json.loads((REPORTS / "a1_runtime_alignment_matrix.json").read_text(encoding="utf-8"))
    rows = {row["capability"] for row in matrix["rows"]}
    for capability in [
        "target lifecycle",
        "evidence/signal",
        "action authorization",
        "learning writeback",
        "closure status",
        "counterfactual",
        "approval record",
        "feedback event",
        "action ledger",
        "host delivery",
        "MCP execution",
        "CIEU residual",
        "obligation registration",
        "release/live boundary",
        "commercial validation",
    ]:
        assert capability in rows


def test_a1_ownership_map_covers_four_repos() -> None:
    ownership = json.loads((REPORTS / "a1_canonical_ownership_map.json").read_text(encoding="utf-8"))
    assert set(ownership["repos"]) == {"Y-star-gov", "gov-mcp", "ystar-bridge-labs", "ystar-company"}
    assert "deterministic validators" in ownership["repos"]["Y-star-gov"]["canonical_owner_of"]
    assert "governed tool execution gateway" in ownership["repos"]["gov-mcp"]["canonical_owner_of"]


def test_a1_backflow_plan_has_priorities_and_conflicts() -> None:
    plan = (REPORTS / "a1_backflow_p0_p1_p2_plan.md").read_text(encoding="utf-8")
    assert "## P0" in plan and "## P1" in plan and "## P2" in plan
    conflicts = json.loads((REPORTS / "a1_duplicate_conflict_register.json").read_text(encoding="utf-8"))
    assert len(conflicts["conflicts"]) >= 5
    assert any("gov-mcp" in item["recommended_next_action"] for item in conflicts["conflicts"])


def test_a1_scorecard_records_maturity_gaps() -> None:
    scorecard = json.loads((REPORTS / "a1_y_star_gov_maturity_scorecard.json").read_text(encoding="utf-8"))
    assert len(scorecard["items"]) >= 10
    assert any(item["score"] >= 4 for item in scorecard["items"])
    assert any("commercial" in item["primary_gap"].lower() for item in scorecard["items"])
