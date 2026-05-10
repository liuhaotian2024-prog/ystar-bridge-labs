"""Tests for E94 strategic input ingestion pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from office.mission_command.e94_strategic_input_ingestion import (  # noqa: E402
    build_strategic_input_packet,
    extract_constraint_set_from_packet,
    extract_evidence_pool_from_packet,
    extract_open_questions_from_packet,
    extract_route_candidates_from_packet,
)


@pytest.fixture
def packet():
    """One full packet built from real repo state — used by all tests."""
    return build_strategic_input_packet(repo_root=REPO_ROOT)


def test_packet_has_required_top_level_fields(packet):
    """Packet must always carry these top-level keys for downstream consumers."""
    assert "packet_id" in packet
    assert "generated_at" in packet
    assert "sources" in packet
    assert "synthesized_views" in packet


def test_strat_001_parses_with_unnumbered_section_format(packet):
    """STRAT-001 uses unnumbered ## headings; parser must still find content."""
    memos = packet["sources"]["strategy_memos"]
    strat_001 = next((m for m in memos if m["archive_id"] == "STRAT-001"), None)
    assert strat_001 is not None, "STRAT-001 must be discoverable"
    assert len(strat_001["sections"]) > 0, (
        "STRAT-001 sections must not be empty even though it uses unnumbered ## headings"
    )
    assert len(strat_001["constraints"]) > 0, (
        "STRAT-001 contains 4 numbered Strategic Positions which must be extracted as constraints"
    )


def test_strat_002_parses_with_numbered_section_format(packet):
    """STRAT-002 uses numbered ## headings; parser must extract claims, constraints, open questions."""
    memos = packet["sources"]["strategy_memos"]
    strat_002 = next((m for m in memos if m["archive_id"] == "STRAT-002"), None)
    assert strat_002 is not None, "STRAT-002 must be discoverable"

    # STRAT-002 has 11 numbered sections
    assert len(strat_002["sections"]) >= 8, (
        f"STRAT-002 should have >=8 sections, got {len(strat_002['sections'])}"
    )

    # §3 has 3 subsections of evidence
    assert len(strat_002["claims"]) > 0, "STRAT-002 §3 must yield claims"

    # §2 has 8 numbered owner constraints
    assert len(strat_002["constraints"]) > 0, "STRAT-002 §2 must yield owner constraints"

    # §8 has 7 open questions
    assert len(strat_002["open_questions"]) > 0, "STRAT-002 §8 must yield open questions"


def test_e34_opportunity_spaces_ingested(packet):
    """All 22 e34 opportunity spaces must be ingested as candidate routes."""
    artifacts = packet["sources"]["e34_artifacts"]
    op_artifact = next(
        (a for a in artifacts if a.get("artifact_id") == "e34_non_obvious_opportunity_spaces"),
        None,
    )
    assert op_artifact is not None, "e34_non_obvious_opportunity_spaces.json must ingest"
    assert len(op_artifact.get("opportunity_spaces", [])) == 22


def test_e34_voids_ingested(packet):
    """All 12 e34 institutional voids must be ingested."""
    artifacts = packet["sources"]["e34_artifacts"]
    void_artifact = next(
        (a for a in artifacts if a.get("artifact_id") == "e34_institutional_void_mapper"),
        None,
    )
    assert void_artifact is not None, "e34_institutional_void_mapper.json must ingest"
    assert len(void_artifact.get("voids", [])) == 12


def test_dead_path_forbidden_patterns_extracted(packet):
    """Defuse dead-path forbidden patterns must be parsed (Chinese 禁止 heading style)."""
    constraints = extract_constraint_set_from_packet(packet)
    assert len(constraints["dead_path_forbidden_patterns"]) > 0, (
        "Dead-path forbidden patterns must be extracted from Chinese-headed dead_path docs"
    )


def test_route_candidates_expand_beyond_baseline(packet):
    """E94 must produce more route candidates than the 6-route hardcoded baseline."""
    routes = extract_route_candidates_from_packet(packet)
    assert len(routes) > 6, (
        f"E94 ingestion must yield >6 routes (baseline was 6), got {len(routes)}"
    )


def test_e34_opportunity_spaces_appear_as_routes(packet):
    """All 22 e34 opportunity spaces should surface as candidate routes."""
    routes = extract_route_candidates_from_packet(packet)
    op_routes = [r for r in routes if r.get("route_type") == "opportunity_candidate"]
    assert len(op_routes) >= 22, (
        f"All 22 e34 opportunity spaces should surface as route candidates, got {len(op_routes)}"
    )


def test_evidence_pool_classifies_verified_vs_unverified(packet):
    """Evidence pool must classify by status (independently_verified / reported_unverified / corrected)."""
    pool = extract_evidence_pool_from_packet(packet)
    assert len(pool) > 0, "Evidence pool must not be empty when STRAT-002 is present"

    statuses = {claim["status"] for claim in pool}
    assert "independently_verified" in statuses, (
        "STRAT-002 §3.1 evidence must be classified as independently_verified"
    )


def test_open_questions_carry_source_memo(packet):
    """Open questions must carry their source memo archive_id for traceability."""
    questions = extract_open_questions_from_packet(packet)
    assert len(questions) > 0
    for q in questions:
        assert "source_memo" in q
        assert q["source_memo"].startswith("STRAT-")


def test_e90_route_candidates_expanded_after_e94():
    """End-to-end: e90._route_candidates() must return more than 6 routes when E94 is active."""
    # Reset to ensure fresh import
    for mod in list(sys.modules.keys()):
        if "mission_command" in mod:
            del sys.modules[mod]
    from office.mission_command.e90_market_grounded_strategy_run import (  # noqa: E402
        _baseline_route_candidates,
        _route_candidates,
    )

    baseline = _baseline_route_candidates()
    full = _route_candidates(repo_root=REPO_ROOT)

    assert len(baseline) == 6, "Baseline must remain 6 (regression guard)"
    assert len(full) > len(baseline), (
        f"After E94, _route_candidates() must return >{len(baseline)} routes, got {len(full)}"
    )


def test_e90_baseline_fallback_when_packet_disabled():
    """E94 ingestion failure must NOT block e90; fallback to baseline."""
    for mod in list(sys.modules.keys()):
        if "mission_command" in mod:
            del sys.modules[mod]
    from office.mission_command.e90_market_grounded_strategy_run import (  # noqa: E402
        _route_candidates,
    )

    # Pass a path that exists but contains no STRAT memos / e34 artifacts
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        empty_root = Path(tmp)
        # When the repo has no strategic input, baseline 6 must still come through
        routes = _route_candidates(repo_root=empty_root)
        assert len(routes) >= 6, (
            "E90 must fall back to baseline 6 when ingestion produces nothing"
        )


def test_freshness_warnings_flag_milestone_vs_memo_drift(packet):
    """When a frozen milestone snapshot coexists with a newer STRAT memo, packet must flag it."""
    warnings = packet["synthesized_views"]["freshness_warnings"]
    assert len(warnings) > 0, (
        "Freshness warnings must surface when milestone inventories are older than STRAT memos"
    )
