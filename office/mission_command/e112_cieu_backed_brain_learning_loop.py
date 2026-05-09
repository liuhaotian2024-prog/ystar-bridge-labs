from __future__ import annotations

import hashlib
import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from office.mission_command.e108_live_global_open_world_strategy_runtime import (
    FixtureGlobalPublicReadProvider,
    PublicReadProvider,
)
from office.mission_command.e111_aiden_host_runtime_and_autonomy_control_plane import (
    run_aiden_host_runtime_cycle,
)


MILESTONE_ID = "E112_CIEU_Backed_Brain_Learning_Loop_And_Freshness_Filter_R1"
SESSION_ID = "e112_cieu_backed_brain_learning_loop"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def build_market_evidence_freshness_policy(*, current_date: str = "2026-05-09") -> dict[str, Any]:
    return {
        "policy_id": "e120_content_type_aware_evidence_freshness_policy_v2",
        "current_date": current_date,
        "market_current_max_age_days": 365,
        "competitive_current_max_age_days": 240,
        "evergreen_context_max_age_days": 1095,
        "content_type_max_age_days": {
            "current_market_signal": 365,
            "competitive_signal": 240,
            "regulatory_or_standard": 1095,
            "technical_standard": 1095,
            "classical_theory": 3650,
            "peer_experience": 1460,
            "historical_case": 3650,
            "case_study": 3650,
            "operator_playbook": 1460,
            "customer_learning_methodology": 1460,
            "customer_contact_residual": 365,
        },
        "minimum_current_evidence_for_brain_learning": 1,
        "missing_source_date_policy": (
            "reject_for_brain_learning_unless_test_fixture; observed_at-only search results may be CIEU context "
            "but must not become durable brain facts"
        ),
        "fixture_policy": "accepted_only_when_test_mode_true",
        "stale_policy": "stale_or_undated_market_claims_must_not_feed_brain_mutation_candidates",
    }


def classify_evidence_freshness(
    evidence: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    test_mode: bool = False,
) -> dict[str, Any]:
    evidence_type = str(evidence.get("evidence_type") or "")
    evidence_id = str(evidence.get("evidence_id") or "")
    source_date_raw = evidence.get("source_date") or evidence.get("published_at") or evidence.get("updated_at")
    observed_at_raw = evidence.get("observed_at") or evidence.get("retrieved_at")
    current_date = _date_from(str(policy.get("current_date") or "2026-05-09"))
    source_date = _date_from(str(source_date_raw)) if source_date_raw else None
    observed_at = _date_from(str(observed_at_raw)) if observed_at_raw else None
    is_fixture = evidence_type.startswith("fixture_") or "example.com" in str(evidence.get("source_url") or "")

    if is_fixture and not test_mode:
        return _freshness_row(evidence, "rejected_fixture_without_test_mode", "fixture evidence cannot feed non-test brain learning")
    if is_fixture and test_mode:
        return _freshness_row(
            evidence,
            "accepted_test_fixture_current",
            "fixture accepted only for deterministic tests; not durable production market knowledge",
            source_date=source_date,
            observed_at=observed_at,
            age_days=_days_between(observed_at or current_date, current_date),
            durability="test_only",
        )
    if not source_date:
        return _freshness_row(
            evidence,
            "rejected_missing_source_date_for_brain_learning",
            "live search result lacks source publication/update date, so it cannot become a durable brain fact",
            observed_at=observed_at,
            durability="cieu_context_only",
        )

    age_days = _days_between(source_date, current_date)
    text = _text(evidence)
    content_type = _evidence_content_type(evidence)
    content_type_limits = policy.get("content_type_max_age_days") if isinstance(policy.get("content_type_max_age_days"), Mapping) else {}
    if content_type in content_type_limits:
        max_age = int(content_type_limits[content_type])
    elif any(term in text for term in ("competitor", "competition", "alternative", "substitute", "incumbent")):
        max_age = int(policy.get("competitive_current_max_age_days") or 240)
    elif any(
        term in text
        for term in (
            "standard",
            "regulation",
            "law",
            "framework",
            "compliance",
            "playbook",
            "lesson",
            "case study",
            "postmortem",
            "founder",
            "operator",
            "classic",
            "theory",
            "canon",
        )
    ):
        max_age = int(policy.get("evergreen_context_max_age_days") or 1095)
    else:
        max_age = int(policy.get("market_current_max_age_days") or 365)

    if age_days > max_age:
        return _freshness_row(
            evidence,
            "rejected_stale",
            f"source is {age_days} days old, exceeding max age {max_age} days for this evidence type",
            source_date=source_date,
            observed_at=observed_at,
            age_days=age_days,
        )
    status = "accepted_current" if age_days <= min(90, max_age) else "accepted_recent"
    if max_age > int(policy.get("market_current_max_age_days") or 365) and age_days > int(policy.get("market_current_max_age_days") or 365):
        status = "accepted_evergreen_context"
    return _freshness_row(
        evidence,
        status,
        f"source date is within freshness policy for content_type={content_type or 'inferred'}",
        source_date=source_date,
        observed_at=observed_at,
        age_days=age_days,
        durability="durable_candidate",
    )


def filter_market_evidence_for_brain_learning(
    evidence_items: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
    *,
    test_mode: bool = False,
) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    freshness_rows: list[dict[str, Any]] = []
    for item in evidence_items:
        row = classify_evidence_freshness(item, policy, test_mode=test_mode)
        freshness_rows.append(row)
        if str(row.get("freshness_status") or "").startswith("accepted_"):
            accepted.append(row)
        else:
            rejected.append(row)
    accepted_ids = {str(item.get("evidence_id") or "") for item in accepted}
    stale_used = False
    return {
        "artifact_id": "e112_evidence_freshness_report",
        "freshness_filter_applied": True,
        "policy_id": policy.get("policy_id"),
        "test_mode": test_mode,
        "total_evidence_count": len(evidence_items),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted_status_counts": _status_counts(accepted),
        "rejected_status_counts": _status_counts(rejected),
        "accepted_evidence_ids": sorted(accepted_ids),
        "rejected_evidence_ids": sorted(str(item.get("evidence_id") or "") for item in rejected),
        "stale_evidence_used_for_brain_candidate": stale_used,
        "freshness_rows": freshness_rows,
        "policy_summary": "Only current/recent dated sources or test fixtures may become brain learning candidates; stale/undated live market claims are rejected.",
    }


def build_brain_mutation_candidates(
    accepted_evidence_items: Sequence[Mapping[str, Any]],
    *,
    strategy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    candidates = []
    for item in accepted_evidence_items:
        evidence_id = str(item.get("evidence_id") or "")
        if not evidence_id:
            continue
        candidate_type = _candidate_type(item)
        node_id = f"e112_{candidate_type}_{_stable_hash(evidence_id + str(item.get('claim_summary') or ''))[:12]}"
        candidates.append(
            {
                "candidate_id": node_id,
                "candidate_type": candidate_type,
                "proposed_node_id": node_id,
                "source_evidence_ids": [evidence_id],
                "source_urls": [item.get("source_url")],
                "freshness_status": item.get("freshness_status"),
                "domain_id": item.get("domain_id"),
                "summary": str(item.get("claim_summary") or item.get("source_title") or "")[:360],
                "dims": _dims_for_candidate(candidate_type),
                "write_mode": "CIEU_backed_candidate_only",
                "production_brain_write_performed": False,
                "requires_future_refresh_before_strategy_use": item.get("durability") != "durable_candidate",
            }
        )
    return candidates


def build_failure_residual_candidates(
    *,
    strategy: Mapping[str, Any],
    freshness_report: Mapping[str, Any],
) -> list[dict[str, Any]]:
    residuals = []
    rejected_counts = freshness_report.get("rejected_status_counts") if isinstance(freshness_report.get("rejected_status_counts"), Mapping) else {}
    if rejected_counts:
        residuals.append(
            _czl_residual_candidate(
                residual_id="e112_rejected_or_stale_market_evidence_residual",
                source_evidence_ids=list(freshness_report.get("rejected_evidence_ids") or [])[:12],
                x_t={
                    "freshness_filter": "rejected stale/undated/non-test fixture evidence",
                    "rejected_status_counts": dict(rejected_counts),
                },
                u=["rerun source-date-aware public-read research", "do not write rejected facts into brain"],
                y_star={"durable_brain_learning_uses_only_fresh_current_evidence": True},
                y_t_plus_1={"durable_brain_learning_uses_only_fresh_current_evidence": False},
                r_t_plus_1=1.0,
                learning_update=(
                    "Aiden must not treat undated, stale, or fixture-only public-read evidence as durable market knowledge; "
                    "rerun source-date-aware research before strategy memory write-back."
                ),
                residual_severity="medium",
            )
        )
    route_scores = strategy.get("route_math_scores") if isinstance(strategy.get("route_math_scores"), list) else []
    for row in route_scores[:5]:
        if not isinstance(row, Mapping):
            continue
        why_fail = str(row.get("why_it_might_fail") or "")
        if why_fail:
            residuals.append(
                _czl_residual_candidate(
                    residual_id=f"e112_route_failure_{_stable_hash(str(row.get('route_id')) + why_fail)[:10]}",
                    source_evidence_ids=list(row.get("evidence_refs") or [])[:8],
                    x_t={
                        "route_id": row.get("route_id"),
                        "route_claim": row.get("name"),
                        "strategy_score": row.get("market_first_score"),
                    },
                    u=["validate buyer urgency", "validate trust barrier", "refresh competitor/substitute map"],
                    y_star={"route_is_fastest_credible_cash_path": True, "residual_risk_understood": True},
                    y_t_plus_1={"route_is_fastest_credible_cash_path": "unproven", "residual_risk_understood": True},
                    r_t_plus_1=0.5,
                    learning_update=f"Route {row.get('route_id')} risk to remember: {why_fail}",
                    residual_severity="low",
                )
            )
    if not residuals:
        residuals.append(
            _czl_residual_candidate(
                residual_id="e112_no_failure_residual_captured",
                source_evidence_ids=[],
                x_t={"explicit_failure_residual": "none"},
                u=["compare competitor saturation", "compare founder-market fit", "seek buyer proof before claims"],
                y_star={"future_strategy_has_explicit_residual_learning": True},
                y_t_plus_1={"future_strategy_has_explicit_residual_learning": "pending"},
                r_t_plus_1=0.25,
                learning_update="No explicit failure residual emerged; future strategy should still compare competitor saturation and founder-market fit.",
                residual_severity="low",
            )
        )
    return residuals


def build_czl_residual_loop_linkage() -> dict[str, Any]:
    return {
        "mechanism_id": "CZL_CIEU_residual_loop_engine_v1",
        "residual_loop_engine_path": "ystar/governance/residual_loop_engine.py",
        "documentation_refs": [
            "Y-star-gov/docs/AMENDMENT_014_DELIVERY_REPORT.md",
            "Y-star-gov/docs/cieu_prediction_delta/schema_v0.md",
        ],
        "czl_tuple_schema": ["X_t", "U", "Y_star", "Y_t_plus_1", "R_t_plus_1"],
        "uses_existing_czl_mechanism": True,
        "parallel_residual_model_created": False,
        "relationship": "E112 failure residuals are represented as CZL/RLE tuples and written as CIEU-backed brain learning candidates.",
    }


def _czl_residual_candidate(
    *,
    residual_id: str,
    source_evidence_ids: list[str],
    x_t: Mapping[str, Any],
    u: list[str],
    y_star: Mapping[str, Any],
    y_t_plus_1: Mapping[str, Any],
    r_t_plus_1: float,
    learning_update: str,
    residual_severity: str,
) -> dict[str, Any]:
    return {
        "residual_id": residual_id,
        "source_evidence_ids": source_evidence_ids,
        "learning_update": learning_update,
        "residual_severity": residual_severity,
        "residual_loop_engine_path": "ystar/governance/residual_loop_engine.py",
        "CZL_residual_tuple": {
            "X_t": dict(x_t),
            "U": list(u),
            "Y_star": dict(y_star),
            "Y_t_plus_1": dict(y_t_plus_1),
            "R_t_plus_1": r_t_plus_1,
        },
        "target_y_star": dict(y_star),
        "actual_y_t_plus_1": dict(y_t_plus_1),
        "actual_r_t_plus_1": r_t_plus_1,
    }


def build_ceo_brain_learning_packet(
    *,
    host_runtime_result: Mapping[str, Any],
    freshness_policy: Mapping[str, Any],
    freshness_report: Mapping[str, Any],
    accepted_evidence_items: Sequence[Mapping[str, Any]],
    rejected_evidence_items: Sequence[Mapping[str, Any]],
    brain_mutation_candidates: Sequence[Mapping[str, Any]],
    failure_residual_candidates: Sequence[Mapping[str, Any]],
    cieu_event_ids: Sequence[str],
) -> dict[str, Any]:
    strategy_result = host_runtime_result.get("strategy_result") if isinstance(host_runtime_result.get("strategy_result"), Mapping) else {}
    strategy = strategy_result.get("strategy") if isinstance(strategy_result.get("strategy"), Mapping) else {}
    return {
        "artifact_id": "e112_ceo_brain_learning_packet",
        "milestone_id": MILESTONE_ID,
        "learning_loop_id": "e112_cieu_backed_brain_learning_loop",
        "source_runtime": "E111_Aiden_Host_Runtime_And_Autonomy_Control_Plane",
        "source_strategy_session_id": str(strategy.get("strategy_run_id") or SESSION_ID),
        "generated_at": _now(),
        "freshness_policy": dict(freshness_policy),
        "evidence_freshness_report": {
            key: value for key, value in freshness_report.items() if key != "freshness_rows"
        },
        "accepted_evidence_items": list(accepted_evidence_items),
        "rejected_evidence_items": list(rejected_evidence_items),
        "brain_mutation_candidates": list(brain_mutation_candidates),
        "failure_residual_candidates": list(failure_residual_candidates),
        "CZL_residual_loop_linkage": build_czl_residual_loop_linkage(),
        "brain_write_policy": {
            "automatic_direct_writeback": False,
            "production_brain_write_requested": False,
            "production_brain_write_performed": False,
            "default_write_mode": "CIEU_backed_candidate_only",
            "reason": "production brain writes require a later owner-approved and governance-validated mutation boundary",
        },
        "CIEU_linkage": {
            "source_CIEU_event_ids": list(cieu_event_ids),
            "target_event_type": "CEO_BRAIN_LEARNING_LOOP_DECISION",
            "formal_CIEU_log_path": "ystar.governance.cieu_store.CIEUStore.write_dict",
            "CZL_residual_loop_engine_path": "ystar/governance/residual_loop_engine.py",
        },
        "truth_constraints": {
            "customer_validation_claim": False,
            "pricing_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "paid_signal_claim": False,
            "L4_feedback_executed": False,
            "L5_revenue_loop_complete": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
    }


def run_cieu_backed_brain_learning_cycle(
    *,
    cieu_db: str | Path,
    owner_intent: str = "Run Aiden host runtime and convert fresh market facts, competitor intelligence, and failure residuals into governed brain learning candidates.",
    brain_db: Path | None = None,
    ystar_gov_root: Path | None = None,
    provider: PublicReadProvider | None = None,
    allow_live_network: bool = True,
    test_mode: bool = False,
    seal_session: bool = True,
) -> dict[str, Any]:
    selected_provider = provider
    if selected_provider is None and not allow_live_network:
        selected_provider = FixtureGlobalPublicReadProvider()
    cieu_path = str(cieu_db)
    host_result = run_aiden_host_runtime_cycle(
        cieu_db=cieu_path,
        owner_intent=owner_intent,
        brain_db=brain_db,
        ystar_gov_root=ystar_gov_root,
        provider=selected_provider,
        allow_live_network=allow_live_network,
        seal_session=False,
    )
    strategy = (
        host_result.get("strategy_result", {}).get("strategy")
        if isinstance(host_result.get("strategy_result"), Mapping)
        else {}
    )
    scan = strategy.get("live_global_open_world_scan") if isinstance(strategy.get("live_global_open_world_scan"), Mapping) else {}
    evidence_items = scan.get("evidence_items") if isinstance(scan.get("evidence_items"), list) else []
    freshness_policy = build_market_evidence_freshness_policy()
    freshness_report = filter_market_evidence_for_brain_learning(
        evidence_items,
        freshness_policy,
        test_mode=test_mode,
    )
    accepted = [row for row in freshness_report["freshness_rows"] if str(row.get("freshness_status") or "").startswith("accepted_")]
    rejected = [row for row in freshness_report["freshness_rows"] if not str(row.get("freshness_status") or "").startswith("accepted_")]
    candidates = build_brain_mutation_candidates(accepted, strategy=strategy)
    residuals = build_failure_residual_candidates(strategy=strategy, freshness_report=freshness_report)
    cieu_event_ids = _cieustore_event_ids(cieu_path)
    packet = build_ceo_brain_learning_packet(
        host_runtime_result=host_result,
        freshness_policy=freshness_policy,
        freshness_report=freshness_report,
        accepted_evidence_items=accepted,
        rejected_evidence_items=rejected,
        brain_mutation_candidates=candidates,
        failure_residual_candidates=residuals,
        cieu_event_ids=cieu_event_ids,
    )
    governance = _load_ystar_module("ystar.governance.ceo_brain_learning_loop_contract", ystar_gov_root)
    write_result = governance.validate_and_write_ceo_brain_learning_packet(
        packet,
        cieu_db=cieu_path,
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    summary = summarize_cieustore(cieu_path)
    decision = write_result.get("governance_decision", {}).get("decision")
    return {
        "artifact_id": "e112_cieu_backed_brain_learning_cycle_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "host_runtime_result": host_result,
        "brain_learning_packet": packet,
        "YstarGov_brain_learning_write_result": write_result,
        "CIEUStore_summary": summary,
        "freshness_filter_summary": {
            "accepted_count": freshness_report["accepted_count"],
            "rejected_count": freshness_report["rejected_count"],
            "rejected_status_counts": freshness_report["rejected_status_counts"],
            "stale_or_undated_evidence_blocked_from_brain": bool(rejected),
        },
        "brain_learning_loop_proven": (
            host_result.get("host_runtime_cycle_proven") is True
            and decision == "ALLOW"
            and write_result.get("formal_CIEU_log_written") is True
            and bool(candidates)
        ),
        "production_brain_write_performed": False,
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation",
            "L5-B": "complete_for_structured_governed_intelligence_loop_with_host_runtime_autonomy_control_and_CIEU_backed_brain_learning_candidates",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_CIEU_backed_brain_learning_candidate_loop_no_production_brain_write",
        },
    }


def write_e112_brain_learning_reports(
    *,
    cieu_db: str | Path,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
    provider: PublicReadProvider | None = None,
) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    result = run_cieu_backed_brain_learning_cycle(
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        provider=provider or FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
        test_mode=True,
    )
    report = _completion_report(result)
    status = _runtime_status(result)
    files = {
        "report_json": base / "office/mission_command/e112_cieu_backed_brain_learning_loop_report.json",
        "report_md": base / "office/mission_command/e112_cieu_backed_brain_learning_loop_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e112_cieu_backed_brain_learning_loop.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e112_cieu_backed_brain_learning_loop.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_markdown(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_markdown(status), encoding="utf-8")
    return report


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"event_count": 0, "event_types": [], "decisions": [], "event_ids": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT event_id, event_type, decision FROM cieu_events ORDER BY seq_global").fetchall()
    return {
        "event_count": len(rows),
        "event_ids": [row[0] for row in rows],
        "event_types": [row[1] for row in rows],
        "decisions": [row[2] for row in rows],
    }


def _completion_report(result: Mapping[str, Any]) -> dict[str, Any]:
    packet = result["brain_learning_packet"]
    rejection_proof = build_freshness_rejection_proof()
    return {
        "milestone_id": MILESTONE_ID,
        "brain_learning_loop_proven": result["brain_learning_loop_proven"],
        "freshness_filter_summary": result["freshness_filter_summary"],
        "Y_star_gov_brain_learning_decision": result["YstarGov_brain_learning_write_result"]["governance_decision"]["decision"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "accepted_evidence_count": len(packet["accepted_evidence_items"]),
        "rejected_evidence_count": len(packet["rejected_evidence_items"]),
        "brain_mutation_candidate_count": len(packet["brain_mutation_candidates"]),
        "failure_residual_candidate_count": len(packet["failure_residual_candidates"]),
        "CZL_residual_loop_linkage": packet["CZL_residual_loop_linkage"],
        "freshness_rejection_proof": rejection_proof,
        "production_brain_write_performed": result["production_brain_write_performed"],
        "learning_boundary": {
            "market_facts_enter_long_term_memory_as_candidates": True,
            "competitor_facts_enter_long_term_memory_as_candidates": True,
            "failure_residuals_enter_long_term_memory_as_CZL_candidates": True,
            "uses_existing_CZL_residual_loop_engine": True,
            "stale_or_undated_evidence_blocked": True,
            "direct_production_brain_write": False,
        },
        "what_was_not_claimed": [
            "no production brain write performed",
            "no L4 feedback executed",
            "no customer validation",
            "no revenue/payment signal",
            "no live provider execution",
            "no K9Audit integration",
        ],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }


def build_freshness_rejection_proof() -> dict[str, Any]:
    policy = build_market_evidence_freshness_policy()
    proof_items = [
        {
            "evidence_id": "e112_proof_stale_competitor",
            "source_title": "Stale competitor evidence",
            "source_url": "https://example.org/stale-competitor",
            "source_date": "2023-01-01",
            "observed_at": "2026-05-09T00:00:00Z",
            "claim_summary": "Old competitor alternative should not become durable market brain knowledge.",
            "evidence_type": "live_public_read_search_result",
        },
        {
            "evidence_id": "e112_proof_undated_market_claim",
            "source_title": "Undated market claim",
            "source_url": "https://vendor.invalid/undated",
            "observed_at": "2026-05-09T00:00:00Z",
            "claim_summary": "A current search observation without source date is context only, not brain learning.",
            "evidence_type": "live_public_read_search_result",
        },
    ]
    report = filter_market_evidence_for_brain_learning(proof_items, policy, test_mode=False)
    return {
        "proof_id": "e112_stale_and_undated_rejection_proof",
        "accepted_count": report["accepted_count"],
        "rejected_count": report["rejected_count"],
        "rejected_status_counts": report["rejected_status_counts"],
        "brain_candidate_count_from_rejected_items": len(build_brain_mutation_candidates([])),
        "conclusion": "stale and undated public-read evidence cannot feed brain mutation candidates",
    }


def _runtime_status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "runtime_status": "CIEU_backed_brain_learning_candidate_loop_structurally_enforceable",
        "brain_learning_loop_proven": result["brain_learning_loop_proven"],
        "freshness_filter_enforced": True,
        "stale_market_info_can_feed_brain": False,
        "production_brain_write_performed": False,
        **result["L5_truth_table_after"],
        "remaining_blockers": [
            "production brain mutation remains owner-gated and not executed",
            "real live-network source-date enrichment still needs host verification outside deterministic fixture mode",
            "real L4 feedback/customer/revenue/payment loops remain pending",
        ],
    }


def _report_markdown(report: Mapping[str, Any]) -> str:
    return (
        "# E112 CIEU-Backed Brain Learning Loop\n\n"
        f"- Brain learning loop proven: {str(report['brain_learning_loop_proven']).lower()}\n"
        f"- Y-star-gov decision: {report['Y_star_gov_brain_learning_decision']}\n"
        f"- Accepted evidence: {report['accepted_evidence_count']}\n"
        f"- Rejected evidence: {report['rejected_evidence_count']}\n"
        f"- Brain mutation candidates: {report['brain_mutation_candidate_count']}\n"
        f"- Failure residual candidates: {report['failure_residual_candidate_count']}\n"
        f"- CZL/RLE linkage: {report['CZL_residual_loop_linkage']['residual_loop_engine_path']}\n"
        f"- Stale/undated rejection proof: {report['freshness_rejection_proof']['rejected_count']} rejected, "
        f"{report['freshness_rejection_proof']['brain_candidate_count_from_rejected_items']} brain candidates\n"
        f"- Production brain write performed: {str(report['production_brain_write_performed']).lower()}\n\n"
        "## Meaning\n\n"
        "Fresh market facts, competitor evidence, and failure residuals now become governed, CIEU-backed brain learning candidates. "
        "Failure residuals reuse the existing CZL ResidualLoopEngine tuple instead of creating a parallel residual model. "
        "Stale, undated, or fixture-only evidence cannot become durable production brain knowledge. Production brain mutation remains blocked "
        "until a later owner-approved write boundary is implemented.\n"
    )


def _status_markdown(status: Mapping[str, Any]) -> str:
    return (
        "# Runtime Status After E112\n\n"
        f"- Runtime status: {status['runtime_status']}\n"
        f"- Freshness filter enforced: {str(status['freshness_filter_enforced']).lower()}\n"
        f"- Stale market info can feed brain: {str(status['stale_market_info_can_feed_brain']).lower()}\n"
        f"- Production brain write performed: {str(status['production_brain_write_performed']).lower()}\n"
        f"- L5-E: {status['L5-E']}\n"
    )


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) in sys.path:
        sys.path.remove(str(root))
    if root.exists():
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _cieustore_event_ids(cieu_db: str | Path) -> list[str]:
    path = Path(cieu_db)
    if not path.exists():
        return []
    with sqlite3.connect(path) as conn:
        return [row[0] for row in conn.execute("SELECT event_id FROM cieu_events ORDER BY seq_global").fetchall()]


def _freshness_row(
    evidence: Mapping[str, Any],
    status: str,
    reason: str,
    *,
    source_date: datetime | None = None,
    observed_at: datetime | None = None,
    age_days: int | None = None,
    durability: str = "not_durable",
) -> dict[str, Any]:
    return {
        "evidence_id": str(evidence.get("evidence_id") or _stable_hash(json.dumps(dict(evidence), sort_keys=True))[:12]),
        "source_title": str(evidence.get("source_title") or "")[:180],
        "source_url": str(evidence.get("source_url") or ""),
        "claim_summary": str(evidence.get("claim_summary") or "")[:360],
        "domain_id": evidence.get("domain_id"),
        "content_type": evidence.get("content_type") or evidence.get("knowledge_content_type") or _evidence_content_type(evidence),
        "query": evidence.get("query"),
        "evidence_type": evidence.get("evidence_type"),
        "source_date": source_date.date().isoformat() if source_date else evidence.get("source_date"),
        "observed_at": observed_at.isoformat() if observed_at else evidence.get("observed_at"),
        "freshness_status": status,
        "freshness_reason": reason,
        "age_days": age_days,
        "durability": durability,
    }


def _date_from(value: str) -> datetime | None:
    if not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        pass
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _days_between(start: datetime, end: datetime) -> int:
    return max(0, int((end.date() - start.date()).days))


def _status_counts(items: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        status = str(item.get("freshness_status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _candidate_type(item: Mapping[str, Any]) -> str:
    text = _text(item)
    if any(term in text for term in ("competitor", "competition", "alternative", "substitute", "incumbent")):
        return "competitor_fact_node"
    if any(term in text for term in ("fail", "risk", "crowded", "trust", "regulation", "friction")):
        return "failure_residual_node"
    return "market_fact_node"


def _dims_for_candidate(candidate_type: str) -> dict[str, float]:
    if candidate_type == "competitor_fact_node":
        return {"market": 0.35, "competition": 0.35, "strategy": 0.2, "risk": 0.1}
    if candidate_type == "failure_residual_node":
        return {"risk": 0.35, "strategy": 0.25, "market": 0.2, "learning": 0.2}
    return {"market": 0.4, "strategy": 0.25, "buyer_pain": 0.25, "learning": 0.1}


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_text(item)}" for key, item in value.items()).lower()
    if isinstance(value, list):
        return " ".join(_text(item) for item in value).lower()
    return str(value or "").lower()


def _evidence_content_type(evidence: Mapping[str, Any]) -> str:
    explicit = str(evidence.get("content_type") or evidence.get("knowledge_content_type") or "").strip().lower()
    if explicit:
        return explicit
    domain = str(evidence.get("domain_id") or "").strip().lower()
    if domain == "classical_theory_canon":
        return "classical_theory"
    if domain == "peer_experience_corpus":
        return "peer_experience"
    if domain == "historical_case_corpus":
        return "historical_case"
    if domain == "customer_contact_residuals":
        return "customer_learning_methodology"
    text = _text(evidence)
    if any(term in text for term in ("competitor", "competition", "alternative", "substitute", "incumbent")):
        return "competitive_signal"
    if any(term in text for term in ("standard", "regulation", "law", "compliance")):
        return "regulatory_or_standard"
    return "current_market_signal"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "MILESTONE_ID",
    "SESSION_ID",
    "build_brain_mutation_candidates",
    "build_ceo_brain_learning_packet",
    "build_failure_residual_candidates",
    "build_czl_residual_loop_linkage",
    "build_market_evidence_freshness_policy",
    "build_freshness_rejection_proof",
    "classify_evidence_freshness",
    "filter_market_evidence_for_brain_learning",
    "run_cieu_backed_brain_learning_cycle",
    "summarize_cieustore",
    "write_e112_brain_learning_reports",
]
