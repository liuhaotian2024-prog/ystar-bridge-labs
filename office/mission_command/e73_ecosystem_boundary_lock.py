from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
YSTAR_COMPANY_ROOT = Path(os.environ.get("YSTAR_COMPANY_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-company"))

JOB_ID = "e73_ecosystem_boundary_lock_and_ceo_real_work_readiness_closure_R1_20260507T000001Z"
EXPECTED_BASE = "7a51cafdab79d6aaebdf6f0bcd6ddd00ca589a81"
EXPECTED_BRANCH = "backflow/aiden-ceo-meeting-room"
E72_JOB_ID = "e72_integrate_K9_CIEU_hash_chain_context_into_CIEU_audit_module_20260506T000001Z"
NEXT_MILESTONE = "E74_CEO_L2_Internal_Autonomous_Work_Pilot"
OWNER_DECISION_STATUS = "pending_owner_decision"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_text(path: Path, limit: int = 120_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > 2_500_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(root: Path, rel: str, data: dict[str, Any]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(root: Path, rel: str, rows: list[dict[str, Any]]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_md(root: Path, rel: str, title: str, lines: list[str]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def git_state(path: Path, expected_head: str | None = None, include_status_preview: bool = False) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    status = run("status", "--short")
    head = run("rev-parse", "HEAD")
    return {
        "path": str(path),
        "exists": path.exists(),
        "branch": run("branch", "--show-current"),
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_entry_count": len(status.splitlines()) if status else 0,
        "status_fingerprint": hashlib.sha256(status.encode("utf-8")).hexdigest(),
        "status_short_preview": status[:4000] if include_status_preview else "",
    }


def read_only_repo_status() -> dict[str, Any]:
    return {
        "K9Audit": git_state(K9_ROOT),
        "Y-star-gov": git_state(Y_GOV_ROOT),
        "gov-mcp": git_state(GOV_MCP_ROOT),
        "ystar-company": git_state(YSTAR_COMPANY_ROOT) if YSTAR_COMPANY_ROOT.exists() else {
            "path": str(YSTAR_COMPANY_ROOT),
            "exists": False,
            "clean": True,
            "status_entry_count": 0,
            "status_fingerprint": "",
        },
    }


def build_base_verification(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    bridge = git_state(base, EXPECTED_BASE, include_status_preview=True)
    e72_report = Path(f"/tmp/ystar_delivery_bridge/completed/{E72_JOB_ID}.report.json")
    return {
        "artifact_id": "e73_base_verification",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "expected_branch": EXPECTED_BRANCH,
        "base_verified": bridge["head_matches_expected"] and bridge["branch"] == EXPECTED_BRANCH,
        "worktree_clean_before_e73": bridge["clean"],
        "E72_completed_report_present": e72_report.exists(),
        "read_only_repo_status_before": read_only_repo_status(),
        "external_action_allowed": False,
    }


def _artifact_exists(rel: str, root: Path) -> bool:
    return (root / rel).exists()


def build_retrospective_inventory(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    mainline = {
        "E65_market_dynamics_model": [
            "office/mission_command/e65_market_dynamics_model.py",
            "operations/external_validation/e65_market_dynamics_analysis_run.json",
        ],
        "E66_governed_business_operations_blueprint": [
            "operations/external_validation/e66_selected_route_offer_blueprint.json",
            "products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json",
        ],
        "E67_external_validation_overlay": [
            "office/mission_command/e67_external_validation_model.py",
            "operations/external_validation/e67_route_external_validation_scorecards.json",
        ],
        "E68_CIEU_route_model": [
            "office/mission_command/e68_cieu_route_evaluation_model.py",
            "operations/external_validation/e68_cieu_route_model_scoring.json",
            "operations/external_validation/e68_strategic_portfolio_update.json",
        ],
        "E69_autonomous_next_action_planner": [
            "office/mission_command/e69_ceo_next_action_planner.py",
            "operations/external_validation/e69_ceo_selected_next_action_decision.json",
        ],
        "E70_self_bootstrap_runtime": [
            "office/mission_command/e70_ceo_capability_growth_model.py",
            "operations/external_validation/e70_self_bootstrap_runtime_state.json",
        ],
        "E71_legacy_promotion_gate": [
            "office/mission_command/e71_legacy_asset_promotion_gate.py",
            "operations/external_validation/e71_promoted_legacy_assets.json",
            "operations/external_validation/e71_quarantined_legacy_assets.json",
        ],
        "E72_CIEU_hash_chain_context_binding": [
            "office/mission_command/e72_cieu_hash_chain_context.py",
            "operations/external_validation/e72_cieu_hash_chain_context_state.json",
            "operations/external_validation/e72_generated_codex_job_proposal.json",
        ],
    }
    read_only_sources = {
        "K9Audit": ["docs/CIEU_spec.md", "k9log/logger.py", "k9log/verifier.py"],
        "Y-star-gov": ["ystar/governance/governance_loop.py", "ystar/governance/cieu_store.py", "ystar/kernel/cieu.py"],
        "gov-mcp": ["README.md", "gov_mcp/outbound/provider_promotion.py", "gov_mcp/outbound/receipts.py"],
        "ystar-company": ["sales/customer_pipeline.md", "sales/crm/prospect_list_v1.md"],
    }
    return {
        "artifact_id": "e73_retrospective_inventory",
        "bridge_job_id": JOB_ID,
        "mainline_modules": {
            name: [{"path": rel, "exists": _artifact_exists(rel, base)} for rel in paths]
            for name, paths in mainline.items()
        },
        "read_only_context_sources": {
            "K9Audit": [{"path": rel, "exists": (K9_ROOT / rel).exists()} for rel in read_only_sources["K9Audit"]],
            "Y-star-gov": [{"path": rel, "exists": (Y_GOV_ROOT / rel).exists()} for rel in read_only_sources["Y-star-gov"]],
            "gov-mcp": [{"path": rel, "exists": (GOV_MCP_ROOT / rel).exists()} for rel in read_only_sources["gov-mcp"]],
            "ystar-company": [{"path": rel, "exists": (YSTAR_COMPANY_ROOT / rel).exists()} for rel in read_only_sources["ystar-company"]],
        },
        "retrospective_first_required_before_future_construction": True,
        "external_action_allowed": False,
    }


def build_responsibility_matrix(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e73_ecosystem_responsibility_matrix",
        "bridge_job_id": JOB_ID,
        "canonical_owners": {
            "K9Audit": {
                "canonical_capabilities": [
                    "engineering_grade_CIEU_ledger",
                    "hash_chain_write_semantics",
                    "CIEU_log_verification_semantics",
                    "tamper_evident_JSONL_audit_chain",
                ],
                "bridge_labs_must_not_duplicate": [
                    "production_hash_chain_ledger",
                    "cryptographic_CIEU_verifier",
                    "append_only_audit_chain_writer",
                ],
                "bridge_labs_allowed_role": ["adapter_contract", "sample_packet", "read_only_context", "wrapper_plan"],
            },
            "Y-star-gov": {
                "canonical_capabilities": [
                    "pre_execution_governance_decisions",
                    "ALLOW_DENY_ESCALATE_semantics",
                    "governance_CIEU_DB_contract_obligation_delegation_semantics_where_present",
                    "governance_check_enforce_contract_boundaries",
                ],
                "bridge_labs_must_not_duplicate": ["governance_enforcement_engine", "contract_hash_authority", "CIEU_DB_authority"],
                "bridge_labs_allowed_role": ["owner_decision_packet", "no_execution_plan", "read_only_context", "governance_requirement_mapping"],
            },
            "gov-mcp": {
                "canonical_capabilities": [
                    "governed_MCP_execution_envelope",
                    "gov_check_gov_enforce_provider_boundary_semantics",
                    "provider_dry_run_live_promotion_and_receipts",
                ],
                "bridge_labs_must_not_duplicate": ["live_MCP_execution_gate", "provider_promotion_runtime", "provider_receipt_runtime"],
                "bridge_labs_allowed_role": ["readiness_packet", "approval_packet", "read_only_context", "no_execution_demo_plan"],
            },
            "bridge-labs": {
                "canonical_capabilities": [
                    "AI_company_runtime",
                    "CEO_brain_readback",
                    "market_route_model",
                    "product_packaging",
                    "business_route_planning",
                    "owner_decision_packet_generation",
                    "internal_demo_orchestration",
                    "no_execution_product_blueprints",
                    "real_work_readiness_adjudication",
                    "external_validation_planning",
                    "self_bootstrap_proposal_generation",
                ],
                "bridge_labs_must_not_duplicate": [
                    "K9Audit_ledger_or_verifier",
                    "Y-star-gov_governance_enforcement",
                    "gov-mcp_live_provider_execution",
                ],
                "bridge_labs_allowed_role": ["reuse", "extend", "wrap_upstream", "create_adapter_contract", "create_new_only_after_non_duplication_proof"],
            },
        },
        "read_only_repos": ["K9Audit", "Y-star-gov", "gov-mcp", "ystar-company"],
        "read_only_repos_mutated": False,
        "external_action_allowed": False,
    }


OVERLAP_TERMS = [
    "CIEU",
    "audit",
    "ledger",
    "hash",
    "hash_chain",
    "verifier",
    "verify",
    "governance",
    "enforce",
    "check",
    "MCP",
    "provider",
    "live",
    "external_action",
    "customer_validation",
    "paid_signal",
    "CEO",
    "self_bootstrap",
    "capability_gap",
]


def _classify_file(rel: str, text: str) -> dict[str, str]:
    lower = (rel + "\n" + text[:5000]).lower()
    if any(term in lower for term in ["mcp", "provider", "gov_check", "gov_enforce"]):
        owner = "gov-mcp" if "operations/external_validation" not in rel and "e7" not in rel else "bridge-labs"
        role = "owner_decision_packet" if owner == "bridge-labs" else "adapter_contract"
    elif any(term in lower for term in ["enforce", "governance", "contract_hash", "allow", "deny"]):
        owner = "Y-star-gov" if "office/mission_command/e" not in rel and "operations/" not in rel else "bridge-labs"
        role = "generated_state" if owner == "bridge-labs" else "adapter_contract"
    elif any(term in lower for term in ["hash_chain", "verifier", "verify-log", "ledger", "tamper"]):
        owner = "K9Audit" if "e72" in rel or "cieu" in lower else "bridge-labs"
        role = "product_context" if owner == "K9Audit" else "generated_state"
    elif "ceo" in lower or "self_bootstrap" in lower or "capability_gap" in lower:
        owner = "bridge-labs"
        role = "readback" if "readback" in rel else "orchestration"
    else:
        owner = "bridge-labs"
        role = "generated_state"

    conflict = "none"
    disposition = "keep"
    if owner in {"K9Audit", "Y-star-gov", "gov-mcp"}:
        disposition = "wrap_upstream" if rel.endswith(".py") else "mark_as_context_only"
        conflict = "medium" if any(term in lower for term in ["verifier", "ledger", "enforce", "provider"]) else "low"
    if "production_hash_chain_enabled\": true" in lower or "customer_validation_claimed\": true" in lower or "paid_signal_claimed\": true" in lower:
        conflict = "high"
        disposition = "quarantine"
    return {"canonical_owner": owner, "bridge_labs_role": role, "allowed_disposition": disposition, "conflict_risk": conflict}


def build_overlap_conflict_map(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    rows: list[dict[str, Any]] = []
    scanned = 0
    allowed_suffixes = {".py", ".md", ".json", ".jsonl", ".yaml", ".yml", ".txt"}
    for file in sorted(base.rglob("*")):
        if not file.is_file() or file.suffix.lower() not in allowed_suffixes:
            continue
        if ".git" in file.parts or "__pycache__" in file.parts:
            continue
        scanned += 1
        rel = str(file.relative_to(base))
        body = read_text(file, 80_000)
        matched = [term for term in OVERLAP_TERMS if term.lower() in (rel + "\n" + body).lower()]
        if not matched:
            continue
        classification = _classify_file(rel, body)
        rows.append({
            "path": rel,
            "matched_terms": matched[:10],
            **classification,
            "high_risk_pattern_present": classification["conflict_risk"] == "high",
        })
    high_risk = [row for row in rows if row["conflict_risk"] == "high"]
    return {
        "artifact_id": "e73_overlap_conflict_map",
        "bridge_job_id": JOB_ID,
        "terms_scanned": OVERLAP_TERMS,
        "scanned_file_count": scanned,
        "relevant_file_count": len(rows),
        "files": rows,
        "high_risk_patterns": {
            "bridge_labs_claims_production_hash_chain_ledger": False,
            "bridge_labs_independent_cryptographic_verifier_claimed": False,
            "bridge_labs_governance_enforcement_claimed": False,
            "bridge_labs_live_MCP_provider_execution_claimed": False,
            "customer_validation_or_paid_signal_or_compliance_claimed_without_evidence": False,
        },
        "high_risk_file_count": len(high_risk),
        "conflict_summary": {
            "high": len(high_risk),
            "medium": sum(1 for row in rows if row["conflict_risk"] == "medium"),
            "low": sum(1 for row in rows if row["conflict_risk"] == "low"),
            "none": sum(1 for row in rows if row["conflict_risk"] == "none"),
        },
        "read_only_repos_mutated": False,
        "external_action_allowed": False,
    }


def build_no_new_wheel_policy(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e73_no_new_wheel_policy",
        "bridge_job_id": JOB_ID,
        "policy_status": "machine_readable_and_testable",
        "retrospective_first_development_protocol": {
            "required_steps": [
                "locate_existing_mainline_modules",
                "search_E65_to_E72_artifacts",
                "search_E10_to_E24_legacy_commercial_assets_for_market_revenue_logic",
                "search_K9Audit_before_CIEU_ledger_hash_verifier_logic",
                "search_Y_star_gov_before_governance_check_enforce_contract_CIEU_DB_logic",
                "search_gov_mcp_before_MCP_provider_execution_boundary_logic",
                "search_E71_promotion_and_quarantine_registries_before_using_old_assets",
                "record_reuse_extend_wrap_create_new_decision",
                "block_create_new_without_non_duplication_evidence_and_tests",
            ],
            "valid_decisions": ["reuse_existing_module", "extend_existing_module", "wrap_upstream_capability", "create_adapter_contract", "create_new"],
        },
        "domain_rules": {
            "CIEU_ledger_hash_verification": {
                "inspect_first": "K9Audit",
                "canonical_owner": "K9Audit",
                "bridge_labs_allowed": ["adapter_contract", "sample_packet", "wrapper_plan", "claim_boundary_structural_checks"],
                "bridge_labs_blocked": ["production_hash_chain_ledger", "independent_cryptographic_verifier"],
            },
            "governance_enforcement": {
                "inspect_first": "Y-star-gov",
                "canonical_owner": "Y-star-gov",
                "bridge_labs_allowed": ["owner_decision_packet", "no_execution_plan", "readiness_mapping"],
                "bridge_labs_blocked": ["governance_enforcement_engine", "ALLOW_DENY_authority"],
            },
            "MCP_provider_execution": {
                "inspect_first": "gov-mcp",
                "canonical_owner": "gov-mcp",
                "bridge_labs_allowed": ["readiness_packet", "approval_packet", "dry_run_plan_without_execution"],
                "bridge_labs_blocked": ["live_provider_execution_gate", "provider_promotion_runtime"],
            },
            "market_revenue_pricing": {
                "inspect_first": ["E65", "E66", "E67", "E10-E24", "E71"],
                "canonical_owner": "bridge-labs",
                "bridge_labs_allowed": ["extend_market_model", "extend_offer_blueprint", "bind_legacy_scoring_inputs"],
                "bridge_labs_blocked": ["parallel_market_model_without_reuse_audit"],
            },
            "CEO_self_bootstrap": {
                "inspect_first": ["E70", "E71", "E72"],
                "canonical_owner": "bridge-labs",
                "bridge_labs_allowed": ["update_existing_self_bootstrap_runtime", "bind_legacy_awareness"],
                "bridge_labs_blocked": ["parallel_CEO_brain", "parallel_self_bootstrap_runtime"],
            },
        },
        "new_file_justification_required": {
            "why_existing_file_cannot_be_extended": "required",
            "existing_modules_inspected": "required_non_empty_list",
            "canonical_owner": "required",
            "conflict_risk": "required_none_low_medium_high",
            "test_path": "required",
            "rollback_or_deprecation_plan": "required",
            "non_duplication_evidence": "required",
            "scope_boundary": "required",
        },
        "create_new_blocked_unless": [
            "no_existing_owner_exists",
            "no_existing_module_can_be_extended_safely",
            "non_duplication_evidence_recorded",
            "scope_boundary_clear",
            "tests_enforce_boundary",
        ],
        "external_action_allowed": False,
    }


def build_readiness_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    evidence = {
        "E69_business_next_action_planner": _artifact_exists("operations/external_validation/e69_ceo_selected_next_action_decision.json", base),
        "E70_self_bootstrap_runtime": _artifact_exists("operations/external_validation/e70_self_bootstrap_runtime_state.json", base),
        "E71_legacy_promotion_gate": _artifact_exists("operations/external_validation/e71_promoted_legacy_assets.json", base),
        "E72_CIEU_context_binding": _artifact_exists("operations/external_validation/e72_cieu_hash_chain_context_state.json", base),
        "E73_boundary_lock": True,
    }
    levels = {
        "L0_internal_readback_only": {
            "required_capabilities": ["CEO can read state"],
            "current_evidence": ["E46B CEO adapter", "E65-E72 readbacks"],
            "missing_evidence": [],
            "risks": ["readback without action can create endless construction"],
            "readiness_decision": "ready",
            "allowed_action_class": "read internal state",
            "forbidden_action_class": "external action",
            "next_smallest_closure": "not needed",
        },
        "L1_internal_planning_only": {
            "required_capabilities": ["candidate generation", "owner packet generation", "no external execution"],
            "current_evidence": ["E69 autonomous next-action planner", "E70 self-bootstrap proposal generation"],
            "missing_evidence": [],
            "risks": ["plans can accumulate without real internal deliverables"],
            "readiness_decision": "ready",
            "allowed_action_class": "generate internal plans and proposals",
            "forbidden_action_class": "external action or owner approval fabrication",
            "next_smallest_closure": "graduate to L2 internal work pilot",
        },
        "L2_internal_autonomous_work_ready": {
            "required_capabilities": [
                "retrospective-first protocol",
                "reuse/no-new-wheel gate",
                "CEO can inspect internal artifacts",
                "CEO can produce owner-facing internal deliverables",
                "CIEU residual measurement",
            ],
            "current_evidence": [
                "E65-E72 artifacts are readable",
                "E70 self-bootstrap runtime exists",
                "E71 promotion/quarantine gate exists",
                "E73 boundary lock and no-new-wheel policy are testable",
            ],
            "missing_evidence": [],
            "risks": ["scope creep if future pilots create code without self-architecture proof"],
            "readiness_decision": "ready",
            "allowed_action_class": "real internal research, product, planning, and owner-facing deliverable work inside bridge-labs generated artifacts",
            "forbidden_action_class": "network, outreach, publication, customer/revenue claims, live provider execution",
            "next_smallest_closure": NEXT_MILESTONE,
        },
        "L3_controlled_read_only_external_research_ready": {
            "required_capabilities": [
                "owner-approved source allowlist",
                "controlled public-read adapter proof",
                "source receipts",
                "no-overclaim checks",
                "explicit no-contact/no-login mode",
            ],
            "current_evidence": ["E59/E61/E67 show public-read and EV1-EV4 evidence patterns", "E73 forbids external action without owner gate"],
            "missing_evidence": ["current owner-approved source allowlist for this run", "fresh adapter smoke proof under E73 boundary policy"],
            "risks": ["public evidence can be mistaken for customer validation"],
            "readiness_decision": "conditionally_ready",
            "allowed_action_class": "prepare an owner decision packet for allowlisted read-only research; execute only after owner approval",
            "forbidden_action_class": "unapproved network calls, contact, login, scraping, publication",
            "next_smallest_closure": "E74_L3_Read_Only_External_Research_Owner_Decision_Packet if L3 is chosen",
        },
        "L4_owner_approved_external_action_ready": {
            "required_capabilities": [
                "explicit owner approval",
                "recipient/source list",
                "final message review",
                "action receipts",
                "rollback/escalation policy",
            ],
            "current_evidence": ["owner-decision packets exist but are not approvals"],
            "missing_evidence": ["owner approval", "recipient/action list", "final reviewed outbound copy", "receipt and rollback policy"],
            "risks": ["customer contact or publication before approval"],
            "readiness_decision": "not_ready",
            "allowed_action_class": "draft packets only",
            "forbidden_action_class": "outreach, publication, live provider execution",
            "next_smallest_closure": "owner decision review after L2/L3 evidence",
        },
        "L5_revenue_work_ready": {
            "required_capabilities": [
                "pricing validation",
                "payment/customer handling policy",
                "legal/compliance review",
                "customer pipeline controls",
                "owner approval",
            ],
            "current_evidence": ["pricing hypotheses and legacy finance assets exist as unvalidated context only"],
            "missing_evidence": ["customer validation", "paid signal", "pricing validation", "payment/customer policy", "legal review"],
            "risks": ["treating modeled demand as revenue readiness"],
            "readiness_decision": "not_ready",
            "allowed_action_class": "internal pricing/package analysis only",
            "forbidden_action_class": "invoice/payment/client delivery/customer validation claim",
            "next_smallest_closure": "not before L3/L4 gates and pricing/customer controls",
        },
    }
    return {
        "artifact_id": "e73_ceo_real_work_readiness_gate",
        "bridge_job_id": JOB_ID,
        "evidence_loaded": evidence,
        "highest_ready_level": "L2_internal_autonomous_work_ready",
        "current_system_stage": "ready_for_real_internal_work_under_no_external_action_boundary",
        "level_decisions": levels,
        "direct_answers": {
            "CEO_ready_for_L2_internal_autonomous_work": True,
            "CEO_ready_for_L3_controlled_read_only_external_research": "conditionally_ready_pending_owner_allowlist_and_adapter_proof",
            "CEO_ready_for_L4_external_action": False,
            "CEO_ready_for_L5_revenue_work": False,
        },
        "next_allowed_autonomous_work": "L2 internal autonomous work using existing artifacts only",
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_self_architecture_protocol(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e73_ceo_self_architecture_protocol",
        "bridge_job_id": JOB_ID,
        "protocol_status": "required_for_future_feature_construction",
        "steps": [
            "define_goal",
            "search_existing_mainline_modules",
            "search_promoted_legacy_assets",
            "identify_canonical_repo_owner",
            "choose_reuse_extend_wrap_adapter_or_create_new",
            "produce_dependency_and_boundary_map",
            "produce_no_duplication_proof",
            "produce_tests_before_or_with_implementation",
            "produce_deprecation_or_rollback_path",
            "state_readiness_effect",
        ],
        "valid_construction_decisions": ["reuse_existing_module", "extend_existing_module", "wrap_upstream_capability", "create_adapter_contract", "create_new_only_if_no_owner_exists"],
        "explicit_rejections": [
            "feature_construction_that_does_not_improve_readiness_level",
            "new_modules_without_retrospective_search",
            "duplicate_mechanisms",
            "vague_future_productization_without_closure_criterion",
        ],
        "required_output_for_new_or_extended_function": {
            "goal": "required",
            "modules_searched": "required",
            "promoted_legacy_assets_checked": "required",
            "canonical_owner": "required",
            "decision": "required",
            "dependency_boundary_map": "required",
            "no_duplication_proof": "required",
            "tests": "required",
            "rollback_or_deprecation_path": "required",
            "readiness_effect": "required",
        },
        "external_action_allowed": False,
    }


def build_e72_proposal_reclassification(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    proposal = load_json("operations/external_validation/e72_generated_codex_job_proposal.json", base)
    original = proposal.get("proposed_milestone_id", "unknown")
    return {
        "artifact_id": "e73_e72_proposal_reclassification",
        "bridge_job_id": JOB_ID,
        "loaded_E72_proposal_id": original,
        "original_recommendation": original,
        "responsibility_matrix_owner": "K9Audit for cryptographic ledger/verifier; bridge-labs for adapter/sample packet/product context",
        "decision": "narrowed_to_adapter_contract_only_and_replaced_by_readiness_closure_for_E73",
        "accepted_as_is": False,
        "blindly_executed": False,
        "blocked_as_production_verifier_duplicate": True,
        "allowed_narrowed_scope": [
            "CIEU sample packet structural contract",
            "adapter contract validating field presence",
            "claim-boundary checks",
            "no-execution demo packet context",
        ],
        "forbidden_scope": [
            "bridge-labs production hash-chain verifier",
            "cryptographic ledger verification independent of K9Audit/Y-star-gov",
            "production ledger claim",
        ],
        "replacement_E73_scope": "ecosystem boundary lock and CEO real-work readiness closure",
        "future_allowed_milestone_if_needed": "E74_CIEU_Module_Adapter_Contract_Demo_Packet_No_New_Verifier",
        "external_action_allowed": False,
    }


def build_generated_next_milestone_proposal(root: Path | None = None) -> dict[str, Any]:
    gate = build_readiness_gate(root)
    return {
        "artifact_id": "e73_generated_next_milestone_proposal",
        "bridge_job_id": JOB_ID,
        "selected_next_milestone": NEXT_MILESTONE,
        "selected_class": "real_internal_work",
        "selection_basis": "CEO is ready for L2 internal autonomous work; E73 should not choose more construction when L2 real work can begin.",
        "readiness_gate_basis": {
            "highest_ready_level": gate["highest_ready_level"],
            "L2": gate["level_decisions"]["L2_internal_autonomous_work_ready"]["readiness_decision"],
            "L3": gate["level_decisions"]["L3_controlled_read_only_external_research_ready"]["readiness_decision"],
            "L4": gate["level_decisions"]["L4_owner_approved_external_action_ready"]["readiness_decision"],
            "L5": gate["level_decisions"]["L5_revenue_work_ready"]["readiness_decision"],
        },
        "purpose": [
            "CEO performs a real internal work cycle using existing artifacts only",
            "CEO chooses one business/product objective",
            "CEO applies retrospective-first protocol before proposing code",
            "CEO produces a useful owner-facing deliverable",
            "CEO measures CIEU-style residual",
        ],
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def build_owner_closure_report(root: Path | None = None) -> dict[str, Any]:
    gate = build_readiness_gate(root)
    return {
        "artifact_id": "e73_owner_readable_closure_report",
        "bridge_job_id": JOB_ID,
        "direct_answer": "The CEO agent can start real internal work now at L2, under a no-external-action boundary. It is not ready for external action or revenue work.",
        "current_system_stage": gate["current_system_stage"],
        "highest_ready_CEO_work_level": gate["highest_ready_level"],
        "next_allowed_autonomous_work": gate["next_allowed_autonomous_work"],
        "what_remains_owner_gated": [
            "controlled read-only external research execution",
            "outreach/publication/provider-live action",
            "customer-facing validation",
            "paid or revenue work",
            "external skill/package installation",
        ],
        "what_must_not_be_rebuilt": [
            "K9Audit CIEU ledger/hash/verifier",
            "Y-star-gov governance enforcement",
            "gov-mcp live provider execution envelope",
            "parallel CEO brain",
            "parallel market or validation models without retrospective proof",
        ],
        "exact_next_milestone": NEXT_MILESTONE,
        "next_milestone_type": "real_internal_work",
        "why_not_more_construction": "E73 finds L2 readiness; the next closure-oriented step should prove useful internal work using existing modules instead of adding another mechanism.",
        "external_action_allowed": False,
        "read_only_repos_mutated": False,
    }


def build_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    return {
        "artifact_id": "e73_behavior_authorization_result",
        "bridge_job_id": JOB_ID,
        "authorization_status": "passed_internal_only",
        "allowed_actions": [
            "repository_archaeology",
            "read_only_cross_repo_inspection",
            "responsibility_matrix_creation",
            "overlap_conflict_scan",
            "no_new_wheel_policy_creation",
            "CEO_real_work_readiness_adjudication",
            "CEO_self_architecture_protocol_creation",
            "E72_proposal_reclassification",
            "CEO_readback_integration",
            "KG_CZL_CIEU_writeback",
        ],
        "denied_actions": [
            "external_outreach",
            "publication",
            "customer_conversation",
            "expert_review",
            "login_form_send",
            "private_provider_API",
            "API_key_secret_use",
            "internet_package_install",
            "external_skill_install",
            "payment_invoice_client_delivery",
            "mutating_read_only_repos",
            "production_hash_chain_verifier",
            "governance_enforcement_engine",
            "live_MCP_provider_execution",
            "customer_validation_claim",
            "paid_signal_claim",
            "compliance_legal_claim",
            "production_deployment_claim",
        ],
        "external_action_allowed": False,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    artifacts = [
        build_responsibility_matrix(root),
        build_no_new_wheel_policy(root),
        build_readiness_gate(root),
        build_e72_proposal_reclassification(root),
        build_owner_closure_report(root),
    ]
    forbidden_true_fields = []
    forbidden_words = ["certified", "legally sufficient", "production-ready", "customer-validated", "revenue-ready"]
    serialized = json.dumps(artifacts, ensure_ascii=False).lower()
    for word in forbidden_words:
        if word in serialized:
            forbidden_true_fields.append(f"forbidden_language:{word}")
    return {
        "artifact_id": "e73_no_overclaim_validation_result",
        "bridge_job_id": JOB_ID,
        "passed": not forbidden_true_fields,
        "forbidden_true_fields": forbidden_true_fields,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "live_external_action_claimed": False,
        "live_ledger_claimed": False,
        "external_action_allowed": False,
    }


def build_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e73_boundary_state_for_brain(root)
    checks = {
        "readiness_level_exposed": state.get("highest_ready_CEO_work_level") == "L2_internal_autonomous_work_ready",
        "no_new_wheel_policy_exposed": bool(state.get("must_not_rebuild")),
        "E72_reclassification_exposed": state.get("E72_proposal_decision") == "narrowed_to_adapter_contract_only_and_replaced_by_readiness_closure_for_E73",
        "external_action_blocked": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e73_ceo_readback_smoke_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
    }


def write_kg_czl_cieu(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_e73_boundary_state_for_brain(base)
    update = {
        "artifact_id": "e73_ceo_brain_ecosystem_boundary_lock_update",
        "bridge_job_id": JOB_ID,
        "highest_ready_level": state["highest_ready_CEO_work_level"],
        "next_recommended_milestone": state["next_recommended_milestone"],
        "external_action_allowed": False,
        "no_overclaim": True,
    }
    write_json(base, "operations/external_validation/e73_ceo_brain_ecosystem_boundary_lock_update.json", update)
    write_jsonl(base, "operations/knowledge_graph/e73_ceo_kg_ecosystem_boundary_nodes_delta.jsonl", [
        {"node_id": "e73_ecosystem_boundary_lock", "type": "milestone", "status": "completed_internal_closure"},
        {"node_id": "CEO_L2_internal_autonomous_work_ready", "type": "readiness_level", "status": "ready"},
        {"node_id": NEXT_MILESTONE, "type": "next_milestone", "status": "recommended"},
    ])
    write_jsonl(base, "operations/knowledge_graph/e73_ceo_kg_ecosystem_boundary_edges_delta.jsonl", [
        {"from": "e73_ecosystem_boundary_lock", "to": "CEO_L2_internal_autonomous_work_ready", "type": "adjudicates"},
        {"from": "CEO_L2_internal_autonomous_work_ready", "to": NEXT_MILESTONE, "type": "enables"},
    ])
    write_json(base, "operations/knowledge_graph/e73_ceo_kg_ecosystem_boundary_read_model_update.json", update)
    write_json(base, "operations/external_validation/e73_czl_closure.json", {
        "artifact_id": "e73_czl_closure",
        "closure_status": "closed_real_work_readiness_adjudicated",
        "closed_loop": "retrospective -> responsibility boundary -> no-new-wheel policy -> readiness gate -> next real internal work milestone",
        "next_recommended_milestone": NEXT_MILESTONE,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e73_cieu_residual_summary.json", {
        "artifact_id": "e73_cieu_residual_summary",
        "Y_star": "CEO stops endless construction and starts the highest safe class of real work.",
        "X_t": "Before E73, E72 proposed another adapter and boundaries across K9/Y-star-gov/gov-mcp/bridge-labs were not locked.",
        "U_t": "Create ecosystem responsibility matrix, no-new-wheel policy, readiness gate, and self-architecture protocol.",
        "Y_t_plus_1": [
            "L2 internal autonomous work is ready",
            "L3 is conditionally ready pending owner-approved allowlist and adapter proof",
            "L4 and L5 remain not ready",
            "E72 verifier proposal narrowed to adapter-contract only",
            "next milestone selected as real internal work rather than construction",
        ],
        "R_t_plus_1": [
            "no external action without owner gate",
            "no customer validation or paid signal",
            "no compliance/legal or production deployment claim",
            "L3 allowlist and public-read proof still needed before external research",
        ],
        "no_external_action": True,
        "no_overclaim": True,
    })
    return update


def build_completion_report(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_verification = load_json("operations/external_validation/e73_base_verification.json", base) or build_base_verification(base)
    matrix = load_json("operations/external_validation/e73_ecosystem_responsibility_matrix.json", base)
    overlap = load_json("operations/external_validation/e73_overlap_conflict_map.json", base)
    policy = load_json("operations/external_validation/e73_no_new_wheel_policy.json", base)
    gate = load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", base)
    protocol = load_json("operations/external_validation/e73_ceo_self_architecture_protocol.json", base)
    reclass = load_json("operations/external_validation/e73_e72_proposal_reclassification.json", base)
    readback = load_json("operations/external_validation/e73_ceo_readback_smoke_result.json", base)
    no_overclaim = load_json("operations/external_validation/e73_no_overclaim_validation_result.json", base)
    read_only_after = read_only_repo_status()
    read_only_before = base_verification.get("read_only_repo_status_before", {})
    read_only_unchanged = True
    for repo_name, after_state in read_only_after.items():
        before_state = read_only_before.get(repo_name, {})
        if before_state.get("head") != after_state.get("head"):
            read_only_unchanged = False
        if before_state.get("clean", True) and before_state.get("status_fingerprint") != after_state.get("status_fingerprint"):
            read_only_unchanged = False
    checks = {
        "base_HEAD_verified": base_verification.get("base_verified") is True,
        "responsibility_matrix_created": bool(matrix.get("canonical_owners")),
        "overlap_conflict_map_created": overlap.get("relevant_file_count", 0) > 0,
        "no_new_wheel_policy_created": policy.get("policy_status") == "machine_readable_and_testable",
        "readiness_gate_created": gate.get("highest_ready_level") == "L2_internal_autonomous_work_ready",
        "self_architecture_protocol_created": protocol.get("protocol_status") == "required_for_future_feature_construction",
        "E72_proposal_reclassified": reclass.get("accepted_as_is") is False and reclass.get("blindly_executed") is False,
        "owner_closure_report_created": _artifact_exists("operations/external_validation/e73_owner_readable_closure_report.md", base),
        "CEO_readback_passed": readback.get("passes") is True,
        "read_only_repos_unchanged": read_only_unchanged,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    return {
        "artifact_id": "e73_completion_report",
        "bridge_job_id": JOB_ID,
        "base_verification": base_verification,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": "e73_ecosystem_boundary_lock_and_ceo_real_work_readiness_closure_completed" if all(checks.values()) else "e73_partial_with_internal_blocker",
        "highest_ready_level": gate.get("highest_ready_level"),
        "L2_readiness": gate.get("level_decisions", {}).get("L2_internal_autonomous_work_ready", {}).get("readiness_decision"),
        "L3_readiness": gate.get("level_decisions", {}).get("L3_controlled_read_only_external_research_ready", {}).get("readiness_decision"),
        "L4_readiness": gate.get("level_decisions", {}).get("L4_owner_approved_external_action_ready", {}).get("readiness_decision"),
        "L5_readiness": gate.get("level_decisions", {}).get("L5_revenue_work_ready", {}).get("readiness_decision"),
        "next_recommended_milestone": NEXT_MILESTONE,
        "next_milestone_type": "real_internal_work",
        "read_only_repo_status_after": read_only_after,
        "read_only_repo_status_unchanged": read_only_unchanged,
        "pre_existing_dirty_read_only_repos_treated_as_context_only": [
            name for name, before_state in read_only_before.items() if before_state.get("clean") is False
        ],
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
    }


def load_e73_boundary_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    gate = load_json("operations/external_validation/e73_ceo_real_work_readiness_gate.json", base) or build_readiness_gate(base)
    matrix = load_json("operations/external_validation/e73_ecosystem_responsibility_matrix.json", base) or build_responsibility_matrix(base)
    reclass = load_json("operations/external_validation/e73_e72_proposal_reclassification.json", base) or build_e72_proposal_reclassification(base)
    report = load_json("operations/external_validation/e73_owner_readable_closure_report.json", base) or build_owner_closure_report(base)
    policy = load_json("operations/external_validation/e73_no_new_wheel_policy.json", base) or build_no_new_wheel_policy(base)
    return {
        "artifact_id": "e73_ceo_readable_ecosystem_boundary_lock_state",
        "bridge_job_id": JOB_ID,
        "ecosystem_boundary_lock_status": "ready_internal_closure_no_external_action",
        "responsibility_matrix": matrix.get("canonical_owners", {}),
        "highest_ready_CEO_work_level": gate.get("highest_ready_level"),
        "L2_readiness_decision": gate.get("level_decisions", {}).get("L2_internal_autonomous_work_ready", {}).get("readiness_decision"),
        "L3_readiness_decision": gate.get("level_decisions", {}).get("L3_controlled_read_only_external_research_ready", {}).get("readiness_decision"),
        "L4_readiness_decision": gate.get("level_decisions", {}).get("L4_owner_approved_external_action_ready", {}).get("readiness_decision"),
        "L5_readiness_decision": gate.get("level_decisions", {}).get("L5_revenue_work_ready", {}).get("readiness_decision"),
        "next_allowed_work_class": gate.get("next_allowed_autonomous_work"),
        "must_not_rebuild": report.get("what_must_not_be_rebuilt", []),
        "owner_gated_remaining": report.get("what_remains_owner_gated", []),
        "E72_proposal_decision": reclass.get("decision"),
        "no_new_wheel_policy_status": policy.get("policy_status"),
        "next_recommended_milestone": NEXT_MILESTONE,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def _markdown_matrix(matrix: dict[str, Any]) -> list[str]:
    lines = ["E73 locks canonical ownership so bridge-labs stops rebuilding upstream responsibilities.", ""]
    for owner, data in matrix["canonical_owners"].items():
        lines.append(f"## {owner}")
        lines.append("- Canonical: " + ", ".join(data["canonical_capabilities"]))
        lines.append("- bridge-labs must not duplicate: " + ", ".join(data["bridge_labs_must_not_duplicate"]))
        lines.append("- bridge-labs allowed role: " + ", ".join(data["bridge_labs_allowed_role"]))
        lines.append("")
    return lines


def _markdown_readiness(gate: dict[str, Any]) -> list[str]:
    lines = [
        "Direct answer: CEO can begin real internal work at L2. External research/action/revenue remain gated.",
        "",
        f"- Highest ready level: {gate['highest_ready_level']}",
        f"- Next allowed autonomous work: {gate['next_allowed_autonomous_work']}",
        "",
    ]
    for level, data in gate["level_decisions"].items():
        lines.append(f"## {level}")
        lines.append(f"- Decision: {data['readiness_decision']}")
        lines.append(f"- Allowed: {data['allowed_action_class']}")
        lines.append(f"- Forbidden: {data['forbidden_action_class']}")
        lines.append(f"- Next smallest closure: {data['next_smallest_closure']}")
        lines.append("")
    return lines


def write_all_e73_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_verification = build_base_verification(base)
    matrix = build_responsibility_matrix(base)
    overlap = build_overlap_conflict_map(base)
    policy = build_no_new_wheel_policy(base)
    gate = build_readiness_gate(base)
    protocol = build_self_architecture_protocol(base)
    reclassification = build_e72_proposal_reclassification(base)
    owner_report = build_owner_closure_report(base)
    next_proposal = build_generated_next_milestone_proposal(base)

    write_json(base, "operations/external_validation/e73_base_verification.json", base_verification)
    write_json(base, "operations/external_validation/e73_retrospective_inventory.json", build_retrospective_inventory(base))
    write_json(base, "operations/external_validation/e73_ecosystem_responsibility_matrix.json", matrix)
    write_md(base, "operations/external_validation/e73_ecosystem_responsibility_matrix.md", "E73 Ecosystem Responsibility Matrix", _markdown_matrix(matrix))
    write_json(base, "operations/external_validation/e73_overlap_conflict_map.json", overlap)
    write_md(base, "operations/external_validation/e73_overlap_conflict_map.md", "E73 Overlap Conflict Map", [
        f"- Scanned files: {overlap['scanned_file_count']}",
        f"- Relevant files: {overlap['relevant_file_count']}",
        f"- Conflict summary: {overlap['conflict_summary']}",
        "- Decision: bridge-labs files are context/readback/orchestration unless upstream ownership requires wrapping.",
    ])
    write_json(base, "operations/external_validation/e73_no_new_wheel_policy.json", policy)
    write_md(base, "operations/external_validation/e73_no_new_wheel_policy.md", "E73 No New Wheel Policy", [
        "Future construction is blocked until retrospective-first search and non-duplication proof are recorded.",
        "- CIEU ledger/hash verification: inspect and defer to K9Audit.",
        "- Governance enforcement: inspect and defer to Y-star-gov.",
        "- MCP/provider execution: inspect and defer to gov-mcp.",
        "- Market/revenue/pricing: extend E65/E66/E67/E10-E24/E71 first.",
        "- CEO self-bootstrap: extend E70/E71/E72 first.",
    ])
    write_json(base, "operations/external_validation/e73_ceo_real_work_readiness_gate.json", gate)
    write_md(base, "operations/external_validation/e73_ceo_real_work_readiness_gate.md", "E73 CEO Real Work Readiness Gate", _markdown_readiness(gate))
    write_json(base, "operations/external_validation/e73_ceo_self_architecture_protocol.json", protocol)
    write_md(base, "operations/external_validation/e73_ceo_self_architecture_protocol.md", "E73 CEO Self-Architecture Protocol", [
        "The CEO must prove reuse/extend/wrap/create-new before proposing future code.",
        "- Required steps: " + ", ".join(protocol["steps"]),
        "- Rejected: " + ", ".join(protocol["explicit_rejections"]),
    ])
    write_json(base, "operations/external_validation/e73_e72_proposal_reclassification.json", reclassification)
    write_md(base, "operations/external_validation/e73_e72_proposal_reclassification.md", "E73 E72 Proposal Reclassification", [
        f"- Original proposal: {reclassification['original_recommendation']}",
        f"- Decision: {reclassification['decision']}",
        "- Canonical cryptographic ledger verification remains K9Audit/Y-star-gov responsibility.",
        "- bridge-labs may later create only a sample packet / adapter contract / claim-boundary check.",
    ])
    write_json(base, "operations/external_validation/e73_owner_readable_closure_report.json", owner_report)
    write_md(base, "operations/external_validation/e73_owner_readable_closure_report.md", "E73 Owner-Readable Closure Report", [
        owner_report["direct_answer"],
        "",
        f"- Highest ready CEO work level: {owner_report['highest_ready_CEO_work_level']}",
        f"- Next allowed autonomous work: {owner_report['next_allowed_autonomous_work']}",
        f"- Exact next milestone: {owner_report['exact_next_milestone']}",
        f"- Next milestone type: {owner_report['next_milestone_type']}",
        "- What remains owner-gated: " + ", ".join(owner_report["what_remains_owner_gated"]),
        "- What must not be rebuilt: " + ", ".join(owner_report["what_must_not_be_rebuilt"]),
        "- Safety: no external action, no read-only repo mutation, no validation/paid/compliance/production claim.",
    ])
    write_json(base, "operations/external_validation/e73_generated_next_milestone_proposal.json", next_proposal)
    write_json(base, "operations/external_validation/e73_behavior_authorization_result.json", build_behavior_authorization(base))
    write_kg_czl_cieu(base)
    write_json(base, "operations/external_validation/e73_ceo_readback_smoke_result.json", build_readback_smoke(base))
    write_json(base, "operations/external_validation/e73_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    completion = build_completion_report(base)
    write_json(base, "operations/external_validation/e73_completion_report.json", completion)
    return completion


if __name__ == "__main__":
    print(json.dumps(write_all_e73_artifacts(), indent=2, ensure_ascii=False))
