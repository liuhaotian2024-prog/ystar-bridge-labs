from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from office.mission_command.e108_live_global_open_world_strategy_runtime import (
    FixtureGlobalPublicReadProvider,
    build_e108_live_global_open_world_strategy,
    run_e108_live_global_open_world_strategy_session,
)


BRIDGE_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"
YSTAR_ROOT = Path(os.environ.get("E108_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
pytestmark = pytest.mark.skipif(not BRAIN_DB.exists(), reason="E108 requires aiden_brain.db")


def _brain_copy(tmp_path: Path) -> Path:
    copied = tmp_path / "aiden_brain_copy.db"
    shutil.copy2(BRAIN_DB, copied)
    return copied


def test_e108_builds_live_global_scan_not_snapshot(tmp_path):
    strategy = build_e108_live_global_open_world_strategy(
        owner_intent="Find the easiest global money path.",
        brain_db=_brain_copy(tmp_path),
        provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
    )
    scan = strategy["live_global_open_world_scan"]

    assert scan["scan_mode"] == "owner_supplied_live_public_read"
    assert scan["live_public_read_performed"] is True
    assert len(scan["scan_domains"]) >= 12
    assert len(scan["evidence_items"]) >= 24
    assert len(scan["opportunity_clusters"]) >= 10
    assert len(strategy["route_candidates"]) >= 10
    assert scan["anchor_proximity_audit"]["globally_ranked_against_non_adjacent_domains"] is True
    assert scan["anchor_proximity_audit"]["selected_route_is_prior_anchor_clone"] is False


def test_e108_candidates_are_dynamic_and_non_anchor_domains_exist(tmp_path):
    strategy = build_e108_live_global_open_world_strategy(
        brain_db=_brain_copy(tmp_path),
        provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
    )

    assert all(candidate["candidate_source"] == "live_evidence_cluster" for candidate in strategy["route_candidates"])
    assert sum(1 for domain in strategy["live_global_open_world_scan"]["scan_domains"] if domain["adjacent_to_prior_anchor"] is False) >= 8
    assert any(candidate["adjacent_to_prior_anchor"] is False for candidate in strategy["route_candidates"])


def test_e108_runtime_writes_live_global_and_math_cieustore_records(tmp_path):
    result = run_e108_live_global_open_world_strategy_session(
        cieu_db=tmp_path / "e108.db",
        brain_db=_brain_copy(tmp_path),
        ystar_gov_root=YSTAR_ROOT,
        provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
    )
    receipt = result["CEO_runtime_receipt"]

    assert result["end_to_end_live_global_open_world_strategy_proven"] is True
    assert receipt["Y_star_gov_live_global_decision"] == "ALLOW"
    assert receipt["Y_star_gov_math_model_decision"] == "ALLOW"
    assert receipt["CIEUStore_written"] is True
    assert receipt["CIEU_event_count"] >= 2
    assert receipt["scan_domain_count"] >= 12
    assert receipt["route_candidate_count"] >= 10
    assert receipt["truth_boundary"]["no_customer_validation"] is True
    assert receipt["truth_boundary"]["no_revenue_or_payment_signal"] is True
