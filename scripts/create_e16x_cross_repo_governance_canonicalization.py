#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace")

EXPECTED_BASE_HEAD = "c80a6b111fffd5e84190d968142c37a0bd1f8f94"
BRANCH = "backflow/aiden-ceo-meeting-room"

REPOS = {
    "ystar_bridge_labs": WORKSPACE_ROOT / "ystar-bridge-labs",
    "y_star_gov": WORKSPACE_ROOT / "Y-star-gov",
    "gov_mcp": WORKSPACE_ROOT / "gov-mcp",
    "ystar_company": WORKSPACE_ROOT / "ystar-company",
}

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".rst",
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
}

SKIP_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".wal",
    ".shm",
    ".pyc",
    ".pyo",
    ".log",
}

SAFETY_STATEMENT = (
    "E16X performs read-only cross-repo inventory and static governance canonicalization only. "
    "It performs no customer contact, email/message sending, publication, payment, account creation, "
    "form submission, login, external validation submission, customer system access, legal/financial "
    "commitment, credential disclosure, core brain/CIEU/memory canonical writeback, real provider API "
    "call, outbound adapter call, or real send receipt."
)


@dataclass(frozen=True)
class RepoReceipt:
    key: str
    path: str
    exists: bool
    branch: str
    head: str
    status_sample: list[str]
    file_count: int
    evidence_files: list[str]
    capability_hits: dict[str, list[str]]
    scan_limit_note: str


def run_git(repo: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        return completed.stderr.strip()
    return completed.stdout.strip()


def is_safe_text_file(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.name.startswith(".ystar_active_agent"):
        return False
    if path.name.startswith("._") or path.name == ".DS_Store":
        return False
    if path.suffix in SKIP_SUFFIXES:
        return False
    return path.suffix in TEXT_SUFFIXES


def relative_files(repo: Path, max_files: int = 5000) -> list[str]:
    if not repo.exists():
        return []
    files: list[str] = []
    for path in repo.rglob("*"):
        if len(files) >= max_files:
            break
        if path.is_file() and is_safe_text_file(path):
            files.append(str(path.relative_to(repo)))
    return sorted(files)


def existing(repo: Path, candidates: Iterable[str]) -> list[str]:
    return [item for item in candidates if (repo / item).exists()]


def find_capability_hits(repo: Path, files: list[str], terms: Mapping[str, list[str]]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for capability, needles in terms.items():
        found: list[str] = []
        lowered_needles = [needle.lower() for needle in needles]
        for rel in files:
            if len(found) >= 18:
                break
            path = repo / rel
            name_hit = any(needle in rel.lower() for needle in lowered_needles)
            text_hit = False
            if not name_hit and path.stat().st_size < 300_000:
                try:
                    sample = path.read_text(encoding="utf-8", errors="ignore").lower()
                except OSError:
                    sample = ""
                text_hit = any(needle in sample for needle in lowered_needles)
            if name_hit or text_hit:
                found.append(rel)
        hits[capability] = found
    return hits


def scan_repo(key: str, repo: Path) -> RepoReceipt:
    if not repo.exists():
        return RepoReceipt(
            key=key,
            path=str(repo),
            exists=False,
            branch="missing",
            head="missing",
            status_sample=[],
            file_count=0,
            evidence_files=[],
            capability_hits={},
            scan_limit_note="repo path missing; no scan performed",
        )

    files = relative_files(repo)
    if key == "ystar_bridge_labs":
        evidence_candidates = [
            "office/mission_command/e8_risk_controlled_action_model.py",
            "office/mission_command/e8_external_action_preflight.py",
            "office/mission_command/e8_execution_gate.py",
            "office/mission_command/e9_suppression_registry.py",
            "office/mission_command/action_authorization_router.py",
            "office/mission_command/e12_action_packet.py",
            "office/mission_command/e12_execution_gate.py",
            "office/mission_command/e12_feedback_capture.py",
            "office/mission_command/e12_signal_evaluator.py",
            "office/mission_command/b2r_capability_domains.py",
            "office/mission_command/b2r_external_validation_messaging.py",
            "office/mission_command/b2r_gov_mcp_execution_contract.py",
            "office/mission_command/c2_ygov_action_decision.py",
            "office/mission_command/c2_gov_mcp_execution_control.py",
            "office/mission_command/c3_validation_batch_selector.py",
            "office/mission_command/e15a_owner_execution_console.py",
            "office/mission_command/e15d_ygov_outbound_policy.py",
            "office/mission_command/e15d_gov_mcp_outbound_adapter.py",
            "scripts/host_delivery_runner.py",
        ]
    elif key == "y_star_gov":
        evidence_candidates = [
            "README.md",
            "ystar/__init__.py",
            "ystar/kernel/cieu.py",
            "ystar/kernel/engine.py",
            "ystar/kernel/czl_protocol.py",
            "ystar/governance/contract_lifecycle.py",
            "ystar/governance/intervention_engine.py",
            "ystar/governance/obligation_triggers.py",
            "ystar/governance/router_registry.py",
            "ystar/governance/y_star_field_validator.py",
            "docs/pre_u_packet_validator/README.md",
            "docs/gov_mcp_setup.md",
            "docs/external_governance_adapter_sdk.md",
            "tests/test_delegation_chain.py",
        ]
    elif key == "gov_mcp":
        evidence_candidates = [
            "README.md",
            "pyproject.toml",
            "gov_mcp/server.py",
            "gov_mcp/router.py",
            "gov_mcp/company_runtime_tools.py",
            "gov_mcp/dispatch_logic.py",
            "gov_mcp/exec_whitelist.yaml",
            "tests/test_server.py",
        ]
    else:
        evidence_candidates = [
            "README.md",
            "approval_validity_revocation_policy/README.md",
            "approval_authority_model/README.md",
            "agentic_pilot_approval_packet_assembler/README.md",
            "controlled_backend_safety_preflight/README.md",
            "runtime_artifact_quarantine/README.md",
            "l8_first_cash_path_operating_loop/README.md",
        ]

    terms = {
        "governance_kernel": ["check(", "enforce(", "intentcontract", "constitutionalcontract", "governance"],
        "cieu_residual": ["cieu", "residual", "prediction delta", "hash chain"],
        "delegation_obligation": ["delegation", "obligation", "omission"],
        "mcp_execution": ["gov_check", "gov_enforce", "execution receipt", "adapter", "mcp"],
        "outbound": ["outbound", "send", "message", "publication", "form", "account"],
        "feedback": ["feedback", "signal", "ledger", "suppression"],
    }

    status = run_git(repo, ["status", "--short"]).splitlines()[:40]
    return RepoReceipt(
        key=key,
        path=str(repo),
        exists=True,
        branch=run_git(repo, ["branch", "--show-current"]),
        head=run_git(repo, ["log", "-1", "--oneline"]),
        status_sample=status,
        file_count=len(files),
        evidence_files=existing(repo, evidence_candidates),
        capability_hits=find_capability_hits(repo, files, terms),
        scan_limit_note="text files scanned with secret/DB/WAL/SHM/log/active-agent content skipped",
    )


def repo_receipts() -> dict[str, Any]:
    return {key: scan_repo(key, repo).__dict__ for key, repo in REPOS.items()}


def build_cross_repo_canonical_ownership(scans: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e16x_cross_repo_canonical_ownership",
        "base_head": EXPECTED_BASE_HEAD,
        "repo_scan_receipts": scans,
        "canonical_ownership": {
            "Y-star-gov": {
                "owns": [
                    "deterministic governance kernel",
                    "IntentContract and ConstitutionalContract semantics",
                    "canonical check/enforce entrypoints",
                    "CIEU evidence chain and residual standards",
                    "obligation, omission, delegation monotonicity governance",
                    "governance loop and intervention standards",
                    "release/live/no-go boundary standards",
                ],
                "evidence": scans["y_star_gov"]["evidence_files"],
                "bridge_relationship": "bridge-labs should emit Y*gov-compatible packets, not become the final governance kernel.",
            },
            "gov-mcp": {
                "owns": [
                    "MCP execution gateway",
                    "gov_check and gov_enforce tool surface",
                    "contract activation through MCP",
                    "execution receipts and normalized deny/allow envelopes",
                    "provider adapter boundary",
                    "future outbound adapter implementation if accepted",
                ],
                "evidence": scans["gov_mcp"]["evidence_files"],
                "bridge_relationship": "bridge-labs E15D adapter contract is prototype input for gov-mcp promotion.",
            },
            "ystar-bridge-labs": {
                "owns": [
                    "Aiden/CEO company runtime dogfood",
                    "commercial validation loop",
                    "offer, target, batch, owner console, feedback artifacts",
                    "prototype outbound governance contracts before promotion",
                    "host-side repository delivery closure",
                ],
                "evidence": scans["ystar_bridge_labs"]["evidence_files"],
                "promotion_boundary": "Anything normative or provider-executing must be backflowed to Y-star-gov or gov-mcp.",
            },
            "ystar-company": {
                "owns": [
                    "historical incubated assets",
                    "legacy company runtime patterns for possible backflow",
                    "archive candidates",
                ],
                "evidence": scans["ystar_company"]["evidence_files"],
                "canonical_role": "not final source of truth unless explicitly promoted",
            },
        },
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_duplicate_overlap_matrix(scans: Mapping[str, Any]) -> dict[str, Any]:
    overlaps = [
        {
            "overlap_id": "e8_risk_model_vs_b2r_capability_domains",
            "duplicate_type": "intentional_evolution",
            "risk_level": "medium",
            "files": [
                "office/mission_command/e8_risk_controlled_action_model.py",
                "office/mission_command/b2r_capability_domains.py",
            ],
            "conflict_summary": "E8 defines risk tiers; B2R defines progressive capability levels. Treating B2R level 5 as risk tier 5 would incorrectly over-risk low-volume transparent validation messages.",
            "recommended_resolution": "Keep E8 risk tiers canonical for action risk. Keep B2R as capability maturity taxonomy and map low-risk validation messaging to E8 Tier 2.",
        },
        {
            "overlap_id": "e8_preflight_vs_action_authorization_router",
            "duplicate_type": "old_router_needs_upgrade",
            "risk_level": "medium",
            "files": [
                "office/mission_command/e8_external_action_preflight.py",
                "office/mission_command/action_authorization_router.py",
            ],
            "conflict_summary": "Preflight and router both gate external actions but router does not fully understand later capability domains.",
            "recommended_resolution": "Upgrade action_authorization_router to call canonical risk tier mapping and capability-domain checks.",
        },
        {
            "overlap_id": "action_authorization_router_vs_c2_decision_control",
            "duplicate_type": "harmful_parallel_logic",
            "risk_level": "high",
            "files": [
                "office/mission_command/action_authorization_router.py",
                "office/mission_command/c2_ygov_action_decision.py",
                "office/mission_command/c2_gov_mcp_execution_control.py",
            ],
            "conflict_summary": "C2 introduced deterministic decision/control envelopes parallel to the older router.",
            "recommended_resolution": "Make C2/E15D policy call the router or promote router vocabulary so one allow/deny source exists before real E16C.",
        },
        {
            "overlap_id": "b2r_gov_mcp_contract_vs_c2_execution_control",
            "duplicate_type": "intentional_evolution",
            "risk_level": "medium",
            "files": [
                "office/mission_command/b2r_gov_mcp_execution_contract.py",
                "office/mission_command/c2_gov_mcp_execution_control.py",
            ],
            "conflict_summary": "B2R declares gateway contract; C2 turns it into execution modes.",
            "recommended_resolution": "Fold both into a canonical gov-mcp execution contract proposal and promote to gov-mcp.",
        },
        {
            "overlap_id": "c2_c3_e15a_feedback_vs_e12_e14_feedback",
            "duplicate_type": "harmful_parallel_logic",
            "risk_level": "high",
            "files": [
                "office/mission_command/e12_feedback_capture.py",
                "office/mission_command/e12_signal_evaluator.py",
                "office/mission_command/e14_feedback_events.py",
                "office/mission_command/c2_feedback_loop.py",
                "office/mission_command/c3_feedback_intake_runtime.py",
                "office/mission_command/e15a_feedback_signal_evaluator.py",
            ],
            "conflict_summary": "Readiness fixtures, owner-reported feedback, and actual customer responses can be confused if schemas remain parallel.",
            "recommended_resolution": "Use E12/E14 feedback event schema as canonical validation feedback and mark C2/C3/E15A fixtures as pre-feedback templates until owner/customer evidence exists.",
        },
        {
            "overlap_id": "e15d_outbound_policy_vs_b2r_external_validation_message_domain",
            "duplicate_type": "canonical_candidate",
            "risk_level": "medium",
            "files": [
                "office/mission_command/b2r_external_validation_messaging.py",
                "office/mission_command/e15d_ygov_outbound_policy.py",
            ],
            "conflict_summary": "B2R defines domain; E15D defines policy and queues for the same outbound validation space.",
            "recommended_resolution": "Keep B2R domain as capability definition and E15D as pilot policy implementation after router alignment.",
        },
        {
            "overlap_id": "e15d_adapter_contract_vs_real_gov_mcp_surface",
            "duplicate_type": "harmful_parallel_logic",
            "risk_level": "high",
            "files": [
                "office/mission_command/e15d_gov_mcp_outbound_adapter.py",
                "gov_mcp/server.py",
                "gov_mcp/router.py",
                "gov_mcp/README.md",
            ],
            "conflict_summary": "bridge-labs defines a future gov-mcp outbound adapter, but gov-mcp currently exposes governance tools and deterministic execution, not a real outbound provider adapter.",
            "recommended_resolution": "Do not proceed to real send-gated pilot until gov-mcp owns and tests the outbound adapter interface.",
        },
        {
            "overlap_id": "e15d_safety_guards_vs_e9_suppression_e8_stop_conditions",
            "duplicate_type": "old_router_needs_upgrade",
            "risk_level": "medium",
            "files": [
                "office/mission_command/e15d_outbound_safety_guards.py",
                "office/mission_command/e9_suppression_registry.py",
                "office/mission_command/e8_execution_gate.py",
            ],
            "conflict_summary": "Kill-switch/rate-limit/suppression logic overlaps with earlier suppression and execution gates.",
            "recommended_resolution": "Make suppression registry and E8 stop conditions canonical guard inputs for E15D outbound safety.",
        },
        {
            "overlap_id": "e15d_send_gated_queue_vs_e15a_owner_console",
            "duplicate_type": "intentional_evolution",
            "risk_level": "low",
            "files": [
                "office/mission_command/e15a_owner_execution_console.py",
                "office/mission_command/e15d_send_gated_pilot_queue.py",
            ],
            "conflict_summary": "E15D queue derives from E15A owner console to reduce owner manual burden.",
            "recommended_resolution": "Keep derivation explicit; do not let queue execute until gov-mcp adapter and owner authorization exist.",
        },
    ]
    return {
        "artifact_id": "e16x_duplicate_overlap_matrix",
        "base_head": EXPECTED_BASE_HEAD,
        "repo_scan_receipts_summary": {key: {"exists": value["exists"], "head": value["head"]} for key, value in scans.items()},
        "overlaps": overlaps,
        "highest_risk_overlaps": [item["overlap_id"] for item in overlaps if item["risk_level"] == "high"],
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_semantic_conflict_report() -> dict[str, Any]:
    conflicts = [
        {
            "conflict_id": "risk_tier_vs_capability_level",
            "severity": "high",
            "conflict": "E8 uses TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION for validation messages, action_authorization_router only allows Tier 2, while B2R/E15D language can look like capability level 5 / Tier 5.",
            "canonical_resolution": "Risk tier and capability level are separate. B2R Level 5 external_validation_message maps to risk_tier TIER_2 when it is low-volume, AI-transparent, non-binding validation messaging.",
            "blocking_for_real_send": True,
        },
        {
            "conflict_id": "execution_mode_enum",
            "severity": "medium",
            "conflict": "C2 modes prepare_only/owner_handoff/dry_run_local/pending_owner_approval/mcp_execute_after_activation overlap E15D modes draft_only/owner_handoff/send_gated_pending_authorization/send_gated_dry_run/gov_mcp_execute_after_activation.",
            "canonical_resolution": "Use one enum: deny, prepare_only, draft_only, owner_handoff, dry_run_local, send_gated_pending_authorization, send_gated_dry_run, gov_mcp_execute_after_activation. Treat mcp_execute_after_activation as deprecated alias.",
            "blocking_for_real_send": True,
        },
        {
            "conflict_id": "owner_approval_state_machine",
            "severity": "medium",
            "conflict": "owner_handoff, owner_review_required, activated envelope, authorization envelope, owner approval present, and constitutional hard gate are used as overlapping states.",
            "canonical_resolution": "Adopt state machine: proposed -> owner_review_required -> activated | rejected | revoked | expired, with constitutional_hard_gate_escalated as separate terminal escalation.",
            "blocking_for_real_send": True,
        },
        {
            "conflict_id": "feedback_semantics",
            "severity": "high",
            "conflict": "Public evidence, owner-reported feedback, customer response, signal fixtures, and CIEU writeback candidates risk being mixed.",
            "canonical_resolution": "Public evidence is not validation feedback. Fixtures are not actual feedback events. Only owner-confirmed external action plus valid customer/owner-recorded response can become validation feedback; CIEU writeback remains candidate until Y-star-gov eligibility passes.",
            "blocking_for_real_send": False,
        },
        {
            "conflict_id": "gov_mcp_boundary",
            "severity": "high",
            "conflict": "bridge-labs defines gov-mcp outbound adapter contract, but gov-mcp currently exposes governance/check/enforce surfaces and deterministic execution rather than a real outbound provider adapter.",
            "canonical_resolution": "E15D adapter stays prototype in bridge-labs until a gov-mcp promotion PR implements outbound dry-run/preflight/receipt schemas and tests. No real send-gated pilot should depend on bridge-labs-only adapter logic.",
            "blocking_for_real_send": True,
        },
    ]
    return {
        "artifact_id": "e16x_semantic_conflict_report",
        "base_head": EXPECTED_BASE_HEAD,
        "conflicts": conflicts,
        "unresolved_conflict_count": len([item for item in conflicts if item["blocking_for_real_send"]]),
        "real_e16c0_should_proceed_now": False,
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_canonical_taxonomy_proposal() -> dict[str, Any]:
    return {
        "artifact_id": "e16x_canonical_taxonomy_proposal",
        "risk_tier": [
            "TIER_0_INTERNAL",
            "TIER_1_PUBLIC_READ_ONLY",
            "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
            "TIER_3_PUBLIC_BROADCAST_OR_LANDING",
            "TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK",
        ],
        "capability_level": {
            "description": "Capability level describes autonomy maturity, not external risk.",
            "levels": [
                "LEVEL_0_INTERNAL_ONLY",
                "LEVEL_1_PUBLIC_READ_ONLY",
                "LEVEL_2_AUTHENTICATED_READ_ONLY",
                "LEVEL_3_AUTHENTICATED_DRAFT_OR_FORM_FILL_WITHOUT_SUBMIT",
                "LEVEL_4_LOW_RISK_SUBMISSION_OR_GOVERNED_PUBLICATION_WITHIN_ENVELOPE",
                "LEVEL_5_EXTERNAL_VALIDATION_MESSAGING_WITHIN_ENVELOPE",
                "LEVEL_6_FINANCIAL_LEGAL_CUSTOMER_SYSTEM_CORE_WRITEBACK_HARD_GATE",
            ],
        },
        "canonical_mapping": {
            "external_validation_message": {
                "capability_level": "LEVEL_5_EXTERNAL_VALIDATION_MESSAGING_WITHIN_ENVELOPE",
                "risk_tier_when_low_volume_transparent_non_binding": "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
                "risk_tier_when_public_broadcast": "TIER_3_PUBLIC_BROADCAST_OR_LANDING",
                "risk_tier_when_commercial_or_legal_commitment": "TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK",
            }
        },
        "capability_domain": [
            "external_validation_message",
            "feedback_capture",
            "authenticated_draft_creation",
            "publication_draft",
            "governed_publication",
            "low_risk_form_submission",
            "payment_or_contract_gate",
            "core_writeback_gate",
        ],
        "execution_mode": [
            "deny",
            "prepare_only",
            "draft_only",
            "owner_handoff",
            "dry_run_local",
            "send_gated_pending_authorization",
            "send_gated_dry_run",
            "gov_mcp_execute_after_activation",
        ],
        "execution_mode_aliases": {
            "mcp_execute_after_activation": "gov_mcp_execute_after_activation"
        },
        "owner_approval_state_machine": [
            "proposed",
            "owner_review_required",
            "activated",
            "rejected",
            "revoked",
            "expired",
            "constitutional_hard_gate_escalated",
        ],
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_router_consolidation_plan() -> dict[str, Any]:
    return {
        "artifact_id": "e16x_router_consolidation_plan",
        "canonical_now": {
            "risk_tier_source": "office/mission_command/e8_risk_controlled_action_model.py",
            "bridge_runtime_router": "office/mission_command/action_authorization_router.py",
            "progressive_domain_source": "office/mission_command/b2r_capability_domains.py",
            "outbound_policy_prototype": "office/mission_command/e15d_ygov_outbound_policy.py",
        },
        "decisions": [
            {
                "question": "Which router is canonical now?",
                "answer": "action_authorization_router remains the bridge-labs action authorization entrypoint, but it is incomplete for B2R/E15D.",
            },
            {
                "question": "Should action_authorization_router be upgraded?",
                "answer": "yes; it should understand capability_domain, capability_level, canonical execution_mode, and E15D outbound policy reason codes.",
            },
            {
                "question": "Should E15D policy call action_authorization_router?",
                "answer": "yes; E15D policy should call action_authorization_router before E16C-0, so outbound policy cannot bypass the older Tier 2 safety discipline.",
            },
            {
                "question": "Should B2R domains be source of truth?",
                "answer": "yes for progressive capability domains inside bridge-labs until promoted to Y-star-gov policy.",
            },
            {
                "question": "Should E8 risk model remain canonical?",
                "answer": "yes for bridge-labs risk tiers; capability levels must not replace risk tiers.",
            },
        ],
        "tests_required_before_e16c0": [
            "external_validation_message Level 5 maps to Tier 2 under low-volume transparent envelope",
            "E15D policy denies or owner-handoffs when router rejects",
            "mcp_execute_after_activation alias normalizes to gov_mcp_execute_after_activation",
            "owner approval state machine blocks send without activated envelope",
            "feedback fixture cannot become validation feedback or CIEU writeback",
        ],
        "recommended_next_action": "Implement router/taxonomy alignment before any real send-gated pilot.",
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_gov_mcp_promotion_plan(scans: Mapping[str, Any]) -> dict[str, Any]:
    gov_hits = scans["gov_mcp"]["capability_hits"]
    outbound_hits = gov_hits.get("outbound", [])
    has_real_provider = any(
        fragment in path.lower()
        for path in outbound_hits
        for fragment in ["email", "message_provider", "publication_provider", "form_submit", "outbound_adapter"]
    )
    return {
        "artifact_id": "e16x_gov_mcp_outbound_promotion_plan",
        "gov_mcp_currently_implements_outbound_provider_adapter": bool(has_real_provider),
        "current_gov_mcp_evidence": scans["gov_mcp"]["evidence_files"],
        "current_limitations": [
            "gov-mcp exposes gov_check/gov_enforce and contract lifecycle tools.",
            "README describes deterministic command execution and custom adapters for non-MCP integrations.",
            "No canonical live outbound email/message/publication/account/form provider adapter was confirmed by the static scan.",
        ],
        "bridge_labs_prototypes_to_promote": [
            "e15d_outbound_authorization_envelope.request.json",
            "e15d_gov_mcp_outbound_adapter_contract.json",
            "e15d_outbound_safety_guard_matrix.json",
            "e15d_outbound_audit_receipts.json",
            "canonical execution_mode enum",
        ],
        "minimal_gov_mcp_pr_before_real_e16c_send": [
            "Add outbound preflight tool or route that accepts Y*gov decision envelope and action intent packet.",
            "Add dry-run outbound execution receipt without provider send.",
            "Add suppression, kill-switch, rate-limit, and idempotency guards.",
            "Add provider adapter interface behind explicit disabled-by-default feature flag.",
            "Add tests proving no real send occurs unless activated envelope and adapter are present.",
        ],
        "tests_gov_mcp_should_own": [
            "adapter contract schema validation",
            "deny/allow/escalate result normalization",
            "kill-switch and suppression guard enforcement",
            "receipt hash/idempotency generation",
            "no-secret/no-credential-printing guarantees",
        ],
        "bridge_labs_should_continue_to_own": [
            "offer and target selection",
            "owner/business decision console",
            "message capsule drafting",
            "feedback interpretation and commercial learning candidates",
        ],
        "recommended_next_action": "Create E16G gov-mcp adapter promotion milestone before real send-gated pilot.",
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_route_reconciliation_packet() -> dict[str, Any]:
    routes = {
        "E16B_owner_manual_send_first": {
            "status": "available_lowest_operational_risk",
            "trigger": "owner wants first validation with no adapter dependency",
            "allowed_actions": ["owner manually sends approved E15A messages", "owner records ledger and feedback"],
            "blocked_actions": ["agent send", "provider API call", "publication", "form submission"],
        },
        "E16C0_one_action_send_gated_pilot_dry_run": {
            "status": "delay_or_revise_to_dry_run_only",
            "trigger": "router taxonomy conflicts resolved and gov-mcp promotion plan accepted",
            "allowed_actions": ["dry-run only", "no provider send"],
            "blocked_actions": ["real send until gov-mcp adapter exists and owner activates envelope"],
        },
        "E16C1_owner_activated_one_action_send_gated_pilot": {
            "status": "blocked_now",
            "trigger": "requires activated owner envelope and gov-mcp adapter implementation",
            "allowed_actions": [],
            "blocked_actions": ["real send-gated pilot today"],
        },
        "E16D_expand_evidence_before_any_send": {
            "status": "available_if_target_message_fit_weakens",
            "trigger": "target/message evidence is insufficient or owner wants more market evidence",
            "allowed_actions": ["public read-only evidence collection"],
            "blocked_actions": ["outbound actions"],
        },
        "E16G_cross_repo_gov_mcp_adapter_promotion_first": {
            "status": "recommended",
            "trigger": "semantic conflicts unresolved or gov-mcp lacks outbound adapter implementation",
            "allowed_actions": ["promote adapter contract to gov-mcp", "add dry-run adapter tests", "align router taxonomy"],
            "blocked_actions": ["real send before promotion"],
        },
    }
    return {
        "artifact_id": "e16x_route_reconciliation_packet",
        "recommended_route": "E16G_cross_repo_gov_mcp_adapter_promotion_first",
        "secondary_route": "E16B_owner_manual_send_first",
        "e16c0_should_proceed": False,
        "e16c0_reconciliation": "Delay and revise E16C-0 to dry-run only until taxonomy/router conflicts are fixed and gov-mcp owns the outbound adapter boundary.",
        "routes": routes,
        "decision_basis": [
            "Risk tier/capability-level semantics need canonicalization.",
            "Execution mode enum needs normalization.",
            "Owner activation state machine needs one source of truth.",
            "gov-mcp does not yet own a confirmed outbound provider adapter.",
            "bridge-labs E15D adapter remains a prototype contract, not execution authority.",
        ],
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_czl(scans: Mapping[str, Any], route_packet: Mapping[str, Any]) -> dict[str, Any]:
    all_scanned = all(item["exists"] for item in scans.values())
    return {
        "artifact_id": "e16x_czl_closure",
        "Y*": "cross-repo canonical ownership and outbound governance conflict resolution",
        "Xt": {
            "base_head": EXPECTED_BASE_HEAD,
            "repos": {key: {"exists": value["exists"], "head": value["head"]} for key, value in scans.items()},
            "e15d_remote_confirmed_base": True,
        },
        "U": [
            "read-only four-repo inventory",
            "canonical ownership map",
            "duplicate/overlap matrix",
            "semantic conflict detection",
            "canonical taxonomy proposal",
            "router consolidation plan",
            "gov-mcp outbound promotion plan",
            "E16 route reconciliation",
        ],
        "Yt+1": {
            "next_route": route_packet["recommended_route"],
            "selected_based_on_cross_repo_truth": True,
            "e16c0_revised_or_delayed": True,
            "no_real_outbound_action": True,
        },
        "Rt+1": 0 if all_scanned else 1,
        "residuals": [] if all_scanned else ["one_or_more_related_repos_missing"],
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def bullet_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_ownership(data: Mapping[str, Any]) -> str:
    lines = ["# E16X Cross-Repo Canonical Ownership", ""]
    for repo, payload in data["canonical_ownership"].items():
        lines.extend([f"## {repo}", "", "Owns:"])
        lines.append(bullet_list(payload["owns"]))
        lines.extend(["", "Evidence:"])
        lines.append(bullet_list(payload.get("evidence") or ["no direct evidence file found"]))
        lines.append("")
    lines.extend(["## Safety", "", f"- {data['no_external_side_effects']}", ""])
    return "\n".join(lines)


def render_duplicate_matrix(data: Mapping[str, Any]) -> str:
    lines = ["# E16X Duplicate / Overlap Matrix", ""]
    for item in data["overlaps"]:
        lines.extend(
            [
                f"## {item['overlap_id']}",
                f"- duplicate_type: {item['duplicate_type']}",
                f"- risk_level: {item['risk_level']}",
                f"- conflict_summary: {item['conflict_summary']}",
                f"- recommended_resolution: {item['recommended_resolution']}",
                "- files:",
                bullet_list(item["files"]),
                "",
            ]
        )
    return "\n".join(lines)


def render_semantic_conflicts(data: Mapping[str, Any]) -> str:
    lines = ["# E16X Semantic Conflict Report", ""]
    for item in data["conflicts"]:
        lines.extend(
            [
                f"## {item['conflict_id']}",
                f"- severity: {item['severity']}",
                f"- conflict: {item['conflict']}",
                f"- canonical_resolution: {item['canonical_resolution']}",
                f"- blocking_for_real_send: {str(item['blocking_for_real_send']).lower()}",
                "",
            ]
        )
    return "\n".join(lines)


def render_taxonomy(data: Mapping[str, Any]) -> str:
    mapping = data["canonical_mapping"]["external_validation_message"]
    lines = [
        "# E16X Canonical Taxonomy Proposal",
        "",
        "## Key Resolution",
        "",
        "B2R Level 5 external validation messaging is a capability maturity level, not risk Tier 5.",
        f"When low-volume, transparent, and non-binding, it maps to `{mapping['risk_tier_when_low_volume_transparent_non_binding']}`.",
        "",
        "## Risk Tiers",
        bullet_list(data["risk_tier"]),
        "",
        "## Execution Modes",
        bullet_list(data["execution_mode"]),
        "",
        f"- alias: mcp_execute_after_activation -> {data['execution_mode_aliases']['mcp_execute_after_activation']}",
        "",
    ]
    return "\n".join(lines)


def render_router_plan(data: Mapping[str, Any]) -> str:
    lines = ["# E16X Router Consolidation Plan", ""]
    lines.extend(f"- {key}: {value}" for key, value in data["canonical_now"].items())
    lines.append("")
    for decision in data["decisions"]:
        lines.extend([f"## {decision['question']}", decision["answer"], ""])
    lines.extend(["## Tests Required Before E16C-0", bullet_list(data["tests_required_before_e16c0"]), ""])
    return "\n".join(lines)


def render_gov_mcp_plan(data: Mapping[str, Any]) -> str:
    lines = [
        "# E16X gov-mcp Outbound Promotion Plan",
        "",
        f"- gov_mcp_currently_implements_outbound_provider_adapter: {str(data['gov_mcp_currently_implements_outbound_provider_adapter']).lower()}",
        f"- recommended_next_action: {data['recommended_next_action']}",
        "",
        "## Minimal gov-mcp PR Before Real E16C Send",
        bullet_list(data["minimal_gov_mcp_pr_before_real_e16c_send"]),
        "",
        "## bridge-labs Should Continue To Own",
        bullet_list(data["bridge_labs_should_continue_to_own"]),
        "",
    ]
    return "\n".join(lines)


def render_route_packet(data: Mapping[str, Any]) -> str:
    lines = [
        "# E16X Route Reconciliation Packet",
        "",
        f"- recommended_route: {data['recommended_route']}",
        f"- secondary_route: {data['secondary_route']}",
        f"- e16c0_should_proceed: {str(data['e16c0_should_proceed']).lower()}",
        f"- e16c0_reconciliation: {data['e16c0_reconciliation']}",
        "",
        "## Decision Basis",
        bullet_list(data["decision_basis"]),
        "",
    ]
    for route, payload in data["routes"].items():
        lines.extend([f"## {route}", f"- status: {payload['status']}", f"- trigger: {payload['trigger']}", ""])
    return "\n".join(lines)


def render_czl(data: Mapping[str, Any]) -> str:
    lines = [
        "# E16X CZL Closure",
        "",
        f"- Y*: {data['Y*']}",
        f"- Xt: base_head={data['Xt']['base_head']}",
        f"- U: {', '.join(data['U'])}",
        f"- Yt+1: next_route={data['Yt+1']['next_route']}, no_real_outbound_action={str(data['Yt+1']['no_real_outbound_action']).lower()}",
        f"- Rt+1: {data['Rt+1']}",
        "",
        "## Safety",
        f"- {data['no_external_side_effects']}",
        "",
    ]
    return "\n".join(lines)


def build_all() -> dict[str, Any]:
    scans = repo_receipts()
    ownership = build_cross_repo_canonical_ownership(scans)
    duplicates = build_duplicate_overlap_matrix(scans)
    conflicts = build_semantic_conflict_report()
    taxonomy = build_canonical_taxonomy_proposal()
    router_plan = build_router_consolidation_plan()
    gov_mcp_plan = build_gov_mcp_promotion_plan(scans)
    route_packet = build_route_reconciliation_packet()
    czl = build_czl(scans, route_packet)
    return {
        "ownership": ownership,
        "duplicates": duplicates,
        "conflicts": conflicts,
        "taxonomy": taxonomy,
        "router_plan": router_plan,
        "gov_mcp_plan": gov_mcp_plan,
        "route_packet": route_packet,
        "czl": czl,
    }


def write_artifacts(repo_root: Path, artifacts: Mapping[str, Any]) -> None:
    external = repo_root / "operations" / "external_validation"
    reports = repo_root / "reports" / "integration"

    write_json(external / "e16x_cross_repo_canonical_ownership.json", artifacts["ownership"])
    write_json(external / "e16x_duplicate_overlap_matrix.json", artifacts["duplicates"])
    write_json(external / "e16x_semantic_conflict_report.json", artifacts["conflicts"])
    write_json(external / "e16x_canonical_taxonomy_proposal.json", artifacts["taxonomy"])
    write_json(external / "e16x_router_consolidation_plan.json", artifacts["router_plan"])
    write_json(external / "e16x_gov_mcp_outbound_promotion_plan.json", artifacts["gov_mcp_plan"])
    write_json(external / "e16x_route_reconciliation_packet.json", artifacts["route_packet"])

    write_text(reports / "e16x_cross_repo_canonical_ownership.md", render_ownership(artifacts["ownership"]))
    write_text(reports / "e16x_duplicate_overlap_matrix.md", render_duplicate_matrix(artifacts["duplicates"]))
    write_text(reports / "e16x_semantic_conflict_report.md", render_semantic_conflicts(artifacts["conflicts"]))
    write_text(reports / "e16x_canonical_taxonomy_proposal.md", render_taxonomy(artifacts["taxonomy"]))
    write_text(reports / "e16x_router_consolidation_plan.md", render_router_plan(artifacts["router_plan"]))
    write_text(reports / "e16x_gov_mcp_outbound_promotion_plan.md", render_gov_mcp_plan(artifacts["gov_mcp_plan"]))
    write_text(reports / "e16x_route_reconciliation_packet.md", render_route_packet(artifacts["route_packet"]))
    write_text(reports / "e16x_czl_closure.md", render_czl(artifacts["czl"]))


def delivery_request(repo_root: Path) -> dict[str, Any]:
    allowed_files = [
        "scripts/create_e16x_cross_repo_governance_canonicalization.py",
        "operations/external_validation/e16x_cross_repo_canonical_ownership.json",
        "operations/external_validation/e16x_duplicate_overlap_matrix.json",
        "operations/external_validation/e16x_semantic_conflict_report.json",
        "operations/external_validation/e16x_canonical_taxonomy_proposal.json",
        "operations/external_validation/e16x_router_consolidation_plan.json",
        "operations/external_validation/e16x_gov_mcp_outbound_promotion_plan.json",
        "operations/external_validation/e16x_route_reconciliation_packet.json",
        "reports/integration/e16x_cross_repo_canonical_ownership.md",
        "reports/integration/e16x_duplicate_overlap_matrix.md",
        "reports/integration/e16x_semantic_conflict_report.md",
        "reports/integration/e16x_canonical_taxonomy_proposal.md",
        "reports/integration/e16x_router_consolidation_plan.md",
        "reports/integration/e16x_gov_mcp_outbound_promotion_plan.md",
        "reports/integration/e16x_route_reconciliation_packet.md",
        "reports/integration/e16x_czl_closure.md",
        "tests/office/test_e16x_cross_repo_canonical_ownership.py",
        "tests/office/test_e16x_duplicate_overlap_matrix.py",
        "tests/office/test_e16x_semantic_conflict_report.py",
        "tests/office/test_e16x_canonical_taxonomy_proposal.py",
        "tests/office/test_e16x_router_consolidation_plan.py",
        "tests/office/test_e16x_gov_mcp_outbound_promotion_plan.py",
        "tests/office/test_e16x_route_reconciliation_packet.py",
        "tests/office/test_e16x_czl_closure.py",
        "operations/repository_delivery/delivery_requests/e16x_cross_repo_governance_canonicalization_delivery.json",
    ]
    return {
        "request_id": "e16x_cross_repo_governance_canonicalization_delivery",
        "milestone_id": "E16X_cross_repo_governance_ownership_outbound_canonicalization_audit",
        "repo_root": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        "expected_branch": BRANCH,
        "expected_base_head": EXPECTED_BASE_HEAD,
        "expected_result_head_optional": "",
        "commit_message": "tools: add cross-repo governance canonicalization audit",
        "allowed_files": allowed_files,
        "forbidden_patterns": [
            "._*",
            "**/._*",
            ".DS_Store",
            "**/.DS_Store",
            "__MACOSX/**",
            "**/__MACOSX/**",
            "**/__pycache__/**",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.db",
            "**/*.sqlite",
            "**/*.sqlite3",
            "**/*.wal",
            "**/*.shm",
            "**/*.log",
            "**/active-agent*",
            "**/active_agent*",
        ],
        "ignored_dirty_patterns": [
            "operations/repository_delivery/delivery_reports/**"
        ],
        "validation_commands": [
            "python3.11 -m py_compile office/mission_command/*.py",
            "python3.11 -m py_compile scripts/*.py",
            "pytest tests/office/test_e16x_*.py -q",
            "pytest tests/office/test_e15d_*.py -q",
            "pytest tests/office/test_e15a_*.py -q",
            "pytest tests/office/test_c3_*.py -q",
            "pytest tests/office/test_c2_*.py -q",
            "pytest tests/office/test_c1_*.py -q",
            "pytest tests/office/test_b2r_*.py -q",
            "pytest tests/office/test_e14_*.py -q",
            "pytest tests/office/test_e12_*.py -q",
            "pytest tests/office/test_e12t_host_delivery_runner.py -q",
            "pytest tests/office/test_repository_delivery_*.py -q",
        ],
        "push_remote": "origin",
        "push_branch": BRANCH,
        "remote_confirmation_required": True,
        "created_by": "Codex E16X",
        "created_at": "2026-05-03T00:00:00+00:00",
        "safety_boundary": "E16X is read-only cross-repo governance ownership and outbound canonicalization audit. It produces reports, taxonomy, promotion plan, and route reconciliation only.",
        "no_external_side_effects_statement": SAFETY_STATEMENT,
        "cleanup_generated_bytecode": True,
    }


def write_delivery_request(repo_root: Path) -> None:
    request = delivery_request(repo_root)
    write_json(
        repo_root / "operations" / "repository_delivery" / "delivery_requests" / "e16x_cross_repo_governance_canonicalization_delivery.json",
        request,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E16X cross-repo governance canonicalization audit artifacts.")
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    artifacts = build_all()
    write_artifacts(repo_root, artifacts)
    write_delivery_request(repo_root)
    if args.json:
        print(json.dumps({"status": "generated", "route": artifacts["route_packet"]["recommended_route"]}, indent=2))
    else:
        print("generated E16X cross-repo governance canonicalization audit")
        print(f"recommended_route: {artifacts['route_packet']['recommended_route']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
