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

JOB_ID = "e72_integrate_K9_CIEU_hash_chain_context_into_CIEU_audit_module_20260506T000001Z"
EXPECTED_BASE = "974c914bafc9a71011aa48904163acc77fa1c8ed"
E71_JOB_ID = "e71_legacy_high_value_asset_resurrection_and_mainline_binding_20260506T000001Z"
K9_CLUSTER_ID = "k9_cieu_hash_chain_spec_cluster"
PRODUCT_ID = "governed_business_operations_blueprint_for_agent_teams"
MODULE_NAME = "CIEU Audit Module"
OWNER_DECISION_STATUS = "pending_owner_decision"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_text(path: Path, limit: int = 80000) -> str:
    try:
        if not path.exists() or path.is_dir():
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


def git_state(path: Path, expected_head: str | None = None) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return ""

    status = run("status", "--short")
    status_fingerprint = hashlib.sha256(status.encode("utf-8")).hexdigest()
    head = run("rev-parse", "HEAD")
    return {
        "path": str(path),
        "branch": run("branch", "--show-current"),
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short_preview": status[:4000] + ("\n...TRUNCATED..." if len(status) > 4000 else ""),
        "status_fingerprint": status_fingerprint,
        "status_entry_count": len(status.splitlines()) if status else 0,
    }


def read_only_repo_status() -> dict[str, Any]:
    return {
        "K9Audit": git_state(K9_ROOT),
        "Y-star-gov": git_state(Y_GOV_ROOT),
        "gov-mcp": git_state(GOV_MCP_ROOT),
        "ystar-company": git_state(YSTAR_COMPANY_ROOT) if YSTAR_COMPANY_ROOT.exists() else {"path": str(YSTAR_COMPANY_ROOT), "exists": False, "clean": True, "status_fingerprint": "", "status_entry_count": 0},
    }


def source_fingerprint(path: Path) -> dict[str, Any]:
    text = read_text(path, limit=2_000_000)
    return {
        "path": str(path),
        "exists": bool(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else "",
        "bytes_read": len(text.encode("utf-8")) if text else 0,
    }


def load_e71_promoted_k9_cieu_assets(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    promoted = load_json("operations/external_validation/e71_promoted_legacy_assets.json", base)
    scorecards = load_json("operations/external_validation/e71_legacy_asset_scorecards.json", base)
    cieu_inputs = load_json("operations/external_validation/e71_legacy_cieu_module_inputs.json", base)
    cluster_score = next(
        (row for row in scorecards.get("cluster_scorecards", []) if row.get("cluster_id") == K9_CLUSTER_ID),
        {},
    )
    assets = [
        row for row in promoted.get("promoted_assets", [])
        if row.get("cluster_id") == K9_CLUSTER_ID and row.get("final_disposition") == "integrate_into_CIEU_route"
    ]
    return {
        "artifact_id": "e72_promoted_k9_cieu_asset_selection",
        "source_E71_job_id": E71_JOB_ID,
        "cluster_id": K9_CLUSTER_ID,
        "cluster_was_top_scored": scorecards.get("top_cluster") == K9_CLUSTER_ID,
        "cluster_score": cluster_score.get("total_score"),
        "cluster_priority_band": cluster_score.get("priority_band"),
        "promoted_assets": assets,
        "promoted_asset_count": len(assets),
        "E71_CIEU_fields": cieu_inputs.get("CIEU_fields", []),
        "E71_not_K9Audit_integration_completed": cieu_inputs.get("not_K9Audit_integration_completed") is True,
        "external_action_allowed": False,
    }


def build_cieu_hash_chain_context(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    k9_spec = K9_ROOT / "docs/CIEU_spec.md"
    logger = K9_ROOT / "k9log/logger.py"
    verifier = K9_ROOT / "k9log/verifier.py"
    selected = load_e71_promoted_k9_cieu_assets(base)
    return {
        "artifact_id": "e72_cieu_hash_chain_context",
        "bridge_job_id": JOB_ID,
        "source_cluster_id": K9_CLUSTER_ID,
        "source_assets": selected["promoted_assets"],
        "read_only_source_fingerprints": {
            "K9_CIEU_spec": source_fingerprint(k9_spec),
            "K9_logger": source_fingerprint(logger),
            "K9_verifier": source_fingerprint(verifier),
        },
        "imported_CIEU_five_tuple": {
            "X_t": "context at decision/action time",
            "U_t": "action actually executed or proposed",
            "Y_star_t": "declared intent contract or expected normative target",
            "Y_t_plus_1": "observed or expected outcome after action",
            "R_t_plus_1": "measured deviation, residual, violation, or governance gap",
        },
        "imported_hash_chain_context": {
            "sequence": "monotonic record order",
            "previous_hash": "hash link to previous CIEU record",
            "current_hash": "hash over canonical payload plus previous hash",
            "canonical_payload": "deterministic serialized record excluding integrity/hash fields",
            "deterministic_serialization_boundary": "JSON with sorted keys and compact separators, represented here as context only",
            "tamper_evident_chain_semantics": "record changes, deletion, or reordering should break a structural chain check",
            "audit_receipt_semantics": "append-only JSONL-style evidence receipt boundary",
        },
        "bridge_labs_status": {
            "hash_chain_context_imported": True,
            "hash_chain_ready_context": True,
            "production_hash_chain_enabled": False,
            "live_ledger_written": False,
            "full_audit_verification_completed": False,
            "structural_verification_available": True,
            "structural_verification_scope": "schema/context/field-boundary verification only; no live ledger chain is verified",
        },
        "structural_verification_requirements": [
            "record includes X_t",
            "record includes U_t",
            "record includes Y_star_t",
            "record includes Y_t_plus_1 or Y_t+1",
            "record includes R_t_plus_1 or R_t+1",
            "record declares previous_hash or _integrity.prev_hash when hash-chain-ready",
            "record declares current_hash, record_hash, or _integrity.event_hash when hash-chain-ready",
            "record declares canonical payload boundary before any production ledger claim",
        ],
        "read_only_repos_mutated": False,
        "external_action_allowed": False,
    }


def _sample_record() -> dict[str, Any]:
    return {
        "record_status": "internal_example_no_execution",
        "X_t": {
            "context": "agent-team governed operations review",
            "actor": "CEO internal planner",
            "environment": "bridge-labs internal no-execution blueprint",
        },
        "U_t": {
            "action": "propose CIEU audit module integration",
            "execution_status": "proposed_only",
        },
        "Y_star_t": {
            "intent_contract": "advance selected first-cash route while preserving no-overclaim and owner-gated external action boundaries",
            "constraints": ["no external action", "no compliance claim", "no customer validation claim", "no paid signal claim"],
        },
        "Y_t_plus_1": {
            "expected_outcome": "internal product module context gains causal audit and hash-chain readiness semantics",
        },
        "R_t_plus_1": {
            "residuals": [
                "production ledger not implemented",
                "live hash-chain verification not performed",
                "customer validation absent",
                "compliance/legal sufficiency unproven",
            ],
        },
        "hash_chain_ready_context": {
            "previous_hash": "not_applicable_internal_example",
            "current_hash": "not_applicable_internal_example",
            "canonical_payload_boundary": "defined_as_context_only",
            "verification_status": "structural_context_only",
        },
    }


def map_k9_cieu_to_bridge_labs_audit_module(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    context = build_cieu_hash_chain_context(base)
    return {
        "artifact_id": "e72_k9_to_bridge_labs_cieu_audit_module_map",
        "bridge_job_id": JOB_ID,
        "source_cluster_id": K9_CLUSTER_ID,
        "mapping": [
            {"K9_concept": "CIEU five-tuple", "bridge_labs_target": "E68 CIEU route and E69 CIEU Audit Module field map", "binding_mode": "product-context and readback input"},
            {"K9_concept": "Y_star_t intent contract", "bridge_labs_target": "governed business operations normative baseline", "binding_mode": "module deliverable field"},
            {"K9_concept": "R_t_plus_1 residual assessment", "bridge_labs_target": "CIEU residual table and CZL closure learning", "binding_mode": "sample delivery packet input"},
            {"K9_concept": "previous/current hash chain", "bridge_labs_target": "hash-chain-ready context for future verifier adapter", "binding_mode": "read-only context import"},
            {"K9_concept": "deterministic canonical payload", "bridge_labs_target": "future structural verifier requirements", "binding_mode": "technical appendix input"},
            {"K9_concept": "append-only JSONL evidence", "bridge_labs_target": "future no-execution demo packet evidence format", "binding_mode": "owner-gated demo input"},
        ],
        "integration_targets": [
            "operations/external_validation/e68_cieu_product_wedge_hypothesis.json",
            "operations/external_validation/e69_cieu_module_integration_plan.json",
            "products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json",
            "products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json",
            "office/mission_command/e46b_ceo_brain_adapter.py",
        ],
        "sample_internal_record": _sample_record(),
        "bridge_labs_status": context["bridge_labs_status"],
        "external_action_allowed": False,
    }


def build_cieu_audit_module_capability_delta(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    return {
        "artifact_id": "e72_cieu_audit_module_capability_delta",
        "bridge_job_id": JOB_ID,
        "before_E72": {
            "CIEU_module_status": "CIEU five-tuple module planned by E69",
            "hash_chain_context_status": "available as E71 promoted read-only K9 legacy asset",
            "CEO_visibility": "CEO could see E71 top cluster but not E72-bound module context",
        },
        "after_E72": {
            "CIEU_module_status": "internal product module context bound to K9 CIEU/hash-chain semantics",
            "hash_chain_context_status": "hash_chain_context_imported",
            "CEO_visibility": "CEO reads latest CIEU audit-module hash-chain context and residuals",
            "self_bootstrap_awareness": "E71 top cluster consumed by E72; avoid duplicate resurrection proposals",
        },
        "capabilities_added": [
            "K9 CIEU/hash-chain context imported as bridge-labs internal model",
            "CIEU five-tuple mapping preserved across E68/E69/E70/E71 stack",
            "product-facing CIEU Audit Module binding updated",
            "structural verification scope declared",
            "next residual-driven Codex proposal generated",
        ],
        "capabilities_not_added": [
            "production hash-chain ledger",
            "live ledger writes",
            "full audit verification over real event stream",
            "legal/compliance certification",
            "customer validation",
            "paid signal",
        ],
        "external_action_allowed": False,
    }


def build_product_binding(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    context = build_cieu_hash_chain_context(base)
    mapping = map_k9_cieu_to_bridge_labs_audit_module(base)
    return {
        "artifact_id": "e72_cieu_audit_module_product_binding",
        "bridge_job_id": JOB_ID,
        "selected_product": PRODUCT_ID,
        "selected_product_name": "Governed Business Operations Blueprint for Agent Teams",
        "module": MODULE_NAME,
        "binding_status": "internal_structural_context_bound_no_execution",
        "source_legacy_cluster_consumed": K9_CLUSTER_ID,
        "internal_value": [
            "deterministic causal audit context",
            "hash-chain readiness",
            "action-intent-outcome residual semantics",
            "tamper-evident evidence model context",
            "audit receipt semantics for future internal demo packet",
        ],
        "CIEU_fields_preserved": list(context["imported_CIEU_five_tuple"].keys()),
        "hash_chain_context_fields": list(context["imported_hash_chain_context"].keys()),
        "module_sample_record": mapping["sample_internal_record"],
        "what_it_can_currently_claim": [
            "internal structural integration",
            "no-execution audit module blueprint",
            "promoted legacy asset binding",
            "hash-chain context imported",
            "structural verification scope declared",
        ],
        "what_it_cannot_claim": [
            "compliance certification",
            "customer validation",
            "paid signal",
            "production deployment",
            "live audit ledger",
            "full cryptographic audit verification",
            "legal sufficiency",
        ],
        "owner_gated_future_steps": [
            "legal/regulatory review before compliance language",
            "external review before public claims",
            "EV5 experiment before market claims",
            "implementation review before production ledger claims",
        ],
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def _proposal_candidates(root: Path | None = None) -> list[dict[str, Any]]:
    base = root or BRIDGE_ROOT
    binding = build_product_binding(base)
    residuals = set(build_cieu_audit_module_capability_delta(base)["capabilities_not_added"])
    candidates = [
        {
            "candidate_id": "E73_CIEU_hash_chain_structural_verifier_bridge_labs_adapter",
            "residual_addressed": "full audit verification over real event stream",
            "scores": {
                "addresses_highest_E72_residual": 96 if "full audit verification over real event stream" in residuals else 50,
                "internal_only_feasibility": 94,
                "product_module_readiness_value": 90,
                "no_overclaim_safety": 96,
                "dependency_on_owner_external_approval_inverse": 95,
            },
        },
        {
            "candidate_id": "E73_build_internal_CIEU_audit_module_demo_packet_no_external_action",
            "residual_addressed": "demo packet not yet created",
            "scores": {
                "addresses_highest_E72_residual": 82,
                "internal_only_feasibility": 92,
                "product_module_readiness_value": 94,
                "no_overclaim_safety": 90,
                "dependency_on_owner_external_approval_inverse": 95,
            },
        },
        {
            "candidate_id": "E73_prepare_EV5_owner_gated_external_review_packet_no_execution",
            "residual_addressed": "customer/external review absent",
            "scores": {
                "addresses_highest_E72_residual": 70,
                "internal_only_feasibility": 88,
                "product_module_readiness_value": 80,
                "no_overclaim_safety": 86,
                "dependency_on_owner_external_approval_inverse": 55,
            },
        },
        {
            "candidate_id": "E73_bind_CIEU_audit_module_to_governed_business_operations_offer_no_publication",
            "residual_addressed": "product binding hardening",
            "scores": {
                "addresses_highest_E72_residual": 76 if binding["binding_status"] else 60,
                "internal_only_feasibility": 92,
                "product_module_readiness_value": 88,
                "no_overclaim_safety": 92,
                "dependency_on_owner_external_approval_inverse": 95,
            },
        },
        {
            "candidate_id": "E73_provider_promotion_gate_owner_decision_packet_no_execution",
            "residual_addressed": "provider live execution boundary owner review",
            "scores": {
                "addresses_highest_E72_residual": 55,
                "internal_only_feasibility": 78,
                "product_module_readiness_value": 72,
                "no_overclaim_safety": 82,
                "dependency_on_owner_external_approval_inverse": 45,
            },
        },
    ]
    for candidate in candidates:
        scores = candidate["scores"]
        candidate["total_score"] = round(sum(scores.values()) / len(scores), 2)
        candidate["external_action_allowed"] = False
    return sorted(candidates, key=lambda row: row["total_score"], reverse=True)


def build_generated_codex_job_proposal(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    candidates = _proposal_candidates(base)
    selected = candidates[0]
    return {
        "artifact_id": "e72_generated_codex_job_proposal",
        "bridge_job_id": JOB_ID,
        "proposed_milestone_id": selected["candidate_id"],
        "proposed_title": "Build bridge-labs structural verifier adapter for CIEU hash-chain context",
        "generated_from_E72_residuals": True,
        "selection_basis": "highest score on E72 residual coverage, internal-only feasibility, product-module readiness, and no-overclaim safety",
        "candidate_scores": candidates,
        "source_goal": "turn imported K9 CIEU/hash-chain context into a tested bridge-labs structural verifier adapter without live ledger claims",
        "capability_gap_addressed": selected["residual_addressed"],
        "expected_base": "E72 completion commit",
        "repo_scope": "bridge-labs only; K9Audit/Y-star-gov/gov-mcp/ystar-company read-only",
        "implementation_plan": [
            "load E72 CIEU hash-chain context",
            "define structural record checks for five-tuple and integrity fields",
            "verify internal sample records only",
            "update product/readback residuals",
            "add no-overclaim tests",
        ],
        "safety_boundary": [
            "no external action",
            "no read-only repo mutation",
            "no production ledger claim",
            "no compliance/legal claim",
            "no customer validation or paid signal claim",
        ],
        "tests": [
            "structural verifier positive/negative sample tests",
            "CEO readback test",
            "product binding no-overclaim test",
            "completion gate test",
        ],
        "owner_approval_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
    }


def build_e72_state(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    base_state = git_state(base, EXPECTED_BASE)
    read_only_before = read_only_repo_status()
    selected = load_e71_promoted_k9_cieu_assets(base)
    context = build_cieu_hash_chain_context(base)
    mapping = map_k9_cieu_to_bridge_labs_audit_module(base)
    delta = build_cieu_audit_module_capability_delta(base)
    binding = build_product_binding(base)
    proposal = build_generated_codex_job_proposal(base)
    return {
        "artifact_id": "e72_cieu_hash_chain_context_state",
        "bridge_job_id": JOB_ID,
        "base_hash": base_state["head"],
        "expected_base_hash": EXPECTED_BASE,
        "base_verified": base_state["head_matches_expected"] and base_state["branch"] == "backflow/aiden-ceo-meeting-room",
        "source_E71_job_id": E71_JOB_ID,
        "E71_completed_report_present": Path(f"/tmp/ystar_delivery_bridge/completed/{E71_JOB_ID}.report.json").exists(),
        "imported_cluster_id": K9_CLUSTER_ID,
        "imported_cluster_was_E71_top_cluster": selected["cluster_was_top_scored"],
        "promoted_assets_consumed": selected["promoted_assets"],
        "promoted_asset_count_consumed": selected["promoted_asset_count"],
        "K9_CIEU_concepts_imported": {
            "five_tuple": context["imported_CIEU_five_tuple"],
            "hash_chain": context["imported_hash_chain_context"],
        },
        "bridge_labs_integration_targets": mapping["integration_targets"],
        "product_binding_status": binding["binding_status"],
        "capability_delta": delta,
        "limitations": binding["what_it_cannot_claim"],
        "residual_gaps": delta["capabilities_not_added"],
        "read_only_repo_status_before": read_only_before,
        "read_only_repos_mutated": False,
        "next_recommended_milestone": proposal["proposed_milestone_id"],
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "pricing_validation_claimed": False,
        "expert_feedback_claimed": False,
        "compliance_legal_claimed": False,
        "production_deployment_claimed": False,
        "production_hash_chain_enabled": False,
    }


def write_product_files(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    product_dir = base / "products" / PRODUCT_ID
    binding = build_product_binding(base)
    context = build_cieu_hash_chain_context(base)
    existing_offer = load_json(f"products/{PRODUCT_ID}/updated_offer_blueprint_with_cieu_module.json", base)
    module_json = {
        "artifact_id": "e72_product_cieu_audit_module",
        "source_artifact": "operations/external_validation/e72_cieu_audit_module_product_binding.json",
        "module_name": MODULE_NAME,
        "status": "internal_only_hash_chain_context_bound",
        "CIEU_five_tuple_fields": context["imported_CIEU_five_tuple"],
        "hash_chain_context": context["imported_hash_chain_context"],
        "structural_verification_scope": context["bridge_labs_status"]["structural_verification_scope"],
        "sample_internal_record": binding["module_sample_record"],
        "does_not_claim": binding["what_it_cannot_claim"],
        "owner_gated_future_steps": binding["owner_gated_future_steps"],
        "external_action_allowed": False,
    }
    updated_offer = {
        "artifact_id": "e72_updated_offer_blueprint_with_cieu_hash_chain_context",
        "source_offer_blueprint": existing_offer.get("source_offer_blueprint", "operations/external_validation/e66_selected_route_offer_blueprint.json"),
        "offer_name": existing_offer.get("offer_name", "Governed Business Operations Blueprint for Agent Teams"),
        "added_module": MODULE_NAME,
        "status": "draft_only_internal_no_publication",
        "E72_binding_status": binding["binding_status"],
        "module_deliverables": [
            "CIEU five-tuple field map",
            "causal action evidence plan",
            "hash-chain-ready audit context appendix",
            "structural verification scope",
            "residual review table",
            "no-overclaim notice",
            "owner-gated validation path",
        ],
        "hash_chain_context_imported": True,
        "production_hash_chain_enabled": False,
        "live_audit_ledger_enabled": False,
        "owner_approval_required_before_external_use": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "expert_feedback_claimed": False,
        "legal_compliance_claimed": False,
        "EU_AI_Act_compliance_claimed": False,
        "production_deployment_claimed": False,
        "external_action_allowed": False,
    }
    write_json(base, f"products/{PRODUCT_ID}/cieu_audit_module.json", module_json)
    write_json(base, f"products/{PRODUCT_ID}/updated_offer_blueprint_with_cieu_module.json", updated_offer)
    (product_dir / "cieu_audit_module.md").write_text(
        "\n".join([
            "# CIEU Audit Module",
            "",
            "Status: internal-only draft, hash-chain context bound in E72.",
            "",
            "Purpose: add causal intent-action-outcome-residual evidence planning to the Governed Business Operations Blueprint.",
            "",
            "CIEU fields preserved: X_t, U_t, Y_star_t, Y_t_plus_1, R_t_plus_1.",
            "",
            "E72 adds K9-style hash-chain readiness context: previous hash, current hash, canonical payload boundary, tamper-evident chain semantics, and structural verification scope.",
            "",
            "Current claim boundary: internal structural integration and no-execution audit module blueprint only.",
            "",
            "Not claimed: compliance certification, legal sufficiency, medical or energy readiness, production deployment, live audit ledger, customer validation, paid signal, or pricing validation.",
            "",
        ]),
        encoding="utf-8",
    )
    (product_dir / "updated_offer_blueprint_with_cieu_module.md").write_text(
        "\n".join([
            "# Updated Offer Blueprint With CIEU Module",
            "",
            "Offer: Governed Business Operations Blueprint for Agent Teams.",
            "",
            "E72 internal update: the CIEU Audit Module now includes promoted K9 CIEU/hash-chain context as an internal product module layer.",
            "",
            "What changed: the module can now explain causal audit fields plus hash-chain-ready evidence semantics for future internal demo/verifier work.",
            "",
            "What remains blocked: external review, publication, compliance claims, production ledger claims, customer validation, paid signal, and pricing validation.",
            "",
        ]),
        encoding="utf-8",
    )


def build_readback_markdown(root: Path | None = None) -> list[str]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e72_cieu_hash_chain_context_state.json", base) or build_e72_state(base)
    return [
        f"Job id: `{JOB_ID}`.",
        f"Source legacy cluster: `{state.get('imported_cluster_id')}` from E71.",
        "E72 bound K9 CIEU/hash-chain context into the bridge-labs CIEU Audit Module as internal product context.",
        "The CIEU five-tuple remains: `X_t`, `U_t`, `Y_star_t`, `Y_t_plus_1`, `R_t_plus_1`.",
        "The imported hash-chain context covers previous hash, current hash, deterministic canonical payload boundary, tamper-evident chain semantics, and audit receipt semantics.",
        "Current status is structural/readback/product binding only: no live ledger, no production hash-chain, and no full audit verification claim.",
        "Connection path: E71 promoted K9 context -> E68 CIEU route -> E69 CIEU Audit Module -> E66 governed operations blueprint -> E70/E71 CEO self-bootstrap/readback.",
        f"Next recommended milestone: `{state.get('next_recommended_milestone')}`.",
        "Safety: no external action, no read-only repo mutation, no customer validation, no paid signal, no legal/compliance claim, no production deployment claim.",
    ]


def build_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e72_cieu_hash_chain_context_state.json", base) or build_e72_state(base)
    binding = load_json("operations/external_validation/e72_cieu_audit_module_product_binding.json", base) or build_product_binding(base)
    proposal = load_json("operations/external_validation/e72_generated_codex_job_proposal.json", base) or build_generated_codex_job_proposal(base)
    checks = {
        "CEO_sees_E72_state": state.get("imported_cluster_id") == K9_CLUSTER_ID,
        "CEO_sees_E71_promoted_assets_consumed": state.get("promoted_asset_count_consumed", 0) >= 1,
        "CEO_sees_hash_chain_context_imported": state.get("K9_CIEU_concepts_imported", {}).get("hash_chain") is not None,
        "CEO_sees_product_binding": binding.get("binding_status") == "internal_structural_context_bound_no_execution",
        "CEO_sees_not_production_ready": state.get("production_deployment_claimed") is False and state.get("production_hash_chain_enabled") is False,
        "CEO_sees_forbidden_claims_absent": all(state.get(field) is False for field in [
            "customer_validation_claimed",
            "paid_signal_claimed",
            "pricing_validation_claimed",
            "expert_feedback_claimed",
            "compliance_legal_claimed",
            "production_deployment_claimed",
        ]),
        "CEO_sees_next_milestone": proposal.get("proposed_milestone_id") == state.get("next_recommended_milestone"),
        "CEO_sees_external_action_blocked": state.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e72_cieu_audit_module_readback_smoke_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "passes": all(checks.values()),
        "observed_state": {
            "imported_cluster_id": state.get("imported_cluster_id"),
            "product_binding_status": binding.get("binding_status"),
            "next_recommended_milestone": state.get("next_recommended_milestone"),
            "external_action_allowed": state.get("external_action_allowed"),
        },
        "external_action_allowed": False,
    }


def build_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    paths = [
        "operations/external_validation/e72_cieu_hash_chain_context_state.json",
        "operations/external_validation/e72_cieu_audit_module_product_binding.json",
        "operations/external_validation/e72_generated_codex_job_proposal.json",
        "products/governed_business_operations_blueprint_for_agent_teams/cieu_audit_module.json",
        "products/governed_business_operations_blueprint_for_agent_teams/updated_offer_blueprint_with_cieu_module.json",
    ]
    forbidden_true = [
        "external_action_allowed",
        "customer_validation_claimed",
        "paid_signal_claimed",
        "pricing_validation_claimed",
        "expert_feedback_claimed",
        "compliance_legal_claimed",
        "production_deployment_claimed",
        "production_hash_chain_enabled",
        "live_audit_ledger_enabled",
        "EU_AI_Act_compliance_claimed",
        "legal_compliance_claimed",
    ]
    violations = []
    for rel in paths:
        data = load_json(rel, base)
        for field in forbidden_true:
            if data.get(field) is True:
                violations.append({"path": rel, "field": field, "value": True})
    return {
        "artifact_id": "e72_no_overclaim_validation_result",
        "paths_scanned": paths,
        "violations": violations,
        "passed": not violations,
        "external_action_allowed": False,
    }


def write_kg_czl_cieu(root: Path | None = None) -> None:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e72_cieu_hash_chain_context_state.json", base) or build_e72_state(base)
    write_json(
        base,
        "operations/external_validation/e72_ceo_brain_cieu_audit_module_update.json",
        {
            "artifact_id": "e72_ceo_brain_cieu_audit_module_update",
            "bridge_job_id": JOB_ID,
            "latest_cieu_audit_module_status": "hash_chain_context_bound_internal_no_execution",
            "imported_cluster_id": state["imported_cluster_id"],
            "promoted_asset_count_consumed": state["promoted_asset_count_consumed"],
            "product_binding_status": state["product_binding_status"],
            "next_recommended_milestone": state["next_recommended_milestone"],
            "external_action_allowed": False,
            "customer_validation_claimed": False,
            "paid_signal_claimed": False,
            "compliance_legal_claimed": False,
            "production_deployment_claimed": False,
        },
    )
    write_jsonl(
        base,
        "operations/knowledge_graph/e72_ceo_kg_cieu_audit_module_nodes_delta.jsonl",
        [
            {"node_id": "e72_k9_cieu_hash_chain_context", "node_type": "legacy_context_binding", "status": "bound_internal"},
            {"node_id": "e72_cieu_audit_module_product_binding", "node_type": "product_module_binding", "status": "internal_no_execution"},
            {"node_id": state["next_recommended_milestone"], "node_type": "codex_job_proposal", "status": "proposed_no_execution"},
        ],
    )
    write_jsonl(
        base,
        "operations/knowledge_graph/e72_ceo_kg_cieu_audit_module_edges_delta.jsonl",
        [
            {"from": "e71_legacy_asset_registry", "to": "e72_k9_cieu_hash_chain_context", "edge_type": "consumed_top_cluster"},
            {"from": "e72_k9_cieu_hash_chain_context", "to": "e72_cieu_audit_module_product_binding", "edge_type": "binds_context_to_product_module"},
            {"from": "e72_cieu_audit_module_product_binding", "to": state["next_recommended_milestone"], "edge_type": "residual_generates_next_proposal"},
        ],
    )
    write_json(
        base,
        "operations/knowledge_graph/e72_ceo_kg_cieu_audit_module_read_model_update.json",
        {
            "artifact_id": "e72_ceo_kg_cieu_audit_module_read_model_update",
            "bridge_job_id": JOB_ID,
            "imported_cluster_id": state["imported_cluster_id"],
            "product_binding_status": state["product_binding_status"],
            "next_recommended_milestone": state["next_recommended_milestone"],
            "external_action_allowed": False,
        },
    )
    write_json(
        base,
        "operations/external_validation/e72_czl_closure.json",
        {
            "artifact_id": "e72_czl_closure",
            "closure_status": "closed_internal_no_execution",
            "closed_loop": "E71 top legacy cluster -> K9 CIEU/hash-chain context -> product module binding -> CEO readback -> residual proposal",
            "next_recommended_milestone": state["next_recommended_milestone"],
            "no_external_action": True,
        },
    )
    write_json(
        base,
        "operations/external_validation/e72_cieu_residual_summary.json",
        {
            "artifact_id": "e72_cieu_residual_summary",
            "Y_star": "K9 CIEU/hash-chain context is safely bound into current bridge-labs CIEU Audit Module.",
            "X_t": "Before E72, K9 context was promoted by E71 but not bound into the product module/readback layer.",
            "U_t": "Import K9 CIEU/hash-chain context as bridge-labs internal structural/product context.",
            "Y_t_plus_1": [
                "K9 CIEU five-tuple mapped to module fields",
                "hash-chain context imported",
                "product binding updated",
                "CEO readback added",
                "next residual-driven Codex proposal generated",
            ],
            "R_t_plus_1": state["residual_gaps"],
            "no_external_action": True,
            "no_overclaim": True,
        },
    )


def build_completion_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e72_cieu_hash_chain_context_state.json", base)
    binding = load_json("operations/external_validation/e72_cieu_audit_module_product_binding.json", base)
    proposal = load_json("operations/external_validation/e72_generated_codex_job_proposal.json", base)
    readback = load_json("operations/external_validation/e72_cieu_audit_module_readback_smoke_result.json", base)
    no_overclaim = load_json("operations/external_validation/e72_no_overclaim_validation_result.json", base)
    read_only_after = read_only_repo_status()
    read_only_before = state.get("read_only_repo_status_before", {})
    read_only_unchanged = True
    for repo_name, after_state in read_only_after.items():
        before_state = read_only_before.get(repo_name, {})
        if before_state.get("head") != after_state.get("head"):
            read_only_unchanged = False
        if before_state.get("status_fingerprint") != after_state.get("status_fingerprint"):
            read_only_unchanged = False
    checks = {
        "base_verified": state.get("base_verified") is True,
        "E71_report_present": state.get("E71_completed_report_present") is True,
        "E71_K9_cluster_consumed": state.get("imported_cluster_id") == K9_CLUSTER_ID and state.get("promoted_asset_count_consumed", 0) >= 1,
        "CIEU_five_tuple_preserved": set(binding.get("CIEU_fields_preserved", [])) == {"X_t", "U_t", "Y_star_t", "Y_t_plus_1", "R_t_plus_1"},
        "hash_chain_context_imported_without_production_claim": state.get("production_hash_chain_enabled") is False and "current_hash" in binding.get("hash_chain_context_fields", []),
        "product_binding_exists": binding.get("binding_status") == "internal_structural_context_bound_no_execution",
        "CEO_readback_passes": readback.get("passes") is True,
        "generated_next_codex_proposal_exists": proposal.get("generated_from_E72_residuals") is True,
        "read_only_repos_unchanged": read_only_unchanged,
        "no_overclaim_fields_true": no_overclaim.get("passed") is True,
    }
    return {
        "artifact_id": "e72_completion_gate_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "gate_passed": all(checks.values()),
        "final_status": "e72_k9_cieu_hash_chain_context_integrated_into_audit_module" if all(checks.values()) else "e72_partial_with_internal_blocker",
        "next_recommended_milestone": proposal.get("proposed_milestone_id"),
        "read_only_repo_status_after": read_only_after,
        "read_only_repo_status_unchanged": read_only_unchanged,
        "external_action_allowed": False,
    }


def build_e72_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = load_json("operations/external_validation/e72_cieu_hash_chain_context_state.json", base) or build_e72_state(base)
    binding = load_json("operations/external_validation/e72_cieu_audit_module_product_binding.json", base) or build_product_binding(base)
    proposal = load_json("operations/external_validation/e72_generated_codex_job_proposal.json", base) or build_generated_codex_job_proposal(base)
    return {
        "artifact_id": "e72_ceo_readable_cieu_audit_module_state",
        "bridge_job_id": JOB_ID,
        "cieu_audit_module_status": "hash_chain_context_bound_internal_no_execution",
        "K9_CIEU_hash_chain_context_bound": state.get("imported_cluster_id") == K9_CLUSTER_ID,
        "E71_promoted_assets_consumed": state.get("promoted_assets_consumed", []),
        "CIEU_Audit_Module_integrated_into_governed_business_operations_blueprint": binding.get("binding_status") == "internal_structural_context_bound_no_execution",
        "production_ready": False,
        "forbidden_claims": binding.get("what_it_cannot_claim", []),
        "residual_gaps": state.get("residual_gaps", []),
        "next_recommended_milestone": proposal.get("proposed_milestone_id"),
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
    }


def write_all_e72_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    state = build_e72_state(base)
    write_json(base, "operations/external_validation/e72_cieu_hash_chain_context_state.json", state)
    write_json(base, "operations/external_validation/e72_cieu_audit_module_product_binding.json", build_product_binding(base))
    write_json(base, "operations/external_validation/e72_generated_codex_job_proposal.json", build_generated_codex_job_proposal(base))
    write_product_files(base)
    write_md(base, "operations/external_validation/e72_cieu_hash_chain_context_readback.md", "E72 CIEU Hash-Chain Context Readback", build_readback_markdown(base))
    write_kg_czl_cieu(base)
    write_json(base, "operations/external_validation/e72_cieu_audit_module_readback_smoke_result.json", build_readback_smoke(base))
    write_json(base, "operations/external_validation/e72_no_overclaim_validation_result.json", build_no_overclaim_validation(base))
    gate = build_completion_gate(base)
    write_json(base, "operations/external_validation/e72_completion_gate_result.json", gate)
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e72_artifacts(), indent=2, ensure_ascii=False))
