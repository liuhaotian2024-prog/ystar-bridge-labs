from __future__ import annotations

import sqlite3

from office.mission_command.e108_live_global_open_world_strategy_runtime import FixtureGlobalPublicReadProvider
from office.mission_command.e112_cieu_backed_brain_learning_loop import (
    build_brain_mutation_candidates,
    build_failure_residual_candidates,
    build_freshness_rejection_proof,
    build_market_evidence_freshness_policy,
    classify_evidence_freshness,
    filter_market_evidence_for_brain_learning,
    run_cieu_backed_brain_learning_cycle,
)


def test_stale_market_evidence_is_rejected_before_brain_candidate():
    policy = build_market_evidence_freshness_policy()
    item = {
        "evidence_id": "old_competitor",
        "source_title": "Old competitor page",
        "source_url": "https://vendor.example/old",
        "source_date": "2023-01-01",
        "observed_at": "2026-05-09T00:00:00Z",
        "claim_summary": "Competitor alternative signal.",
        "evidence_type": "live_public_read_search_result",
    }
    row = classify_evidence_freshness(item, policy)
    assert row["freshness_status"] == "rejected_stale"
    report = filter_market_evidence_for_brain_learning([item], policy)
    candidates = build_brain_mutation_candidates(
        [row for row in report["freshness_rows"] if row["freshness_status"].startswith("accepted_")]
    )
    assert candidates == []


def test_undated_live_search_result_is_not_durable_brain_learning():
    policy = build_market_evidence_freshness_policy()
    item = {
        "evidence_id": "undated_live_result",
        "source_title": "Current search result but no page date",
        "source_url": "https://vendor.example/no-date",
        "observed_at": "2026-05-09T00:00:00Z",
        "claim_summary": "Market claim without source publication date.",
        "evidence_type": "live_public_read_search_result",
    }
    row = classify_evidence_freshness(item, policy)
    assert row["freshness_status"] == "rejected_missing_source_date_for_brain_learning"


def test_current_competitor_fact_becomes_cieu_backed_candidate():
    policy = build_market_evidence_freshness_policy()
    item = {
        "evidence_id": "fresh_competitor",
        "source_title": "Fresh competitor page",
        "source_url": "https://vendor.example/current",
        "source_date": "2026-04-30",
        "observed_at": "2026-05-09T00:00:00Z",
        "claim_summary": "Competitor and alternative signal is current.",
        "evidence_type": "live_public_read_search_result",
    }
    report = filter_market_evidence_for_brain_learning([item], policy)
    accepted = [row for row in report["freshness_rows"] if row["freshness_status"].startswith("accepted_")]
    candidates = build_brain_mutation_candidates(accepted)
    assert report["accepted_count"] == 1
    assert candidates[0]["candidate_type"] == "competitor_fact_node"
    assert candidates[0]["write_mode"] == "CIEU_backed_candidate_only"
    assert candidates[0]["production_brain_write_performed"] is False


def test_content_type_policy_accepts_durable_operator_and_case_knowledge():
    policy = build_market_evidence_freshness_policy()
    rows = [
        {
            "evidence_id": "peer_lessons",
            "domain_id": "peer_experience_corpus",
            "content_type": "peer_experience",
            "source_title": "Founder lessons",
            "source_url": "https://www.ycombinator.com/library",
            "source_date": "2025-01-01",
            "observed_at": "2026-05-09T00:00:00Z",
            "claim_summary": "Founder/operator lessons should become reusable patterns.",
            "evidence_type": "idle_learning_public_read_evidence",
        },
        {
            "evidence_id": "customer_method",
            "domain_id": "customer_contact_residuals",
            "content_type": "customer_learning_methodology",
            "source_title": "How to talk to users",
            "source_url": "https://www.ycombinator.com/library/6g-how-to-talk-to-users",
            "source_date": "2024-01-01",
            "observed_at": "2026-05-09T00:00:00Z",
            "claim_summary": "Customer conversations are a methodology for future residual learning, not a customer-validation claim.",
            "evidence_type": "idle_learning_public_read_evidence",
        },
        {
            "evidence_id": "historical_case",
            "domain_id": "historical_case_corpus",
            "content_type": "historical_case",
            "source_title": "Startup failure cases",
            "source_url": "https://www.cbinsights.com/research/startup-failure-reasons-top/",
            "source_date": "2025-10-01",
            "observed_at": "2026-05-09T00:00:00Z",
            "claim_summary": "Historical failure cases prevent overfitting to today's preferred thesis.",
            "evidence_type": "idle_learning_public_read_evidence",
        },
    ]

    accepted = [classify_evidence_freshness(item, policy) for item in rows]

    assert {row["freshness_status"] for row in accepted} <= {"accepted_current", "accepted_recent", "accepted_evergreen_context"}
    assert accepted[0]["content_type"] == "peer_experience"
    assert accepted[1]["content_type"] == "customer_learning_methodology"
    assert accepted[2]["content_type"] == "historical_case"


def test_fixture_evidence_is_test_only_not_non_test_brain_learning():
    policy = build_market_evidence_freshness_policy()
    item = {
        "evidence_id": "fixture_market",
        "source_title": "Fixture",
        "source_url": "https://example.com/live/test/1",
        "observed_at": "2026-05-08T00:00:00Z",
        "claim_summary": "Fixture market signal.",
        "evidence_type": "fixture_live_public_read_search_result",
    }
    non_test = classify_evidence_freshness(item, policy, test_mode=False)
    test = classify_evidence_freshness(item, policy, test_mode=True)
    assert non_test["freshness_status"] == "rejected_fixture_without_test_mode"
    assert test["freshness_status"] == "accepted_test_fixture_current"
    assert test["durability"] == "test_only"


def test_failure_residuals_reuse_czl_tuple_shape():
    residuals = build_failure_residual_candidates(
        strategy={
            "route_math_scores": [
                {
                    "route_id": "route_a",
                    "name": "Route A",
                    "market_first_score": 1.2,
                    "why_it_might_fail": "competition is underestimated",
                    "evidence_refs": ["fresh_competitor"],
                }
            ]
        },
        freshness_report={"rejected_status_counts": {}, "rejected_evidence_ids": []},
    )
    residual = residuals[0]
    assert residual["residual_loop_engine_path"] == "ystar/governance/residual_loop_engine.py"
    assert set(residual["CZL_residual_tuple"]) == {"X_t", "U", "Y_star", "Y_t_plus_1", "R_t_plus_1"}
    assert residual["CZL_residual_tuple"]["R_t_plus_1"] > 0


def test_rejection_proof_blocks_stale_and_undated_evidence():
    proof = build_freshness_rejection_proof()
    assert proof["accepted_count"] == 0
    assert proof["rejected_count"] == 2
    assert proof["brain_candidate_count_from_rejected_items"] == 0


def test_full_e112_cycle_writes_brain_learning_cieu_record_without_production_brain_write(tmp_path):
    db = tmp_path / "e112_cycle.db"
    result = run_cieu_backed_brain_learning_cycle(
        cieu_db=db,
        provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
        test_mode=True,
        seal_session=False,
    )
    assert result["brain_learning_loop_proven"] is True
    assert result["production_brain_write_performed"] is False
    assert result["freshness_filter_summary"]["accepted_count"] > 0
    assert result["brain_learning_packet"]["brain_mutation_candidates"]
    assert result["brain_learning_packet"]["failure_residual_candidates"]
    assert result["brain_learning_packet"]["CZL_residual_loop_linkage"]["uses_existing_czl_mechanism"] is True
    assert result["brain_learning_packet"]["failure_residual_candidates"][0]["CZL_residual_tuple"]
    assert result["YstarGov_brain_learning_write_result"]["governance_decision"]["decision"] == "ALLOW"
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT event_type FROM cieu_events ORDER BY seq_global").fetchall()
    event_types = [row[0] for row in rows]
    assert "CEO_BRAIN_LEARNING_LOOP_DECISION" in event_types
    assert "AIDEN_HOST_RUNTIME_CYCLE_DECISION" in event_types
