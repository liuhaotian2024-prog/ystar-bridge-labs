from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e105_open_world_market_discovery_runtime import (
    build_candidates_from_clusters,
    build_open_world_market_discovery_strategy,
    default_open_world_public_read_evidence,
    discover_opportunity_clusters,
    run_e105_open_world_market_discovery_strategy_session,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E105_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E105 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e105_discovers_clusters_and_candidates_from_evidence_feed(tmp_path):
    strategy = build_open_world_market_discovery_strategy(brain_db=_brain_copy(tmp_path))
    proof = strategy["open_world_discovery_proof"]

    assert proof["closed_route_preset_used"] is False
    assert proof["candidate_generation_mode"] == "dynamic_evidence_cluster_derivation"
    assert len(proof["query_expansion_rounds"]) >= 3
    assert len(proof["opportunity_clusters"]) >= 5
    assert proof["unseeded_cluster_count"] >= 1
    assert len(strategy["route_candidates"]) >= 5
    assert all(candidate["source_cluster_ids"] for candidate in strategy["route_candidates"])


def test_e105_unseeded_evidence_category_creates_new_candidate():
    evidence = default_open_world_public_read_evidence() + [
        {
            "evidence_id": "new_vertical_signal",
            "source_title": "Unusual category signal",
            "source_url": "https://example.org/unusual",
            "category": "warehouse_robotics_margin_leak",
            "claim_summary": "Warehouse operators face robotics exception costs and margin leakage.",
            "evidence_type": "public_read_only",
        }
    ]
    clusters = discover_opportunity_clusters(evidence, query_rounds=[{"round_id": "r", "queries": ["warehouse robotics"]}])
    candidates = build_candidates_from_clusters(clusters)

    assert any(cluster["cluster_id"] == "warehouse_robotics_margin_leak" for cluster in clusters)
    assert any(candidate["route_id"] == "warehouse_robotics_margin_leak_rescue" for candidate in candidates)


def test_e105_run_writes_three_cieustore_records_and_passes_governance(tmp_path):
    result = run_e105_open_world_market_discovery_strategy_session(
        cieu_db=tmp_path / "e105.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
    )
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_open_world_strategy_proven"] is True
    assert receipt["Y_star_gov_strategic_decision"] == "ALLOW"
    assert receipt["Y_star_gov_market_refresh_decision"] == "ALLOW"
    assert receipt["Y_star_gov_open_world_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["CIEU_event_count"] >= 3
    assert receipt["closed_route_preset_used"] is False
    assert receipt["candidate_generation_mode"] == "dynamic_evidence_cluster_derivation"
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True
