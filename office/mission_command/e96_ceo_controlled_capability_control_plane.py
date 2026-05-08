from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from office.aiden_meeting_room.governed_gateway import answer_owner_governed
from office.mission_command.action_semantics import classify_structured_action
from office.mission_command.e90_market_grounded_strategy_run import (
    run_e90_market_grounded_strategy_session,
)
from office.mission_command.e91_ceo_operating_doctrine_registry import (
    build_ceo_operating_doctrine_registry,
)


BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
MILESTONE_ID = "E96_CEO_Controlled_Capability_Control_Plane_And_Strategy_Intelligence_Leap_R1"


@dataclass(frozen=True)
class CapabilityCatalogEntry:
    capability_id: str
    title: str
    owner_repo: str
    status: str
    entrypoint: str
    governance_path: str
    cieustore_recording: str
    autonomy_level: str
    risk_boundary: str
    gaps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EntrypointQuarantineFinding:
    path: str
    risk_type: str
    current_status: str
    required_control_path: str
    why_it_matters: str
    external_action_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CONTROLLED_CAPABILITIES: tuple[CapabilityCatalogEntry, ...] = (
    CapabilityCatalogEntry(
        "owner_facing_aiden_governed_gateway",
        "Owner-facing Aiden behavior gateway",
        "bridge-labs",
        "active_runtime",
        "office/aiden_meeting_room/governed_gateway.py::answer_owner_governed",
        "E94 behavior-center runtime gateway -> Y-star-gov behavior-center contract",
        "Y-star-gov CIEUStore behavior-center runtime records",
        "autonomous_for_internal_low_risk_and_dry_run_routes",
        "real external side effects still require governed adapter and hard-risk screen",
    ),
    CapabilityCatalogEntry(
        "raw_answer_owner_kernel",
        "Raw Aiden behavior-center intent kernel",
        "bridge-labs",
        "internal_kernel_only",
        "office/aiden_meeting_room/aiden_response_engine.py::answer_owner",
        "must be wrapped by answer_owner_governed for owner-facing use",
        "not direct; recorded only through governed gateway",
        "not_owner_facing",
        "direct owner-facing use is a bypass",
        ("legacy boundary wording is more conservative than current low-risk autonomy policy",),
    ),
    CapabilityCatalogEntry(
        "brain_grounding_and_provenance",
        "Aiden brain activation and provenance",
        "bridge-labs",
        "active_runtime_partial_writeback",
        "office/mission_command/e93_brain_grounded_live_runtime.py::query_brain_for_stage",
        "E94 requires brain provenance before behavior-center runtime decision",
        "brain provenance is written in behavior-center CIEUStore records",
        "autonomous_read_provenance_only",
        "production brain writes require explicit sleep/dream commit policy",
    ),
    CapabilityCatalogEntry(
        "ceo_behavior_center_runtime_contract",
        "Y-star-gov behavior-center runtime validation",
        "Y-star-gov",
        "active_runtime",
        "ystar/governance/ceo_behavior_center_runtime_contract.py::validate_and_write_ceo_behavior_center_runtime_packet",
        "deterministic ALLOW/REQUIRE_REVISION/DENY/ESCALATE behavior-center governance",
        "formal CIEUStore write_dict path",
        "governance_reflex",
        "does not execute external actions",
    ),
    CapabilityCatalogEntry(
        "ceo_major_action_runtime_hook",
        "CEO major-action runtime hook",
        "Y-star-gov",
        "active_runtime",
        "ystar/governance/ceo_cognitive_os_runtime_hook.py::validate_ceo_runtime_envelope",
        "pre-action packet and post-action residual validation",
        "formal CIEUStore writer via CEO Cognitive OS CIEU log adapter",
        "governance_reflex",
        "ALLOW means approved next step, not external execution",
    ),
    CapabilityCatalogEntry(
        "gov_mcp_dry_run_boundary",
        "gov-mcp provider/tool dry-run boundary",
        "gov-mcp",
        "active_dry_run_only",
        "gov_mcp/outbound/dry_run_adapter.py::dry_run_outbound_action",
        "called after Y-star-gov ALLOW for provider/tool dry-run routes",
        "receipt can be attached to CIEUStore runtime records",
        "autonomous_dry_run_only",
        "provider_action_executed=false and external_side_effect=false",
    ),
    CapabilityCatalogEntry(
        "ceo_intelligence_loop_compiler",
        "Structured CEO intelligence loop compiler",
        "bridge-labs",
        "active_structured_fixture_runtime",
        "office/mission_command/e89_ceo_intelligence_loop_runtime_compiler.py::run_ceo_intelligence_runtime_session",
        "E91 doctrine gate then Y-star-gov intelligence-loop contract",
        "formal CIEUStore intelligence-loop record",
        "autonomous_for_test_or_structured_internal_planning",
        "non-test live cognition cannot be static_template",
        ("some generation remains deterministic fixture rather than live external observation",),
    ),
    CapabilityCatalogEntry(
        "ceo_market_strategy_benchmark",
        "Market-grounded strategy benchmark and route selection",
        "bridge-labs",
        "active_benchmark_limited_external_grounding",
        "office/mission_command/e90_market_grounded_strategy_run.py::run_e90_market_grounded_strategy_session",
        "E91 doctrine gate then Y-star-gov strategic benchmark validator",
        "formal CIEUStore benchmark/pre-action/residual records",
        "autonomous_for_internal_strategy_and_no_send_preflight",
        "no customer validation or revenue claim without real feedback",
        ("live fresh external observation remains blocked when test_mode=false",),
    ),
    CapabilityCatalogEntry(
        "ceo_doctrine_registry",
        "CEO operating doctrine registry",
        "bridge-labs",
        "active_but_needs_integrity_cleanup",
        "office/mission_command/e91_ceo_operating_doctrine_registry.py::build_ceo_operating_doctrine_registry",
        "Y-star-gov doctrine invocation contract",
        "CEO_OPERATING_DOCTRINE_INVOCATION_DECISION CIEUStore records",
        "mandatory_preflight_for_major_actions",
        "registry cannot substitute report-only artifacts for live doctrines",
        ("some discovered callable paths are broad or imprecise and need catalog hygiene",),
    ),
    CapabilityCatalogEntry(
        "codex_executor_boundary",
        "CEO principal to Codex executor boundary",
        "bridge-labs",
        "active_runtime",
        "office/mission_command/e92_ceo_principal_codex_executor_boundary.py::run_ceo_codex_executor_boundary_session",
        "Y-star-gov CEO Codex executor contract",
        "order, handoff-prompt, receipt, and residual CIEUStore records",
        "autonomous_engineering_order_generation",
        "Codex cannot change strategy or execute external actions without escalation",
    ),
    CapabilityCatalogEntry(
        "sleep_dream_learning_candidate",
        "Behavior-center sleep/dream residual learning",
        "bridge-labs",
        "partial_isolated_write_proof",
        "office/mission_command/e95_behavior_center_caller_migration_and_sleep_dream_loop.py::apply_sleep_dream_learning_candidate",
        "E95 residual-derived candidate; production commit still policy-gated",
        "candidate and isolated proof only by default",
        "autonomous_candidate_generation_only",
        "production brain DB commit requires explicit controlled policy",
    ),
)


KNOWN_BYPASS_ENTRYPOINTS: tuple[EntrypointQuarantineFinding, ...] = (
    EntrypointQuarantineFinding(
        "worker.js",
        "cloud_llm_persona_responder",
        "quarantined_until_governed_gateway_adapter",
        "must route role=ceo through CEOImplementationOrder or answer_owner_governed before model call",
        "It can answer as CEO through an external model without brain provenance, Y-star-gov validation, or CIEUStore.",
    ),
    EntrypointQuarantineFinding(
        "scripts/meeting_room/server.py",
        "meeting_room_canned_dialogue_and_tts",
        "quarantined_until_governed_gateway_adapter",
        "dialogue endpoint must call answer_owner_governed for Aiden and mark TTS as provider boundary",
        "It has an Aiden dialogue endpoint and optional ElevenLabs network call outside the governed behavior path.",
    ),
    EntrypointQuarantineFinding(
        "scripts/linkedin_auth.py",
        "live_social_posting_and_login",
        "quarantined_high_risk_live_external_action",
        "must be unreachable except through future gov-mcp live-ready preflight, owner approval, and receipt guard",
        "It can login, persist cookies, and publish LinkedIn posts.",
    ),
    EntrypointQuarantineFinding(
        "scripts/publish_x.py",
        "live_publication",
        "quarantined_high_risk_live_external_action",
        "must be replaced by gov-mcp no-send/live-ready publication adapter before use",
        "It can publish to X/Twitter using credentials.",
    ),
    EntrypointQuarantineFinding(
        "scripts/publish_x_v2.py",
        "live_publication",
        "quarantined_high_risk_live_external_action",
        "must be replaced by gov-mcp no-send/live-ready publication adapter before use",
        "It can publish to X/Twitter using OAuth credentials.",
    ),
    EntrypointQuarantineFinding(
        "scripts/publish_telegram.py",
        "live_publication",
        "quarantined_high_risk_live_external_action",
        "must be replaced by gov-mcp no-send/live-ready Telegram adapter before use",
        "It can send Telegram channel messages.",
    ),
    EntrypointQuarantineFinding(
        "scripts/telegram_bridge.py",
        "remote_command_bridge",
        "quarantined_high_risk_remote_control",
        "must require CEOImplementationOrder, owner approval, and command receipt before use",
        "It can send commands to a bot that controls the Mac.",
    ),
    EntrypointQuarantineFinding(
        "scripts/create_channel.py",
        "live_channel_creation_and_publication",
        "quarantined_high_risk_live_external_action",
        "must require future gov-mcp live-ready preflight plus explicit owner approval",
        "It can create a public channel and send an initial public message.",
    ),
    EntrypointQuarantineFinding(
        "scripts/post_ep01.py",
        "live_publication",
        "quarantined_high_risk_live_external_action",
        "must require future gov-mcp live-ready preflight plus explicit owner approval",
        "It can post content to a public Telegram channel.",
    ),
)


def build_controlled_capability_catalog(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or BRIDGE_ROOT
    registry = build_ceo_operating_doctrine_registry(root)
    capabilities = [entry.to_dict() for entry in CONTROLLED_CAPABILITIES]
    quarantine = [entry.to_dict() for entry in discover_quarantined_entrypoints(root)]
    integrity = audit_doctrine_registry_integrity(root, registry)
    return {
        "artifact_id": "e96_controlled_capability_catalog",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "repo_root": str(root),
        "controlled_capability_count": len(capabilities),
        "controlled_capabilities": capabilities,
        "quarantined_entrypoint_count": len(quarantine),
        "quarantined_entrypoints": quarantine,
        "doctrine_registry_integrity": integrity,
        "status_summary": _status_counts(capabilities),
        "truth_boundaries": {
            "L5-D": "absent_or_not_executed",
            "no_live_external_execution": True,
            "L5_D_revenue_customer_payment_loop_complete": False,
            "live_provider_execution_enabled": False,
            "K9Audit_write_integrated": False,
            "customer_validation_claimed": False,
        },
    }


def discover_quarantined_entrypoints(repo_root: Path | None = None) -> list[EntrypointQuarantineFinding]:
    root = repo_root or BRIDGE_ROOT
    findings = [entry for entry in KNOWN_BYPASS_ENTRYPOINTS if (root / entry.path).exists()]
    findings.extend(_scan_additional_external_surfaces(root, findings))
    return sorted(findings, key=lambda item: item.path)


def _scan_additional_external_surfaces(
    root: Path,
    known: Iterable[EntrypointQuarantineFinding],
) -> list[EntrypointQuarantineFinding]:
    known_paths = {item.path for item in known}
    patterns = (
        re.compile(r"TelegramClient|send_message|create_tweet|post_to_linkedin|api\.post|session\.post", re.I),
        re.compile(r"ELEVENLABS_API_KEY|ANTHROPIC_API_KEY|LI_API_BASE|X_API_KEY|TELEGRAM_BOT_TOKEN", re.I),
    )
    extra: list[EntrypointQuarantineFinding] = []
    for rel in _tracked_candidate_files(root):
        if rel in known_paths:
            continue
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not any(pattern.search(text) for pattern in patterns):
            continue
        if _has_control_signal(text):
            status = "review_required_external_surface_with_some_local_controls"
            why = "It contains external-capable code and local safety language, but is not the canonical governed gateway."
        else:
            status = "quarantined_external_surface_no_canonical_gateway"
            why = "It contains external-capable code without the current behavior-center/Y-star-gov/gov-mcp control path."
        extra.append(
            EntrypointQuarantineFinding(
                rel,
                "auto_discovered_external_surface",
                status,
                "register in E96 control plane and route through Y-star-gov/gov-mcp before use",
                why,
            )
        )
    return extra


def _tracked_candidate_files(root: Path) -> list[str]:
    paths: list[str] = []
    for base in ("scripts", "office", "worker.js", "frontend"):
        candidate = root / base
        if candidate.is_file():
            paths.append(base)
        elif candidate.exists():
            for path in candidate.rglob("*"):
                if path.is_file() and path.suffix in {".py", ".js", ".html"}:
                    paths.append(str(path.relative_to(root)))
    return paths


def _has_control_signal(text: str) -> bool:
    return any(
        signal in text
        for signal in (
            "no_send",
            "dry_run",
            "owner_approval",
            "owner_decision",
            "external_action_executed",
            "provider_action_executed",
            "validate_and_write",
            "answer_owner_governed",
        )
    )


def audit_doctrine_registry_integrity(root: Path, registry: Mapping[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or build_ceo_operating_doctrine_registry(root)
    issues: list[dict[str, Any]] = []
    for doctrine in registry.get("doctrines", []):
        path = str(doctrine.get("callable_implementation_path") or "")
        if not path:
            issues.append(
                {
                    "doctrine_id": doctrine.get("doctrine_id"),
                    "issue": "missing_callable_path",
                    "recommended_status": "report_only_until_adapter_exists",
                }
            )
            continue
        if path.startswith(("ystar/", "gov_mcp/")):
            continue
        local = root / path.split("::", 1)[0]
        if not local.exists():
            issues.append(
                {
                    "doctrine_id": doctrine.get("doctrine_id"),
                    "callable_implementation_path": path,
                    "issue": "callable_path_not_found_in_bridge_labs_tree",
                    "recommended_status": "mapped_but_not_runtime_active",
                }
            )
        elif path.startswith("tests/") or "/tests/" in path:
            issues.append(
                {
                    "doctrine_id": doctrine.get("doctrine_id"),
                    "callable_implementation_path": path,
                    "issue": "test_file_cannot_be_canonical_runtime_callable",
                    "recommended_status": "needs_runtime_adapter",
                }
            )
    return {
        "status": "needs_registry_hygiene" if issues else "clean",
        "issue_count": len(issues),
        "issues": issues,
        "registry_claims_need_hygiene": bool(issues),
    }


def decide_autonomy_for_action(action: Mapping[str, Any]) -> dict[str, Any]:
    structured = classify_structured_action(dict(action))
    text = f"{structured.raw_title} {structured.source}".lower()
    hard_risk = _contains_any(
        text,
        (
            "payment",
            "contract",
            "legal",
            "credential",
            "password",
            "secret",
            "customer system",
            "production deploy",
            "login",
            "create account",
        ),
    )
    read_only_no_login_or_contact = (
        structured.live_read_only_research
        and _contains_any(text, ("read-only", "read only", "without login", "no login", "no account", "no outreach"))
        and _contains_any(text, ("no contact", "no outreach", "no form submission", "no publication", "without login"))
        and not structured.payment
    )
    live_external = structured.external_side_effect or structured.publication or structured.email_or_message
    if read_only_no_login_or_contact:
        autonomy = "ALLOW_AUTONOMOUS_PUBLIC_READ_ONLY_WITH_RECEIPT"
        may_execute = True
        owner_packet_required = False
    elif hard_risk or structured.payment:
        autonomy = "DENY_OR_OWNER_DECISION_HARD_RISK"
        may_execute = False
        owner_packet_required = True
    elif structured.live_read_only_research:
        autonomy = "ALLOW_AUTONOMOUS_PUBLIC_READ_ONLY_WITH_RECEIPT"
        may_execute = True
        owner_packet_required = False
    elif "dry_run" in text or "dry-run" in text or structured.obligation_dry_run:
        autonomy = "ALLOW_AUTONOMOUS_DRY_RUN_NO_SEND"
        may_execute = True
        owner_packet_required = False
    elif live_external:
        autonomy = "GOVERNED_PREFLIGHT_ONLY_UNTIL_LIVE_ADAPTER"
        may_execute = False
        owner_packet_required = False
    elif structured.review_gated:
        autonomy = "ALLOW_AUTONOMOUS_REVIEW_ARTIFACT_CANDIDATE"
        may_execute = True
        owner_packet_required = False
    else:
        autonomy = "ALLOW_AUTONOMOUS_INTERNAL_RUNTIME"
        may_execute = True
        owner_packet_required = False
    return {
        "action_id": structured.action_id,
        "structured_action": structured.to_dict(),
        "autonomy_decision": autonomy,
        "may_execute_without_owner": may_execute,
        "owner_decision_packet_required": owner_packet_required,
        "human_work_minimization": "owner is only needed for hard-risk approval or unavailable live provider authorization",
        "no_external_side_effect_guarantee": not live_external or not may_execute,
    }


def build_market_strategy_intelligence_leap(
    *,
    catalog: Mapping[str, Any],
    e90_result: Mapping[str, Any],
) -> dict[str, Any]:
    strategy = e90_result.get("strategy", {})
    route_scores = strategy.get("route_scoring", [])
    routes = strategy.get("route_candidates", [])
    enhanced_routes = []
    for route in routes:
        route_id = str(route.get("route_id") or route.get("candidate_id") or route.get("id") or route.get("name"))
        base_score = _route_score(route_id, route_scores)
        control_bonus = _control_bonus_for_route(route)
        owner_burden_penalty = _owner_burden_penalty(route)
        evidence_gap_penalty = _evidence_gap_penalty(route)
        strategic_score = max(0, min(100, base_score + control_bonus - owner_burden_penalty - evidence_gap_penalty))
        enhanced_routes.append(
            {
                "route_id": route_id,
                "name": route.get("name") or route.get("description"),
                "route_type": route.get("route_type"),
                "base_e90_score": base_score,
                "risk_control_bonus": control_bonus,
                "owner_burden_penalty": owner_burden_penalty,
                "evidence_gap_penalty": evidence_gap_penalty,
                "strategic_intelligence_score": strategic_score,
                "autonomous_next_step": _autonomous_next_step_for_route(route),
                "hard_stop": _hard_stop_for_route(route),
            }
        )
    ranked = sorted(enhanced_routes, key=lambda item: item["strategic_intelligence_score"], reverse=True)
    selected = ranked[0] if ranked else {}
    return {
        "artifact_id": "e96_market_strategy_intelligence_leap",
        "benchmark_basis": "E90 strategy result plus E96 controlled capability catalog and quarantine audit",
        "route_count": len(enhanced_routes),
        "ranked_routes": ranked,
        "selected_first_cash_path": {
            "route_id": selected.get("route_id"),
            "reason": "highest governed executability, strongest reuse of existing CIEU/Y-star-gov/gov-mcp controls, and lowest owner burden before live feedback",
            "next_48h": [
                "Package a no-send governed-agent action proof packet from existing CIEUStore and gov-mcp dry-run receipts.",
                "Run autonomous public-read-only evidence refresh if a safe read-only mechanism is available.",
                "Generate one owner-facing L4 feedback preflight packet, not a send.",
            ],
            "next_7d": [
                "Convert the proof packet into a repeatable dashboard-backed review workflow.",
                "Use gov-mcp dry-run receipts to test a low-risk transparent feedback envelope.",
                "Only request owner approval for hard-risk live external action, not for internal analysis or dry-runs.",
            ],
        },
        "do_not_pursue_now": [
            "Direct customer contact without governed live adapter.",
            "Payment, legal, credential, or account-creation actions.",
            "Standalone social publishing scripts outside gov-mcp/Y-star-gov control.",
            "Static strategy memos that bypass brain provenance and doctrine gate.",
        ],
        "capability_catalog_used": catalog.get("artifact_id"),
        "quarantine_count": catalog.get("quarantined_entrypoint_count"),
        "claim_boundaries": {
            "no_customer_validation_claimed": True,
            "no_revenue_or_paid_signal_claimed": True,
            "no_live_provider_execution": True,
            "K9Audit_not_integrated": True,
        },
    }


def run_e96_controlled_capability_strategy_session(
    *,
    owner_intent: str | None = None,
    repo_root: Path | None = None,
    cieu_db: str | Path | None = None,
) -> dict[str, Any]:
    root = repo_root or BRIDGE_ROOT
    db_path = Path(cieu_db) if cieu_db is not None else root / ".runtime" / "e96_controlled_capability_control_plane.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    owner_intent = owner_intent or (
        "Build the controlled CEO capability catalog, quarantine bypass entrypoints, and select the "
        "highest-leverage first-cash strategy while minimizing human approval burden."
    )
    behavior_result = answer_owner_governed(
        owner_intent,
        repo_root=root,
        cieu_db=db_path,
        session_id="e96_behavior_center_control_plane_session",
    )
    catalog = build_controlled_capability_catalog(root)
    e90_result = run_e90_market_grounded_strategy_session(
        cieu_db=str(db_path),
        owner_intent=owner_intent,
        repo_root=root,
        test_mode=True,
    )
    strategy_leap = build_market_strategy_intelligence_leap(catalog=catalog, e90_result=e90_result)
    autonomous_work_queue = build_autonomous_work_queue(catalog, strategy_leap)
    cieu_summary = summarize_cieustore_records(db_path)
    result = {
        "artifact_id": "e96_controlled_capability_strategy_session",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "base_inputs": {
            "owner_intent": owner_intent,
            "repo_root": str(root),
            "cieu_db": str(db_path),
        },
        "behavior_center_decision": behavior_result.get("behavior_center_decision"),
        "behavior_route": behavior_result.get("route_result", {}).get("route_type"),
        "controlled_capability_catalog": catalog,
        "market_strategy_intelligence_leap": strategy_leap,
        "autonomous_work_queue": autonomous_work_queue,
        "CIEUStore_summary": cieu_summary,
        "end_to_end_chain_proven": _chain_proven(behavior_result, e90_result, cieu_summary),
        "L5_truth_table_after_E96": l5_truth_table_after_e96(),
        "what_was_not_claimed": [
            "No L4 feedback was executed.",
            "No live provider action was enabled.",
            "No customer validation, paid signal, pricing validation, payment, or revenue evidence was claimed.",
            "No K9Audit write or bridge was claimed.",
        ],
        "recommended_next_milestone": "E97_Governed_Low_Risk_Public_Read_Observation_And_Feedback_Preflight_Activation_R1",
    }
    return result


def build_autonomous_work_queue(
    catalog: Mapping[str, Any],
    strategy_leap: Mapping[str, Any],
) -> dict[str, Any]:
    actions = [
        {
            "action_id": "e96_package_governed_action_proof_packet",
            "action_title": "Build a no-send governed agent action proof packet using existing CIEUStore and gov-mcp dry-run receipts.",
            "source": "e96_strategy_runtime",
        },
        {
            "action_id": "e96_refresh_public_read_evidence",
            "action_title": "Run live read-only research to collect public evidence with no contact, no login, no form submission, and no publication.",
            "source": "experiment_tier1_research",
        },
        {
            "action_id": "e96_prepare_l4_feedback_preflight",
            "action_title": "Prepare owner-review L4 feedback preflight packet and gov-mcp dry-run receipt; do not send message.",
            "source": "research_planning",
        },
        {
            "action_id": "e96_direct_social_publish_blocked",
            "action_title": "Publish public social post directly through LinkedIn or X.",
            "source": "live_external_action",
        },
        {
            "action_id": "e96_payment_path_blocked",
            "action_title": "Create payment link and process payment for a customer.",
            "source": "revenue_payment_action",
        },
    ]
    decisions = [decide_autonomy_for_action(action) for action in actions]
    return {
        "queue_id": "e96_autonomous_work_queue",
        "human_approval_minimized": True,
        "allowed_without_owner_count": sum(1 for item in decisions if item["may_execute_without_owner"]),
        "hard_risk_owner_or_deny_count": sum(
            1 for item in decisions if item["autonomy_decision"] == "DENY_OR_OWNER_DECISION_HARD_RISK"
        ),
        "decisions": decisions,
        "selected_first_cash_path": strategy_leap.get("selected_first_cash_path", {}),
        "catalog_quarantine_count": catalog.get("quarantined_entrypoint_count", 0),
    }


def summarize_cieustore_records(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_exists": False, "event_count": 0, "event_types": [], "decisions": []}
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute(
            "SELECT event_type, decision, params_json, result_json FROM cieu_events ORDER BY seq_global"
        ).fetchall()
    except sqlite3.Error:
        rows = []
    finally:
        conn.close()
    decisions: list[str] = []
    for _, decision, params_json, result_json in rows:
        if decision:
            decisions.append(str(decision))
            continue
        for payload in (params_json, result_json):
            try:
                data = json.loads(payload) if payload else {}
            except Exception:
                data = {}
            nested_decision = (
                data.get("decision")
                or data.get("governance_decision", {}).get("decision")
                or data.get("runtime_decision", {}).get("decision")
            )
            if nested_decision:
                decisions.append(str(nested_decision))
                break
    return {
        "db_exists": True,
        "event_count": len(rows),
        "event_types": sorted({str(row[0]) for row in rows}),
        "decisions": decisions,
    }


def write_e96_reports(result: Mapping[str, Any], *, repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or BRIDGE_ROOT
    mission_dir = root / "office" / "mission_command"
    status_dir = root / "operations" / "baseline" / "e87r_full_repo_baseline"
    catalog_dir = root / "operations" / "controlled_capability_catalog"
    mission_dir.mkdir(parents=True, exist_ok=True)
    status_dir.mkdir(parents=True, exist_ok=True)
    catalog_dir.mkdir(parents=True, exist_ok=True)
    report_path = mission_dir / "e96_ceo_controlled_capability_control_plane_report.json"
    readback_path = mission_dir / "e96_ceo_controlled_capability_control_plane_readback.md"
    status_json = status_dir / "current_runtime_status_after_e96_ceo_controlled_capability_control_plane.json"
    status_md = status_dir / "current_runtime_status_after_e96_ceo_controlled_capability_control_plane.md"
    catalog_json = catalog_dir / "e96_controlled_capability_catalog.json"
    catalog_md = catalog_dir / "e96_controlled_capability_catalog.md"

    report = _report(result)
    status = _status(result)
    catalog = result["controlled_capability_catalog"]
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    readback_path.write_text(_report_markdown(report), encoding="utf-8")
    status_json.write_text(json.dumps(status, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    status_md.write_text(_status_markdown(status), encoding="utf-8")
    catalog_json.write_text(json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    catalog_md.write_text(_catalog_markdown(catalog), encoding="utf-8")
    return {
        "report_json": str(report_path),
        "readback_md": str(readback_path),
        "status_json": str(status_json),
        "status_md": str(status_md),
        "catalog_json": str(catalog_json),
        "catalog_md": str(catalog_md),
    }


def l5_truth_table_after_e96() -> dict[str, str]:
    return {
        "L5-A Runtime Foundation": "complete_internal_runtime_foundation_with_controlled_capability_catalog_and_entry_quarantine",
        "L5-B CEO Intelligence Loop": "complete_for_structured_governed_intelligence_loop_with_strategy_control_plane_upgrade",
        "L5-B+": "partial_dynamic_intelligence_pending_live_external_observation_and_real_feedback",
        "L5-C Controlled External Action": "partial_low_risk_autonomy_dry_run_only_high_risk_quarantined",
        "L5-D Revenue/Customer/Payment Loop": "absent_or_not_executed",
    }


def _chain_proven(
    behavior_result: Mapping[str, Any],
    e90_result: Mapping[str, Any],
    cieu_summary: Mapping[str, Any],
) -> bool:
    return (
        behavior_result.get("behavior_center_decision") == "ALLOW"
        and e90_result.get("end_to_end_chain_proven") is True
        and int(cieu_summary.get("event_count", 0)) >= 6
    )


def _route_score(route_id: str, scores: Iterable[Mapping[str, Any]]) -> int:
    for score in scores:
        candidate_id = str(score.get("route_id") or score.get("candidate_id") or score.get("id") or "")
        if candidate_id == route_id:
            return int(score.get("total_score") or score.get("score") or 60)
    return 60


def _control_bonus_for_route(route: Mapping[str, Any]) -> int:
    route_type = str(route.get("route_type") or "")
    if route_type in {"internal_runtime", "provider_tool_dry_run"}:
        return 18
    if route_type == "external_feedback_candidate":
        return 10
    if route_type == "owner_decision_required":
        return 4
    return 8


def _owner_burden_penalty(route: Mapping[str, Any]) -> int:
    text = json.dumps(route, sort_keys=True).lower()
    if _contains_any(text, ("owner must", "owner decision", "manual", "approve")):
        return 10
    return 2


def _evidence_gap_penalty(route: Mapping[str, Any]) -> int:
    text = json.dumps(route, sort_keys=True).lower()
    penalty = 0
    if "customer validation" in text:
        penalty += 8
    if "payment" in text or "revenue" in text:
        penalty += 4
    return penalty


def _autonomous_next_step_for_route(route: Mapping[str, Any]) -> str:
    route_type = str(route.get("route_type") or "")
    if route_type == "provider_tool_dry_run":
        return "run gov-mcp dry-run receipt and attach to CIEUStore; no live provider call"
    if route_type == "internal_runtime":
        return "execute internal package/report/test loop through governed gateway and CIEUStore"
    if route_type == "external_feedback_candidate":
        return "prepare no-send L4 feedback preflight packet and public-read evidence refresh"
    return "prepare owner decision packet only if hard-risk boundary is reached"


def _hard_stop_for_route(route: Mapping[str, Any]) -> list[str]:
    text = json.dumps(route, sort_keys=True).lower()
    stops = []
    for term in ("payment", "legal", "contract", "credential", "login", "send", "publish"):
        if term in text:
            stops.append(term)
    return sorted(set(stops))


def _status_counts(entries: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        status = str(entry.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _report(result: Mapping[str, Any]) -> dict[str, Any]:
    strategy = result["market_strategy_intelligence_leap"]
    catalog = result["controlled_capability_catalog"]
    return {
        "milestone_id": MILESTONE_ID,
        "repos_read": ["bridge-labs", "Y-star-gov", "gov-mcp"],
        "repos_modified": ["bridge-labs"],
        "existing_systems_reused": [
            "answer_owner_governed",
            "E94 behavior-center runtime gateway",
            "E90 market strategy runtime session",
            "E91 doctrine registry",
            "Y-star-gov CIEUStore writers through existing runtime calls",
            "gov-mcp dry_run_outbound_action through existing E90/E94 calls",
        ],
        "controlled_capability_count": catalog["controlled_capability_count"],
        "quarantined_entrypoint_count": catalog["quarantined_entrypoint_count"],
        "doctrine_registry_integrity": catalog["doctrine_registry_integrity"],
        "selected_first_cash_path": strategy["selected_first_cash_path"],
        "autonomous_work_queue": result["autonomous_work_queue"],
        "CIEUStore_summary": result["CIEUStore_summary"],
        "end_to_end_chain_proven": result["end_to_end_chain_proven"],
        "L5_truth_table_after_E96": result["L5_truth_table_after_E96"],
        "what_was_not_claimed": result["what_was_not_claimed"],
        "recommended_next_milestone": result["recommended_next_milestone"],
    }


def _status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "L5_truth_table_after_E96": result["L5_truth_table_after_E96"],
        "end_to_end_chain_proven": result["end_to_end_chain_proven"],
        "controlled_capability_catalog_status": "active_runtime_catalog_written",
        "entrypoint_quarantine_status": "known_external_bypass_surfaces_quarantined_by_catalog",
        "low_risk_autonomy_status": "internal_public_read_and_dry_run_routes_may_continue_without_owner",
        "hard_risk_scope": [
            "payment",
            "legal_or_contract_commitment",
            "credentials_or_login",
            "customer_system_access",
            "live_publication_or_contact_without_adapter",
            "production_deployment",
        ],
        "no_claims": result["what_was_not_claimed"],
        "next": result["recommended_next_milestone"],
    }


def _report_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# E96 CEO Controlled Capability Control Plane Readback",
        "",
        f"- controlled_capabilities: `{report['controlled_capability_count']}`",
        f"- quarantined_entrypoints: `{report['quarantined_entrypoint_count']}`",
        f"- end_to_end_chain_proven: `{str(report['end_to_end_chain_proven']).lower()}`",
        f"- CIEUStore_events: `{report['CIEUStore_summary']['event_count']}`",
        "",
        "## Selected First-Cash Path",
        f"- route_id: `{report['selected_first_cash_path'].get('route_id')}`",
        f"- reason: {report['selected_first_cash_path'].get('reason')}",
        "",
        "## Autonomy Policy",
        "- Internal runtime, public-read-only, and gov-mcp dry-run work should not be pushed back to the owner.",
        "- Hard-risk actions remain denied or owner-decision-gated.",
        "- Live external execution is not enabled in E96.",
        "",
        "## Not Claimed",
    ]
    lines.extend(f"- {item}" for item in report["what_was_not_claimed"])
    return "\n".join(lines).rstrip() + "\n"


def _status_markdown(status: Mapping[str, Any]) -> str:
    lines = [
        "# Current Runtime Status After E96",
        "",
        f"- end_to_end_chain_proven: `{str(status['end_to_end_chain_proven']).lower()}`",
        f"- controlled_capability_catalog_status: `{status['controlled_capability_catalog_status']}`",
        f"- entrypoint_quarantine_status: `{status['entrypoint_quarantine_status']}`",
        f"- low_risk_autonomy_status: `{status['low_risk_autonomy_status']}`",
        "",
        "## L5 Truth Table",
    ]
    lines.extend(f"- {key}: `{value}`" for key, value in status["L5_truth_table_after_E96"].items())
    lines.append("")
    lines.append("## Hard-Risk Scope")
    lines.extend(f"- {item}" for item in status["hard_risk_scope"])
    return "\n".join(lines).rstrip() + "\n"


def _catalog_markdown(catalog: Mapping[str, Any]) -> str:
    lines = [
        "# E96 Controlled Capability Catalog",
        "",
        f"- controlled_capability_count: `{catalog['controlled_capability_count']}`",
        f"- quarantined_entrypoint_count: `{catalog['quarantined_entrypoint_count']}`",
        "",
        "## Controlled Capabilities",
    ]
    for item in catalog["controlled_capabilities"]:
        lines.append(f"- `{item['capability_id']}`: {item['status']} via `{item['entrypoint']}`")
    lines.append("")
    lines.append("## Quarantined Entrypoints")
    for item in catalog["quarantined_entrypoints"]:
        lines.append(f"- `{item['path']}`: {item['current_status']} ({item['risk_type']})")
    lines.append("")
    lines.append("## Registry Integrity")
    integrity = catalog["doctrine_registry_integrity"]
    lines.append(f"- issue_count: `{integrity['issue_count']}`")
    for issue in integrity["issues"]:
        lines.append(f"- `{issue.get('doctrine_id')}`: {issue.get('issue')}")
    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "MILESTONE_ID",
    "audit_doctrine_registry_integrity",
    "build_autonomous_work_queue",
    "build_controlled_capability_catalog",
    "build_market_strategy_intelligence_leap",
    "decide_autonomy_for_action",
    "discover_quarantined_entrypoints",
    "l5_truth_table_after_e96",
    "run_e96_controlled_capability_strategy_session",
    "summarize_cieustore_records",
    "write_e96_reports",
]
