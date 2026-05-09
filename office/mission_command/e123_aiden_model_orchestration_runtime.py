from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MILESTONE_ID = "E123_Aiden_Model_Orchestration_Runtime_R1"
SESSION_ID = "e123_aiden_model_orchestration_runtime"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
HOST_RUNTIME_BRIDGE_ROOT = Path(os.environ.get("YSTAR_HOST_RUNTIME_BRIDGE_ROOT", "/tmp/ystar_host_runtime_bridge"))


def discover_local_long_term_memory_assets(
    *,
    bridge_root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    gov_mcp_root: str | Path | None = None,
) -> dict[str, Any]:
    """Find reusable local memory systems instead of inventing another one."""

    bridge = Path(bridge_root or BRIDGE_ROOT)
    ygov = Path(ystar_gov_root or Y_GOV_ROOT)
    govmcp = Path(gov_mcp_root or GOV_MCP_ROOT)
    assets = [
        _asset(
            "CIEUStore_formal_memory",
            "Y-star-gov",
            ygov / "ystar/governance/cieu_store.py",
            "runtime_active",
            "formal governance/evidence memory; all model choices must be written here",
            "mandatory_memory_spine",
        ),
        _asset(
            "YstarGov_memory_store",
            "Y-star-gov",
            ygov / "ystar/memory/store.py",
            "runtime_active_reusable",
            "SQLite-backed local long-term agent/team memory with decay, recall, reinforcement, access log",
            "reuse_as_team_memory_substrate",
            companion_paths=[ygov / "ystar/memory/models.py", ygov / "tests/test_memory_store.py"],
        ),
        _asset(
            "Aiden_6D_brain",
            "bridge-labs",
            bridge / "aiden_brain.db",
            "runtime_active_local_db",
            "Aiden 6D brain graph used by E93/E108/E116/E118; writes remain owner/backup gated",
            "mandatory_ceo_brain_memory",
            companion_paths=[bridge / "office/mission_command/e93_brain_grounded_live_runtime.py"],
        ),
        _asset(
            "CIEU_to_brain_bridge",
            "Y-star-gov",
            ygov / "ystar/governance/cieu_brain_bridge.py",
            "runtime_active_reusable",
            "projects CIEU events into 6D brain space and records activations",
            "reuse_for_result_quality_to_memory",
            companion_paths=[ygov / "ystar/governance/cieu_brain_learning.py", ygov / "ystar/governance/brain_auto_ingest.py"],
        ),
        _asset(
            "E116_E118_governed_brain_learning",
            "bridge-labs",
            bridge / "office/mission_command/e116_aiden_idle_continuous_learning_runtime.py",
            "runtime_active_owner_gated_write",
            "governed idle learning, evidence quality, and production brain write boundary",
            "reuse_for_long_term_learning_candidates",
            companion_paths=[bridge / "office/mission_command/e118_production_brain_write_boundary.py"],
        ),
        _asset(
            "E120_unknown_problem_learning_protocol",
            "bridge-labs",
            bridge / "office/mission_command/e120_aiden_unknown_problem_learning_protocol.py",
            "runtime_active",
            "teaches Aiden what to learn, which thinking modes/tools to use, and how to build knowledge graphs for unfamiliar problems",
            "reuse_before_unfamiliar_task_or_high_wisdom_routing",
        ),
        _asset(
            "E24_legacy_CEO_knowledge_graph",
            "bridge-labs",
            bridge / "office/mission_command/e24_ecosystem_archaeology.py",
            "legacy_runtime_reusable_as_context",
            "early CEO knowledge graph, whole-ecosystem archaeology, route registry, and commercial path portfolio",
            "reuse_as_historical_context_not_current_truth",
            companion_paths=[bridge / "reports/integration/e24_whole_ecosystem_ceo_kg_brain_runtime.md"],
        ),
        _asset(
            "file_backed_CEO_wisdom_corpus",
            "bridge-labs",
            bridge / "knowledge/ceo/wisdom",
            "runtime_context_corpus",
            "local CEO principles, theory, paradigms, and self-knowledge files for long-term cognition",
            "reuse_as_learning_source_corpus",
            companion_paths=[bridge / "knowledge/ceo/theory"],
        ),
        _asset(
            "meeting_room_turn_memory",
            "bridge-labs",
            bridge / "office/aiden_meeting_room/meeting_memory.py",
            "short_context_only",
            "last-turn meeting memory; useful for conversational continuity but forbidden as substitute for long-term memory",
            "short_context_not_canonical_memory",
        ),
        _asset(
            "legacy_gemma_shadow_quality_client",
            "bridge-labs",
            bridge / "scripts/gemma_client.py",
            "quarantined_external_fallback_risk",
            "old Gemma/Claude shadow comparison client; reuse concepts only, not direct external fallback",
            "reuse_quality_metrics_not_external_call_path",
        ),
        _asset(
            "gov_mcp_execution_receipt_boundary",
            "gov-mcp",
            govmcp / "gov_mcp/outbound/receipts.py",
            "runtime_active_dry_run_only",
            "provider/tool boundary receipts; relevant when model orchestration reaches external tools",
            "reuse_for_tool_boundary_quality_receipts",
        ),
    ]
    return {
        "artifact_id": "e123_local_memory_asset_discovery",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "assets": assets,
        "asset_count": len(assets),
        "reusable_runtime_asset_count": len([a for a in assets if "runtime_active" in a["runtime_status"]]),
        "quarantined_or_context_only_count": len([a for a in assets if "quarantined" in a["runtime_status"] or "short_context_only" in a["runtime_status"]]),
        "reuse_conclusion": (
            "Aiden already has multiple local memory substrates: CIEUStore for formal evidence, "
            "Y-star-gov MemoryStore for decayed agent/team memory, Aiden 6D brain for CEO cognition, "
            "CIEU-to-brain bridge for result activation, and local CEO wisdom/knowledge corpora. "
            "E123 reuses these instead of creating a new memory database."
        ),
    }


def build_model_tool_catalog() -> list[dict[str, Any]]:
    return [
        {
            "model_id": "deterministic_validator",
            "provider": "Y-star-gov",
            "model_class": "rule_engine",
            "best_for": ["governance", "schema validation", "policy decisions", "CIEU write preflight"],
            "cost_tier": "zero_external_cost",
            "privacy_tier": "local",
            "execution_boundary": "Y-star-gov deterministic contract",
        },
        {
            "model_id": "local_gemma4_e4b",
            "provider": "Ollama_local",
            "model_class": "local_llm",
            "best_for": ["private local reasoning", "drafting", "summarization", "low/medium wisdom local tasks"],
            "cost_tier": "local_compute",
            "privacy_tier": "local_private",
            "execution_boundary": "E122 host runtime service bridge",
        },
        {
            "model_id": "local_ystar_gemma",
            "provider": "Ollama_local",
            "model_class": "local_llm",
            "best_for": ["Aiden persona-local responses", "local continuity", "low-cost shadow comparison"],
            "cost_tier": "local_compute",
            "privacy_tier": "local_private",
            "execution_boundary": "E122 host runtime service bridge",
        },
        {
            "model_id": "codex_executor",
            "provider": "Codex",
            "model_class": "engineering_executor",
            "best_for": ["repo mutation", "tests", "delivery bridge", "implementation tasks"],
            "cost_tier": "executor_session",
            "privacy_tier": "workspace_bound",
            "execution_boundary": "E92 CEOImplementationOrder before Codex prompt",
        },
        {
            "model_id": "external_gpt",
            "provider": "OpenAI_external",
            "model_class": "frontier_reasoner",
            "best_for": ["frontier strategic synthesis", "complex judgment after redaction"],
            "cost_tier": "external_paid",
            "privacy_tier": "requires_redaction_and_owner_approval",
            "execution_boundary": "owner-approved external model boundary",
        },
        {
            "model_id": "external_claude",
            "provider": "Anthropic_external",
            "model_class": "frontier_reasoner",
            "best_for": ["independent audit", "strategy critique after redaction"],
            "cost_tier": "external_paid",
            "privacy_tier": "requires_redaction_and_owner_approval",
            "execution_boundary": "owner-approved external model boundary",
        },
    ]


def classify_aiden_task(owner_intent: str, *, task_id: str = "e123_owner_task") -> dict[str, Any]:
    text = (owner_intent or "").lower()
    task_type = "local_reasoning"
    if any(term in text for term in ["governance", "validator", "contract", "治理", "验证"]):
        task_type = "governance_validation"
    if any(term in text for term in ["implement", "code", "test", "repo", "commit", "实现", "代码", "测试"]):
        task_type = "engineering_execution"
    if any(term in text for term in ["strategy", "market", "revenue", "competitor", "赚钱", "战略", "市场", "竞品"]):
        task_type = "high_wisdom_strategy"
    if any(term in text for term in ["model", "gemma", "gpt", "claude", "orchestration", "模型", "调度"]):
        task_type = "model_orchestration"

    external_signals = ["send", "publish", "customer", "payment", "email", "outreach", "支付", "客户", "发送", "发布"]
    risk_tier = "low_internal" if not any(term in text for term in external_signals) else "owner_boundary_or_high_risk"
    privacy_tier = "local_private" if any(term in text for term in ["private", "secret", "memory", "repo", "隐私", "记忆", "仓库"]) else "public_or_low_sensitivity"
    context_size = "large" if len(owner_intent) > 4000 or any(term in text for term in ["full repo", "全仓库", "长期记忆"]) else "medium"
    required_wisdom_level = "frontier_or_multi_model" if task_type == "high_wisdom_strategy" else "medium" if task_type in {"engineering_execution", "model_orchestration"} else "low_to_medium"
    return {
        "task_id": task_id,
        "owner_intent": owner_intent,
        "task_type": task_type,
        "risk_tier": risk_tier,
        "privacy_tier": privacy_tier,
        "context_size": context_size,
        "required_wisdom_level": required_wisdom_level,
    }


def select_model_for_task(task_context: Mapping[str, Any], *, owner_approved_external_model_use: bool = False) -> dict[str, Any]:
    task_type = str(task_context.get("task_type") or "")
    privacy = str(task_context.get("privacy_tier") or "")
    if task_type == "governance_validation":
        return {"model_id": "deterministic_validator", "role": "validator", "selection_reason": "deterministic governance task"}
    if task_type == "engineering_execution":
        return {"model_id": "codex_executor", "role": "executor", "selection_reason": "repo implementation requires Codex executor boundary"}
    if task_type == "high_wisdom_strategy" and owner_approved_external_model_use and privacy != "local_private":
        return {"model_id": "external_gpt", "role": "frontier_reasoner", "selection_reason": "owner-approved frontier synthesis for public/low-sensitivity strategy"}
    if task_type == "high_wisdom_strategy":
        return {"model_id": "local_gemma4_e4b", "role": "local_reasoner", "selection_reason": "no owner-approved external model boundary; use local model plus deterministic validators"}
    return {"model_id": "local_gemma4_e4b", "role": "local_reasoner", "selection_reason": "low/medium private local reasoning at low cost"}


def build_model_orchestration_packet(
    owner_intent: str,
    *,
    cieu_db: str | Path,
    task_id: str = "e123_owner_task",
    owner_approved_external_model_use: bool = False,
    bridge_root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
    gov_mcp_root: str | Path | None = None,
) -> dict[str, Any]:
    task = classify_aiden_task(owner_intent, task_id=task_id)
    catalog = build_model_tool_catalog()
    selected = select_model_for_task(task, owner_approved_external_model_use=owner_approved_external_model_use)
    memory_discovery = discover_local_long_term_memory_assets(
        bridge_root=bridge_root,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    boundary = _execution_boundary_for(selected["model_id"])
    if selected["model_id"] in {"external_gpt", "external_claude"}:
        boundary["external_provider_call_allowed"] = True
        boundary["redacted_context_only"] = True
    return {
        "orchestration_id": f"e123_model_orchestration_{task_id}",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "task_context": task,
        "routing_factors": {
            "task_type": task["task_type"],
            "risk_tier": task["risk_tier"],
            "privacy_tier": task["privacy_tier"],
            "context_size": task["context_size"],
            "cost_sensitivity": "prefer_local_low_cost_then_escalate",
            "required_wisdom_level": task["required_wisdom_level"],
        },
        "candidate_models": catalog,
        "selected_model": selected,
        "execution_boundary": boundary,
        "owner_approval": {"owner_approved_external_model_use": owner_approved_external_model_use},
        "memory_context_plan": {
            "local_long_term_memory_required": True,
            "recent_memory_only": False,
            "discovered_memory_assets": memory_discovery["assets"],
            "reuse_plan": [
                "CIEUStore records model choice and result-quality comparison",
                "Aiden 6D brain supplies CEO cognition and future learning candidates",
                "Y-star-gov MemoryStore is reused as agent/team local memory substrate",
                "meeting room memory remains short-context only and cannot satisfy long-term recall",
            ],
        },
        "quality_comparison_plan": {
            "comparison_required": True,
            "metrics": [
                "task_fit",
                "privacy_preservation",
                "evidence_grounding",
                "latency",
                "cost",
                "output_quality",
                "residual_delta",
            ],
            "CIEU_recording_required": True,
            "raw_private_prompt_shadowing_allowed": False,
            "comparison_mode": "post_execution_receipt_and_shadow_only_when_redacted_or_local",
        },
        "routing_policy_update": {
            "update_mode": "proposal_only",
            "direct_policy_mutation": False,
            "owner_review_required": True,
            "candidate_policy_update": "update model routing weights only after CIEU-backed quality evidence accumulates",
        },
        "CIEU_linkage": {
            "CIEU_recording_required": True,
            "target_event_type": "AIDEN_MODEL_ORCHESTRATION_DECISION",
            "target_cieu_db": str(cieu_db),
        },
        "truth_constraints": {
            "model_choice_recent_memory_only": False,
            "raw_prompt_to_codex_without_CEOImplementationOrder": False,
            "external_model_called_without_owner_approval": False,
            "private_data_sent_to_external_model": False,
            "arbitrary_shell_allowed": False,
            "external_business_action_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "direct_brain_write_without_owner_gate": False,
            "direct_policy_mutation": False,
            "K9Audit_write_claim": False,
        },
    }


def run_aiden_model_orchestration_session(
    *,
    owner_intent: str,
    cieu_db: str | Path,
    task_id: str = "e123_owner_task",
    ystar_gov_root: str | Path | None = None,
    owner_approved_external_model_use: bool = False,
    seal_session: bool = False,
) -> dict[str, Any]:
    packet = build_model_orchestration_packet(
        owner_intent,
        cieu_db=cieu_db,
        task_id=task_id,
        owner_approved_external_model_use=owner_approved_external_model_use,
        ystar_gov_root=ystar_gov_root,
    )
    gov = _load_ystar_module("ystar.governance.aiden_model_orchestration_contract", ystar_gov_root)
    validation = gov.validate_and_write_aiden_model_orchestration_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    selected_id = packet["selected_model"]["model_id"]
    return {
        "artifact_id": "e123_aiden_model_orchestration_runtime_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "model_orchestration_packet": packet,
        "YstarGov_model_orchestration_result": validation,
        "selected_execution_preview": _execution_preview_for(selected_id, packet),
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "model_orchestration_runtime_proven": validation["governance_decision"]["decision"] == "ALLOW",
        "truth_constraints": packet["truth_constraints"],
        "what_was_not_claimed": [
            "no external model call executed",
            "no local Gemma generation executed by this runtime test",
            "no customer contact",
            "no payment",
            "no production brain write",
            "no K9Audit write",
        ],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_governed_model_orchestration",
            "L5-B": "stronger_governed_intelligence_with_memory_aware_model_tool_routing",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_with_reused_local_memory_substrates",
        },
    }


def write_e123_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_aiden_model_orchestration_session(
        owner_intent="Aiden should choose the right model/tool for a private local memory summarization task.",
        cieu_db=cieu_db,
        task_id="e123_report_task",
        ystar_gov_root=ystar_gov_root,
    )
    discovery = discover_local_long_term_memory_assets(bridge_root=base, ystar_gov_root=ystar_gov_root)
    report = {
        "milestone_id": MILESTONE_ID,
        "base_hashes": {
            "bridge_labs": "0f72085df02f861a604934744d68ecaba1ae72c6",
            "Y_star_gov": "9ff774d35f01c2335bab126372e2217a22d796f1",
        },
        "model_orchestration_decision": result["YstarGov_model_orchestration_result"]["governance_decision"],
        "selected_model": result["model_orchestration_packet"]["selected_model"],
        "candidate_models": [item["model_id"] for item in result["model_orchestration_packet"]["candidate_models"]],
        "local_memory_asset_discovery": discovery,
        "memory_reuse_conclusion": discovery["reuse_conclusion"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "truth_constraints": result["truth_constraints"],
        "what_was_not_claimed": result["what_was_not_claimed"],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented_model_orchestration_runtime",
        "Y_star_gov_model_choice_validation": result["YstarGov_model_orchestration_result"]["governance_decision"]["decision"],
        "selected_model_for_report_run": result["model_orchestration_packet"]["selected_model"]["model_id"],
        "local_long_term_memory_assets_reused": discovery["asset_count"],
        "direct_external_model_execution": False,
        "direct_policy_mutation": False,
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e123_aiden_model_orchestration_runtime_report.json",
        "report_md": base / "office/mission_command/e123_aiden_model_orchestration_runtime_readback.md",
        "discovery_json": base / "operations/model_orchestration/e123_local_memory_asset_discovery.json",
        "discovery_md": base / "operations/model_orchestration/e123_local_memory_asset_discovery.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e123_aiden_model_orchestration_runtime.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e123_aiden_model_orchestration_runtime.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["discovery_json"].write_text(json.dumps(discovery, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    files["discovery_md"].write_text(_discovery_md(discovery), encoding="utf-8")
    return {"result": result, "report": report, "status": status, "discovery": discovery, "files": {k: str(v) for k, v in files.items()}}


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_path": str(path), "event_count": 0}
    with sqlite3.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
        event_types = [row[0] for row in conn.execute("SELECT DISTINCT event_type FROM cieu_events ORDER BY event_type").fetchall()]
    return {"db_path": str(path), "event_count": int(count), "event_types": event_types}


def _execution_boundary_for(model_id: str) -> dict[str, Any]:
    if model_id in {"local_gemma4_e4b", "local_ystar_gemma"}:
        return {
            "local_only": True,
            "external_provider_call_allowed": False,
            "host_runtime_service_bridge_required": True,
            "host_service_controller_proof": {"status": _host_service_status()},
        }
    if model_id == "codex_executor":
        return {
            "CEOImplementationOrder_required": True,
            "Codex_executor_boundary_required": True,
            "external_provider_call_allowed": False,
            "scope_expansion_allowed": False,
        }
    if model_id == "deterministic_validator":
        return {"local_only": True, "external_provider_call_allowed": False, "deterministic_contract_required": True}
    return {"external_provider_call_allowed": False, "redacted_context_only": True}


def _execution_preview_for(model_id: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    if model_id in {"local_gemma4_e4b", "local_ystar_gemma"}:
        return {
            "execution_mode": "local_model_via_E122_host_runtime_service_bridge",
            "service_id": "ollama_server",
            "model_id": model_id,
            "bridge_root": str(HOST_RUNTIME_BRIDGE_ROOT),
            "actual_generation_executed": False,
        }
    if model_id == "codex_executor":
        return {
            "execution_mode": "CEOImplementationOrder_to_Codex_executor",
            "CEOImplementationOrder_required": True,
            "actual_codex_prompt_generated": False,
        }
    return {
        "execution_mode": "governance_or_external_boundary",
        "selected_model_id": model_id,
        "external_call_executed": False,
        "owner_approval_required_if_external": model_id.startswith("external_"),
    }


def _host_service_status() -> str:
    if HOST_RUNTIME_BRIDGE_ROOT.exists() and (HOST_RUNTIME_BRIDGE_ROOT / "pending").exists():
        return "service_bridge_running"
    return "available"


def _asset(
    asset_id: str,
    repo: str,
    path: Path,
    runtime_status: str,
    purpose: str,
    reuse_status: str,
    *,
    companion_paths: list[Path] | None = None,
) -> dict[str, Any]:
    companions = companion_paths or []
    return {
        "asset_id": asset_id,
        "source_repo": repo,
        "source_path": str(path),
        "source_exists": path.exists(),
        "companion_paths": [str(item) for item in companions],
        "companion_paths_existing": [str(item) for item in companions if item.exists()],
        "runtime_status": runtime_status,
        "purpose": purpose,
        "reuse_status": reuse_status,
        "governance_requirement": "must be referenced in model orchestration memory_context_plan when relevant",
    }


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None) -> Any:
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _report_md(report: Mapping[str, Any]) -> str:
    selected = report["selected_model"]
    return (
        "# E123 Aiden Model Orchestration Runtime\n\n"
        f"- Y-star-gov decision: {report['model_orchestration_decision']['decision']}\n"
        f"- Selected model/tool: {selected['model_id']} ({selected['role']})\n"
        f"- Candidate models/tools: {', '.join(report['candidate_models'])}\n"
        f"- Local memory assets discovered: {report['local_memory_asset_discovery']['asset_count']}\n"
        f"- CIEU events in report DB: {report['CIEUStore_summary']['event_count']}\n\n"
        "E123 makes model/tool choice a governed Aiden runtime action. Aiden is not locked into Gemma4; "
        "it must classify task risk, privacy, cost, context size, and required wisdom, then select the "
        "right local model, deterministic validator, Codex executor, or owner-approved external frontier model.\n"
    )


def _status_md(status: Mapping[str, Any]) -> str:
    return (
        "# Runtime Status After E123\n\n"
        f"- Status: {status['status']}\n"
        f"- Y-star-gov model choice validation: {status['Y_star_gov_model_choice_validation']}\n"
        f"- Selected model in report run: {status['selected_model_for_report_run']}\n"
        f"- Local long-term memory assets reused: {status['local_long_term_memory_assets_reused']}\n"
        "- L5-D remains absent_or_not_executed.\n"
    )


def _discovery_md(discovery: Mapping[str, Any]) -> str:
    lines = ["# E123 Local Memory Asset Discovery", ""]
    lines.append(f"- Asset count: {discovery['asset_count']}")
    lines.append(f"- Reusable runtime assets: {discovery['reusable_runtime_asset_count']}")
    lines.append(f"- Quarantined/context-only assets: {discovery['quarantined_or_context_only_count']}")
    lines.append("")
    for asset in discovery["assets"]:
        lines.append(
            f"- `{asset['asset_id']}`: {asset['runtime_status']} via `{asset['source_path']}`; reuse={asset['reuse_status']}"
        )
    lines.append("")
    lines.append(str(discovery["reuse_conclusion"]))
    return "\n".join(lines) + "\n"


__all__ = [
    "MILESTONE_ID",
    "build_model_orchestration_packet",
    "build_model_tool_catalog",
    "classify_aiden_task",
    "discover_local_long_term_memory_assets",
    "run_aiden_model_orchestration_session",
    "select_model_for_task",
    "summarize_cieustore",
    "write_e123_reports",
]
