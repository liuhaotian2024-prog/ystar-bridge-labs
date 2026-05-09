from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from office.mission_command.e112_cieu_backed_brain_learning_loop import (
    build_market_evidence_freshness_policy,
    classify_evidence_freshness,
)
from office.mission_command.e114_live_web_capability_utilized_strategy_run import (
    build_default_e114_live_public_read_evidence_snapshot,
    build_host_live_public_read_provider,
)
from office.mission_command.e116_aiden_idle_continuous_learning_runtime import (
    attach_learning_quality_scores,
)
from office.mission_command.e119_aiden_operating_pattern_doctrine_registry import (
    build_operating_pattern_invocation_proof,
)
from office.mission_command.e120_aiden_unknown_problem_learning_protocol import (
    build_aiden_unknown_problem_learning_protocol,
)


MILESTONE_ID = "E121_Aiden_Host_Autonomous_Web_Observer_And_Local_Gemma_Runtime_R1"
SESSION_ID = "e121_aiden_host_autonomous_web_observer"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


class PublicReadProvider(Protocol):
    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict[str, Any]]:
        ...


def build_aiden_autonomous_query_frontier(
    *,
    owner_intent: str = "Aiden should autonomously understand the public world and find valuable opportunity terrain.",
) -> dict[str, Any]:
    """Build a broad, multi-round public-read frontier, not a recent-memory anchor."""

    domains = [
        _domain("ai_security_compliance", "agentic AI controls, AI governance, security review blockers"),
        _domain("healthcare_admin", "payer friction, revenue-cycle automation, prior authorization"),
        _domain("construction_bids", "small contractor bid leakage, RFIs, scope mismatch"),
        _domain("grant_ops", "grant compliance, reporting, audit readiness"),
        _domain("cpa_tax_accounting", "CPA tax workflow bottlenecks and AI accounting competition"),
        _domain("insurance_claims", "claims leakage, cycle time, autonomy governance"),
        _domain("legal_ops", "legal AI trust, task-based legal delivery, contract review"),
        _domain("local_services_dispatch", "missed calls, emergency dispatch, local service revenue leakage"),
        _domain("manufacturing_quality", "visual inspection, traceability, shop-floor quality"),
        _domain("developer_tooling", "agent teams, MCP operations, tool governance"),
        _domain("education_operations", "school admin burden, compliance, tutoring operations"),
        _domain("energy_and_facilities", "facility energy, maintenance, safety operations"),
    ]
    return {
        "frontier_id": "e121_host_autonomous_public_read_frontier",
        "owner_intent": owner_intent,
        "recent_memory_anchor_removed": True,
        "round_count": 4,
        "domain_hypotheses": domains,
        "rounds": [
            {
                "round_id": "round_0_broad_world_scan",
                "purpose": "find broad current economic and operational pressure zones",
                "queries": [
                    "2026 fastest growing operational AI bottlenecks small business",
                    "2026 agentic AI governance market current competitors funding",
                    "2026 industries with urgent workflow bottlenecks AI automation",
                ],
            },
            {
                "round_id": "round_1_domain_expansion",
                "purpose": "expand across adjacent markets instead of staying near old strategy anchors",
                "queries": [
                    f"2026 {item['domain_id'].replace('_', ' ')} AI automation buyer pain competitors"
                    for item in domains[:8]
                ],
            },
            {
                "round_id": "round_2_competition_and_right_to_win",
                "purpose": "check saturation, incumbents, founder-market fit, and buyer-visible differentiation",
                "queries": [
                    "2026 funded AI startups compliance automation Vanta Drata Secureframe alternatives",
                    "2026 AI workflow automation saturated markets founder market fit risks",
                    "2026 security questionnaire automation competitors pricing buyer pain",
                ],
            },
            {
                "round_id": "round_3_theory_case_and_failure_scan",
                "purpose": "bring durable theory, peer experience, and failure cases into the observation frame",
                "queries": [
                    "decision theory value of information startup strategy uncertainty",
                    "startup failure postmortem no market need competition founder market fit",
                    "operator playbook talk to users founder sales early B2B",
                ],
            },
        ],
        "output_obligations": [
            "source-dated public evidence",
            "accepted/rejected freshness rows",
            "learning quality scores",
            "knowledge graph candidate nodes",
            "CIEU-backed observation decision",
            "Gemma local runtime feasibility",
        ],
    }


def probe_local_gemma_runtime(
    *,
    requested: bool = True,
    ollama_list_output: str | None = None,
    ollama_path: str | None = None,
    timeout_seconds: int = 4,
) -> dict[str, Any]:
    """Probe whether Aiden can run on local Gemma through Ollama.

    The probe is read-only: it checks installed local models and never pulls,
    installs, or calls an external model provider.
    """

    path = ollama_path or shutil.which("ollama")
    output = ollama_list_output
    probe_error = ""
    if output is None and path:
        try:
            completed = subprocess.run(
                [path, "list"],
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            output = (completed.stdout or "") + "\n" + (completed.stderr or "")
            if completed.returncode != 0:
                probe_error = f"ollama list exited {completed.returncode}"
        except Exception as exc:  # pragma: no cover - host-specific probe safety
            output = ""
            probe_error = str(exc)
    output = output or ""
    model = _select_gemma_model(output)
    available = bool(model)
    return {
        "runtime_id": "local_ollama_gemma4_probe",
        "requested": requested,
        "available": available,
        "status": "available" if available else "not_available",
        "runtime_host": "127.0.0.1" if available else "host-local",
        "model_name": model or "gemma4",
        "preferred_model": "gemma4",
        "compatible_fallback_models": ["gemma4:*", "gemma3:*", "gemma:*"],
        "ollama_path": path or "",
        "probe_error": probe_error,
        "external_provider_api_used": False,
        "private_data_exfiltration_allowed": False,
        "side_effects_performed": False,
        "can_embed_aiden": available,
        "feasibility_conclusion": (
            "Aiden can be hosted on local Gemma through Ollama for bounded structured reasoning."
            if available
            else "Feasible but not active until Ollama and a Gemma4-compatible local model are installed on the Mac host."
        ),
        "correct_path_if_missing": [
            "Install/start Ollama on the Mac host.",
            "Pull a Gemma4-compatible local model, for example `ollama pull gemma4` if available in the local Ollama library.",
            "Rerun this probe and keep external_provider_api_used=false.",
            "Route any Gemma-backed Aiden prompt through Y-star-gov before use.",
        ],
        "official_research_refs": [
            "https://developers.googleblog.com/en/introducing-gemma-4/",
            "https://ollama.com/library/gemma4",
        ],
    }


def collect_autonomous_public_read_evidence(
    *,
    use_host_live_network: bool = False,
    provider: PublicReadProvider | None = None,
    max_results_per_domain: int = 3,
) -> dict[str, Any]:
    frontier = build_aiden_autonomous_query_frontier()
    if use_host_live_network:
        selected_provider = provider or build_host_live_public_read_provider()
        raw_rows: list[dict[str, Any]] = []
        for domain in frontier["domain_hypotheses"]:
            domain_id = domain["domain_id"]
            query = f"2026 {domain_id.replace('_', ' ')} buyer pain competitors AI automation"
            for row in selected_provider.search(query, domain_id=domain_id, max_results=max_results_per_domain):
                raw_rows.append(_normalize_evidence(row, domain_id=domain_id, query=query, live_network=True))
    else:
        raw_rows = [
            _normalize_evidence(row, domain_id=str(row.get("domain_id") or "unknown"), query=str(row.get("query") or ""), live_network=False)
            for row in build_default_e114_live_public_read_evidence_snapshot()
        ]

    policy = build_market_evidence_freshness_policy()
    freshness_rows = [classify_evidence_freshness(row, policy, test_mode=False) for row in raw_rows]
    accepted_freshness = [row for row in freshness_rows if str(row.get("freshness_status") or "").startswith("accepted_")]
    scored = attach_learning_quality_scores(accepted_freshness)
    accepted = [row for row in scored if float(row.get("learning_quality", {}).get("quality_score") or 0.0) >= 0.6]
    low_quality = [
        {**row, "freshness_status": "rejected_low_learning_quality"}
        for row in scored
        if float(row.get("learning_quality", {}).get("quality_score") or 0.0) < 0.6
    ]
    rejected = [row for row in freshness_rows if not str(row.get("freshness_status") or "").startswith("accepted_")] + low_quality
    scores = [float(row.get("learning_quality", {}).get("quality_score") or 0.0) for row in accepted]
    return {
        "frontier": frontier,
        "raw_evidence_count": len(raw_rows),
        "accepted": accepted,
        "rejected": rejected,
        "source_date_policy": policy,
        "learning_quality_summary": {
            "learning_quality_gate_applied": True,
            "average_quality_score": round(sum(scores) / len(scores), 3) if scores else 0.0,
            "minimum_quality_score": round(min(scores), 3) if scores else 0.0,
            "low_quality_evidence_ids": [str(row.get("evidence_id")) for row in low_quality],
            "quality_basis": "E117/E118 deterministic_public_read_quality_score_v2",
        },
        "observation_mode": "host_live_public_read" if use_host_live_network else "dated_snapshot_public_read",
        "stale_or_undated_rejected": bool(rejected),
    }


def build_aiden_host_autonomous_web_observer_packet(
    *,
    use_host_live_network: bool = False,
    require_local_gemma: bool = False,
    provider: PublicReadProvider | None = None,
    local_gemma_probe: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = collect_autonomous_public_read_evidence(use_host_live_network=use_host_live_network, provider=provider)
    gemma = dict(local_gemma_probe or probe_local_gemma_runtime(requested=require_local_gemma))
    gemma["requested"] = bool(require_local_gemma)
    packet = {
        "observer_cycle_id": SESSION_ID,
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "execution_boundary": {
            "runs_on_owner_host": True,
            "sandbox_restricted": False,
            "host_public_read_bridge": True,
            "external_side_effect_allowed": False,
            "network_scope": "public_read_get_head_only",
        },
        "query_frontier": evidence["frontier"],
        "public_read_policy": {
            "public_read_only": True,
            "allowed_http_methods": ["GET", "HEAD"],
            "login_allowed": False,
            "form_submission_allowed": False,
            "contact_allowed": False,
            "payment_allowed": False,
            "account_creation_allowed": False,
            "private_data_collection_allowed": False,
            "robots_and_terms_boundary": "public pages only; no bypassing auth, paywalls, forms, or private data",
        },
        "source_date_policy": evidence["source_date_policy"],
        "evidence_items": evidence["accepted"],
        "rejected_evidence_items": evidence["rejected"],
        "learning_quality_summary": evidence["learning_quality_summary"],
        "knowledge_graph_update_plan": {
            "candidate_node_types": [
                "current_market_fact",
                "competitor_signal",
                "buyer_pain_signal",
                "classical_theory_node",
                "peer_experience_node",
                "historical_case_node",
                "assumption_node",
                "CZL_residual_node",
            ],
            "candidate_edge_types": [
                "supports",
                "contradicts",
                "competes_with",
                "generalizes",
                "falsifies",
                "updates_strategy",
                "requires_followup",
            ],
            "production_brain_write_requires_owner_gate": True,
            "CIEU_before_brain_write": True,
            "write_mode": "CIEU_backed_observation_candidates_only",
        },
        "local_gemma_runtime": gemma,
        "governance_chain": {
            "governance_links": [
                "E112_content_type_freshness_filter",
                "E119_operating_pattern_doctrine",
                "E120_unknown_problem_learning_protocol",
                "CIEUStore_formal_recording",
            ],
            "Y_star_gov_contract": "ystar/governance/aiden_host_autonomous_web_observer_contract.py",
        },
        "CIEU_linkage": {
            "CIEU_recording_required": True,
            "target_event_type": "AIDEN_HOST_AUTONOMOUS_WEB_OBSERVER_DECISION",
            "formal_CIEU_log_path": "ystar.governance.cieu_store.CIEUStore.write_dict",
        },
        "truth_constraints": {
            "login_attempted": False,
            "form_submitted": False,
            "message_sent": False,
            "payment_attempted": False,
            "external_action_executed": False,
            "provider_action_executed": False,
            "scraped_private_data": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "live_provider_execution_claim": False,
            "K9Audit_integration_claim": False,
            "raw_unvalidated_codex_prompt_used": False,
            "external_llm_provider_used_for_local_gemma": False,
        },
        "what_was_not_claimed": [
            "not a literal exhaustive copy of the entire internet",
            "no external action",
            "no customer validation",
            "no revenue/payment signal",
            "no production brain write",
            "no K9Audit integration",
        ],
        "observation_mode": evidence["observation_mode"],
    }
    return packet


def build_e121_operating_pattern_proof() -> dict[str, Any]:
    return build_operating_pattern_invocation_proof(
        {
            "action_id": "e121_aiden_host_autonomous_web_observer",
            "action_type": "host_autonomous_public_read_observation_and_local_llm_boundary",
            "market_strategy_required": True,
            "codex_execution_required": False,
            "brain_write_related": True,
            "external_action_related": False,
            "self_governance_related": False,
            "unknown_problem_related": True,
            "durable_learning_related": True,
            "autonomous_web_observation_related": True,
            "local_llm_related": True,
        }
    )


def run_e121_aiden_host_autonomous_web_observer_session(
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    use_host_live_network: bool = False,
    require_local_gemma: bool = False,
    provider: PublicReadProvider | None = None,
    local_gemma_probe: Mapping[str, Any] | None = None,
    seal_session: bool = False,
) -> dict[str, Any]:
    yroot = ystar_gov_root or Y_GOV_ROOT
    packet = build_aiden_host_autonomous_web_observer_packet(
        use_host_live_network=use_host_live_network,
        require_local_gemma=require_local_gemma,
        provider=provider,
        local_gemma_probe=local_gemma_probe,
    )
    pattern_proof = build_e121_operating_pattern_proof()
    pattern_gov = _load_ystar_module("ystar.governance.aiden_operating_pattern_doctrine_contract", yroot)
    pattern_result = pattern_gov.validate_and_write_aiden_operating_pattern_invocation(
        pattern_proof,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    unknown_protocol = build_aiden_unknown_problem_learning_protocol(
        unknown_problem_statement="Aiden must autonomously observe the public web and decide what knowledge to learn without recent-memory anchoring."
    )
    unknown_gov = _load_ystar_module("ystar.governance.aiden_unknown_problem_learning_protocol_contract", yroot)
    unknown_result = unknown_gov.validate_and_write_aiden_unknown_problem_learning_protocol(
        unknown_protocol,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=False,
    )
    web_gov = _load_ystar_module("ystar.governance.aiden_host_autonomous_web_observer_contract", yroot)
    observer_result = web_gov.validate_and_write_aiden_host_autonomous_web_observer_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    summary = _cieustore_summary(cieu_db)
    proven = (
        pattern_result["governance_decision"]["decision"] == "ALLOW"
        and unknown_result["governance_decision"]["decision"] == "ALLOW"
        and observer_result["governance_decision"]["decision"] == "ALLOW"
    )
    return {
        "artifact_id": "e121_aiden_host_autonomous_web_observer_session_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "packet": packet,
        "operating_pattern_result": pattern_result,
        "unknown_problem_learning_result": unknown_result,
        "observer_governance_result": observer_result,
        "CIEUStore_summary": summary,
        "host_autonomous_web_observer_proven": proven,
        "local_gemma_feasibility": packet["local_gemma_runtime"],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_host_public_read_observer_boundary",
            "L5-B": "stronger_governed_intelligence_with_autonomous_public_read_world_observation_and_local_gemma_feasibility",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_with_source_dated_public_world_observation_candidates",
        },
    }


def write_e121_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    use_host_live_network: bool = False,
    require_local_gemma: bool = False,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_e121_aiden_host_autonomous_web_observer_session(
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        use_host_live_network=use_host_live_network,
        require_local_gemma=require_local_gemma,
    )
    packet = result["packet"]
    report = {
        "milestone_id": MILESTONE_ID,
        "base_hashes": {
            "bridge_labs": "d516f8beaaa59811f0c1334926545bbfdffa9709",
            "Y_star_gov": "7fdc267c421918eb6d239e91d3c3bcabcf1cddc7",
        },
        "what_was_implemented": [
            "host-local autonomous public-read observer packet",
            "multi-round query frontier beyond recent-memory anchors",
            "source-date and content-type freshness filtering",
            "learning quality gate before durable observation use",
            "Y-star-gov autonomous web observer contract",
            "local Ollama/Gemma4 feasibility probe and no-external-provider boundary",
        ],
        "observer_governance_decision": result["observer_governance_result"]["governance_decision"],
        "operating_pattern_decision": result["operating_pattern_result"]["governance_decision"]["decision"],
        "unknown_problem_learning_decision": result["unknown_problem_learning_result"]["governance_decision"]["decision"],
        "evidence_summary": {
            "observation_mode": packet["observation_mode"],
            "accepted_count": len(packet["evidence_items"]),
            "rejected_count": len(packet["rejected_evidence_items"]),
            "domain_count": len({row.get("domain_id") for row in packet["evidence_items"]}),
            "average_quality_score": packet["learning_quality_summary"]["average_quality_score"],
        },
        "local_gemma_feasibility": result["local_gemma_feasibility"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "truth_constraints": packet["truth_constraints"],
        "what_was_not_claimed": packet["what_was_not_claimed"],
        "L5_truth_table_after": result["L5_truth_table_after"],
        "host_run_command": (
            "PYTHONPATH=. python3 -m office.mission_command.e121_aiden_host_autonomous_web_observer "
            "--use-host-live-network --cieu-db /tmp/e121_aiden_host_web_observer.db"
        ),
        "local_gemma_probe_command": (
            "PYTHONPATH=. python3 -m office.mission_command.e121_aiden_host_autonomous_web_observer "
            "--require-local-gemma --cieu-db /tmp/e121_aiden_gemma_probe.db"
        ),
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "host_autonomous_public_read_observer_active": result["host_autonomous_web_observer_proven"],
        "local_gemma_feasibility_status": result["local_gemma_feasibility"]["status"],
        "public_read_only": packet["public_read_policy"]["public_read_only"],
        "external_action_executed": False,
        "customer_validation_claim": False,
        "revenue_or_payment_signal": False,
        "production_brain_write": False,
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e121_aiden_host_autonomous_web_observer_report.json",
        "report_md": base / "office/mission_command/e121_aiden_host_autonomous_web_observer_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e121_aiden_host_autonomous_web_observer.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e121_aiden_host_autonomous_web_observer.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return {"result": result, "report": report, "status": status, "files": {key: str(value) for key, value in files.items()}}


def _normalize_evidence(row: Mapping[str, Any], *, domain_id: str, query: str, live_network: bool) -> dict[str, Any]:
    item = dict(row)
    item.setdefault("domain_id", domain_id)
    item.setdefault("query", query)
    item.setdefault("observed_at", _now())
    item.setdefault("evidence_type", "live_public_read_search_result" if live_network else "live_public_read_evidence_snapshot")
    item.setdefault("content_type", _content_type_for_domain(domain_id))
    item["evidence_id"] = item.get("evidence_id") or f"e121_{_stable_hash(str(item.get('source_url')) + domain_id)[:12]}"
    return item


def _content_type_for_domain(domain_id: str) -> str:
    if domain_id in {"cpa_tax_accounting", "ai_security_compliance", "cyber_insurance"}:
        return "competitive_signal"
    if domain_id in {"classical_theory_canon"}:
        return "classical_theory"
    if domain_id in {"peer_experience_corpus"}:
        return "peer_experience"
    if domain_id in {"historical_case_corpus"}:
        return "historical_case"
    return "current_market_signal"


def _select_gemma_model(output: str) -> str:
    candidates: list[str] = []
    for line in output.splitlines():
        name = line.strip().split()[0] if line.strip() else ""
        lowered = name.lower()
        if "gemma4" in lowered:
            return name
        if "gemma" in lowered:
            candidates.append(name)
    return candidates[0] if candidates else ""


def _domain(domain_id: str, hypothesis: str) -> dict[str, Any]:
    return {"domain_id": domain_id, "hypothesis": hypothesis}


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None) -> Any:
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    return importlib.import_module(module_name)


def _cieustore_summary(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_path": str(path), "total_records": 0, "event_type_counts": {}}
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT event_type, COUNT(*) FROM cieu_events GROUP BY event_type").fetchall()
    return {
        "db_path": str(path),
        "total_records": sum(int(row[1]) for row in rows),
        "event_type_counts": {str(row[0]): int(row[1]) for row in rows},
    }


def _report_md(report: Mapping[str, Any]) -> str:
    return (
        f"# {MILESTONE_ID}\n\n"
        f"- Observer decision: {report['observer_governance_decision']['decision']}\n"
        f"- Accepted evidence: {report['evidence_summary']['accepted_count']}\n"
        f"- Evidence domains: {report['evidence_summary']['domain_count']}\n"
        f"- Local Gemma status: {report['local_gemma_feasibility']['status']}\n"
        f"- External action executed: false\n"
        f"- Customer/revenue/payment claimed: false\n"
    )


def _status_md(status: Mapping[str, Any]) -> str:
    truth = status["L5_truth_table_after"]
    return (
        f"# Runtime Status After {MILESTONE_ID}\n\n"
        f"- Host autonomous public-read observer active: {status['host_autonomous_public_read_observer_active']}\n"
        f"- Local Gemma feasibility status: {status['local_gemma_feasibility_status']}\n"
        f"- L5-A: {truth['L5-A']}\n"
        f"- L5-B: {truth['L5-B']}\n"
        f"- L5-C: {truth['L5-C']}\n"
        f"- L5-D: {truth['L5-D']}\n"
        f"- L5-E: {truth['L5-E']}\n"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run E121 Aiden host autonomous public-read observer.")
    parser.add_argument("--cieu-db", default="/tmp/e121_aiden_host_web_observer.db")
    parser.add_argument("--ystar-gov-root", default=str(Y_GOV_ROOT))
    parser.add_argument("--use-host-live-network", action="store_true")
    parser.add_argument("--require-local-gemma", action="store_true")
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args(argv)
    if args.write_reports:
        result = write_e121_reports(
            cieu_db=args.cieu_db,
            ystar_gov_root=args.ystar_gov_root,
            use_host_live_network=args.use_host_live_network,
            require_local_gemma=args.require_local_gemma,
        )
    else:
        result = run_e121_aiden_host_autonomous_web_observer_session(
            cieu_db=args.cieu_db,
            ystar_gov_root=args.ystar_gov_root,
            use_host_live_network=args.use_host_live_network,
            require_local_gemma=args.require_local_gemma,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "MILESTONE_ID",
    "SESSION_ID",
    "build_aiden_autonomous_query_frontier",
    "probe_local_gemma_runtime",
    "collect_autonomous_public_read_evidence",
    "build_aiden_host_autonomous_web_observer_packet",
    "run_e121_aiden_host_autonomous_web_observer_session",
    "write_e121_reports",
]
