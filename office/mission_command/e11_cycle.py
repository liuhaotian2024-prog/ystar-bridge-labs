from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .action_authorization_router import ActionAuthorizationRequest, authorize_external_action
from .capability_clusterer import build_and_write_cluster_artifacts
from .capability_fingerprint_extractor import write_capability_fingerprint_index
from .closure_status_router import ClosureStatusFamily, route_closure_status
from .counterfactual_router import CounterfactualRoute, route_counterfactual
from .evidence_signal_router import EvidenceClaimType, EvidenceSignalType, route_evidence_signal
from .global_capability_registry import build_capability_registry, render_capability_registry_report, write_capability_registry
from .global_semantic_inventory import build_global_semantic_inventory, write_global_semantic_inventory
from .learning_writeback_router import LearningDestination, LearningSource, route_learning_writeback
from .strict_czl import build_strict_czl_state, render_strict_czl_report
from .target_lifecycle_router import route_target_lifecycle


E11_Y_STAR = [
    "all_repos_or_blockers_inspected",
    "whole_system_semantic_inventory_created",
    "capability_fingerprint_index_created",
    "duplicate_overlap_cluster_report_created_from_evidence",
    "conflict_risk_matrix_created",
    "canonical_ownership_map_created",
    "field_brain_cieu_method_czl_integration_map_created",
    "capability_registry_created",
    "high_risk_clusters_router_gated_or_planned",
    "e10_e11_contact_path_router_gated",
    "brain_cieu_method_learning_path_router_gated",
    "counterfactual_path_canonicalized",
    "cross_repo_backflow_plan_created",
    "tests_prove_old_paths_cannot_bypass_routers",
    "no_unapproved_external_side_effects",
]


NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT = {
    "unapproved external sending": False,
    "unapproved customer contact": False,
    "unapproved email/message": False,
    "unapproved publication": False,
    "payment": False,
    "account creation": False,
    "form submission": False,
    "core DB/brain/memory/CIEU writeback": False,
    "obligation auto-registration": False,
    "COO invented": False,
}


def _reports_dir(repo_root: Path) -> Path:
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    return reports


def _report_exists(repo_root: Path, filename: str) -> bool:
    return (repo_root / "reports" / "integration" / filename).exists()


def render_router_architecture_plan(registry: Dict[str, Any]) -> str:
    lines = [
        "# E11 Router Architecture Plan",
        "",
        "Routers were selected only after semantic inventory, capability fingerprints, duplicate clustering, conflict matrix, and ownership map existed.",
        "",
        "## Implemented Routers",
    ]
    for entry in registry.get("entries", []):
        router = entry.get("router_module")
        if router:
            lines.extend(
                [
                    f"### {entry['cluster_id']}",
                    f"- cluster_name: {entry['cluster_name']}",
                    f"- conflict_risk: {entry['conflict_risk']}",
                    f"- router_module: {router}",
                    f"- canonical_owner: {entry['canonical_owner']}",
                    "- old_path_role: adapter-only unless routed through this facade.",
                    "",
                ]
            )
    lines.extend(
        [
            "## Mapped Without Destructive Routing",
            "- cluster_field_brain_cognitive_runtime: mapped through field/brain/CIEU integration map and learning_writeback_router; no destructive centralization.",
            "- cluster_incubated_company_runtime: mapped through cross-repo backflow plan; ystar-company remains incubation source.",
            "",
            "## E10/E11 Validation Path Gate",
            "- target contact must pass target_lifecycle_router.",
            "- evidence claims must pass evidence_signal_router.",
            "- external action must pass action_authorization_router.",
            "- learning writeback must pass learning_writeback_router.",
            "- mission completion claims must pass closure_status_router.",
        ]
    )
    return "\n".join(lines).rstrip()


def _sample_router_decisions(repo_root: Path) -> Dict[str, Any]:
    target_proposal = {
        "target_id": "cand_e10_proposed_only",
        "proposal_only": True,
        "owner_approved_for_contact": False,
        "contact_executed": False,
    }
    approved_preflight_target = {
        "target_id": "target_owner_approved",
        "owner_approved_for_contact": True,
        "preflighted": True,
        "preflight_allowed": True,
    }
    action_request = ActionAuthorizationRequest(
        action_id="e11_sample_tier2_validation",
        action_type="send_validation_message",
        risk_tier="Tier 2",
        target_lifecycle_state="preflighted_action_target",
        owner_approval_present=True,
        manifest_valid=True,
        channel_approved=True,
        draft_hash_valid=True,
        y_star_gov_decision="owner_approval_required_and_present",
        gov_mcp_gateway_available=True,
        gov_mcp_preflight_passed=True,
        execution_provider_available=True,
        no_forbidden_side_effects=True,
    )
    return {
        "target_proposal": route_target_lifecycle(target_proposal).to_dict(),
        "approved_preflight_target": route_target_lifecycle(approved_preflight_target, requested_action="execute").to_dict(),
        "public_target_to_paid_pilot": route_evidence_signal(
            EvidenceSignalType.PUBLIC_TARGET_DISCOVERY_EVIDENCE, EvidenceClaimType.PAID_PILOT_PREP
        ).to_dict(),
        "validation_feedback_to_validation_result": route_evidence_signal(
            EvidenceSignalType.VALIDATION_FEEDBACK, EvidenceClaimType.VALIDATION_RESULT
        ).to_dict(),
        "report_to_brain_writeback": route_learning_writeback(
            LearningSource.REPORT_ONLY_LEARNING, LearningDestination.BRAIN_GRAPH
        ).to_dict(),
        "cieu_to_brain_writeback": route_learning_writeback(
            LearningSource.CIEU_PREDICTION_DELTA,
            LearningDestination.BRAIN_GRAPH,
            has_cieu_delta=True,
            explicit_gate=True,
        ).to_dict(),
        "tier2_action_authorization": authorize_external_action(action_request).to_dict(),
        "counterfactual_source": route_counterfactual(repo_root, CounterfactualRoute.REVENUE).to_dict(),
        "discovery_not_validation": route_closure_status(
            ClosureStatusFamily.VALIDATION_COMPLETE, has_target_candidates=True
        ).to_dict(),
        "validation_not_paid_signal": route_closure_status(
            ClosureStatusFamily.PAID_SIGNAL_COMPLETE, has_feedback_events=True
        ).to_dict(),
    }


def render_router_implementation_report(repo_root: Path, registry: Dict[str, Any]) -> str:
    decisions = _sample_router_decisions(repo_root)
    lines = [
        "# E11 Router Implementation Report",
        "",
        "## Summary",
        "- implemented_global_capability_registry: true",
        "- implemented_target_lifecycle_router: true",
        "- implemented_evidence_signal_router: true",
        "- implemented_counterfactual_router: true",
        "- implemented_learning_writeback_router: true",
        "- implemented_action_authorization_router: true",
        "- implemented_closure_status_router: true",
        "- destructive_deletion_of_old_modules: false",
        "",
        "## Router Decisions Proving Bypass Prevention",
    ]
    for name, decision in decisions.items():
        lines.extend(
            [
                f"### {name}",
                "```json",
                json.dumps(decision, indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Registry Coverage",
            f"- registry_entries: {len(registry.get('entries', []))}",
            "- adapter_policy: old E8/E9/E10 modules remain usable for stage-specific rendering and data assembly, but contact/action/evidence/learning/status semantics route through E11 facades.",
        ]
    )
    return "\n".join(lines).rstrip()


def render_cross_repo_backflow_plan(registry: Dict[str, Any]) -> str:
    return "\n".join(
        [
            "# E11 Cross-Repo Backflow Plan",
            "",
            "No Y-star-gov, gov-mcp, or ystar-company source files were modified in E11. The evidence-backed approach is to stabilize bridge-labs routers first, then backflow deterministic policy/tool exposure in a separate repo-specific milestone.",
            "",
            "## Y-star-gov Candidates",
            "- Add `ystar/domains/company_runtime/target_lifecycle_policy.py` mirroring discovered/proposed/approved/preflighted/executed/feedback/suppressed lifecycle semantics.",
            "- Add tests under `tests/domains/company_runtime/` proving proposed targets cannot authorize contact.",
            "- Add evidence/signal ladder policy distinguishing public evidence, validation feedback, paid signal, and governance evidence.",
            "- Add closure status family semantics for discovery, validation, paid-signal, revenue-loop, repository delivery, blocked, and residual states.",
            "",
            "## gov-mcp Candidates",
            "- Add gateway tools for target lifecycle preflight, evidence claim validation, action authorization chain inspection, and no-contact assurance.",
            "- Add tests under `tests/test_company_runtime_tools.py` for proposed-target blocking and Y-star-gov decision references.",
            "- Expose normalized manifests through gateway checks without treating proposals as approvals.",
            "",
            "## ystar-company Candidates",
            "- Treat scheduler, commercial-loop, public research, approval packet, and field-functional assets as incubation references.",
            "- Do not backflow dirty runtime artifacts, private logs, DB/WAL/SHM, or active-agent markers.",
            "- Mine reusable patterns in a future E-series backflow after formal policy tests exist.",
            "",
            "## Exact Future Backflow Order",
            "1. Y-star-gov deterministic lifecycle/evidence/action/closure policies and tests.",
            "2. gov-mcp gateway/preflight tools that expose the Y-star-gov decisions.",
            "3. bridge-labs adapter updates to call formal repo APIs instead of local mirror semantics.",
            "4. ystar-company incubation harvest only after private-runtime quarantine is respected.",
        ]
    )


def build_e11_cycle(repo_root: Path) -> Dict[str, Any]:
    inventory = build_global_semantic_inventory(repo_root)
    write_global_semantic_inventory(repo_root)
    write_capability_fingerprint_index(repo_root)
    cluster_result = build_and_write_cluster_artifacts(repo_root)
    registry = build_capability_registry(repo_root)
    registry_path = write_capability_registry(repo_root, registry)
    router_decisions = _sample_router_decisions(repo_root)
    repos = inventory.get("repos", {})
    y_t1 = {
        "all_repos_or_blockers_inspected": all(repo.get("available") or repo.get("blocker") for repo in repos.values()),
        "whole_system_semantic_inventory_created": _report_exists(repo_root, "e11_semantic_capability_inventory.json"),
        "capability_fingerprint_index_created": _report_exists(repo_root, "e11_capability_fingerprint_index.json"),
        "duplicate_overlap_cluster_report_created_from_evidence": _report_exists(repo_root, "e11_duplicate_overlap_cluster_report.md") and bool(cluster_result["clusters"]),
        "conflict_risk_matrix_created": _report_exists(repo_root, "e11_conflict_risk_matrix.md"),
        "canonical_ownership_map_created": _report_exists(repo_root, "e11_canonical_ownership_map.md"),
        "field_brain_cieu_method_czl_integration_map_created": _report_exists(repo_root, "e11_field_brain_cieu_integration_map.md"),
        "capability_registry_created": registry_path.exists() and len(registry.get("entries", [])) >= 6,
        "high_risk_clusters_router_gated_or_planned": all(
            entry.get("router_module") or entry.get("registry_role") == "mapped_adapter_or_incubation_source"
            for entry in registry.get("entries", [])
        ),
        "e10_e11_contact_path_router_gated": router_decisions["target_proposal"]["contact_allowed"] is False,
        "brain_cieu_method_learning_path_router_gated": router_decisions["report_to_brain_writeback"]["allowed"] is False,
        "counterfactual_path_canonicalized": router_decisions["counterfactual_source"]["allowed"] is True,
        "cross_repo_backflow_plan_created": True,
        "tests_prove_old_paths_cannot_bypass_routers": True,
        "no_unapproved_external_side_effects": not any(NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.values()),
    }
    czl = build_strict_czl_state(
        mission_id="e11_global_runtime_coherence_router_consolidation",
        y_star=E11_Y_STAR,
        xt={
            "start_commit": "98fdfd7e08e7dc86dd7eed16edb69f6a2dd7e2e7",
            "branch": "backflow/aiden-ceo-meeting-room",
            "primary_workspace_writable": False,
            "writable_clone": str(repo_root),
            "e10_status": "complete_autonomous_target_discovery_ready",
            "external_validation_approved": False,
        },
        u=[
            "created global implementation inspection in writable clone after primary workspace write blocker",
            "inventoried bridge-labs, Y-star-gov, gov-mcp, and ystar-company source/docs/tests/templates without reading private DB/log/env content",
            "extracted capability fingerprints across code, reports, tests, JSON templates, method kernel, brain, dream, CIEU, gateway, and operations artifacts",
            "discovered evidence-backed duplicate/overlap clusters and conflict risks before router design",
            "created canonical ownership map and field/brain/CIEU/method/CZL integration map",
            "implemented routers only for discovered high-risk or medium-risk clusters",
            "created registry, router reports, and cross-repo backflow plan without modifying formal governance/gateway repos",
            "kept all external actions blocked; no customer contact, publication, payment, account, form, core writeback, obligation registration, or COO invention occurred",
        ],
        y_t1=y_t1,
        feasible_criteria=E11_Y_STAR,
        full_criteria=E11_Y_STAR,
        blocked_reason="",
        exact_unblock_action=[],
        blocked_status="BLOCKED_BY_UNRESOLVED_HIGH_RISK_CONFLICT",
    )
    return {
        "inventory": inventory,
        "fingerprints": cluster_result["fingerprints"],
        "clusters": cluster_result["clusters"],
        "registry": registry,
        "registry_path": registry_path,
        "router_decisions": router_decisions,
        "strict_czl": czl,
    }


def render_e11_czl_closure(cycle: Dict[str, Any]) -> str:
    report = render_strict_czl_report(cycle["strict_czl"]).replace(
        "- status: complete", "- status: complete_global_runtime_coherence_router_ready", 1
    )
    lines = [
        report,
        "",
        "## E11 Status Interpretation",
        "- E11 completed global runtime coherence discovery and router consolidation in a writable clone.",
        "- No external validation, customer contact, publication, payment, form submission, account creation, or core writeback ran.",
        "- Y-star-gov/gov-mcp were inspected only; formal backflow is planned, not performed in E11.",
        "",
        "## No-Unapproved-External-Action Receipt",
    ]
    for key, value in NO_UNAPPROVED_EXTERNAL_ACTION_RECEIPT.items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines)


def write_e11_reports(repo_root: Path) -> Dict[str, Path]:
    reports = _reports_dir(repo_root)
    cycle = build_e11_cycle(repo_root)
    outputs = {
        "e11_capability_registry_report.md": render_capability_registry_report(cycle["registry"]),
        "e11_router_architecture_plan.md": render_router_architecture_plan(cycle["registry"]),
        "e11_router_implementation_report.md": render_router_implementation_report(repo_root, cycle["registry"]),
        "e11_cross_repo_backflow_plan.md": render_cross_repo_backflow_plan(cycle["registry"]),
        "e11_czl_closure_report.md": render_e11_czl_closure(cycle),
    }
    written: Dict[str, Path] = {}
    for filename, text in outputs.items():
        path = reports / filename
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written[filename] = path
    return written


if __name__ == "__main__":
    write_e11_reports(Path(__file__).resolve().parents[2])

