#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping


DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
YSTAR_COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
BRIDGE_BASE_HEAD = "7330fe1ebfa19a6fbbe9741d56f4bbcda898cce6"

SAFETY_STATEMENT = (
    "E16G performs code/static alignment and no-send/dry-run adapter promotion only. "
    "It performs no customer contact, email/message sending, publication, payment, account creation, "
    "form submission, login, external validation submission, customer system access, legal/financial "
    "commitment, credential disclosure, core brain/CIEU/memory writeback, real provider API call, "
    "real outbound adapter call, or real send receipt."
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_git(repo: Path, args: list[str]) -> str:
    if not repo.exists():
        return "missing"
    completed = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, timeout=30, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()


def repo_status(repo: Path) -> dict[str, Any]:
    return {
        "path": str(repo),
        "exists": repo.exists(),
        "branch": run_git(repo, ["branch", "--show-current"]),
        "head": run_git(repo, ["rev-parse", "HEAD"]),
        "last_commit": run_git(repo, ["log", "-1", "--oneline"]),
        "status_sample": run_git(repo, ["status", "--short"]).splitlines()[:30],
    }


def gov_mcp_outbound_paths() -> list[str]:
    paths = [
        "gov_mcp/outbound/__init__.py",
        "gov_mcp/outbound/models.py",
        "gov_mcp/outbound/policy.py",
        "gov_mcp/outbound/safety_guards.py",
        "gov_mcp/outbound/adapter_contract.py",
        "gov_mcp/outbound/dry_run_adapter.py",
        "gov_mcp/outbound/receipts.py",
        "gov_mcp/outbound/idempotency.py",
        "tests/test_outbound_models.py",
        "tests/test_outbound_policy.py",
        "tests/test_outbound_safety_guards.py",
        "tests/test_outbound_adapter_contract.py",
        "tests/test_outbound_dry_run_adapter.py",
        "tests/test_outbound_receipts.py",
        "tests/test_outbound_idempotency.py",
    ]
    return paths


def build_promotion_result(repo_root: Path) -> dict[str, Any]:
    plan = read_json(repo_root / "operations/external_validation/e16x_gov_mcp_outbound_promotion_plan.json")
    return {
        "artifact_id": "e16g_gov_mcp_adapter_promotion_result",
        "source_e16x_artifact": "operations/external_validation/e16x_gov_mcp_outbound_promotion_plan.json",
        "e16x_recommended_next_action": plan["recommended_next_action"],
        "gov_mcp_repo_status": repo_status(GOV_MCP_ROOT),
        "gov_mcp_canonical_outbound_paths": gov_mcp_outbound_paths(),
        "canonical_surface_promoted_to_gov_mcp": True,
        "provider_adapter_mode": "local_no_send",
        "real_provider_adapter_implemented": False,
        "real_send_enabled": False,
        "bridge_labs_e15d_adapter_status": "prototype_source_only",
        "ownership_after_e16g": {
            "gov_mcp": [
                "canonical outbound no-send adapter contract",
                "outbound preflight/dry-run/no-send receipts",
                "safety guard and idempotency model",
                "future provider adapter boundary",
            ],
            "ystar_bridge_labs": [
                "company runtime and commercial validation flow",
                "target/message/owner console/feedback artifacts",
                "route decision records and repository delivery evidence",
            ],
            "Y-star-gov": [
                "deterministic governance kernel",
                "IntentContract/ConstitutionalContract",
                "CIEU/core writeback eligibility standards",
            ],
        },
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_router_alignment(repo_root: Path) -> dict[str, Any]:
    router_plan = read_json(repo_root / "operations/external_validation/e16x_router_consolidation_plan.json")
    semantic = read_json(repo_root / "operations/external_validation/e16x_semantic_conflict_report.json")
    return {
        "artifact_id": "e16g_bridge_labs_router_alignment",
        "source_e16x_router_plan": router_plan["canonical_now"],
        "semantic_conflicts_addressed": [
            "risk_tier_vs_capability_level",
            "execution_mode_enum",
            "owner_approval_state_machine",
            "gov_mcp_boundary",
        ],
        "bridge_labs_runtime_changes": "no core runtime behavior changed in E16G; alignment is explicit artifact-level canonicalization",
        "router_alignment_rules": [
            "action_authorization_router remains bridge-labs local action authorization entrypoint.",
            "E8 risk tiers remain canonical for bridge-labs operational risk.",
            "B2R capability levels remain capability maturity, not risk tier.",
            "E15D outbound policy must reference the gov-mcp adapter contract before any E16C pilot.",
            "mcp_execute_after_activation is legacy alias; gov_mcp_execute_after_activation is canonical.",
            "Feedback fixtures cannot become validation feedback or CIEU writeback without action_id/ledger_id/feedback_event_id provenance.",
        ],
        "remaining_before_real_send": [
            "wire bridge-labs outbound policy to gov-mcp adapter once gov-mcp promotion commit is remote-confirmed",
            "add E16C dry-run integration test against gov_mcp.outbound",
            "obtain explicit owner authorization envelope before any real send-gated pilot",
        ],
        "real_e16c0_allowed_now": False,
        "semantic_conflict_count_from_e16x": semantic["unresolved_conflict_count"],
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_mapping(repo_root: Path) -> dict[str, Any]:
    taxonomy = read_json(repo_root / "operations/external_validation/e16x_canonical_taxonomy_proposal.json")
    return {
        "artifact_id": "e16g_risk_capability_execution_mapping",
        "source_e16x_taxonomy": "operations/external_validation/e16x_canonical_taxonomy_proposal.json",
        "risk_tier_rule": "RiskTier is operational risk; CapabilityLevel is autonomy/capability maturity.",
        "external_validation_message_mapping": {
            "capability_level": "LEVEL_5_EXTERNAL_VALIDATION_MESSAGING_WITHIN_ENVELOPE",
            "risk_tier": "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION",
            "conditions": [
                "low volume",
                "AI transparent",
                "opt-out present",
                "owner envelope constrained",
                "no payment/account/form/login/publication",
                "suppression checked",
            ],
        },
        "canonical_execution_mode": "gov_mcp_execute_after_activation",
        "legacy_aliases": taxonomy["execution_mode_aliases"],
        "owner_authorization_states": [
            "owner_review_required",
            "activation_preflight_passed",
            "activation_ready_but_not_approved",
            "activated",
            "revoked",
            "expired",
            "blocked_by_scope_mismatch",
            "blocked_by_hard_gate",
        ],
        "feedback_cieu_eligibility": {
            "public_evidence_is_validation_feedback": False,
            "owner_reported_feedback_status": "provisional_until_provenance_recorded",
            "customer_response_requires": ["action_id", "ledger_id", "feedback_event_id"],
            "core_cieu_writeback": "hard_gated",
        },
        "source_taxonomy_modes": taxonomy["execution_mode"],
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_route_update(repo_root: Path) -> dict[str, Any]:
    route = read_json(repo_root / "operations/external_validation/e16x_route_reconciliation_packet.json")
    return {
        "artifact_id": "e16g_e16_route_update_packet",
        "prior_recommended_route": route["recommended_route"],
        "e16g_result": "gov-mcp canonical no-send adapter contract prepared for repository delivery",
        "recommended_next_route": "E16C0_revised_one_action_send_gated_pilot_dry_run_only",
        "secondary_route": "E16B_owner_manual_send_first",
        "blocked_routes": {
            "E16C1_owner_activated_one_action_send_gated_pilot": "blocked until gov-mcp adapter is remote-confirmed, bridge-labs integration test exists, and owner activates envelope",
            "real_provider_send": "blocked; no real provider adapter call in E16G",
        },
        "why": [
            "E16G promotes no-send/dry-run adapter contract into gov-mcp.",
            "Real provider adapter is still intentionally absent.",
            "Bridge-labs now treats E15D adapter as prototype source and gov-mcp as canonical adapter owner.",
            "Next safe engineering route is dry-run-only E16C0 against gov_mcp.outbound, not real send.",
        ],
        "owner_hard_gate_remains_for": [
            "payment",
            "contract",
            "legal obligation",
            "financial commitment",
            "customer system access",
            "credential disclosure",
            "core brain/CIEU/memory canonical writeback",
        ],
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def build_czl(repo_root: Path, route_update: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "e16g_czl_closure",
        "Y*": "gov-mcp owns canonical outbound no-send adapter surface and bridge-labs aligns router/taxonomy/route semantics to that canonical boundary",
        "Xt": {
            "bridge_base_head": BRIDGE_BASE_HEAD,
            "e16x_delivery_report": "operations/repository_delivery/delivery_reports/e16x_cross_repo_governance_canonicalization_delivery.md",
            "gov_mcp_status": repo_status(GOV_MCP_ROOT),
            "Y_star_gov_status": repo_status(Y_GOV_ROOT),
            "ystar_company_status": repo_status(YSTAR_COMPANY_ROOT),
        },
        "U": [
            "read E16X promotion/taxonomy/router/semantic conflict artifacts",
            "promote no-send outbound adapter contract to gov-mcp",
            "generate bridge-labs router alignment artifacts",
            "generate risk/capability/execution mapping",
            "generate E16 route update packet",
        ],
        "Yt+1": {
            "gov_mcp_canonical_no_send_adapter_surface": True,
            "bridge_labs_uses_gov_mcp_as_canonical_adapter_owner": True,
            "real_external_action_executed": False,
            "next_route": route_update["recommended_next_route"],
        },
        "Rt+1": 0,
        "no_external_side_effects": SAFETY_STATEMENT,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_promotion(data: Mapping[str, Any]) -> str:
    return f"""# E16G gov-mcp Adapter Promotion Result

E16G promotes the no-send outbound adapter contract into gov-mcp as the canonical execution gateway surface. bridge-labs keeps the company validation runtime and no longer treats E15D's adapter contract as final execution authority.

- canonical_surface_promoted_to_gov_mcp: {str(data['canonical_surface_promoted_to_gov_mcp']).lower()}
- provider_adapter_mode: {data['provider_adapter_mode']}
- real_provider_adapter_implemented: {str(data['real_provider_adapter_implemented']).lower()}
- real_send_enabled: {str(data['real_send_enabled']).lower()}

## gov-mcp Canonical Paths
{bullets(data['gov_mcp_canonical_outbound_paths'])}

## Safety
- {data['no_external_side_effects']}
"""


def render_router_alignment(data: Mapping[str, Any]) -> str:
    return f"""# E16G Bridge-Labs Router Alignment

bridge-labs does not copy gov-mcp implementation. It records the canonical boundary and keeps company-specific validation artifacts local.

## Router Alignment Rules
{bullets(data['router_alignment_rules'])}

## Remaining Before Real Send
{bullets(data['remaining_before_real_send'])}

- real_e16c0_allowed_now: {str(data['real_e16c0_allowed_now']).lower()}
"""


def render_mapping(data: Mapping[str, Any]) -> str:
    mapping = data["external_validation_message_mapping"]
    return f"""# E16G Risk / Capability / Execution Mapping

RiskTier is operational risk. CapabilityLevel is progressive autonomy maturity.

- external_validation_message capability_level: {mapping['capability_level']}
- external_validation_message risk_tier: {mapping['risk_tier']}
- canonical_execution_mode: {data['canonical_execution_mode']}
- legacy_alias: mcp_execute_after_activation -> {data['legacy_aliases']['mcp_execute_after_activation']}

## Conditions
{bullets(mapping['conditions'])}
"""


def render_route(data: Mapping[str, Any]) -> str:
    return f"""# E16G E16 Route Update Packet

- prior_recommended_route: {data['prior_recommended_route']}
- recommended_next_route: {data['recommended_next_route']}
- secondary_route: {data['secondary_route']}

## Why
{bullets(data['why'])}

## Blocked Routes
{bullets([f"{key}: {value}" for key, value in data['blocked_routes'].items()])}
"""


def render_czl(data: Mapping[str, Any]) -> str:
    return f"""# E16G CZL Closure

- Y*: {data['Y*']}
- Xt: bridge_base_head={data['Xt']['bridge_base_head']}
- U: {', '.join(data['U'])}
- Yt+1: next_route={data['Yt+1']['next_route']}, real_external_action_executed={str(data['Yt+1']['real_external_action_executed']).lower()}
- Rt+1: {data['Rt+1']}

## Safety
- {data['no_external_side_effects']}
"""


def write_artifacts(repo_root: Path) -> dict[str, Any]:
    promotion = build_promotion_result(repo_root)
    router = build_router_alignment(repo_root)
    mapping = build_mapping(repo_root)
    route = build_route_update(repo_root)
    czl = build_czl(repo_root, route)

    external = repo_root / "operations" / "external_validation"
    reports = repo_root / "reports" / "integration"
    write_json(external / "e16g_gov_mcp_adapter_promotion_result.json", promotion)
    write_json(external / "e16g_bridge_labs_router_alignment.json", router)
    write_json(external / "e16g_risk_capability_execution_mapping.json", mapping)
    write_json(external / "e16g_e16_route_update_packet.json", route)
    write_text(reports / "e16g_gov_mcp_adapter_promotion_result.md", render_promotion(promotion))
    write_text(reports / "e16g_bridge_labs_router_alignment.md", render_router_alignment(router))
    write_text(reports / "e16g_risk_capability_execution_mapping.md", render_mapping(mapping))
    write_text(reports / "e16g_e16_route_update_packet.md", render_route(route))
    write_text(reports / "e16g_czl_closure.md", render_czl(czl))
    return {"promotion": promotion, "router": router, "mapping": mapping, "route": route, "czl": czl}


def delivery_request() -> dict[str, Any]:
    allowed_files = [
        "scripts/create_e16g_gov_mcp_adapter_promotion_alignment.py",
        "scripts/repository_delivery_transport.py",
        "scripts/repository_delivery_transport_doctor.py",
        "operations/external_validation/e16g_gov_mcp_adapter_promotion_result.json",
        "operations/external_validation/e16g_bridge_labs_router_alignment.json",
        "operations/external_validation/e16g_risk_capability_execution_mapping.json",
        "operations/external_validation/e16g_e16_route_update_packet.json",
        "operations/repository_delivery/delivery_reports/repository_delivery_transport_doctor.json",
        "operations/repository_delivery/delivery_reports/repository_delivery_transport_doctor.md",
        "reports/integration/e16g_gov_mcp_adapter_promotion_result.md",
        "reports/integration/e16g_bridge_labs_router_alignment.md",
        "reports/integration/e16g_risk_capability_execution_mapping.md",
        "reports/integration/e16g_e16_route_update_packet.md",
        "reports/integration/e16g_czl_closure.md",
        "tests/office/test_e16g_gov_mcp_adapter_promotion_result.py",
        "tests/office/test_e16g_bridge_labs_router_alignment.py",
        "tests/office/test_e16g_risk_capability_execution_mapping.py",
        "tests/office/test_e16g_route_update_packet.py",
        "tests/office/test_e16g_czl_closure.py",
        "tests/office/test_repository_delivery_transport_doctor.py",
        "operations/repository_delivery/delivery_requests/e16g_bridge_labs_router_alignment_delivery.json",
    ]
    return {
        "request_id": "e16g_bridge_labs_router_alignment_delivery",
        "milestone_id": "E16G_bridge_labs_router_alignment_to_gov_mcp_outbound_adapter",
        "repo_root": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "expected_base_head": BRIDGE_BASE_HEAD,
        "expected_result_head_optional": "",
        "commit_message": "tools: align outbound governance with gov-mcp canonical adapter",
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
        "ignored_dirty_patterns": ["operations/repository_delivery/delivery_reports/**"],
        "validation_commands": [
            "python3.11 -m py_compile office/mission_command/*.py",
            "python3.11 -m py_compile scripts/*.py",
            "pytest tests/office/test_e16g_*.py -q",
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
        "push_branch": "backflow/aiden-ceo-meeting-room",
        "remote_confirmation_required": True,
        "created_by": "Codex E16G",
        "created_at": "2026-05-03T00:00:00+00:00",
        "safety_boundary": "E16G bridge-labs alignment only; no real outbound action or provider call.",
        "no_external_side_effects_statement": SAFETY_STATEMENT,
        "cleanup_generated_bytecode": True,
    }


def write_delivery_request(repo_root: Path) -> None:
    write_json(
        repo_root / "operations/repository_delivery/delivery_requests/e16g_bridge_labs_router_alignment_delivery.json",
        delivery_request(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    artifacts = write_artifacts(repo_root)
    write_delivery_request(repo_root)
    if args.json:
        print(json.dumps({"status": "generated", "next_route": artifacts["route"]["recommended_next_route"]}, indent=2))
    else:
        print("generated E16G bridge-labs gov-mcp adapter promotion alignment artifacts")
        print(f"recommended_next_route: {artifacts['route']['recommended_next_route']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
