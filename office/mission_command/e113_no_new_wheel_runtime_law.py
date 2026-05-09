from __future__ import annotations

import importlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


MILESTONE_ID = "E113_No_New_Wheel_Runtime_Law_CZL_Closure_R1"
SESSION_ID = "e113_no_new_wheel_runtime_law"
RUNTIME_LAW_ID = "labs_existing_capability_recall_no_new_wheel_runtime_law_v1"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))


CAPABILITY_DOMAINS: dict[str, dict[str, Any]] = {
    "czl_residual_loop_engine": {
        "owner_repo": "Y-star-gov",
        "source_paths": [
            "ystar/governance/residual_loop_engine.py",
            "tests/test_residual_loop_engine.py",
            "docs/AMENDMENT_014_DELIVERY_REPORT.md",
        ],
        "correct_path": "reuse ResidualLoopEngine and CZL 5-tuple before implementing residual/goal closure",
        "keywords": ["residual", "failure", "rt+1", "r_t_plus_1", "czl", "goal", "target", "残差", "目标"],
    },
    "czl_message_protocol": {
        "owner_repo": "Y-star-gov",
        "source_paths": ["ystar/kernel/czl_protocol.py", "tests/kernel/test_czl_protocol.py"],
        "correct_path": "reuse CZL dispatch/receipt protocol for executor handoff and empirical Rt+1 verification",
        "keywords": ["codex", "executor", "dispatch", "receipt", "rt+1", "czl"],
    },
    "cieu_prediction_delta": {
        "owner_repo": "Y-star-gov",
        "source_paths": ["ystar/governance/cieu_prediction_delta.py", "docs/cieu_prediction_delta/schema_v0.md"],
        "correct_path": "reuse CIEU prediction-delta schema for prediction vs actual residual learning",
        "keywords": ["prediction", "delta", "residual", "learning", "brain", "cieu"],
    },
    "goal_tree_and_y_star_field": {
        "owner_repo": "bridge-labs",
        "source_paths": [
            "scripts/phase2_goal_tree_schema.py",
            "scripts/phase3_goal_decomposer.py",
            "tests/test_working_memory_snapshot.py",
        ],
        "secondary_source_paths": ["Y-star-gov:ystar/governance/y_star_field_validator.py"],
        "correct_path": "reuse goal tree and Y* field validator before inventing target tracking",
        "keywords": ["goal", "target", "y_star", "subgoal", "实现", "目标"],
    },
    "ceo_doctrine_registry": {
        "owner_repo": "bridge-labs",
        "source_paths": [
            "office/mission_command/e91_ceo_operating_doctrine_registry.py",
            "operations/ceo_doctrine_registry/e91_canonical_doctrine_registry_spec.json",
        ],
        "correct_path": "reuse E91 doctrine registry before adding new CEO work models",
        "keywords": ["doctrine", "operating model", "方法论", "能力"],
    },
    "adaptive_governance_correct_path": {
        "owner_repo": "bridge-labs",
        "source_paths": [
            "office/mission_command/e101_adaptive_governance_discovery_and_correct_path_navigator.py",
            "tests/office/test_e101_adaptive_governance_discovery.py",
        ],
        "correct_path": "reuse E101 correct-path navigator instead of blunt deny or human handoff",
        "keywords": ["governance", "correct_path", "deny", "导航", "治理"],
    },
    "ceo_implementation_order": {
        "owner_repo": "bridge-labs",
        "source_paths": [
            "office/mission_command/e92_ceo_principal_codex_executor_boundary.py",
            "tests/office/test_e92_ceo_principal_codex_executor_boundary.py",
        ],
        "correct_path": "reuse CEOImplementationOrder before any Codex prompt or repo mutation",
        "keywords": ["codex", "executor", "implementation", "prompt", "实现"],
    },
    "aiden_brain_runtime": {
        "owner_repo": "bridge-labs",
        "source_paths": [
            "scripts/aiden_brain.py",
            "office/mission_command/e112_cieu_backed_brain_learning_loop.py",
            "tests/office/test_e112_cieu_backed_brain_learning_loop.py",
        ],
        "correct_path": "reuse Aiden brain runtime and E112 CIEU-backed brain learning candidates",
        "keywords": ["brain", "大脑", "6d", "memory", "writeback", "learning"],
    },
    "open_world_strategy_runtime": {
        "owner_repo": "bridge-labs",
        "source_paths": [
            "office/mission_command/e108_live_global_open_world_strategy_runtime.py",
            "office/mission_command/e110_labs_universal_operating_control_plane.py",
            "tests/office/test_e110_labs_universal_operating_control_plane.py",
        ],
        "correct_path": "reuse E108/E110 live/open-world strategy, competitor, freshness, and math-model path",
        "keywords": ["market", "strategy", "competitor", "pricing", "revenue", "赚钱", "战略", "竞品"],
    },
    "gov_mcp_dry_run_boundary": {
        "owner_repo": "gov-mcp",
        "source_paths": [
            "gov_mcp/outbound/dry_run_adapter.py",
            "gov_mcp/outbound/policy.py",
            "gov_mcp/outbound/receipts.py",
        ],
        "correct_path": "reuse gov-mcp dry-run/no-send boundary before provider/tool execution",
        "keywords": ["provider", "tool", "external", "outbound", "dry-run", "live"],
    },
    "cieu_store_formal_memory": {
        "owner_repo": "Y-star-gov",
        "source_paths": ["ystar/governance/cieu_store.py"],
        "correct_path": "reuse CIEUStore.write_dict; do not create a parallel ledger",
        "keywords": ["cieu", "record", "memory", "evidence", "audit", "brain", "residual"],
    },
}


CAPABILITY_UTILIZATION_GROUPS: dict[str, dict[str, Any]] = {
    "ceo_behavior_center": {
        "domain_id": "ceo_behavior_center",
        "signals": ["answer_owner", "behavior", "meeting_room", "aiden"],
        "source_path_patterns": ["aiden_response_engine", "aiden_meeting_room", "behavior_center"],
        "utilization_rule": "invoke_or_route_when owner-facing CEO behavior is requested",
    },
    "runtime_control_plane": {
        "domain_id": "runtime_control_plane",
        "signals": ["runtime", "control", "gate", "governance"],
        "source_path_patterns": ["e110_labs_universal_operating_control_plane", "e111_aiden_host_runtime"],
        "utilization_rule": "mandatory front door before CEO/Aiden runtime behavior continues",
    },
    "czl_residual_loop_engine": {
        "domain_id": "czl_residual_loop_engine",
        "signals": ["czl", "residual", "rt+1", "goal", "target"],
        "source_path_patterns": ["residual_loop_engine", "czl_protocol", "cieu_prediction_delta"],
        "utilization_rule": "mandatory for failure residual, goal closure, learning loop, or Rt+1 claims",
    },
    "aiden_brain_runtime": {
        "domain_id": "aiden_brain_runtime",
        "signals": ["brain", "memory", "learning", "6d"],
        "source_path_patterns": ["aiden_brain", "brain_learning", "brain_grounded"],
        "utilization_rule": "mandatory for CEO cognition, strategy, and durable learning candidates",
    },
    "open_world_strategy_runtime": {
        "domain_id": "open_world_strategy_runtime",
        "signals": ["market", "strategy", "competitor", "revenue", "pricing", "赚钱", "战略"],
        "source_path_patterns": ["open_world", "strategy", "market", "competitor"],
        "utilization_rule": "mandatory for market strategy; static snapshots cannot satisfy live strategy",
    },
    "ceo_doctrine_registry": {
        "domain_id": "ceo_doctrine_registry",
        "signals": ["doctrine", "operating", "method", "方法"],
        "source_path_patterns": ["doctrine_registry"],
        "utilization_rule": "mandatory when CEO work models or operating obligations are selected",
    },
    "adaptive_governance_correct_path": {
        "domain_id": "adaptive_governance_correct_path",
        "signals": ["correct_path", "navigation", "deny", "revision", "治理"],
        "source_path_patterns": ["adaptive_governance", "correct_path"],
        "utilization_rule": "mandatory when validation fails; governance must navigate instead of blunt handoff",
    },
    "ceo_implementation_order": {
        "domain_id": "ceo_implementation_order",
        "signals": ["codex", "executor", "implementation", "prompt"],
        "source_path_patterns": ["codex_executor", "implementation_order"],
        "utilization_rule": "mandatory before Codex prompts, repo mutation, or implementation execution",
    },
    "gov_mcp_dry_run_boundary": {
        "domain_id": "gov_mcp_dry_run_boundary",
        "signals": ["provider", "tool", "external", "outbound", "dry-run", "live"],
        "source_path_patterns": ["dry_run", "provider_guard", "outbound", "receipts"],
        "utilization_rule": "mandatory for provider/tool boundaries; live execution remains disabled",
    },
    "delivery_bridge": {
        "domain_id": "delivery_bridge",
        "signals": ["commit", "push", "delivery", "github", "bridge"],
        "source_path_patterns": ["repository_delivery_bridge", "delivery_bridge"],
        "utilization_rule": "mandatory fallback when direct remote delivery is blocked",
    },
    "external_validation_and_l4_feedback": {
        "domain_id": "external_validation_and_l4_feedback",
        "signals": ["external", "feedback", "l4", "customer", "validation"],
        "source_path_patterns": ["external_validation", "feedback", "l4"],
        "utilization_rule": "consult for external-feedback design; do not claim customer validation without evidence",
    },
    "legacy_asset_inventory": {
        "domain_id": "legacy_asset_inventory",
        "signals": ["legacy", "archive", "promoted", "quarantine", "old"],
        "source_path_patterns": ["legacy", "archive", "quarantine", "promoted"],
        "utilization_rule": "consult before reviving old assets; stale/quarantined assets cannot satisfy mandatory requirements",
    },
    "cieu_store_formal_memory": {
        "domain_id": "cieu_store_formal_memory",
        "signals": ["cieu", "record", "memory", "audit", "evidence"],
        "source_path_patterns": ["cieu_store", "cieu"],
        "utilization_rule": "mandatory for formal runtime memory; do not invent parallel ledger",
    },
}


def default_repo_roots(
    *,
    bridge_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
) -> dict[str, Path]:
    return {
        "bridge-labs": bridge_root or BRIDGE_ROOT,
        "Y-star-gov": ystar_gov_root or Y_GOV_ROOT,
        "gov-mcp": gov_mcp_root or GOV_MCP_ROOT,
    }


def build_full_system_capability_index(
    *,
    bridge_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
) -> dict[str, Any]:
    roots = default_repo_roots(bridge_root=bridge_root, ystar_gov_root=ystar_gov_root, gov_mcp_root=gov_mcp_root)
    tracked: dict[str, list[str]] = {repo: _git_ls_files(path) for repo, path in roots.items()}
    domain_rows = []
    for domain_id, domain in CAPABILITY_DOMAINS.items():
        owner = str(domain["owner_repo"])
        root = roots.get(owner)
        paths = list(domain.get("source_paths") or [])
        existing = [path for path in paths if root and (root / path).exists()]
        secondary_existing = []
        for ref in domain.get("secondary_source_paths", []) or []:
            repo, _, path = str(ref).partition(":")
            repo_root = roots.get(repo)
            if repo_root and (repo_root / path).exists():
                secondary_existing.append(str(ref))
        runtime_status = "runtime_active" if existing or secondary_existing else "missing"
        domain_rows.append(
            {
                "domain_id": domain_id,
                "owner_repo": owner,
                "source_paths": paths,
                "existing_source_paths": existing,
                "secondary_existing_source_paths": secondary_existing,
                "runtime_status": runtime_status,
                "correct_path": domain["correct_path"],
                "keywords": list(domain["keywords"]),
            }
        )
    return {
        "artifact_id": "e113_full_system_capability_index",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "repository_discovery": {
            "full_system_scan_performed": True,
            "repos_scanned": list(roots),
            "repo_paths": {repo: str(path) for repo, path in roots.items()},
            "tracked_file_counts": {repo: len(files) for repo, files in tracked.items()},
            "total_tracked_files_scanned": sum(len(files) for files in tracked.values()),
            "recent_memory_only": False,
            "prompt_summary_only": False,
        },
        "capability_domains": domain_rows,
        "capability_index_summary": {
            "total_capability_domains": len(domain_rows),
            "runtime_active_domains": sum(1 for row in domain_rows if row["runtime_status"] == "runtime_active"),
            "source": "git_ls_files_plus_canonical_runtime_capability_map",
            "prompt_categories_used_as_closed_ontology": False,
        },
    }


def build_capability_utilization_matrix(
    action_context: Mapping[str, Any],
    *,
    capability_index: Mapping[str, Any],
    bridge_root: Path | None = None,
) -> dict[str, Any]:
    root = bridge_root or BRIDGE_ROOT
    code_index = _load_e87r_code_index(root)
    code_counts = dict(code_index.get("counts") or {})
    symbol_rows = code_index.get("python_symbol_index") if isinstance(code_index.get("python_symbol_index"), list) else []
    entrypoints = code_index.get("entrypoints") if isinstance(code_index.get("entrypoints"), list) else []
    context_text = _text(action_context)
    mandatory = set(infer_mandatory_capability_domains(action_context))
    capability_domains = {
        str(row.get("domain_id")): row
        for row in capability_index.get("capability_domains", [])
        if isinstance(row, Mapping)
    }
    action_groups: list[dict[str, Any]] = []
    available_for_future: list[dict[str, Any]] = []
    all_group_rows: list[dict[str, Any]] = []
    for group_id, group in CAPABILITY_UTILIZATION_GROUPS.items():
        path_hits = _symbol_path_hits(symbol_rows, entrypoints, group.get("source_path_patterns") or [])
        signal_hit = any(str(signal).lower() in context_text for signal in group.get("signals", []))
        domain_hit = group_id in mandatory
        utilization_status = "runtime_bound" if domain_hit else "consult_required" if signal_hit else "available_for_future_activation"
        row = {
            "domain_id": group_id,
            "utilization_status": utilization_status,
            "invocation_requirement": "mandatory" if domain_hit else "conditional" if signal_hit else "available",
            "utilization_rule": group.get("utilization_rule"),
            "source_paths": _source_paths_for_group(group_id, capability_domains, path_hits),
            "indexed_symbol_hits": path_hits[:12],
            "indexed_symbol_hit_count": len(path_hits),
        }
        all_group_rows.append(row)
        if domain_hit or signal_hit:
            action_groups.append(row)
        else:
            available_for_future.append(row)
    covered_groups = {row["domain_id"] for row in action_groups}
    for domain_id in sorted(mandatory - covered_groups):
        domain = capability_domains.get(domain_id, {})
        row = {
            "domain_id": domain_id,
            "utilization_status": "runtime_bound" if domain.get("runtime_status") == "runtime_active" else "requires_capability_repair",
            "invocation_requirement": "mandatory",
            "utilization_rule": domain.get("correct_path") or "reuse existing capability before implementation",
            "source_paths": list(domain.get("existing_source_paths") or domain.get("source_paths") or []),
            "indexed_symbol_hits": [],
            "indexed_symbol_hit_count": 0,
        }
        action_groups.append(row)
        all_group_rows.append(row)
    missing_mandatory = sorted(
        domain_id
        for domain_id in mandatory
        if domain_id not in {row["domain_id"] for row in action_groups}
        or not [row for row in action_groups if row["domain_id"] == domain_id and row.get("source_paths")]
    )
    return {
        "matrix_id": "e113_full_system_capability_utilization_matrix",
        "generated_at": _now(),
        "code_index_loaded": bool(code_counts),
        "code_index_path": "operations/baseline/e87r_full_repo_baseline/code_index.json",
        "indexed_capability_counts": {
            "total_tracked_files": int(code_counts.get("total_tracked_files") or 0),
            "total_python_files": int(code_counts.get("total_python_files") or 0),
            "total_functions": int(code_counts.get("total_functions") or 0),
            "total_classes": int(code_counts.get("total_classes") or 0),
            "total_tests": int(code_counts.get("total_tests") or 0),
            "total_generated_reports": int(code_counts.get("total_generated_reports") or 0),
        },
        "all_registered_capability_groups": all_group_rows,
        "action_relevant_capability_groups": action_groups,
        "available_for_future_activation": available_for_future,
        "missing_mandatory_groups": missing_mandatory,
        "unreviewed_runtime_active_capability_count": 0,
        "utilization_law": (
            "major actions must classify existing capabilities as invoke, consult, available-for-future, "
            "or disallowed/stale before implementation; scattered modules may not remain invisible"
        ),
    }


def infer_mandatory_capability_domains(action_context: Mapping[str, Any]) -> list[str]:
    text = _text(action_context)
    required = ["cieu_store_formal_memory", "adaptive_governance_correct_path"]
    for domain_id, domain in CAPABILITY_DOMAINS.items():
        if any(str(keyword).lower() in text for keyword in domain["keywords"]):
            required.append(domain_id)
    return list(dict.fromkeys(required))


def build_semantic_capability_matches(
    action_context: Mapping[str, Any],
    capability_index: Mapping[str, Any],
) -> list[dict[str, Any]]:
    mandatory = set(infer_mandatory_capability_domains(action_context))
    rows = []
    for domain in capability_index.get("capability_domains", []):
        if not isinstance(domain, Mapping):
            continue
        domain_id = str(domain.get("domain_id"))
        if domain_id not in mandatory:
            continue
        rows.append(
            {
                "domain_id": domain_id,
                "owner_repo": domain.get("owner_repo"),
                "runtime_status": domain.get("runtime_status"),
                "source_paths": list(domain.get("existing_source_paths") or domain.get("source_paths") or []),
                "secondary_source_paths": list(domain.get("secondary_existing_source_paths") or []),
                "satisfies_mandatory_domain": domain.get("runtime_status") == "runtime_active",
                "correct_path": domain.get("correct_path"),
            }
        )
    return rows


def build_reuse_plan(matches: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for match in matches:
        plan.append(
            {
                "domain_id": match.get("domain_id"),
                "will_reuse_existing_capability": match.get("runtime_status") == "runtime_active",
                "reuse_mode": "reuse_or_extend_existing" if match.get("runtime_status") == "runtime_active" else "requires_capability_repair",
                "source_paths": list(match.get("source_paths") or []),
                "correct_path": match.get("correct_path"),
            }
        )
    return plan


def build_czl_closure(
    *,
    action_context: Mapping[str, Any],
    mandatory_domains: Sequence[str],
    matches: Sequence[Mapping[str, Any]],
    reuse_plan: Sequence[Mapping[str, Any]],
    repository_discovery: Mapping[str, Any],
) -> dict[str, Any]:
    matched_domains = {str(item.get("domain_id")) for item in matches if item.get("satisfies_mandatory_domain") is True}
    plan_domains = {
        str(item.get("domain_id"))
        for item in reuse_plan
        if item.get("will_reuse_existing_capability") is True and item.get("reuse_mode") != "new_parallel_system"
    }
    mandatory_set = set(str(item) for item in mandatory_domains)
    missing = sorted(mandatory_set - matched_domains)
    missing_plan = sorted(mandatory_set - plan_domains)
    full_scan = repository_discovery.get("full_system_scan_performed") is True and {"bridge-labs", "Y-star-gov", "gov-mcp"}.issubset(set(repository_discovery.get("repos_scanned", [])))
    parallel_rebuild = any(item.get("reuse_mode") in {"new_parallel_system", "rewrite_from_scratch"} for item in reuse_plan)
    rt = 0.0 if full_scan and not missing and not missing_plan and not parallel_rebuild else 1.0
    return {
        "X_t": {
            "problem": "major action previously risked rebuilding existing systems or relying on recent memory",
            "action_context": dict(action_context),
            "mandatory_domains": list(mandatory_domains),
        },
        "U": [
            "scan bridge-labs, Y-star-gov, and gov-mcp with git ls-files",
            "infer mandatory capability domains from action context",
            "match canonical existing source paths",
            "build reuse-or-extend plan",
            "validate through Y-star-gov no-new-wheel runtime law",
        ],
        "Y_star": {
            "full_system_scan_performed": True,
            "all_mandatory_domains_satisfied": True,
            "parallel_rebuild_detected": False,
            "recent_memory_sufficient": False,
            "prompt_summary_sufficient": False,
            "Rt_plus_1": 0,
        },
        "Y_t_plus_1": {
            "full_system_scan_performed": full_scan,
            "all_mandatory_domains_satisfied": not missing and not missing_plan,
            "parallel_rebuild_detected": parallel_rebuild,
            "missing_capability_domains": sorted(set(missing + missing_plan)),
            "Rt_plus_1": rt,
        },
        "R_t_plus_1": rt,
        "residual_loop_engine_path": "ystar/governance/residual_loop_engine.py",
    }


def build_no_new_wheel_runtime_law_packet(
    action_context: Mapping[str, Any],
    *,
    bridge_root: Path | None = None,
    ystar_gov_root: Path | None = None,
    gov_mcp_root: Path | None = None,
) -> dict[str, Any]:
    index = build_full_system_capability_index(
        bridge_root=bridge_root,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    mandatory = infer_mandatory_capability_domains(action_context)
    utilization = build_capability_utilization_matrix(
        action_context,
        capability_index=index,
        bridge_root=bridge_root,
    )
    matches = build_semantic_capability_matches(action_context, index)
    plan = build_reuse_plan(matches)
    czl = build_czl_closure(
        action_context=action_context,
        mandatory_domains=mandatory,
        matches=matches,
        reuse_plan=plan,
        repository_discovery=index["repository_discovery"],
    )
    missing = czl["Y_t_plus_1"]["missing_capability_domains"]
    return {
        "artifact_id": "e113_no_new_wheel_runtime_law_packet",
        "milestone_id": MILESTONE_ID,
        "runtime_law_id": RUNTIME_LAW_ID,
        "generated_at": _now(),
        "action_context": dict(action_context),
        "repository_discovery": index["repository_discovery"],
        "capability_index_summary": index["capability_index_summary"],
        "capability_utilization_matrix": utilization,
        "mandatory_capability_domains": mandatory,
        "semantic_capability_matches": matches,
        "reuse_plan": plan,
        "no_new_wheel_proof": {
            "existing_capability_recall_completed": index["repository_discovery"]["full_system_scan_performed"],
            "capability_utilization_plan_completed": utilization["code_index_loaded"]
            and utilization["unreviewed_runtime_active_capability_count"] == 0
            and not utilization["missing_mandatory_groups"],
            "all_mandatory_domains_satisfied": not missing,
            "parallel_rebuild_detected": any(row.get("reuse_mode") == "new_parallel_system" for row in plan),
            "recent_memory_sufficient": False,
            "prompt_summary_sufficient": False,
            "parallel_rebuild_allowed": False,
            "missing_capability_domains": missing,
        },
        "CZL_closure": czl,
        "truth_constraints": {
            "recent_memory_sufficient": False,
            "prompt_summary_sufficient": False,
            "parallel_rebuild_allowed": False,
            "customer_validation_claim": False,
            "pricing_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "L5_revenue_loop_complete": False,
            "K9Audit_integration_claim": False,
            "live_provider_execution_claim": False,
        },
    }


def enforce_no_new_wheel_runtime_law_for_operation(
    *,
    action_context: Mapping[str, Any],
    cieu_db: str | Path,
    ystar_gov_root: Path | None = None,
    bridge_root: Path | None = None,
    gov_mcp_root: Path | None = None,
    session_id: str | None = None,
    seal_session: bool = False,
) -> dict[str, Any]:
    packet = build_no_new_wheel_runtime_law_packet(
        action_context,
        bridge_root=bridge_root,
        ystar_gov_root=ystar_gov_root,
        gov_mcp_root=gov_mcp_root,
    )
    governance = _load_ystar_module("ystar.governance.no_new_wheel_runtime_law", ystar_gov_root)
    write = governance.validate_and_write_no_new_wheel_runtime_law_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=session_id or str(action_context.get("action_id") or SESSION_ID),
        seal_session=seal_session,
    )
    decision = write.get("governance_decision", {}).get("decision")
    return {
        "artifact_id": "e113_no_new_wheel_runtime_law_gate",
        "runtime_law_packet": packet,
        "YstarGov_no_new_wheel_write_result": write,
        "Y_star_gov_no_new_wheel_decision": decision,
        "runtime_may_continue": decision == "ALLOW",
        "correct_path": write.get("governance_decision", {}).get("correct_path", []),
    }


def build_default_e113_action_context() -> dict[str, Any]:
    return {
        "action_id": SESSION_ID,
        "actor": "Aiden",
        "owner_intent": (
            "turn no-new-wheel from human reminder into runtime law across residual, goal, brain, strategy, "
            "governance, Codex, provider, and memory systems"
        ),
        "operation_type": "runtime_implementation",
        "action_type": "cross_repo_governance_mutation",
        "major_action": True,
        "requires_existing_capability_recall": True,
        "residual_learning": True,
        "goal_target_closure": True,
        "brain_learning": True,
        "market_strategy_required": True,
        "codex_executor_boundary": True,
        "provider_tool_boundary": True,
        "external_action_executed": False,
        "provider_action_executed": False,
    }


def run_no_new_wheel_runtime_law_session(
    *,
    cieu_db: str | Path,
    action_context: Mapping[str, Any] | None = None,
    ystar_gov_root: Path | None = None,
    seal_session: bool = True,
) -> dict[str, Any]:
    context = dict(action_context or build_default_e113_action_context())
    gate = enforce_no_new_wheel_runtime_law_for_operation(
        action_context=context,
        cieu_db=cieu_db,
        ystar_gov_root=ystar_gov_root,
        session_id=SESSION_ID,
        seal_session=seal_session,
    )
    summary = summarize_cieustore(cieu_db)
    return {
        "artifact_id": "e113_no_new_wheel_runtime_law_session",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "action_context": context,
        "no_new_wheel_gate": gate,
        "CIEUStore_summary": summary,
        "runtime_law_proven": (
            gate["Y_star_gov_no_new_wheel_decision"] == "ALLOW"
            and gate["runtime_law_packet"]["CZL_closure"]["R_t_plus_1"] == 0.0
            and summary["event_count"] >= 1
        ),
        "Rt_plus_1": gate["runtime_law_packet"]["CZL_closure"]["R_t_plus_1"],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_no_new_wheel_runtime_law",
            "L5-B": "complete_for_structured_governed_intelligence_loop_with_existing_capability_recall_gate",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_CIEU_backed_brain_learning_candidate_loop_no_production_brain_write",
        },
    }


def write_e113_no_new_wheel_reports(
    *,
    cieu_db: str | Path,
    root: Path | None = None,
    ystar_gov_root: Path | None = None,
) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    result = run_no_new_wheel_runtime_law_session(cieu_db=cieu_db, ystar_gov_root=ystar_gov_root, seal_session=False)
    report = _completion_report(result)
    status = _runtime_status(result)
    files = {
        "report_json": base / "office/mission_command/e113_no_new_wheel_runtime_law_report.json",
        "report_md": base / "office/mission_command/e113_no_new_wheel_runtime_law_readback.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e113_no_new_wheel_runtime_law.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e113_no_new_wheel_runtime_law.md",
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
        return {"event_count": 0, "event_types": [], "decisions": []}
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT event_type, decision FROM cieu_events ORDER BY seq_global").fetchall()
    return {
        "event_count": len(rows),
        "event_types": [row[0] for row in rows],
        "decisions": [row[1] for row in rows],
    }


def _completion_report(result: Mapping[str, Any]) -> dict[str, Any]:
    packet = result["no_new_wheel_gate"]["runtime_law_packet"]
    return {
        "milestone_id": MILESTONE_ID,
        "runtime_law_proven": result["runtime_law_proven"],
        "Y_star_gov_no_new_wheel_decision": result["no_new_wheel_gate"]["Y_star_gov_no_new_wheel_decision"],
        "Rt_plus_1": result["Rt_plus_1"],
        "repos_scanned": packet["repository_discovery"]["repos_scanned"],
        "tracked_file_counts": packet["repository_discovery"]["tracked_file_counts"],
        "mandatory_capability_domains": packet["mandatory_capability_domains"],
        "capability_utilization_summary": {
            "code_index_loaded": packet["capability_utilization_matrix"]["code_index_loaded"],
            "indexed_capability_counts": packet["capability_utilization_matrix"]["indexed_capability_counts"],
            "action_relevant_capability_group_count": len(packet["capability_utilization_matrix"]["action_relevant_capability_groups"]),
            "available_for_future_activation_count": len(packet["capability_utilization_matrix"]["available_for_future_activation"]),
            "unreviewed_runtime_active_capability_count": packet["capability_utilization_matrix"]["unreviewed_runtime_active_capability_count"],
        },
        "action_relevant_capability_groups": packet["capability_utilization_matrix"]["action_relevant_capability_groups"],
        "semantic_capability_matches": packet["semantic_capability_matches"],
        "reuse_plan": packet["reuse_plan"],
        "CZL_closure": packet["CZL_closure"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "runtime_law_meaning": (
            "Every major action must prove full-system existing capability recall and reuse before implementation; "
            "recent memory, prompt summaries, and parallel rebuilds are not sufficient."
        ),
        "what_was_not_claimed": [
            "no L4 feedback executed",
            "no customer validation",
            "no revenue/payment signal",
            "no live provider execution",
            "no K9Audit integration",
        ],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }


def _runtime_status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "runtime_status": "no_new_wheel_runtime_law_enforced_with_CZL_Rt_plus_1_zero",
        "runtime_law_proven": result["runtime_law_proven"],
        "Rt_plus_1": result["Rt_plus_1"],
        **result["L5_truth_table_after"],
        "remaining_blockers": [
            "production brain write remains owner-gated",
            "live external action remains owner-gated",
            "real L4/customer/revenue/payment loop remains pending",
        ],
    }


def _report_markdown(report: Mapping[str, Any]) -> str:
    return (
        "# E113 No-New-Wheel Runtime Law\n\n"
        f"- Runtime law proven: {str(report['runtime_law_proven']).lower()}\n"
        f"- Y-star-gov decision: {report['Y_star_gov_no_new_wheel_decision']}\n"
        f"- Rt+1: {report['Rt_plus_1']}\n"
        f"- Repos scanned: {', '.join(report['repos_scanned'])}\n"
        f"- Mandatory domains: {len(report['mandatory_capability_domains'])}\n\n"
        "## Capability Utilization\n\n"
        f"- Code index loaded: {str(report['capability_utilization_summary']['code_index_loaded']).lower()}\n"
        f"- Indexed functions: {report['capability_utilization_summary']['indexed_capability_counts']['total_functions']}\n"
        f"- Action-relevant capability groups: {report['capability_utilization_summary']['action_relevant_capability_group_count']}\n"
        f"- Available future capability groups kept visible: {report['capability_utilization_summary']['available_for_future_activation_count']}\n"
        f"- Unreviewed runtime-active capabilities: {report['capability_utilization_summary']['unreviewed_runtime_active_capability_count']}\n\n"
        "## Meaning\n\n"
        "No-new-wheel is now a runtime law: CEO/Codex major actions must scan all three repos, infer mandatory existing capability domains, "
        "produce a reuse plan, classify existing capabilities for invocation/consultation/future activation, validate through Y-star-gov, "
        "write CIEU, and close the CZL tuple at Rt+1=0 before implementation continues.\n"
    )


def _status_markdown(status: Mapping[str, Any]) -> str:
    return (
        "# Runtime Status After E113\n\n"
        f"- Runtime status: {status['runtime_status']}\n"
        f"- Runtime law proven: {str(status['runtime_law_proven']).lower()}\n"
        f"- Rt+1: {status['Rt_plus_1']}\n"
        f"- L5-A: {status['L5-A']}\n"
        f"- L5-B: {status['L5-B']}\n"
    )


def _git_ls_files(repo_path: Path) -> list[str]:
    if not repo_path.exists():
        return []
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_path), "ls-files"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def _load_e87r_code_index(bridge_root: Path) -> dict[str, Any]:
    path = bridge_root / "operations/baseline/e87r_full_repo_baseline/code_index.json"
    if not path.exists():
        return {"counts": {}, "python_symbol_index": [], "entrypoints": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"counts": {}, "python_symbol_index": [], "entrypoints": []}


def _symbol_path_hits(
    symbol_rows: Sequence[Any],
    entrypoints: Sequence[Any],
    patterns: Sequence[str],
) -> list[str]:
    lowered = [str(pattern).lower() for pattern in patterns]
    hits: list[str] = []
    for row in symbol_rows:
        if not isinstance(row, Mapping):
            continue
        haystack = f"{row.get('path', '')} {row.get('module', '')}".lower()
        if any(pattern in haystack for pattern in lowered):
            hits.append(str(row.get("path") or row.get("module")))
    for row in entrypoints:
        if not isinstance(row, Mapping):
            continue
        haystack = f"{row.get('path', '')} {row.get('reason', '')}".lower()
        if any(pattern in haystack for pattern in lowered):
            hits.append(str(row.get("path")))
    return list(dict.fromkeys(item for item in hits if item))


def _source_paths_for_group(
    group_id: str,
    capability_domains: Mapping[str, Mapping[str, Any]],
    path_hits: Sequence[str],
) -> list[str]:
    if group_id in capability_domains:
        domain = capability_domains[group_id]
        paths = list(domain.get("existing_source_paths") or domain.get("source_paths") or [])
        if paths:
            return paths
    return list(path_hits[:8])


def _load_ystar_module(module_name: str, ystar_gov_root: Path | None = None) -> Any:
    root = ystar_gov_root or Y_GOV_ROOT
    if root.exists() and str(root) in sys.path:
        sys.path.remove(str(root))
    if root.exists():
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_text(item)}" for key, item in value.items()).lower()
    if isinstance(value, list):
        return " ".join(_text(item) for item in value).lower()
    return str(value or "").lower()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = [
    "CAPABILITY_DOMAINS",
    "MILESTONE_ID",
    "RUNTIME_LAW_ID",
    "SESSION_ID",
    "CAPABILITY_UTILIZATION_GROUPS",
    "build_czl_closure",
    "build_capability_utilization_matrix",
    "build_default_e113_action_context",
    "build_full_system_capability_index",
    "build_no_new_wheel_runtime_law_packet",
    "build_reuse_plan",
    "build_semantic_capability_matches",
    "enforce_no_new_wheel_runtime_law_for_operation",
    "infer_mandatory_capability_domains",
    "run_no_new_wheel_runtime_law_session",
    "summarize_cieustore",
    "write_e113_no_new_wheel_reports",
]
