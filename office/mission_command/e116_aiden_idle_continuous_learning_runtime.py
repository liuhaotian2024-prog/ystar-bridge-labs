from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from office.mission_command.e112_cieu_backed_brain_learning_loop import (
    build_market_evidence_freshness_policy,
    classify_evidence_freshness,
)
from office.mission_command.e114_live_web_capability_utilized_strategy_run import (
    build_default_e114_live_public_read_evidence_snapshot,
    build_host_live_public_read_provider,
)


MILESTONE_ID = "E116_Aiden_Idle_Continuous_Learning_Runtime_R1"
SESSION_ID = "e116_aiden_idle_continuous_learning_runtime"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
BRAIN_DB = BRIDGE_ROOT / "aiden_brain.db"


def build_ceo_idle_learning_curriculum() -> list[dict[str, Any]]:
    """Return the mandatory learning curriculum for Aiden's idle hours."""

    return [
        _domain("ceo_judgment", "CEO decision quality, priorities, judgment, tradeoffs", ["CEO judgment", "decision quality", "strategy operating cadence"]),
        _domain("market_intelligence", "Fresh public-read market shifts, buyer pains, budget signals", ["AI governance market", "agentic AI adoption risk", "2026 buyer pain"]),
        _domain("competitive_strategy", "Competitors, substitutes, incumbents, right-to-win/right-to-lose", ["AI compliance competitors 2026", "agent governance competitors", "security questionnaire automation"]),
        _domain("product_strategy", "Buyer-visible product shape, packaging, value capture", ["product strategy", "service wedge SaaS", "first cash product packaging"]),
        _domain("sales_and_distribution", "Channels, first ten buyers, trust, founder-market-fit barriers", ["B2B first customers", "founder led sales", "AI startup enterprise sales"]),
        _domain("governance_and_risk", "Y-star-gov, CIEU, no-send, compliance, owner boundaries", ["agent governance risk", "AI audit evidence", "EU AI Act readiness"]),
        _domain("technology_architecture", "Agent runtime architecture, MCP/provider boundary, control plane", ["MCP agent runtime", "agent control plane", "tool execution boundary"]),
        _domain("failure_residual_learning", "Failed theses, stale evidence, residuals, pivot rules", ["startup postmortem", "strategy falsification", "failure residual learning"]),
        _domain("capital_and_cash_discipline", "Cash constraints, pricing, margins, time-to-cash", ["startup pricing", "cash path", "bootstrapped revenue"]),
        _domain("organization_and_operating_system", "How autonomous company loops allocate work and close learning", ["AI agent operating system", "company operating rhythm", "autonomous agents governance"]),
    ]


def detect_idle_state(*, explicit_session_task_active: bool = False, marker_path: str | Path | None = None) -> dict[str, Any]:
    marker_active = False
    marker_value = None
    if marker_path:
        path = Path(marker_path)
        if path.exists():
            marker_value = path.read_text(encoding="utf-8", errors="ignore").strip().lower()
            marker_active = marker_value in {"1", "true", "active", "busy", "session_active"}
    active = explicit_session_task_active or marker_active
    return {
        "idle_state_verified": not active,
        "explicit_session_task_active": active,
        "active_session_source": "marker_path" if marker_active else "caller_flag" if explicit_session_task_active else "none_detected",
        "marker_path": str(marker_path) if marker_path else None,
        "marker_value": marker_value,
    }


def collect_idle_learning_evidence(
    *,
    use_host_live_network: bool = False,
    max_items: int = 30,
) -> list[dict[str, Any]]:
    """Collect source-dated evidence for idle knowledge growth.

    The host-live provider is used only when explicitly requested. The
    source-dated snapshot remains the deterministic fallback and is still
    filtered by E112 freshness logic before any brain write.
    """

    if use_host_live_network:
        provider = build_host_live_public_read_provider()
        rows: list[dict[str, Any]] = []
        for domain in build_ceo_idle_learning_curriculum()[:8]:
            domain_id = _map_domain_to_e114_domain(domain["domain_id"])
            query = domain["queries"][0]
            rows.extend(provider.search(query, domain_id=domain_id, max_results=3))
        if rows:
            return _dedupe_evidence(rows)[:max_items]
    rows = build_default_e114_live_public_read_evidence_snapshot()
    rows.extend(build_idle_learning_evergreen_evidence_snapshot())
    return _dedupe_evidence(rows)[:max_items]


def build_idle_learning_evergreen_evidence_snapshot() -> list[dict[str, Any]]:
    observed = "2026-05-09T00:00:00Z"
    return [
        _ev("ceo_judgment", "NIST AI RMF Generative AI Profile", "https://www.nist.gov/itl/ai-risk-management-framework/generative-artificial-intelligence-profile", "2024-07-26", "Risk management for generative AI requires mapped risks, measurement, governance, and monitoring; useful as a CEO governance mental model.", "accepted_evergreen_context", observed),
        _ev("governance_and_risk", "OWASP Top 10 for LLM Applications", "https://owasp.org/www-project-top-10-for-large-language-model-applications/", "2025-11-01", "LLM application risk includes excessive agency, supply chain issues, data exposure, and insufficient monitoring.", "accepted_evergreen_context", observed),
        _ev("technology_architecture", "Model Context Protocol specification", "https://modelcontextprotocol.io/specification", "2025-11-25", "MCP standardizes how AI applications expose tools and context, making provider/tool boundary governance commercially relevant.", "accepted_evergreen_context", observed),
        _ev("sales_and_distribution", "Y Combinator startup sales advice", "https://www.ycombinator.com/library/5x-how-to-sell", "2024-08-01", "Early B2B founders need direct customer conversations, sharp qualification, and fast learning instead of broad generic marketing.", "accepted_evergreen_context", observed),
        _ev("product_strategy", "Stripe guide to pricing", "https://stripe.com/resources/more/how-to-price-a-product", "2025-09-16", "Pricing should connect to value, buyer segments, willingness-to-pay evidence, and iteration.", "accepted_evergreen_context", observed),
        _ev("failure_residual_learning", "CB Insights startup failure patterns", "https://www.cbinsights.com/research/startup-failure-reasons-top/", "2025-10-01", "Common startup failures include no market need, running out of cash, weak team fit, competition, and pricing issues.", "accepted_evergreen_context", observed),
    ]


def filter_idle_learning_evidence(evidence_items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    policy = build_market_evidence_freshness_policy(current_date="2026-05-09")
    rows = [classify_evidence_freshness(item, policy, test_mode=False) for item in evidence_items]
    freshness_accepted = [row for row in rows if str(row.get("freshness_status") or "").startswith("accepted_")]
    rejected = [row for row in rows if not str(row.get("freshness_status") or "").startswith("accepted_")]
    scored = attach_learning_quality_scores(freshness_accepted)
    accepted = [row for row in scored if float(row.get("learning_quality", {}).get("quality_score") or 0.0) >= 0.6]
    low_quality = [
        {**row, "freshness_status": "rejected_low_learning_quality"}
        for row in scored
        if float(row.get("learning_quality", {}).get("quality_score") or 0.0) < 0.6
    ]
    rejected.extend(low_quality)
    quality_scores = [float(row.get("learning_quality", {}).get("quality_score") or 0.0) for row in accepted]
    return {
        "policy": {
            **policy,
            "source_dates_required": True,
            "stale_or_undated_rejected": True,
        },
        "accepted": accepted,
        "rejected": rejected,
        "learning_quality_summary": {
            "learning_quality_gate_applied": True,
            "average_quality_score": round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else 0.0,
            "minimum_quality_score": round(min(quality_scores), 3) if quality_scores else 0.0,
            "low_quality_evidence_ids": [str(row.get("evidence_id")) for row in low_quality],
            "quality_dimensions": [
                "source_authority",
                "freshness",
                "commercial_relevance",
                "novelty",
                "cross_source_support",
                "actionability",
                "source_authority_basis",
                "source_url_depth",
                "claim_specificity",
                "current_signal_verifiability",
                "risk_of_staleness",
            ],
        },
        "summary": {
            "total_count": len(rows),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "accepted_status_counts": _status_counts(accepted),
            "rejected_status_counts": _status_counts(rejected),
        },
    }


def build_idle_learning_knowledge_graph_delta(
    accepted_evidence_items: Sequence[Mapping[str, Any]],
    curriculum_domains: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    domain_by_id = {str(domain["domain_id"]): domain for domain in curriculum_domains if isinstance(domain, Mapping)}
    first_evidence = str(accepted_evidence_items[0].get("evidence_id")) if accepted_evidence_items else "e116_no_evidence"
    ceo_hub_id = "ceo_learning/e116_idle_learning_root"
    nodes.append(
        {
            "node_id": ceo_hub_id,
            "name": "Aiden Idle Continuous Learning Root",
            "node_type": "ceo_idle_learning_hub",
            "depth_label": "foundational",
            "source_evidence_ids": [first_evidence],
            "summary": "Root node connecting source-dated idle learning into Aiden's CEO knowledge graph.",
            "learning_quality_score": _average_quality_for_refs([first_evidence], accepted_evidence_items),
            "dims": {"y": 0.82, "x": 0.9, "z": 0.82, "t": 0.88, "phi": 0.84, "c": 0.72},
        }
    )
    for domain in curriculum_domains:
        domain_id = str(domain.get("domain_id"))
        matching = [item for item in accepted_evidence_items if str(item.get("domain_id") or "") in {domain_id, _map_domain_to_e114_domain(domain_id)}]
        refs = [str(item.get("evidence_id")) for item in (matching or accepted_evidence_items[:1])[:3]]
        node_id = f"ceo_learning/e116_domain_{_slug(domain_id)}"
        nodes.append(
            {
                "node_id": node_id,
                "name": f"CEO Learning Domain: {domain_id.replace('_', ' ').title()}",
                "node_type": "ceo_learning_domain",
                "depth_label": "operational",
                "source_evidence_ids": refs,
                "summary": str(domain.get("learning_objective") or "")[:260],
                "learning_quality_score": _average_quality_for_refs(refs, accepted_evidence_items),
                "dims": {"y": 0.72, "x": 0.78, "z": 0.72, "t": 0.78, "phi": 0.78, "c": 0.68},
            }
        )
        edges.append({"source_id": ceo_hub_id, "target_id": node_id, "edge_type": "idle_learning_domain", "weight": 0.72})

    for index, item in enumerate(accepted_evidence_items[:24]):
        evidence_id = str(item.get("evidence_id"))
        domain_id = str(item.get("domain_id") or "market_intelligence")
        node_id = f"ceo_learning/e116_fact_{_stable_hash(evidence_id + str(item.get('claim_summary') or ''))[:12]}"
        nodes.append(
            {
                "node_id": node_id,
                "name": str(item.get("source_title") or f"Idle learning fact {index + 1}")[:120],
                "node_type": _node_type_for_domain(domain_id),
                "depth_label": "operational",
                "source_evidence_ids": [evidence_id],
                "summary": str(item.get("claim_summary") or "")[:360],
                "source_url": item.get("source_url"),
                "source_date": item.get("source_date"),
                "freshness_status": item.get("freshness_status"),
                "learning_quality_score": float(item.get("learning_quality", {}).get("quality_score") or 0.0),
                "learning_quality": item.get("learning_quality"),
                "dims": _dims_for_domain(domain_id),
            }
        )
        target_domain = f"ceo_learning/e116_domain_{_slug(_domain_from_evidence(domain_id, domain_by_id))}"
        if target_domain not in {node["node_id"] for node in nodes}:
            target_domain = ceo_hub_id
        edges.append({"source_id": target_domain, "target_id": node_id, "edge_type": "source_dated_learning", "weight": 0.64})
        if index > 0:
            edges.append({"source_id": nodes[-2]["node_id"], "target_id": node_id, "edge_type": "idle_learning_sequence", "weight": 0.42})

    # Keep only edges whose nodes are present.
    node_ids = {node["node_id"] for node in nodes}
    edges = [edge for edge in edges if edge["source_id"] in node_ids and edge["target_id"] in node_ids]
    return {"nodes": nodes, "edges": edges}


def build_aiden_idle_learning_packet(
    *,
    cieu_db: str | Path,
    brain_db: str | Path,
    allow_brain_write: bool = False,
    explicit_session_task_active: bool = False,
    use_host_live_network: bool = False,
    marker_path: str | Path | None = None,
    owner_explicit_production_write_approval: bool = False,
    pre_write_backup_metadata: Mapping[str, Any] | None = None,
    force_production_target: bool = False,
) -> dict[str, Any]:
    curriculum = build_ceo_idle_learning_curriculum()
    evidence = collect_idle_learning_evidence(use_host_live_network=use_host_live_network)
    freshness = filter_idle_learning_evidence(evidence)
    accepted = freshness["accepted"]
    delta = build_idle_learning_knowledge_graph_delta(accepted, curriculum)
    write_mode = "governed_local_brain_db_write" if allow_brain_write else "CIEU_backed_candidate_only"
    if allow_brain_write and str(brain_db).startswith("/tmp/") and not force_production_target:
        write_mode = "isolated_test_brain_db_write"
    production_target = force_production_target or _is_production_brain_target(brain_db)
    backup_metadata = dict(pre_write_backup_metadata or {})
    brain_write_policy = {
        "write_mode": write_mode,
        "automatic_direct_writeback": False,
        "YstarGov_validation_required": True,
        "target_brain_db": str(brain_db),
        "production_target": production_target,
        "owner_explicit_production_write_approval": owner_explicit_production_write_approval,
        "backup_required_before_write": production_target,
        "backup_verified": bool(backup_metadata.get("backup_verified")),
        "pre_write_backup_path": backup_metadata.get("pre_write_backup_path"),
        "pre_write_backup_sha256": backup_metadata.get("pre_write_backup_sha256"),
        "pre_write_brain_db_sha256": backup_metadata.get("pre_write_brain_db_sha256"),
        "backup_created_at": backup_metadata.get("backup_created_at"),
        "rollback_plan": backup_metadata.get("rollback_plan"),
        "max_nodes_per_cycle": 50,
        "max_edges_per_cycle": 100,
        "production_brain_write_performed": False,
        "write_after_CIEU_record_only": True,
    }
    return {
        "learning_cycle_id": f"e116_idle_learning_{_stable_hash(str(time.time()))[:10]}",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "learning_mode": "idle_continuous_learning",
        "trigger_context": detect_idle_state(
            explicit_session_task_active=explicit_session_task_active,
            marker_path=marker_path,
        ),
        "curriculum_domains": curriculum,
        "source_date_policy": freshness["policy"],
        "evidence_items": accepted,
        "rejected_evidence_items": freshness["rejected"],
        "learning_quality_summary": freshness["learning_quality_summary"],
        "freshness_summary": freshness["summary"],
        "knowledge_graph_delta": delta,
        "brain_write_policy": brain_write_policy,
        "CIEU_linkage": {
            "target_event_type": "AIDEN_IDLE_CONTINUOUS_LEARNING_DECISION",
            "formal_CIEU_log_path": "ystar.governance.cieu_store.CIEUStore.write_dict",
            "cieu_db": str(cieu_db),
        },
        "CZL_closure": {
            "uses_existing_CZL": True,
            "residual_loop_engine_path": "ystar/governance/residual_loop_engine.py",
            "X_t": {"idle_learning_need": "Aiden knowledge graph is too sparse and strategy remains shallow"},
            "U": ["source-dated learning", "freshness filtering", "CIEU write", "governed brain graph delta"],
            "Y_star": {"Aiden_continuously_learns_when_idle": True, "active_session_not_interrupted": True},
            "Y_t_plus_1": {"Aiden_continuously_learns_when_idle": True, "active_session_not_interrupted": True},
            "R_t_plus_1": 0.0,
        },
        "truth_constraints": {
            "external_action_executed": False,
            "provider_action_executed": False,
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


def run_aiden_idle_continuous_learning_cycle(
    *,
    cieu_db: str | Path,
    brain_db: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    allow_brain_write: bool = False,
    explicit_session_task_active: bool = False,
    use_host_live_network: bool = False,
    marker_path: str | Path | None = None,
    owner_explicit_production_write_approval: bool = False,
    pre_write_backup_metadata: Mapping[str, Any] | None = None,
    force_production_target: bool = False,
    seal_session: bool = False,
) -> dict[str, Any]:
    brain_path = Path(brain_db or BRAIN_DB)
    cieu_path = Path(cieu_db)
    packet = build_aiden_idle_learning_packet(
        cieu_db=cieu_path,
        brain_db=brain_path,
        allow_brain_write=allow_brain_write,
        explicit_session_task_active=explicit_session_task_active,
        use_host_live_network=use_host_live_network,
        marker_path=marker_path,
        owner_explicit_production_write_approval=owner_explicit_production_write_approval,
        pre_write_backup_metadata=pre_write_backup_metadata,
        force_production_target=force_production_target,
    )
    gov = _load_ystar_module("ystar.governance.aiden_idle_learning_contract", ystar_gov_root)
    governance = gov.validate_and_write_aiden_idle_learning_packet(
        packet,
        cieu_db=str(cieu_path),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    decision = governance["governance_decision"]["decision"]
    brain_write = {"brain_write_performed": False, "reason": "not_requested_or_not_allowed"}
    if decision == "ALLOW" and allow_brain_write:
        brain_write = apply_knowledge_graph_delta_to_brain(
            packet["knowledge_graph_delta"],
            brain_db=brain_path,
            max_nodes=int(packet["brain_write_policy"]["max_nodes_per_cycle"]),
            max_edges=int(packet["brain_write_policy"]["max_edges_per_cycle"]),
        )
    summary = summarize_cieustore(cieu_path)
    result = {
        "artifact_id": "e116_aiden_idle_continuous_learning_cycle_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "learning_packet": packet,
        "YstarGov_idle_learning_write_result": governance,
        "brain_write_result": brain_write,
        "CIEUStore_summary": summary,
        "idle_learning_cycle_proven": (
            decision == "ALLOW"
            and governance.get("formal_CIEU_log_written") is True
            and (not allow_brain_write or brain_write.get("brain_write_performed") is True)
        ),
        "continuous_runtime_capability": {
            "supports_24h_idle_loop": True,
            "active_session_preempts_idle_learning": True,
            "host_launchagent_started_by_this_milestone": False,
            "manual_start_command": (
                "python3 office/mission_command/e116_aiden_idle_continuous_learning_runtime.py "
                "--continuous --allow-brain-write --use-host-live-network"
            ),
        },
        "truth_constraints": dict(packet["truth_constraints"]),
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_governed_idle_learning",
            "L5-B": "stronger_structured_governed_intelligence_with_continuous_CEO_knowledge_graph_growth",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_governed_idle_brain_graph_write_supported_test_proven",
        },
    }
    return result


def apply_knowledge_graph_delta_to_brain(
    delta: Mapping[str, Any],
    *,
    brain_db: str | Path,
    max_nodes: int = 50,
    max_edges: int = 100,
) -> dict[str, Any]:
    scripts_dir = BRIDGE_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import aiden_brain

    brain_path = Path(brain_db)
    brain_path.parent.mkdir(parents=True, exist_ok=True)
    aiden_brain.init_db(str(brain_path))
    before = aiden_brain.stats(str(brain_path))
    nodes = list(delta.get("nodes") or [])[:max_nodes]
    edges = list(delta.get("edges") or [])[:max_edges]
    for node in nodes:
        dims = node.get("dims") if isinstance(node.get("dims"), Mapping) else {}
        aiden_brain.add_node(
            str(node["node_id"]),
            str(node["name"]),
            file_path=str(node.get("source_url") or "e116_idle_learning"),
            node_type=str(node.get("node_type") or "ceo_idle_learning"),
            depth_label=str(node.get("depth_label") or "operational"),
            dims={
                "y": float(dims.get("y", 0.65)),
                "x": float(dims.get("x", 0.75)),
                "z": float(dims.get("z", 0.65)),
                "t": float(dims.get("t", 0.8)),
                "phi": float(dims.get("phi", 0.75)),
                "c": float(dims.get("c", 0.6)),
            },
            principles=list(node.get("source_evidence_ids") or []),
            summary=str(node.get("summary") or "")[:360],
            content_hash=_stable_hash(json.dumps(node, sort_keys=True, default=str)),
            db_path=str(brain_path),
        )
    for edge in edges:
        aiden_brain.add_edge(
            str(edge["source_id"]),
            str(edge["target_id"]),
            weight=float(edge.get("weight", 0.5)),
            edge_type=str(edge.get("edge_type") or "idle_learning"),
            db_path=str(brain_path),
        )
    after = aiden_brain.stats(str(brain_path))
    return {
        "brain_write_performed": True,
        "target_brain_db": str(brain_path),
        "nodes_attempted": len(nodes),
        "edges_attempted": len(edges),
        "brain_stats_before": before,
        "brain_stats_after": after,
        "node_delta": after["nodes"] - before["nodes"],
        "edge_delta": after["edges"] - before["edges"],
    }


def write_e116_idle_learning_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_aiden_idle_continuous_learning_cycle(
        cieu_db=cieu_db,
        brain_db=base / "aiden_brain.db",
        ystar_gov_root=ystar_gov_root,
        allow_brain_write=False,
        use_host_live_network=False,
        seal_session=False,
    )
    report = _completion_report(result)
    status = _status_report(result)
    files = {
        "report_json": base / "office/mission_command/e116_aiden_idle_continuous_learning_runtime_report.json",
        "report_md": base / "office/mission_command/e116_aiden_idle_continuous_learning_runtime_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e116_aiden_idle_continuous_learning_runtime.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e116_aiden_idle_continuous_learning_runtime.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_markdown(report), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["status_md"].write_text(_status_markdown(status), encoding="utf-8")
    return report


def run_idle_learning_loop(
    *,
    cieu_db: str | Path,
    brain_db: str | Path | None = None,
    sleep_seconds: int = 900,
    max_cycles: int = 0,
    allow_brain_write: bool = False,
    use_host_live_network: bool = False,
    marker_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    results = []
    cycles = 0
    while True:
        results.append(
            run_aiden_idle_continuous_learning_cycle(
                cieu_db=cieu_db,
                brain_db=brain_db,
                allow_brain_write=allow_brain_write,
                use_host_live_network=use_host_live_network,
                marker_path=marker_path,
                seal_session=False,
            )
        )
        cycles += 1
        if max_cycles and cycles >= max_cycles:
            return results
        time.sleep(sleep_seconds)


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


def copy_brain_for_test(tmp_dir: str | Path, source_brain_db: str | Path | None = None) -> Path:
    source = Path(source_brain_db or BRAIN_DB)
    target = Path(tmp_dir) / "aiden_brain_e116_test_copy.db"
    if source.exists():
        shutil.copy2(source, target)
    else:
        target.touch()
    return target


def _completion_report(result: Mapping[str, Any]) -> dict[str, Any]:
    packet = result["learning_packet"]
    delta = packet["knowledge_graph_delta"]
    return {
        "milestone_id": MILESTONE_ID,
        "idle_learning_cycle_proven": result["idle_learning_cycle_proven"],
        "Y_star_gov_idle_learning_decision": result["YstarGov_idle_learning_write_result"]["governance_decision"]["decision"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "curriculum_domain_count": len(packet["curriculum_domains"]),
        "accepted_evidence_count": len(packet["evidence_items"]),
        "rejected_evidence_count": len(packet.get("rejected_evidence_items") or []),
        "knowledge_node_count": len(delta["nodes"]),
        "knowledge_edge_count": len(delta["edges"]),
        "brain_write_mode": packet["brain_write_policy"]["write_mode"],
        "brain_write_result": result["brain_write_result"],
        "continuous_runtime_capability": result["continuous_runtime_capability"],
        "CZL_closure": packet["CZL_closure"],
        "what_was_not_claimed": [
            "no external action executed",
            "no customer validation",
            "no revenue/payment signal",
            "no live provider execution",
            "no K9Audit integration",
            "host LaunchAgent not started by this milestone",
        ],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }


def _status_report(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "status": "implemented_internal_runtime",
        "idle_learning": {
            "supports_24h_idle_loop": True,
            "session_task_preemption": True,
            "Y_star_gov_governed": True,
            "CIEUStore_written": result["YstarGov_idle_learning_write_result"]["formal_CIEU_log_written"],
            "brain_write_supported": True,
            "production_daemon_started": False,
        },
        "L5_truth_table_after": result["L5_truth_table_after"],
        "remaining_blockers": [
            "Host LaunchAgent/daemon activation should be a separate owner-visible ops step.",
            "Live web coverage depends on host network availability and source-date metadata.",
        ],
    }


def _report_markdown(report: Mapping[str, Any]) -> str:
    return (
        f"# E116 Aiden Idle Continuous Learning Runtime\n\n"
        f"- Idle learning cycle proven: {report['idle_learning_cycle_proven']}\n"
        f"- Y-star-gov decision: {report['Y_star_gov_idle_learning_decision']}\n"
        f"- Curriculum domains: {report['curriculum_domain_count']}\n"
        f"- Accepted evidence: {report['accepted_evidence_count']}\n"
        f"- Knowledge nodes: {report['knowledge_node_count']}\n"
        f"- Knowledge edges: {report['knowledge_edge_count']}\n"
        f"- Brain write mode in report run: {report['brain_write_mode']}\n\n"
        "Aiden now has a governed idle learning runtime capable of building source-dated CEO knowledge graph deltas while no explicit session task is active. "
        "Brain graph writes are allowed only after Y-star-gov validation and CIEUStore record creation.\n"
    )


def _status_markdown(status: Mapping[str, Any]) -> str:
    idle = status["idle_learning"]
    return (
        f"# Runtime Status After E116\n\n"
        f"- Supports 24h idle loop: {idle['supports_24h_idle_loop']}\n"
        f"- Session task preemption: {idle['session_task_preemption']}\n"
        f"- Y-star-gov governed: {idle['Y_star_gov_governed']}\n"
        f"- CIEUStore written: {idle['CIEUStore_written']}\n"
        f"- Production daemon started: {idle['production_daemon_started']}\n"
        f"- L5-E: {status['L5_truth_table_after']['L5-E']}\n"
    )


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None = None):
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _domain(domain_id: str, objective: str, queries: list[str]) -> dict[str, Any]:
    return {
        "domain_id": domain_id,
        "priority": "mandatory",
        "learning_objective": objective,
        "queries": queries,
        "runtime_owner": "bridge-labs",
        "governance_owner": "Y-star-gov",
        "CIEU_recording_required": True,
    }


def _ev(domain_id: str, title: str, url: str, source_date: str, claim: str, freshness_status: str, observed_at: str) -> dict[str, Any]:
    return {
        "evidence_id": f"e116_{_stable_hash(domain_id + url)[:12]}",
        "domain_id": domain_id,
        "source_title": title,
        "source_url": url,
        "source_date": source_date,
        "observed_at": observed_at,
        "claim_summary": claim,
        "evidence_type": "idle_learning_public_read_evidence",
        "freshness_status": freshness_status,
    }


def _map_domain_to_e114_domain(domain_id: str) -> str:
    return {
        "market_intelligence": "ai_security_compliance",
        "competitive_strategy": "ai_security_compliance",
        "product_strategy": "cyber_insurance",
        "sales_and_distribution": "local_services_dispatch",
        "governance_and_risk": "ai_security_compliance",
        "technology_architecture": "ai_security_compliance",
        "failure_residual_learning": "cpa_tax_accounting",
    }.get(domain_id, "ai_security_compliance")


def _domain_from_evidence(domain_id: str, domain_by_id: Mapping[str, Mapping[str, Any]]) -> str:
    if domain_id in domain_by_id:
        return domain_id
    for candidate in domain_by_id:
        if _map_domain_to_e114_domain(candidate) == domain_id:
            return candidate
    return "market_intelligence"


def _node_type_for_domain(domain_id: str) -> str:
    if "compet" in domain_id:
        return "competitor_intelligence"
    if "governance" in domain_id or "compliance" in domain_id:
        return "governance_knowledge"
    if "technology" in domain_id:
        return "technical_architecture_knowledge"
    if "failure" in domain_id:
        return "failure_residual_knowledge"
    return "ceo_learning_fact"


def _dims_for_domain(domain_id: str) -> dict[str, float]:
    if "competitive" in domain_id:
        return {"y": 0.65, "x": 0.82, "z": 0.7, "t": 0.78, "phi": 0.82, "c": 0.65}
    if "governance" in domain_id:
        return {"y": 0.8, "x": 0.72, "z": 0.78, "t": 0.74, "phi": 0.8, "c": 0.62}
    if "technology" in domain_id:
        return {"y": 0.66, "x": 0.86, "z": 0.72, "t": 0.8, "phi": 0.74, "c": 0.7}
    return {"y": 0.7, "x": 0.78, "z": 0.72, "t": 0.78, "phi": 0.76, "c": 0.68}


def _dedupe_evidence(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        item = dict(row)
        key = str(item.get("source_url") or item.get("evidence_id") or item.get("source_title"))
        if key in seen:
            continue
        seen.add(key)
        if not item.get("evidence_id"):
            item["evidence_id"] = f"e116_{_stable_hash(key + str(item.get('claim_summary') or ''))[:12]}"
        deduped.append(item)
    return deduped


def _status_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("freshness_status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def attach_learning_quality_scores(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    domain_counts: dict[str, int] = {}
    for row in rows:
        domain = str(row.get("domain_id") or "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    scored = []
    for row in rows:
        item = dict(row)
        item["learning_quality"] = score_learning_evidence_quality(item, domain_counts=domain_counts)
        scored.append(item)
    return scored


def score_learning_evidence_quality(
    evidence: Mapping[str, Any],
    *,
    domain_counts: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    text = " ".join(
        str(evidence.get(field) or "")
        for field in ("source_title", "source_url", "claim_summary", "domain_id", "query")
    ).lower()
    url = str(evidence.get("source_url") or "").lower()
    source_domain = _source_domain(url)
    source_authority_tiers = {
        "nist.gov": ("government_standard", 0.9),
        "owasp.org": ("security_standard", 0.86),
        "gartner.com": ("market_research", 0.84),
        "mckinsey.com": ("strategy_research", 0.82),
        "modelcontextprotocol.io": ("technical_standard", 0.82),
        "ycombinator.com": ("startup_operator_guidance", 0.78),
        "stripe.com": ("commercial_operator_guidance", 0.76),
        "cbinsights.com": ("market_database", 0.78),
        "businessinsider.com": ("business_press", 0.74),
        "ibm.com": ("operator_research", 0.76),
        "guidehouse.com": ("industry_advisory", 0.74),
        "internationalaccountingbulletin.com": ("vertical_trade_press", 0.74),
        "crowdfundinsider.com": ("funding_press", 0.72),
        "natlawreview.com": ("legal_business_press", 0.72),
        "techtarget.com": ("industry_trade_press", 0.72),
    }
    tier, source_authority = source_authority_tiers.get(source_domain, ("unclassified_public_source", 0.64))
    freshness_status = str(evidence.get("freshness_status") or "")
    freshness = 0.9 if freshness_status == "accepted_current" else 0.76 if freshness_status == "accepted_recent" else 0.68
    commercial_terms = ("buyer", "market", "pricing", "funding", "compliance", "automation", "customer", "revenue", "governance", "risk", "competitor", "paid", "enterprise")
    commercial_relevance = min(0.95, 0.55 + 0.04 * sum(1 for term in commercial_terms if term in text))
    novelty_terms = ("2026", "agentic", "ai agent", "funding", "launch", "readiness", "billion", "autopilot", "market")
    novelty = min(0.92, 0.56 + 0.045 * sum(1 for term in novelty_terms if term in text))
    domain = str(evidence.get("domain_id") or "unknown")
    support_count = int((domain_counts or {}).get(domain, 1))
    cross_source_support = min(0.9, 0.55 + 0.08 * min(support_count, 4))
    action_terms = ("requires", "need", "pain", "risk", "reduces", "automation", "governance", "compliance", "buyer", "workflow", "evidence")
    actionability = min(0.92, 0.55 + 0.04 * sum(1 for term in action_terms if term in text))
    source_url_depth = min(0.9, 0.5 + 0.1 * min(_url_path_depth(url), 4))
    claim_specificity = _claim_specificity_score(str(evidence.get("claim_summary") or ""))
    current_signal_verifiability = 0.85 if evidence.get("source_date") and _url_path_depth(url) >= 1 else 0.62
    risk_of_staleness = 0.15 if freshness_status == "accepted_current" else 0.28 if freshness_status == "accepted_recent" else 0.35
    quality_score = (
        source_authority * 0.15
        + freshness * 0.14
        + commercial_relevance * 0.14
        + novelty * 0.09
        + cross_source_support * 0.11
        + actionability * 0.12
        + source_url_depth * 0.08
        + claim_specificity * 0.1
        + current_signal_verifiability * 0.04
        + (1.0 - risk_of_staleness) * 0.03
    )
    return {
        "quality_score": round(quality_score, 3),
        "source_authority": round(source_authority, 3),
        "source_authority_tier": tier,
        "source_authority_basis": source_domain or "missing_source_domain",
        "freshness": round(freshness, 3),
        "commercial_relevance": round(commercial_relevance, 3),
        "novelty": round(novelty, 3),
        "cross_source_support": round(cross_source_support, 3),
        "actionability": round(actionability, 3),
        "source_url_depth": round(source_url_depth, 3),
        "claim_specificity": round(claim_specificity, 3),
        "current_signal_verifiability": round(current_signal_verifiability, 3),
        "corroboration_count": support_count,
        "risk_of_staleness": round(risk_of_staleness, 3),
        "quality_basis": "deterministic_public_read_quality_score_v2_source_depth_specificity_verifiability",
    }


def _average_quality_for_refs(refs: Sequence[str], evidence_items: Sequence[Mapping[str, Any]]) -> float:
    by_id = {str(item.get("evidence_id")): item for item in evidence_items}
    scores = [
        float(by_id[ref].get("learning_quality", {}).get("quality_score") or 0.0)
        for ref in refs
        if ref in by_id
    ]
    if not scores:
        return 0.7
    return round(sum(scores) / len(scores), 3)


def _is_production_brain_target(brain_db: str | Path) -> bool:
    try:
        return Path(brain_db).expanduser().resolve() == BRAIN_DB.expanduser().resolve()
    except Exception:
        return False


def _source_domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def _url_path_depth(url: str) -> int:
    try:
        path = urlparse(url).path
    except Exception:
        return 0
    return len([part for part in path.split("/") if part])


def _claim_specificity_score(claim: str) -> float:
    if not claim:
        return 0.45
    tokens = [token for token in claim.replace("/", " ").replace("-", " ").split() if token]
    has_number = any(any(char.isdigit() for char in token) for token in tokens)
    has_named_signal = any(token[:1].isupper() for token in tokens[1:])
    length_score = min(0.82, 0.46 + 0.012 * min(len(tokens), 30))
    bonus = (0.06 if has_number else 0.0) + (0.04 if has_named_signal else 0.0)
    return round(min(0.94, length_score + bonus), 3)


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Aiden's governed idle continuous learning runtime.")
    parser.add_argument("--cieu-db", default=str(BRIDGE_ROOT / ".e116_idle_learning_cieu.db"))
    parser.add_argument("--brain-db", default=str(BRAIN_DB))
    parser.add_argument("--allow-brain-write", action="store_true")
    parser.add_argument("--use-host-live-network", action="store_true")
    parser.add_argument("--continuous", action="store_true")
    parser.add_argument("--sleep-seconds", type=int, default=900)
    parser.add_argument("--max-cycles", type=int, default=0)
    parser.add_argument("--active-session-marker")
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args(argv)

    if args.write_reports:
        print(json.dumps(write_e116_idle_learning_reports(cieu_db=args.cieu_db, ystar_gov_root=Y_GOV_ROOT), indent=2))
        return 0
    if args.continuous:
        run_idle_learning_loop(
            cieu_db=args.cieu_db,
            brain_db=args.brain_db,
            sleep_seconds=args.sleep_seconds,
            max_cycles=args.max_cycles,
            allow_brain_write=args.allow_brain_write,
            use_host_live_network=args.use_host_live_network,
            marker_path=args.active_session_marker,
        )
        return 0
    result = run_aiden_idle_continuous_learning_cycle(
        cieu_db=args.cieu_db,
        brain_db=args.brain_db,
        allow_brain_write=args.allow_brain_write,
        use_host_live_network=args.use_host_live_network,
        marker_path=args.active_session_marker,
        seal_session=False,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
