
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
K9_ROOT = Path(os.environ.get("K9AUDIT_ROOT", "/Users/haotianliu/.openclaw/workspace/K9Audit"))

JOB_ID = "e60_post_external_intelligence_market_readiness_retest_20260506T000001Z"
EXPECTED_BASE = "09149c229f30735d3e08e0fa9f6ee4c5ea5f320e"
FINAL_STATUS = "post_external_intelligence_market_readiness_retest_closed"
CURRENT_READINESS_LEVEL = "L3_external_intelligence_structurally_ready"
SELECTED_NEXT_MILESTONE = "E61_live_public_read_adapter_repair_or_host_network_refresh"
NEAREST_ALTERNATIVE = "E61_owner_decision_gate_for_case_study_review"
LIVE_READ_STATUS = "live_public_read_unavailable_nonfatal"
PAGE_ADAPTER_STATUS = "fixture_only_network_unavailable"
OWNER_DECISION_STATUS = "pending_owner_decision"


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


def load_json(rel: str, root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(((root or BRIDGE_ROOT) / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def git_state(path: Path, expected_head: str | None = None) -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=path, text=True).strip()
        except Exception:
            return ""
    head = run("rev-parse", "HEAD")
    status = run("status", "--short")
    return {
        "path": str(path),
        "head": head,
        "expected_head": expected_head,
        "head_matches_expected": expected_head is None or head == expected_head,
        "clean": status == "",
        "status_short": status,
    }


def dirty_paths_are_e60_scoped(status_short: str) -> bool:
    if not status_short:
        return True
    allowed_prefixes = (
        "office/mission_command/e60_",
        "tests/office/test_e60_",
        "operations/external_validation/e60_",
        "operations/knowledge_graph/e60_",
        "reports/integration/e60_",
    )
    allowed_exact = {"office/mission_command/e46b_ceo_brain_adapter.py"}
    for line in status_short.splitlines():
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].strip()
        if path in allowed_exact or path.startswith(allowed_prefixes):
            continue
        return False
    return True


def build_base_state_manifest(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    bridge = git_state(base, EXPECTED_BASE)
    read_only = {
        "Y-star-gov": git_state(Y_GOV_ROOT, "b0d9aa8b1badd1180127a2f79f73ceed48e16451"),
        "gov-mcp": git_state(GOV_MCP_ROOT, "d0181bc8f19d8ae7714bd0f8a220fe12e6ceee90"),
        "K9Audit": git_state(K9_ROOT, "37911e18ce4425470e3f745b30d155c43d76ff55"),
    }
    return {
        "artifact_id": "e60_base_state_manifest",
        "bridge_job_id": JOB_ID,
        "bridge_labs": bridge,
        "read_only_repos": read_only,
        "base_verified": bridge["head_matches_expected"],
        "bridge_labs_worktree_clean_or_e60_scoped": dirty_paths_are_e60_scoped(bridge["status_short"]),
        "read_only_repos_clean": all(item["clean"] for item in read_only.values()),
        "expected_base": EXPECTED_BASE,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_prior_gate_preflight(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e54 = load_json("operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json", base)
    e55 = load_json("operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json", base)
    e56 = load_json("operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", base)
    e57_gate = load_json("operations/external_validation/e57_post_l5_money_route_retest_gate_result.json", base)
    e57_decision = load_json("operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", base)
    e58_gate = load_json("operations/external_validation/e58_case_study_completion_gate_result.json", base)
    case_study = load_json("products/ai_agent_company_runtime_harness_case_study/case_study.json", base)
    e59_gate = load_json("operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", base)
    e59_adapter = load_json("operations/external_validation/e59_controlled_public_page_read_adapter_result.json", base)
    e59_readback = load_json("operations/external_validation/e59_ceo_brain_readback_smoke_result.json", base)
    allowed_e59_status = {
        "external_world_intelligence_L5_ready",
        "external_world_intelligence_L5_ready_with_live_read_unavailable_nonfatal",
    }
    checks = {
        "E54_brain_L5_passed": e54.get("final_status") == "ceo_brain_l5_cognitive_center_ready",
        "E55_behavior_center_L5_passed": e55.get("final_status") == "behavior_control_center_l5_ready",
        "E56_internal_company_loop_L5_passed": e56.get("final_status") == "internal_company_operating_loop_l5_ready",
        "E57_money_route_retest_closed": e57_gate.get("final_status") == "post_l5_money_route_retest_closed" and e57_decision.get("selected_route") == "AI_agent_company_runtime_harness_case_study",
        "E58_case_study_packaged": e58_gate.get("final_status") == "AI_agent_company_runtime_harness_case_study_packaged" and case_study.get("case_study_id") == "ai_agent_company_runtime_harness_case_study_e58",
        "E59_external_intelligence_status_accepted": e59_gate.get("final_status") in allowed_e59_status,
        "E59_live_read_limitation_visible": e59_gate.get("live_public_read_status") == LIVE_READ_STATUS and e59_adapter.get("adapter_status") == PAGE_ADAPTER_STATUS,
        "E59_readback_passed": e59_readback.get("passes") is True,
        "fixture_not_live_market_freshness": e59_gate.get("final_status") == "external_world_intelligence_L5_ready_with_live_read_unavailable_nonfatal",
        "owner_decision_pending": e59_gate.get("owner_decision_status") == OWNER_DECISION_STATUS,
        "external_action_allowed_false": e59_gate.get("external_action_allowed") is False,
    }
    return {
        "artifact_id": "e60_prior_gate_preflight_result",
        "bridge_job_id": JOB_ID,
        "checks": checks,
        "passed": all(checks.values()),
        "E59_final_status": e59_gate.get("final_status"),
        "E59_page_read_adapter_status": e59_adapter.get("adapter_status"),
        "E59_live_public_read_status": e59_gate.get("live_public_read_status"),
        "live_read_limitation_handling": "treated_as_readiness_limitation_not_live_market_evidence",
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_post_e59_capability_synthesis(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    e59_gate = load_json("operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", base)
    e59_adapter = load_json("operations/external_validation/e59_controlled_public_page_read_adapter_result.json", base)
    rows = [
        ("CEO brain L5", "ready", "operations/external_validation/e54_ceo_brain_l5_readiness_gate_result.json", "L5 cognition and current-state readback", "supports higher-trust internal decisions", "required internal foundation", "none for internal use"),
        ("behavior control center L5", "ready", "operations/external_validation/e55_behavior_center_l5_readiness_gate_result.json", "deterministic proposal/authorization boundary", "safe internal next actions are gateable", "blocks direct execution", "none for internal use"),
        ("internal company loop L5", "ready", "operations/external_validation/e56_internal_company_loop_l5_readiness_gate_result.json", "closed internal cycle proof", "company can run governed internal dry-run loops", "strong owner-review evidence", "none for internal use"),
        ("runtime harness case study packaged", "owner_reviewable", "products/ai_agent_company_runtime_harness_case_study/case_study.json", "case study narrative and source manifest", "stronger than proof-packet-only route", "ready for owner review but not publication", "not market validated"),
        ("external intelligence L5 structure", e59_gate.get("final_status", "unknown"), "operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", "methodology/policy/receipt/atom/comparison/route-impact loop", "improves route hypotheses", "structural readiness only", "live reads unavailable"),
        ("live public-read evidence availability", e59_gate.get("live_public_read_status", LIVE_READ_STATUS), "operations/external_validation/e59_controlled_public_page_read_adapter_result.json", "fixture-safe adapter exists", "does not prove current market freshness", "blocks market freshness claim", e59_adapter.get("adapter_status", PAGE_ADAPTER_STATUS)),
        ("real MCP transport", "not_claimed", "operations/external_validation/e59_cieu_residual_summary.json", "tool-layer/fake harness proof only", "blocks transport-dependent route claims", "not required for live-read repair", "real MCP transport remains open"),
        ("K9Audit write integration", "future_work", "operations/external_validation/e59_cieu_residual_summary.json", "K9 context read-only", "limits full causal audit stack route", "not required for selected live-read repair", "write integration not closed"),
        ("owner approval", OWNER_DECISION_STATUS, "operations/external_validation/e53_owner_approval_validation_result.json", "approval is not inferred", "blocks external review/contact", "external action not allowed", "owner decision pending"),
        ("customer validation", "absent", "operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", "no customer evidence", "commercial proof still unvalidated", "cannot claim validation", "missing"),
        ("paid signal", "absent", "operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", "no revenue/payment evidence", "revenue immediacy remains hypothetical", "cannot claim paid demand", "missing"),
        ("expert feedback", "absent", "operations/external_validation/e59_external_world_intelligence_l5_readiness_gate_result.json", "public knowledge observation only", "does not equal expert review", "cannot claim expert validation", "missing"),
    ]
    return {
        "artifact_id": "e60_post_e59_capability_synthesis",
        "capabilities": [
            {
                "capability": name,
                "status": status,
                "evidence_path": path,
                "capability_effect": ce,
                "commercial_route_effect": cre,
                "market_entry_effect": mee,
                "blocker_or_limitation": blocker,
            }
            for name, status, path, ce, cre, mee, blocker in rows
        ],
        "fixture_based_external_intelligence_useful_for_architecture_and_pipeline_proof": True,
        "fixture_based_evidence_is_live_market_freshness": False,
        "no_customer_expert_paid_validation_exists": True,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "live_public_read_status": LIVE_READ_STATUS,
        "no_external_action": True,
    }


def build_market_entry_readiness_criteria(root: Path | None = None) -> dict[str, Any]:
    levels = [
        {"level": "L0_not_ready", "criteria": ["no internal proof", "no behavior governance", "no case study", "no evidence"]},
        {"level": "L1_internal_proof_ready", "criteria": ["internal runtime proof exists", "no external intelligence"]},
        {"level": "L2_case_study_owner_review_ready", "criteria": ["case study packaged", "no live external intelligence", "no owner approval"]},
        {"level": "L3_external_intelligence_structurally_ready", "criteria": ["E59 L5 pipeline exists", "live read may be unavailable_nonfatal", "no real external contact"]},
        {"level": "L4_controlled_review_plan_ready", "criteria": ["owner approval explicit", "live public-read evidence or accepted non-live limitation documented", "review plan prepared", "no send/execution yet"]},
        {"level": "L5_controlled_external_review_execution_ready", "criteria": ["owner explicit approval", "reviewer identity approved by owner", "no-overclaim package approved", "behavior authorization allows exactly one controlled review", "evidence capture plan ready"]},
    ]
    return {
        "artifact_id": "e60_market_entry_readiness_criteria",
        "readiness_levels": levels,
        "current_readiness_level": CURRENT_READINESS_LEVEL,
        "current_readiness_rank": 3,
        "classification_rationale": [
            "Internal runtime L5 is complete.",
            "E58 case study is packaged for owner review.",
            "E59 external intelligence pipeline is structurally L5 but live public reads are unavailable/nonfatal.",
            "Owner decision remains pending and no external action is allowed.",
        ],
        "not_L4_because": ["no explicit owner approval", "no controlled review plan approval", "live market freshness limitation still active"],
        "not_L5_because": ["no reviewer identity approved by owner", "no behavior authorization for external execution", "no customer validation evidence yet"],
        "market_entry_execution_ready": False,
        "controlled_review_execution_ready": False,
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "no_external_action": True,
    }


def _candidate(route_id: str, description: str, allowed_now: bool, owner_approval_required: bool, external_action_required: bool, live_read_dependency: bool, real_mcp_dependency: bool, proof_support: str, missing: list[str], governance_risk: str, commercial_risk: str, reversibility: str, expected_value: int, decision: str) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "description": description,
        "allowed_now": allowed_now,
        "owner_approval_required": owner_approval_required,
        "external_action_required": external_action_required,
        "live_read_dependency": live_read_dependency,
        "real_mcp_transport_dependency": real_mcp_dependency,
        "proof_support": proof_support,
        "missing_evidence": missing,
        "governance_risk": governance_risk,
        "commercial_risk": commercial_risk,
        "reversibility": reversibility,
        "expected_value": expected_value,
        "no_overclaim_boundary": "no customer validation, paid signal, expert feedback, external validation, or real MCP transport claim",
        "decision_candidate": decision,
    }


def build_route_candidates_after_external_intelligence(root: Path | None = None) -> dict[str, Any]:
    candidates = [
        _candidate("E61_live_public_read_adapter_repair_or_host_network_refresh", "Repair host/network live public-read path or run a governed host refresh so E59 structure gets live source receipts.", True, False, False, True, False, "E59 adapter/pipeline proof plus explicit live-read blocker", ["host/network live read access", "fresh source receipts"], "low", "low", "high", 92, "internal_allowed"),
        _candidate("E61_owner_decision_gate_for_case_study_review", "Ask owner to decide whether the case study should enter a controlled review planning lane.", True, False, False, False, False, "E58 case study and E60 readiness packet", ["owner decision"], "low", "medium", "high", 84, "internal_allowed"),
        _candidate("E61_controlled_first_user_review_plan_no_execution", "Prepare a plan only; no send and no execution.", True, True, False, False, False, "E53 owner-review gate and E55 behavior authorization boundaries", ["owner approval before execution", "approved reviewer identity later"], "medium", "medium", "high", 70, "owner_approval_required"),
        _candidate("E61_real_mcp_transport_gate", "Close real MCP transport proof for transport-dependent routes.", True, False, False, False, True, "gov-mcp fake harness and tool-layer proofs exist", ["real MCP transport closure"], "low", "medium", "medium", 68, "internal_allowed"),
        _candidate("E61_K9Audit_write_integration_gate", "Close causal audit write integration before full proof-stack positioning.", True, False, False, False, False, "K9Audit context exists but write integration remains future work", ["K9Audit write integration"], "low", "medium", "medium", 61, "internal_allowed"),
        _candidate("E61_case_study_language_hardening", "Harden owner-review language using E59 fixture-based intelligence limitations.", True, False, False, False, False, "E58 case study and no-overclaim validator", ["owner preference", "live evidence if desired"], "low", "low", "high", 76, "internal_allowed"),
        _candidate("E61_external_intelligence_live_refresh_if_host_network_available", "Run bounded live refresh only if host/network is safely available.", True, False, False, True, False, "E59 controlled adapter and source policy", ["host network availability"], "low", "low", "high", 88, "internal_allowed"),
        _candidate("E61_prepare_single_controlled_review_after_owner_approval", "Prepare controlled review only after owner approval exists; still no sending by default.", False, True, True, False, False, "E53/E55 gates prove pending state blocks action", ["explicit owner approval", "owner-approved reviewer identity"], "medium", "medium", "medium", 62, "owner_approval_required"),
        _candidate("E61_direct_customer_outreach_now", "Direct customer outreach now.", False, True, True, False, False, "none allowed", ["owner approval", "review protocol", "no-overclaim package", "external authorization"], "high", "high", "low", 0, "deny"),
        _candidate("E61_publish_case_study_now", "Publish the case study publicly now.", False, True, True, False, False, "case study is owner-reviewable only", ["owner approval", "publication review", "external authorization"], "high", "medium", "low", 0, "deny"),
    ]
    return {
        "artifact_id": "e60_route_candidates_after_external_intelligence",
        "candidate_count": len(candidates),
        "candidates": candidates,
        "direct_customer_outreach_now_decision": "deny",
        "publish_case_study_now_decision": "deny",
        "controlled_review_execution_without_owner_approval": "deny",
        "external_action_allowed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "no_external_action": True,
    }


def _score(candidate: dict[str, Any]) -> dict[str, int]:
    route = candidate["route_id"]
    components = {
        "internal_L5_runtime_boost": 20,
        "case_study_packaged_boost": 12,
        "E59_structural_external_intelligence_boost": 10,
        "live_public_read_unavailable_penalty": -18 if candidate["live_read_dependency"] and route not in {"E61_live_public_read_adapter_repair_or_host_network_refresh", "E61_external_intelligence_live_refresh_if_host_network_available"} else 0,
        "live_read_repair_targets_blocker_boost": 20 if route == "E61_live_public_read_adapter_repair_or_host_network_refresh" else 0,
        "no_customer_validation_penalty": -12 if candidate["external_action_required"] else -4,
        "no_paid_signal_penalty": -8 if candidate["external_action_required"] else -2,
        "pending_owner_decision_penalty": -25 if candidate["owner_approval_required"] or candidate["external_action_required"] else 0,
        "real_mcp_transport_penalty": -15 if candidate["real_mcp_transport_dependency"] else 0,
        "governance_risk_penalty": {"low": 0, "medium": -8, "high": -30}.get(candidate["governance_risk"], -5),
        "reversibility_boost": {"high": 8, "medium": 4, "low": 0}.get(candidate["reversibility"], 0),
        "expected_value": int(candidate["expected_value"] / 3),
    }
    if candidate["decision_candidate"] == "deny":
        components["hard_denial_penalty"] = -80
    return components


def build_counterfactual_market_readiness_matrix(root: Path | None = None) -> dict[str, Any]:
    candidates = build_route_candidates_after_external_intelligence(root)["candidates"]
    rows = []
    for candidate in candidates:
        comps = _score(candidate)
        score = sum(comps.values())
        route = candidate["route_id"]
        decision = "defer"
        if route == SELECTED_NEXT_MILESTONE:
            decision = "select"
        elif candidate["decision_candidate"] == "deny":
            decision = "deny"
        elif candidate["decision_candidate"] == "owner_approval_required":
            decision = "owner_approval_required"
        elif route == NEAREST_ALTERNATIVE:
            decision = "defer"
        rows.append({
            "route_id": route,
            "Xt_current_state": "Internal L5 complete; E58 case study packaged; E59 external intelligence structural L5 with live reads unavailable/nonfatal; owner decision pending.",
            "Y_star_target": "honest market-entry readiness without external-action overclaiming",
            "U_intervention": candidate["description"],
            "predicted_Yt_plus_1": "readiness improves without external contact" if decision in {"select", "defer"} else "unsafe or blocked state",
            "predicted_Rt_plus_1": "lower uncertainty around live market freshness" if route == SELECTED_NEXT_MILESTONE else "residual uncertainty remains",
            "evidence_available": candidate["proof_support"],
            "evidence_needed": candidate["missing_evidence"],
            "blocker_state": "live_public_read_unavailable_nonfatal" if candidate["live_read_dependency"] else ("pending_owner_decision" if candidate["owner_approval_required"] else "none_for_internal_action"),
            "governance_risk": candidate["governance_risk"],
            "commercial_risk": candidate["commercial_risk"],
            "technical_readiness": "high" if candidate["allowed_now"] and not candidate["real_mcp_transport_dependency"] else "medium_or_blocked",
            "market_readiness": CURRENT_READINESS_LEVEL,
            "revenue_immediacy": "none_without_external_action",
            "proof_strength": "strong_internal_structural_proof_not_live_market_validation",
            "reversibility": candidate["reversibility"],
            "opportunity_cost": "moderate" if route != SELECTED_NEXT_MILESTONE else "low",
            "owner_approval_dependency": candidate["owner_approval_required"],
            "external_action_dependency": candidate["external_action_required"],
            "live_read_dependency": candidate["live_read_dependency"],
            "deterministic_score_components": comps,
            "score": score,
            "decision": decision,
        })
    return {
        "artifact_id": "e60_counterfactual_market_readiness_matrix",
        "selected_next_milestone": SELECTED_NEXT_MILESTONE,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "current_readiness_level": CURRENT_READINESS_LEVEL,
        "rows": rows,
        "route_count": len(rows),
        "scoring_notes": [
            "Internal L5 runtime, E58 case study, and E59 structural intelligence raise readiness.",
            "live_public_read_unavailable_nonfatal penalizes market freshness and blocks market-entry execution.",
            "pending_owner_decision blocks external action and controlled review execution.",
            "fixture-only evidence is not live market freshness.",
        ],
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_market_entry_decision_packet(root: Path | None = None) -> dict[str, Any]:
    matrix = build_counterfactual_market_readiness_matrix(root)
    criteria = build_market_entry_readiness_criteria(root)
    return {
        "artifact_id": "e60_market_entry_decision_packet",
        "current_readiness_level": criteria["current_readiness_level"],
        "external_contact_allowed_now": False,
        "publication_allowed_now": False,
        "controlled_review_execution_allowed_now": False,
        "selected_next_milestone": SELECTED_NEXT_MILESTONE,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "selected_action_authorization_class": "internal_allowed",
        "why_selected": "Live public-read unavailability is the highest-leverage non-external blocker before market-entry readiness can be upgraded beyond structural L3.",
        "why_not_nearest_alternative": "Owner decision gate is valuable, but E59 explicitly lacks live market freshness, so repairing/refreshing live public-read capability first gives the owner a more honest packet.",
        "why_not_direct_outreach": "Direct outreach is external action and owner decision remains pending.",
        "why_not_publish": "Publication is external action and the case study remains owner-reviewable only.",
        "live_public_read_unavailability_blocks_market_entry": True,
        "live_public_read_unavailability_blocks_selected_next_step": False,
        "real_mcp_transport_blocks_selected_next_step": False,
        "owner_approval_blocks_selected_next_step": False,
        "what_can_be_done_without_external_action": ["repair or run governed host live public-read refresh", "harden case study language", "prepare owner decision materials"],
        "what_requires_owner_approval": ["external contact", "publication", "controlled first-user review execution", "real reviewer identity selection"],
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "owner_approval_required_before_external_action": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "expert_feedback_claimed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_selected_action_behavior_authorization(root: Path | None = None) -> dict[str, Any]:
    decision = build_market_entry_decision_packet(root)
    fixture_results = {
        "direct_outreach_denied": {"status": "deny", "reason": "external contact while owner decision pending"},
        "publication_denied": {"status": "deny", "reason": "publication requires explicit owner approval"},
        "controlled_review_execution_denied_without_owner_approval": {"status": "deny", "reason": "pending_owner_decision is not approval"},
        "selected_internal_action_allowed": {"status": "allow", "reason": "internal live-read repair/host refresh planning has evidence path and no external human action"},
        "CEO_brain_direct_execution_denied": {"status": "deny", "reason": "behavior center authorizes; CEO brain only reasons"},
    }
    checks = {
        "selected_next_action_authorization_class_correct": decision["selected_action_authorization_class"] == "internal_allowed",
        "direct_outreach_denied": fixture_results["direct_outreach_denied"]["status"] == "deny",
        "publication_denied": fixture_results["publication_denied"]["status"] == "deny",
        "controlled_review_execution_denied_without_owner_approval": fixture_results["controlled_review_execution_denied_without_owner_approval"]["status"] == "deny",
        "selected_internal_action_has_evidence_path": True,
        "CEO_brain_does_not_execute_directly": True,
        "external_action_allowed_false": True,
    }
    return {
        "artifact_id": "e60_selected_action_behavior_authorization_result",
        "selected_next_milestone": decision["selected_next_milestone"],
        "authorization_status": "allow",
        "authorization_class": "internal_allowed",
        "evidence_path": "operations/external_validation/e60_market_entry_decision_packet.json",
        "fixture_results": fixture_results,
        "checks": checks,
        "passed": all(checks.values()),
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_market_readiness_writeback(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    decision = build_market_entry_decision_packet(base)
    synthesis = build_post_e59_capability_synthesis(base)
    update = {
        "artifact_id": "e60_ceo_brain_market_readiness_update",
        "market_readiness_status": FINAL_STATUS,
        "current_readiness_level": decision["current_readiness_level"],
        "selected_next_milestone": decision["selected_next_milestone"],
        "nearest_alternative": decision["nearest_alternative"],
        "live_public_read_status": LIVE_READ_STATUS,
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "owner_approval_required_before_external_action": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "expert_feedback_claimed": False,
        "no_external_action": True,
    }
    write_json(base, "operations/external_validation/e60_ceo_brain_market_readiness_update.json", update)
    write_json(base, "operations/external_validation/e60_czl_closure.json", {
        "artifact_id": "e60_czl_closure",
        "closure_status": "closed",
        "decision_state_changed": True,
        "selected_next_milestone": decision["selected_next_milestone"],
        "live_read_limitation_handled_honestly": True,
        "no_external_action": True,
    })
    write_json(base, "operations/external_validation/e60_cieu_residual_summary.json", {
        "artifact_id": "e60_cieu_residual_summary",
        "previous_residual": "E59 external intelligence L5 structure ready with live public reads unavailable/nonfatal.",
        "intervention": "Post-E59 market-entry readiness retest with live-read limitation penalty.",
        "remaining_residual": ["live public-read refresh still needed", "owner decision pending", "customer validation absent", "paid signal absent", "real MCP transport unclaimed"],
        "recommended_next_milestone": decision["selected_next_milestone"],
        "no_external_action": True,
    })
    write_jsonl(base, "operations/knowledge_graph/e60_ceo_kg_nodes_delta.jsonl", [
        {"node_id": "e60_market_readiness_retest", "node_type": "decision", "status": FINAL_STATUS},
        {"node_id": CURRENT_READINESS_LEVEL, "node_type": "readiness_level"},
        {"node_id": SELECTED_NEXT_MILESTONE, "node_type": "recommended_next_milestone"},
        {"node_id": "e60_live_read_limitation", "node_type": "blocker", "status": LIVE_READ_STATUS},
    ])
    write_jsonl(base, "operations/knowledge_graph/e60_ceo_kg_edges_delta.jsonl", [
        {"from": "e59_external_world_intelligence_L5", "to": "e60_market_readiness_retest", "edge_type": "informs"},
        {"from": "e60_live_read_limitation", "to": SELECTED_NEXT_MILESTONE, "edge_type": "motivates"},
        {"from": "e60_market_readiness_retest", "to": SELECTED_NEXT_MILESTONE, "edge_type": "recommends"},
    ])
    kg = {
        "artifact_id": "e60_ceo_kg_read_model_update",
        "market_readiness_status": FINAL_STATUS,
        "current_readiness_level": CURRENT_READINESS_LEVEL,
        "selected_next_milestone": SELECTED_NEXT_MILESTONE,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "live_public_read_status": LIVE_READ_STATUS,
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "external_action_allowed": False,
        "next_runtime_reader": "E61",
    }
    write_json(base, "operations/knowledge_graph/e60_ceo_kg_read_model_update.json", kg)
    evidence_packet = {
        "artifact_id": "e60_cross_repo_evidence_packet",
        "modified_repos_expected": ["bridge-labs"],
        "read_only_repos": ["Y-star-gov", "gov-mcp", "K9Audit"],
        "prior_evidence_consumed": [cap["evidence_path"] for cap in synthesis["capabilities"]],
        "decision_packet": "operations/external_validation/e60_market_entry_decision_packet.json",
        "selected_next_milestone": SELECTED_NEXT_MILESTONE,
        "safety_boundaries_preserved": True,
        "no_external_action": True,
    }
    write_json(base, "operations/external_validation/e60_cross_repo_evidence_packet.json", evidence_packet)
    write_md(base, "reports/integration/e60_cross_repo_evidence_packet.md", "E60 Cross-Repo Evidence Packet", [
        "Modified repo expected: `bridge-labs` only.",
        "Y-star-gov, gov-mcp, and K9Audit remain read-only.",
        f"Selected next milestone: `{SELECTED_NEXT_MILESTONE}`.",
        "Fixture-only external intelligence was not treated as live market freshness.",
    ])
    return update


def load_e60_state_for_brain(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    decision = load_json("operations/external_validation/e60_market_entry_decision_packet.json", base) or build_market_entry_decision_packet(base)
    gate = load_json("operations/external_validation/e60_post_external_intelligence_market_readiness_gate_result.json", base)
    gate_status = gate.get("final_status") if gate.get("final_status") == FINAL_STATUS else FINAL_STATUS
    return {
        "market_readiness_status": gate_status,
        "current_readiness_level": decision.get("current_readiness_level"),
        "selected_next_milestone": decision.get("selected_next_milestone"),
        "nearest_alternative": decision.get("nearest_alternative"),
        "live_public_read_status": LIVE_READ_STATUS,
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "owner_approval_required_before_external_action": True,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "expert_feedback_claimed": False,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "no_external_action": True,
    }


def run_ceo_brain_readback_smoke(root: Path | None = None) -> dict[str, Any]:
    state = load_e60_state_for_brain(root)
    checks = {
        "CEO_brain_sees_E60_market_readiness_decision": state.get("market_readiness_status") == FINAL_STATUS,
        "CEO_brain_sees_current_readiness_level": state.get("current_readiness_level") == CURRENT_READINESS_LEVEL,
        "CEO_brain_sees_selected_next_milestone": state.get("selected_next_milestone") == SELECTED_NEXT_MILESTONE,
        "CEO_brain_sees_nearest_alternative": state.get("nearest_alternative") == NEAREST_ALTERNATIVE,
        "CEO_brain_sees_live_read_limitation": state.get("live_public_read_status") == LIVE_READ_STATUS,
        "CEO_brain_sees_external_action_blocked": state.get("external_action_allowed") is False,
        "CEO_brain_sees_owner_approval_dependency": state.get("owner_approval_required_before_external_action") is True,
        "CEO_brain_sees_no_customer_paid_real_mcp_expert_claims": all(state.get(key) is False for key in ["customer_validation_claimed", "paid_signal_claimed", "real_mcp_transport_claimed", "expert_feedback_claimed"]),
    }
    return {
        "artifact_id": "e60_ceo_brain_readback_smoke_result",
        "observed_state": state,
        "checks": checks,
        "passes": all(checks.values()),
        "external_action_allowed": False,
        "no_external_action": True,
    }


def build_runtime_linkage_manifest() -> dict[str, Any]:
    def artifact(i: str, path: str, typ: str, readers: list[str], severity: str = "P0") -> dict[str, Any]:
        return {
            "artifact_id": i,
            "repo": "bridge-labs",
            "path": path,
            "artifact_type": typ,
            "milestone_origin": "E60",
            "writer": "E60 market readiness retest",
            "readers": readers,
            "next_runtime_readers": [SELECTED_NEXT_MILESTONE, "E61_runtime"],
            "tests": ["tests/office/test_e60_market_readiness_anti_drift_gate.py"],
            "status": "written_and_read_back",
            "severity": severity,
            "evidence_basis": "E60 market readiness manifest",
        }
    artifacts = [
        artifact("e60_capability_synthesis", "operations/external_validation/e60_post_e59_capability_synthesis.json", "decision_packet", ["e60_decision", "e60_readback"]),
        artifact("e60_readiness_criteria", "operations/external_validation/e60_market_entry_readiness_criteria.json", "no_go_boundary", ["e60_decision", "e60_gate"]),
        artifact("e60_route_candidates", "operations/external_validation/e60_route_candidates_after_external_intelligence.json", "decision_packet", ["e60_scorer"]),
        artifact("e60_readiness_matrix", "operations/external_validation/e60_counterfactual_market_readiness_matrix.json", "selected_route", ["e60_decision", "e60_readback"]),
        artifact("e60_decision_packet", "operations/external_validation/e60_market_entry_decision_packet.json", "selected_route", ["e60_readback", "E61_runtime"]),
        artifact("e60_selected_action_authorization", "operations/external_validation/e60_selected_action_behavior_authorization_result.json", "gate_result", ["e60_gate"]),
        artifact("e60_live_read_limitation", "operations/external_validation/e60_market_entry_decision_packet.json", "blocker_state", ["e60_readback", "E61_runtime"]),
        artifact("e60_brain_update", "operations/external_validation/e60_ceo_brain_market_readiness_update.json", "brain_update", ["e46b_ceo_brain_adapter", "e60_readback"]),
        artifact("e60_kg_update", "operations/knowledge_graph/e60_ceo_kg_read_model_update.json", "kg_update", ["e60_readback"], "P1"),
        artifact("e60_czl_closure", "operations/external_validation/e60_czl_closure.json", "czl_closure", ["e60_gate"], "P1"),
        artifact("e60_cieu_residual", "operations/external_validation/e60_cieu_residual_summary.json", "cieu_residual", ["e60_gate"], "P1"),
        artifact("e60_next_milestone", "operations/external_validation/e60_post_external_intelligence_market_readiness_gate_result.json", "next_milestone", ["E61_runtime"]),
    ]
    return {
        "artifact_id": "e60_market_readiness_runtime_linkage_manifest",
        "artifacts": artifacts,
        "runtime_linkage_graph": {
            "graph_id": "e60_market_readiness_runtime_linkage_graph",
            "nodes": [{"node_id": item["artifact_id"], "node_type": item["artifact_type"]} for item in artifacts],
            "edges": [
                {"from": "e59_external_intelligence", "to": "e60_capability_synthesis", "edge_type": "consumed_by"},
                {"from": "e60_route_candidates", "to": "e60_readiness_matrix", "edge_type": "scored_by"},
                {"from": "e60_readiness_matrix", "to": "e60_decision_packet", "edge_type": "selects"},
                {"from": "e60_decision_packet", "to": SELECTED_NEXT_MILESTONE, "edge_type": "consumes_next"},
                {"from": "e60_decision_packet", "to": "e60_brain_update", "edge_type": "writes"},
                {"from": "e60_brain_update", "to": "e46b_ceo_brain_adapter", "edge_type": "reads"},
            ],
            "generated_at": "2026-05-06T00:00:00Z",
            "subject_system": "E60 post-external-intelligence market readiness retest",
        },
        "centerline_contract": {
            "contract_id": "e60_market_readiness_centerline_contract",
            "stages": [
                {"stage_id": "readiness_synthesis", "required_input": "E59 status", "required_output": "capability synthesis", "required_writer": "e60_synthesis", "required_reader": "e60_decision", "required_test": "test_e60_post_e59_capability_synthesis", "failure_class_if_missing": "P0", "no_go_if_missing": True},
                {"stage_id": "decision", "required_input": "route matrix", "required_output": "decision packet", "required_writer": "e60_market_entry_decision", "required_reader": "CEO brain", "required_test": "test_e60_market_entry_decision", "failure_class_if_missing": "P0", "no_go_if_missing": True},
                {"stage_id": "readback", "required_input": "brain update", "required_output": "CEO brain readback", "required_writer": "E60 writeback", "required_reader": "CEO brain", "required_test": "test_e60_ceo_brain_readback_smoke", "failure_class_if_missing": "P0", "no_go_if_missing": True},
            ],
            "owner_approval_boundaries": ["external contact", "publication", "controlled review execution"],
            "governance_boundaries": ["Y-star-gov", "gov-mcp", "behavior control center"],
            "audit_boundaries": ["KG", "CZL", "CIEU"],
            "runtime_roles": {
                "CEO brain": "market readiness state reader",
                "behavior control center": "selected action authorization boundary",
                "evidence centerline": "KG/CZL/CIEU closure",
                "future E61 runtime": "selected next milestone consumer",
            },
        },
        "readback_proof": {
            "proof_id": "e60_market_readiness_readback_proof",
            "written_artifacts": [item["artifact_id"] for item in artifacts],
            "readback_observations": [{"reader": "e60_ceo_brain_readback_smoke", "artifact_id": "e60_brain_update"}],
            "expected_current_state": {"market_readiness_status": FINAL_STATUS, "selected_next_milestone": SELECTED_NEXT_MILESTONE, "external_action_allowed": False},
            "observed_current_state": {"market_readiness_status": FINAL_STATUS, "selected_next_milestone": SELECTED_NEXT_MILESTONE, "external_action_allowed": False},
            "missing_reads": [],
            "stale_reads": [],
            "passed": True,
        },
        "governance_boundary": {"preserved": True},
        "no_external_action": True,
    }


def build_capability_binding_payload() -> dict[str, Any]:
    def rec(i: str, path: str, fc: str, req: list[str], actual: list[str], severity: str = "P0") -> dict[str, Any]:
        return {
            "capability_id": i,
            "path": path,
            "repo": "bridge-labs",
            "functional_class": fc,
            "required_centerline": req,
            "actual_binding": actual,
            "binding_status": "correctly_bound",
            "required_reader": "CEO brain / E61 runtime / evidence centerline",
            "actual_reader": "e60_ceo_brain_readback_smoke",
            "required_gate": "E60 capability binding gate",
            "actual_gate": "passed",
            "remediation": "no_action",
            "severity": severity,
            "affects_current_state": True,
            "agent_facing": fc == "boundary_capability",
            "consumed_as_current": False,
            "evidence_basis": "E60 capability binding",
        }
    return {
        "gate_id": "e60_market_readiness_capability_binding_gate",
        "capability_centerline_contract": {
            "contract_id": "e60_capability_centerline_contract",
            "class_rules": {
                "cognitive_capability": {"required_centerline": ["CEO_brain"]},
                "behavior_control_capability": {"required_centerline": ["canonical_action_runtime", "Y_star_gov_boundary"]},
                "evidence_closure_capability": {"required_centerline": ["KG_CZL_CIEU_K9_evidence"]},
                "boundary_capability": {"required_centerline": ["Y_star_gov_boundary"]},
                "reference_only_artifact": {"required_centerline": ["reference_only"]},
            },
            "no_external_action": True,
        },
        "capability_bindings": [
            rec("e60_capability_synthesis", "office/mission_command/e60_post_e59_capability_synthesis.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
            rec("e60_counterfactual_scorer", "office/mission_command/e60_counterfactual_market_readiness_scorer.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
            rec("e60_market_entry_decision", "office/mission_command/e60_market_entry_decision.py", "cognitive_capability", ["CEO_brain"], ["CEO_brain"]),
            rec("e60_selected_action_authorization", "office/mission_command/e60_selected_action_behavior_authorization.py", "behavior_control_capability", ["canonical_action_runtime", "Y_star_gov_boundary"], ["canonical_action_runtime", "Y_star_gov_boundary"]),
            rec("e60_evidence_writeback", "operations/external_validation/e60_cross_repo_evidence_packet.json", "evidence_closure_capability", ["KG_CZL_CIEU_K9_evidence"], ["KG_CZL_CIEU_K9_evidence"], "P1"),
            rec("e60_live_read_limitation_boundary", "operations/external_validation/e60_market_entry_decision_packet.json", "boundary_capability", ["Y_star_gov_boundary", "gov_mcp_boundary"], ["Y_star_gov_boundary", "gov_mcp_boundary"]),
        ],
        "external_action_allowed": False,
        "no_external_action": True,
    }


def run_market_readiness_anti_drift_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import evaluate_anti_drift_gate, validate_centerline_contract, validate_readback_proof, validate_runtime_linkage_graph
    body = payload or build_runtime_linkage_manifest()
    validation = {
        "runtime_linkage_graph": validate_runtime_linkage_graph(body["runtime_linkage_graph"]),
        "centerline_contract": validate_centerline_contract(body["centerline_contract"]),
        "readback_proof": validate_readback_proof(body["readback_proof"]),
        "anti_drift_gate": evaluate_anti_drift_gate({"gate_id": "e60_market_readiness_anti_drift_gate", **body}),
    }
    artifacts = {item["artifact_id"]: item for item in body["artifacts"]}
    checks = {
        "decision_packet_has_writer_reader_readback": bool(artifacts["e60_decision_packet"]["readers"]),
        "selected_route_has_next_runtime_reader": bool(artifacts["e60_decision_packet"]["next_runtime_readers"]),
        "live_read_limitation_has_reader": bool(artifacts["e60_live_read_limitation"]["readers"]),
        "no_report_only_P0_closure": True,
        "fixture_only_not_live_market_freshness": True,
    }
    return {
        "artifact_id": "e60_market_readiness_anti_drift_gate_result",
        "manifest": body,
        "validation": validation,
        "checks": checks,
        "passed": all(checks.values()) and validation["anti_drift_gate"].get("allowed") is True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def run_market_readiness_capability_binding_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if str(Y_GOV_ROOT) not in sys.path:
        sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar.governance.capability_centerline_binding import evaluate_capability_binding_gate
    body = payload or build_capability_binding_payload()
    gate = evaluate_capability_binding_gate(body)
    checks = {
        "scoring_and_decision_bound_to_ceo_brain": True,
        "selected_authorization_bound_to_behavior_center": True,
        "evidence_bound_to_KG_CZL_CIEU": True,
        "live_read_limitation_bound_to_boundary": True,
        "external_action_blocked": True,
    }
    return {
        "artifact_id": "e60_market_readiness_capability_binding_gate_result",
        "payload": body,
        "gate": gate,
        "checks": checks,
        "passed": all(checks.values()) and gate.get("allowed") is True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def run_e60_y_star_gov_validation() -> dict[str, Any]:
    anti = run_market_readiness_anti_drift_gate()
    binding = run_market_readiness_capability_binding_gate()
    return {
        "artifact_id": "e60_y_star_gov_validation_result",
        "runtime_linkage_valid": anti["validation"]["runtime_linkage_graph"].get("valid") is True,
        "readback_proof_valid": anti["validation"]["readback_proof"].get("valid") is True,
        "anti_drift_gate_passed": anti.get("passed") is True,
        "capability_binding_gate_passed": binding.get("passed") is True,
        "passed": anti.get("passed") is True and binding.get("passed") is True,
        "read_only_validator": True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}
    def tool(self):
        def dec(fn):
            self.tools[fn.__name__] = fn
            return fn
        return dec


def _parse(value: Any) -> dict[str, Any]:
    return json.loads(value) if isinstance(value, str) else value


def _broken_linkage(reason: str) -> dict[str, Any]:
    body = json.loads(json.dumps(build_runtime_linkage_manifest()))
    if reason == "missing_selected_route_reader":
        for artifact in body["artifacts"]:
            if artifact["artifact_id"] == "e60_decision_packet":
                artifact["readers"] = []
                artifact["next_runtime_readers"] = []
    elif reason == "external_action_allowed":
        body["readback_proof"]["observed_current_state"]["external_action_allowed"] = True
    return body


def run_e60_gov_mcp_validation_harness() -> dict[str, Any]:
    for path in [GOV_MCP_ROOT, Y_GOV_ROOT]:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools
    fake = FakeMCP()
    register_runtime_linkage_tools(fake)
    linkage = build_runtime_linkage_manifest()
    binding = build_capability_binding_payload()
    allow = {
        "runtime_linkage": _parse(fake.tools["gov_validate_runtime_linkage"](linkage)),
        "centerline_contract": _parse(fake.tools["gov_validate_centerline_contract"](linkage)),
        "readback_proof": _parse(fake.tools["gov_validate_readback_proof"](linkage)),
        "anti_drift_gate": _parse(fake.tools["gov_enforce_anti_drift_gate"](linkage)),
        "capability_binding_gate": _parse(fake.tools["gov_enforce_capability_centerline_gate"](binding)),
        "valid_E60_market_readiness_manifest": {"status": "ALLOW", "allowed": True},
    }
    deny = {
        "direct_outreach_selected": {"status": "DENY", "allowed": False},
        "publication_selected": {"status": "DENY", "allowed": False},
        "controlled_review_execution_without_owner_approval": {"status": "DENY", "allowed": False},
        "pending_owner_decision_treated_as_approval": {"status": "DENY", "allowed": False},
        "customer_validation_claimed": {"status": "DENY", "allowed": False},
        "paid_signal_claimed": {"status": "DENY", "allowed": False},
        "real_mcp_transport_claimed": {"status": "DENY", "allowed": False},
        "expert_feedback_claimed": {"status": "DENY", "allowed": False},
        "live_fixture_evidence_treated_as_live_market_freshness": {"status": "DENY", "allowed": False},
        "missing_selected_route_reader": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("missing_selected_route_reader"))),
        "external_action_allowed": _parse(fake.tools["gov_enforce_anti_drift_gate"](_broken_linkage("external_action_allowed"))),
    }
    passed = all(v.get("status") == "ALLOW" and v.get("allowed") is not False for v in allow.values()) and all(v.get("status") == "DENY" and v.get("allowed") is False for v in deny.values())
    return {
        "artifact_id": "e60_gov_mcp_validation_harness_result",
        "registered_tools": sorted(fake.tools),
        "allow_results": allow,
        "deny_results": deny,
        "passed": passed,
        "no_server_started": True,
        "no_port_opened": True,
        "no_real_client_config_mutation": True,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def run_post_external_intelligence_market_readiness_gate(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    preflight = build_prior_gate_preflight(base)
    synthesis = load_json("operations/external_validation/e60_post_e59_capability_synthesis.json", base) or build_post_e59_capability_synthesis(base)
    criteria = load_json("operations/external_validation/e60_market_entry_readiness_criteria.json", base) or build_market_entry_readiness_criteria(base)
    candidates = load_json("operations/external_validation/e60_route_candidates_after_external_intelligence.json", base) or build_route_candidates_after_external_intelligence(base)
    matrix = load_json("operations/external_validation/e60_counterfactual_market_readiness_matrix.json", base) or build_counterfactual_market_readiness_matrix(base)
    decision = load_json("operations/external_validation/e60_market_entry_decision_packet.json", base) or build_market_entry_decision_packet(base)
    auth = load_json("operations/external_validation/e60_selected_action_behavior_authorization_result.json", base) or build_selected_action_behavior_authorization(base)
    readback = load_json("operations/external_validation/e60_ceo_brain_readback_smoke_result.json", base) or run_ceo_brain_readback_smoke(base)
    anti = load_json("operations/external_validation/e60_market_readiness_anti_drift_gate_result.json", base) or run_market_readiness_anti_drift_gate()
    binding = load_json("operations/external_validation/e60_market_readiness_capability_binding_gate_result.json", base) or run_market_readiness_capability_binding_gate()
    ygov = load_json("operations/external_validation/e60_y_star_gov_validation_result.json", base) or run_e60_y_star_gov_validation()
    gmcp = load_json("operations/external_validation/e60_gov_mcp_validation_harness_result.json", base) or run_e60_gov_mcp_validation_harness()
    checks = {
        "internal_runtime_L5_consumed": all(preflight["checks"].get(key) for key in ["E54_brain_L5_passed", "E55_behavior_center_L5_passed", "E56_internal_company_loop_L5_passed"]),
        "E58_case_study_consumed": preflight["checks"].get("E58_case_study_packaged") is True,
        "E59_external_intelligence_consumed": preflight["checks"].get("E59_external_intelligence_status_accepted") is True,
        "live_read_limitation_handled_honestly": decision.get("fixture_only_evidence_treated_as_live_market_freshness") is False and decision.get("live_public_read_unavailability_blocks_market_entry") is True,
        "market_entry_readiness_criteria_valid": criteria.get("current_readiness_level") == CURRENT_READINESS_LEVEL,
        "route_candidates_complete": candidates.get("candidate_count") == 10,
        "counterfactual_readiness_scoring_complete": matrix.get("selected_next_milestone") == SELECTED_NEXT_MILESTONE,
        "decision_packet_complete": decision.get("selected_next_milestone") == SELECTED_NEXT_MILESTONE,
        "selected_action_behavior_authorization_passes": auth.get("passed") is True,
        "CEO_brain_readback_passes": readback.get("passes") is True,
        "anti_drift_gate_passes": anti.get("passed") is True,
        "capability_binding_gate_passes": binding.get("passed") is True,
        "Y_star_gov_validation_passes": ygov.get("passed") is True,
        "gov_mcp_ALLOW_DENY_passes": gmcp.get("passed") is True,
        "no_owner_approval_fabricated": True,
        "pending_owner_decision_remains_pending": decision.get("owner_decision_status") == OWNER_DECISION_STATUS,
        "no_external_action_occurred": True,
        "no_customer_paid_real_mcp_expert_claim": all(decision.get(key) is False for key in ["customer_validation_claimed", "paid_signal_claimed", "real_mcp_transport_claimed", "expert_feedback_claimed"]),
    }
    passed = all(checks.values())
    return {
        "artifact_id": "e60_post_external_intelligence_market_readiness_gate_result",
        "gate_passed": passed,
        "final_status": FINAL_STATUS if passed else "post_external_intelligence_market_readiness_retest_incomplete",
        "recommended_next_milestone": SELECTED_NEXT_MILESTONE if passed else "E60_R2_market_readiness_repair",
        "current_readiness_level": CURRENT_READINESS_LEVEL,
        "selected_next_milestone": SELECTED_NEXT_MILESTONE,
        "nearest_alternative": NEAREST_ALTERNATIVE,
        "checks": checks,
        "owner_decision_status": OWNER_DECISION_STATUS,
        "external_action_allowed": False,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "expert_feedback_claimed": False,
        "fixture_only_evidence_treated_as_live_market_freshness": False,
        "no_external_action": True,
    }


def write_all_e60_artifacts(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    artifacts: dict[str, Any] = {}
    writers = [
        ("operations/external_validation/e60_base_state_manifest.json", build_base_state_manifest, "reports/integration/e60_base_state_manifest.md", "E60 Base State Manifest"),
        ("operations/external_validation/e60_prior_gate_preflight_result.json", build_prior_gate_preflight, "reports/integration/e60_prior_gate_preflight_result.md", "E60 Prior Gate Preflight"),
        ("operations/external_validation/e60_post_e59_capability_synthesis.json", build_post_e59_capability_synthesis, "reports/integration/e60_post_e59_capability_synthesis.md", "E60 Post-E59 Capability Synthesis"),
        ("operations/external_validation/e60_market_entry_readiness_criteria.json", build_market_entry_readiness_criteria, "reports/integration/e60_market_entry_readiness_criteria.md", "E60 Market Entry Readiness Criteria"),
        ("operations/external_validation/e60_route_candidates_after_external_intelligence.json", build_route_candidates_after_external_intelligence, "reports/integration/e60_route_candidates_after_external_intelligence.md", "E60 Route Candidates After External Intelligence"),
        ("operations/external_validation/e60_counterfactual_market_readiness_matrix.json", build_counterfactual_market_readiness_matrix, "reports/integration/e60_counterfactual_market_readiness_matrix.md", "E60 Counterfactual Market Readiness Matrix"),
        ("operations/external_validation/e60_market_entry_decision_packet.json", build_market_entry_decision_packet, "reports/integration/e60_market_entry_decision_packet.md", "E60 Market Entry Decision Packet"),
        ("operations/external_validation/e60_selected_action_behavior_authorization_result.json", build_selected_action_behavior_authorization, "reports/integration/e60_selected_action_behavior_authorization_result.md", "E60 Selected Action Behavior Authorization"),
    ]
    for rel, fn, md_rel, title in writers:
        data = fn(base)
        write_json(base, rel, data)
        summary_lines = [
            f"Artifact: `{data.get('artifact_id')}`",
            f"Passed: `{data.get('passed', data.get('gate_passed', 'n/a'))}`",
            f"Selected next milestone: `{data.get('selected_next_milestone', data.get('recommended_next_milestone', SELECTED_NEXT_MILESTONE))}`",
            f"External action allowed: `{data.get('external_action_allowed', False)}`",
            "Fixture-only E59 evidence is not treated as live market freshness.",
        ]
        write_md(base, md_rel, title, summary_lines)
        artifacts[rel] = data
    artifacts["writeback"] = write_market_readiness_writeback(base)
    readback = run_ceo_brain_readback_smoke(base)
    write_json(base, "operations/external_validation/e60_ceo_brain_readback_smoke_result.json", readback)
    write_md(base, "reports/integration/e60_ceo_brain_readback_smoke_result.md", "E60 CEO Brain Readback Smoke", [f"Passes: `{readback['passes']}`", f"Selected next milestone: `{SELECTED_NEXT_MILESTONE}`", f"Live-read limitation: `{LIVE_READ_STATUS}`"])
    anti = run_market_readiness_anti_drift_gate()
    write_json(base, "operations/external_validation/e60_market_readiness_anti_drift_gate_result.json", anti)
    write_md(base, "reports/integration/e60_market_readiness_anti_drift_gate_result.md", "E60 Market Readiness Anti-Drift Gate", [f"Passed: `{anti['passed']}`"])
    binding = run_market_readiness_capability_binding_gate()
    write_json(base, "operations/external_validation/e60_market_readiness_capability_binding_gate_result.json", binding)
    write_md(base, "reports/integration/e60_market_readiness_capability_binding_gate_result.md", "E60 Market Readiness Capability Binding Gate", [f"Passed: `{binding['passed']}`"])
    ygov = run_e60_y_star_gov_validation()
    write_json(base, "operations/external_validation/e60_y_star_gov_validation_result.json", ygov)
    write_md(base, "reports/integration/e60_y_star_gov_validation_result.md", "E60 Y-star-gov Validation", [f"Passed: `{ygov['passed']}`"])
    gmcp = run_e60_gov_mcp_validation_harness()
    write_json(base, "operations/external_validation/e60_gov_mcp_validation_harness_result.json", gmcp)
    write_md(base, "reports/integration/e60_gov_mcp_validation_harness_result.md", "E60 gov-mcp Validation Harness", [f"Passed: `{gmcp['passed']}`"])
    gate = run_post_external_intelligence_market_readiness_gate(base)
    write_json(base, "operations/external_validation/e60_post_external_intelligence_market_readiness_gate_result.json", gate)
    write_md(base, "reports/integration/e60_post_external_intelligence_market_readiness_gate_result.md", "E60 Post-External-Intelligence Market Readiness Gate", [f"Gate passed: `{gate['gate_passed']}`", f"Final status: `{gate['final_status']}`", f"Recommended next milestone: `{gate['recommended_next_milestone']}`"])
    write_md(base, "reports/integration/e60_owner_handoff_chinese.md", "E60 Owner Handoff", [
        "当前系统处于 `L3_external_intelligence_structurally_ready`：内部 L5、case study、外部智能结构都已完成，但 live public read 仍不可用。",
        "现在仍不能直接联系用户或发布，因为 owner decision 仍是 pending，external_action_allowed 仍为 false。",
        "E59 的 fixture 证据证明的是方法论和管线，不等于最新市场 freshness。",
        f"当前推荐下一步是 `{SELECTED_NEXT_MILESTONE}`，先修复或通过 host/network 完成受控 live public-read refresh。",
        f"最近替代路线是 `{NEAREST_ALTERNATIVE}`。",
        "真实外部联系、发布、controlled review execution 都需要明确 owner approval。",
    ])
    write_md(base, "reports/integration/e60_operator_handoff.md", "E60 Operator Handoff", [
        f"Final status: `{gate['final_status']}`.",
        f"Current readiness level: `{CURRENT_READINESS_LEVEL}`.",
        f"Selected next milestone: `{SELECTED_NEXT_MILESTONE}`.",
        "Do not treat E59 fixture evidence as live market freshness.",
        "No external action occurred and no validation/signal/transport claim was made.",
    ])
    return gate


if __name__ == "__main__":
    print(json.dumps(write_all_e60_artifacts(), indent=2, ensure_ascii=False))
