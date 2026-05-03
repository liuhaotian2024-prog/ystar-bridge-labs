#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(DEFAULT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(DEFAULT_REPO_ROOT))

from office.mission_command.e15d_controlled_outbound_domain import (
    build_e15d_controlled_outbound_domain,
    load_e15a_console,
    validate_e15d_controlled_outbound_domain,
)
from office.mission_command.e15d_czl_closure import build_e15d_czl_closure, validate_e15d_czl_closure
from office.mission_command.e15d_draft_only_execution_simulator import (
    build_e15d_draft_only_execution_receipts,
    validate_e15d_draft_only_execution_receipts,
)
from office.mission_command.e15d_e16_pilot_decision_packet import (
    build_e15d_e16_pilot_decision_packet,
    validate_e15d_e16_pilot_decision_packet,
)
from office.mission_command.e15d_gov_mcp_outbound_adapter import (
    build_e15d_gov_mcp_outbound_adapter_contract,
    validate_e15d_gov_mcp_outbound_adapter_contract,
)
from office.mission_command.e15d_outbound_audit_receipts import (
    build_e15d_outbound_audit_receipts,
    validate_e15d_outbound_audit_receipts,
)
from office.mission_command.e15d_outbound_authorization_envelope import (
    build_e15d_outbound_authorization_envelope_request,
    validate_e15d_outbound_authorization_envelope_request,
)
from office.mission_command.e15d_outbound_safety_guards import (
    build_e15d_outbound_safety_guard_matrix,
    validate_e15d_outbound_safety_guard_matrix,
)
from office.mission_command.e15d_send_gated_pilot_queue import (
    build_e15d_send_gated_pilot_queue,
    validate_e15d_send_gated_pilot_queue,
)
from office.mission_command.e15d_ygov_outbound_policy import (
    build_e15d_ygov_outbound_policy,
    validate_e15d_ygov_outbound_policy,
)


BASE_HEAD = "663925811432d7667efa291c1f73a9e49b2ac909"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_envelope(envelope: Mapping[str, Any]) -> str:
    return f"""# E15D Outbound Authorization Envelope Request

## 人话摘要

这是未来 E16 pilot 的窄授权请求，不是 owner approval。默认状态是 `{envelope['status']}`，所以 send-gated 执行仍然 blocked。

- draft_only_allowed_now: {str(envelope['draft_only_allowed_now']).lower()}
- send_allowed_now: {str(envelope['send_allowed_now']).lower()}
- max_actions_per_batch: {envelope['max_actions_per_batch']}
- max_actions_per_day: {envelope['max_actions_per_day']}

## Not Authorized

""" + "\n".join(f"- {item}" for item in envelope["not_authorized"]) + "\n"


def render_controlled_pilot_report(
    domain: Mapping[str, Any],
    envelope: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> str:
    lines = [
        "# E15D Controlled Outbound Execution Pilot",
        "",
        "E15D turns low-risk validation messaging into a governed capability instead of a permanent hard block or unrestricted send path.",
        "",
        f"- domain_state: {domain['current_state']}",
        f"- owner_authorization_present: {str(envelope['owner_authorization_present']).lower()}",
        f"- real_send_allowed_now: {str(domain['real_send_allowed_now']).lower()}",
        f"- policy_decisions: {len(policy['decisions'])}",
        "",
        "## Progressive Governed Domains",
    ]
    lines.extend(f"- {item}" for item in domain["progressive_governed_domains"])
    lines.extend(["", "## Hard Gates"])
    lines.extend(f"- {item}" for item in domain["hard_gates"])
    return "\n".join(lines).rstrip() + "\n"


def render_adapter_contract(contract: Mapping[str, Any]) -> str:
    lines = [
        "# E15D gov-mcp Outbound Adapter Contract",
        "",
        f"- gateway_owner: {contract['gateway_owner']}",
        f"- executes_real_external_action_in_e15d: {str(contract['executes_real_external_action_in_e15d']).lower()}",
        "",
        "## Execution Modes",
    ]
    lines.extend(f"- {mode}" for mode in contract["execution_modes"])
    lines.extend(["", "## Currently Executable In E15D"])
    lines.extend(f"- {mode}" for mode in contract["currently_executable_modes_in_e15d"])
    return "\n".join(lines).rstrip() + "\n"


def render_queue_report(receipts: Mapping[str, Any], queue: Mapping[str, Any]) -> str:
    lines = [
        "# E15D Draft-Only and Send-Gated Queue",
        "",
        f"- draft_receipts: {len(receipts['receipts'])}",
        f"- send_gated_rows: {len(queue['rows'])}",
        f"- blocked_until_authorized: {str(queue['blocked_until_authorized']).lower()}",
        "",
    ]
    for row in queue["rows"]:
        lines.append(f"- {row['action_id']}: mode={row['mcp_execution_mode']}, blocked={str(row['blocked_until_authorized']).lower()}")
    return "\n".join(lines).rstrip() + "\n"


def render_guard_report(guard_matrix: Mapping[str, Any], audit_receipts: Mapping[str, Any]) -> str:
    lines = [
        "# E15D Safety Guards and Audit Receipts",
        "",
        f"- guard_count: {len(guard_matrix['guards'])}",
        f"- audit_receipts: {len(audit_receipts['receipts'])}",
        f"- external_action_executed: {str(audit_receipts['external_action_executed']).lower()}",
        "",
        "## Guards",
    ]
    lines.extend(f"- {name}: {data['failure_effect']}" for name, data in guard_matrix["guards"].items())
    return "\n".join(lines).rstrip() + "\n"


def render_e16_packet(packet: Mapping[str, Any]) -> str:
    lines = [
        "# E15D E16 Controlled Pilot Decision Packet",
        "",
        f"- recommended_route: {packet['recommended_route']}",
        f"- recommendation_reason: {packet['recommendation_reason']}",
        "",
    ]
    for route_id, route in packet["routes"].items():
        lines.extend(
            [
                f"## {route_id}",
                f"- trigger: {route['trigger']}",
                f"- owner_involvement: {route['owner_involvement']}",
                f"- allowed_actions: {', '.join(route['allowed_actions'])}",
                f"- blocked_actions: {', '.join(route['blocked_actions'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_delivery_request(repo_root: Path) -> Path:
    allowed_files = [
        "office/mission_command/e15d_controlled_outbound_domain.py",
        "office/mission_command/e15d_outbound_authorization_envelope.py",
        "office/mission_command/e15d_ygov_outbound_policy.py",
        "office/mission_command/e15d_gov_mcp_outbound_adapter.py",
        "office/mission_command/e15d_draft_only_execution_simulator.py",
        "office/mission_command/e15d_send_gated_pilot_queue.py",
        "office/mission_command/e15d_outbound_safety_guards.py",
        "office/mission_command/e15d_outbound_audit_receipts.py",
        "office/mission_command/e15d_e16_pilot_decision_packet.py",
        "office/mission_command/e15d_czl_closure.py",
        "scripts/create_e15d_controlled_outbound_execution_pilot.py",
        "operations/external_validation/e15d_controlled_outbound_domain.json",
        "operations/external_validation/e15d_outbound_authorization_envelope.request.json",
        "operations/external_validation/e15d_outbound_authorization_envelope.request.md",
        "operations/external_validation/e15d_ygov_outbound_policy.json",
        "operations/external_validation/e15d_gov_mcp_outbound_adapter_contract.json",
        "operations/external_validation/e15d_draft_only_execution_receipts.json",
        "operations/external_validation/e15d_send_gated_pilot_queue.json",
        "operations/external_validation/e15d_outbound_safety_guard_matrix.json",
        "operations/external_validation/e15d_outbound_audit_receipts.json",
        "operations/external_validation/e15d_e16_controlled_pilot_decision_packet.json",
        "reports/integration/e15d_controlled_outbound_execution_pilot.md",
        "reports/integration/e15d_gov_mcp_outbound_adapter_contract.md",
        "reports/integration/e15d_draft_only_and_send_gated_queue.md",
        "reports/integration/e15d_safety_guards_and_audit_receipts.md",
        "reports/integration/e15d_e16_controlled_pilot_decision_packet.md",
        "reports/integration/e15d_czl_closure.md",
        "tests/office/test_e15d_controlled_outbound_domain.py",
        "tests/office/test_e15d_outbound_authorization_envelope.py",
        "tests/office/test_e15d_ygov_outbound_policy.py",
        "tests/office/test_e15d_gov_mcp_outbound_adapter.py",
        "tests/office/test_e15d_draft_only_execution_simulator.py",
        "tests/office/test_e15d_send_gated_pilot_queue.py",
        "tests/office/test_e15d_outbound_safety_guards.py",
        "tests/office/test_e15d_outbound_audit_receipts.py",
        "tests/office/test_e15d_e16_pilot_decision_packet.py",
        "tests/office/test_e15d_czl_closure.py",
        "operations/repository_delivery/delivery_requests/e15d_controlled_outbound_execution_pilot_delivery.json",
    ]
    request = {
        "request_id": "e15d_controlled_outbound_execution_pilot_delivery",
        "milestone_id": "E15D_y_gov_governed_controlled_outbound_execution_pilot_architecture",
        "repo_root": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "expected_base_head": BASE_HEAD,
        "expected_result_head_optional": "",
        "commit_message": "feat: add controlled outbound execution pilot architecture",
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
            "pytest tests/office/test_e15d_*.py -q",
            "pytest tests/office/test_e15a_*.py -q",
            "pytest tests/office/test_c3_*.py -q",
            "pytest tests/office/test_c2_*.py -q",
            "pytest tests/office/test_c1_*.py -q",
            "pytest tests/office/test_b2r_*.py -q",
            "pytest tests/office/test_e14_*.py -q",
            "pytest tests/office/test_e12_*.py -q",
            "pytest tests/office/test_repository_delivery_*.py -q",
            "pytest tests/office/test_e12t_host_delivery_runner.py -q",
        ],
        "push_remote": "origin",
        "push_branch": "backflow/aiden-ceo-meeting-room",
        "remote_confirmation_required": True,
        "created_by": "Codex E15D",
        "created_at": "2026-05-03T00:00:00+00:00",
        "safety_boundary": "E15D defines controlled outbound capability, authorization envelope request, Y*gov policy, gov-mcp adapter contract, draft-only receipts, send-gated queue, safety guards, audit receipts, and E16 decision packet. No real outbound action is executed.",
        "no_external_side_effects_statement": "E15D executes no real customer contact, email/message sending, publication, payment, account creation, form submission, login, external validation submission, customer system access, legal/financial commitment, credential disclosure, or core brain/CIEU/memory writeback.",
        "cleanup_generated_bytecode": True,
    }
    path = repo_root / "operations" / "repository_delivery" / "delivery_requests" / "e15d_controlled_outbound_execution_pilot_delivery.json"
    write_json(path, request)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    ops = root / "operations" / "external_validation"
    reports = root / "reports" / "integration"

    console = load_e15a_console(root)
    domain = build_e15d_controlled_outbound_domain(console)
    envelope = build_e15d_outbound_authorization_envelope_request(console, domain)
    policy = build_e15d_ygov_outbound_policy(console, envelope)
    adapter = build_e15d_gov_mcp_outbound_adapter_contract()
    draft_receipts = build_e15d_draft_only_execution_receipts(console, policy)
    guard_matrix = build_e15d_outbound_safety_guard_matrix(envelope)
    queue = build_e15d_send_gated_pilot_queue(console, envelope, policy, draft_receipts, guard_matrix)
    audit_receipts = build_e15d_outbound_audit_receipts(queue, envelope, guard_matrix)
    e16_packet = build_e15d_e16_pilot_decision_packet(console=console, queue=queue, audit_receipts=audit_receipts)
    closure = build_e15d_czl_closure(
        base_head=BASE_HEAD,
        domain=domain,
        envelope=envelope,
        policy=policy,
        adapter=adapter,
        draft_receipts=draft_receipts,
        queue=queue,
        guard_matrix=guard_matrix,
        audit_receipts=audit_receipts,
        e16_packet=e16_packet,
    ).to_dict()

    errors = (
        validate_e15d_controlled_outbound_domain(domain)
        + validate_e15d_outbound_authorization_envelope_request(envelope)
        + validate_e15d_ygov_outbound_policy(policy)
        + validate_e15d_gov_mcp_outbound_adapter_contract(adapter)
        + validate_e15d_draft_only_execution_receipts(draft_receipts)
        + validate_e15d_outbound_safety_guard_matrix(guard_matrix)
        + validate_e15d_send_gated_pilot_queue(queue)
        + validate_e15d_outbound_audit_receipts(audit_receipts)
        + validate_e15d_e16_pilot_decision_packet(e16_packet)
        + validate_e15d_czl_closure(closure)
    )
    if errors:
        raise SystemExit("E15D validation failed:\n" + "\n".join(errors))

    write_json(ops / "e15d_controlled_outbound_domain.json", domain)
    write_json(ops / "e15d_outbound_authorization_envelope.request.json", envelope)
    write_text(ops / "e15d_outbound_authorization_envelope.request.md", render_envelope(envelope))
    write_json(ops / "e15d_ygov_outbound_policy.json", policy)
    write_json(ops / "e15d_gov_mcp_outbound_adapter_contract.json", adapter)
    write_json(ops / "e15d_draft_only_execution_receipts.json", draft_receipts)
    write_json(ops / "e15d_send_gated_pilot_queue.json", queue)
    write_json(ops / "e15d_outbound_safety_guard_matrix.json", guard_matrix)
    write_json(ops / "e15d_outbound_audit_receipts.json", audit_receipts)
    write_json(ops / "e15d_e16_controlled_pilot_decision_packet.json", e16_packet)

    write_text(reports / "e15d_controlled_outbound_execution_pilot.md", render_controlled_pilot_report(domain, envelope, policy))
    write_text(reports / "e15d_gov_mcp_outbound_adapter_contract.md", render_adapter_contract(adapter))
    write_text(reports / "e15d_draft_only_and_send_gated_queue.md", render_queue_report(draft_receipts, queue))
    write_text(reports / "e15d_safety_guards_and_audit_receipts.md", render_guard_report(guard_matrix, audit_receipts))
    write_text(reports / "e15d_e16_controlled_pilot_decision_packet.md", render_e16_packet(e16_packet))
    write_text(
        reports / "e15d_czl_closure.md",
        "# E15D CZL Closure\n\n```json\n" + json.dumps(closure, indent=2, ensure_ascii=False) + "\n```\n",
    )
    write_delivery_request(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
