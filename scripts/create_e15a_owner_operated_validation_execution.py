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

from office.mission_command.e15a_czl_closure import build_e15a_czl_closure, validate_e15a_czl_closure
from office.mission_command.e15a_feedback_capture_pack import (
    build_e15a_feedback_capture_form,
    render_e15a_feedback_capture_form,
    validate_e15a_feedback_capture_form,
)
from office.mission_command.e15a_feedback_signal_evaluator import (
    build_e15a_feedback_signal_evaluation_fixture,
    validate_e15a_feedback_signal_fixture,
)
from office.mission_command.e15a_ledger_transition_runtime import (
    build_e15a_ledger_state_after_owner_handoff,
    build_e15a_ledger_transition_template,
    validate_e15a_ledger_state_after_owner_handoff,
)
from office.mission_command.e15a_owner_confirmation_packet import (
    build_e15a_owner_send_confirmation_fixture,
    build_e15a_owner_send_confirmation_template,
    validate_e15a_owner_send_confirmation_fixture,
)
from office.mission_command.e15a_owner_execution_console import (
    build_e15a_owner_execution_console,
    render_e15a_owner_execution_console,
    validate_e15a_owner_execution_console,
)
from office.mission_command.e15a_result_packet import build_e15a_result_packet, validate_e15a_result_packet
from office.mission_command.e15a_target_replacement_router import (
    build_e15a_target_replacement_plan,
    validate_e15a_target_replacement_plan,
)


BASE_HEAD = "518899d81c8f2612e1ec66c17dfead53dcd6e3e6"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_feedback_signal_report(fixture: Mapping[str, Any]) -> str:
    lines = [
        "# E15A Feedback Capture and Signal Loop",
        "",
        "E15A does not invent feedback. This fixture defines how later owner-entered replies will be normalized.",
        "",
    ]
    for case in fixture.get("cases", []):
        lines.extend(
            [
                f"## {case['feedback_type']}",
                f"- normalized_signal: {case['normalized_signal']}",
                f"- signal_strength: {case['signal_strength']}",
                f"- sales_implication: {case['sales_implication']}",
                f"- governance_implication: {case['governance_implication']}",
                f"- next_action_route: {case['next_action_route']}",
                "",
            ]
        )
    invalid = fixture.get("invalid_no_response_without_sent_ledger", {})
    lines.extend(
        [
            "## Invalid no_response",
            f"- normalized_signal: {invalid.get('normalized_signal')}",
            "- no_response is invalid unless owner has a real sent ledger and wait window.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_target_replacement_report(plan: Mapping[str, Any], result_packet: Mapping[str, Any]) -> str:
    lines = [
        "# E15A Target Replacement and Next Route",
        "",
        f"- default_route: {plan['default_route']}",
        f"- next_route_recommendation: {result_packet['next_route_recommendation']}",
        f"- recommendation_reason: {result_packet['recommendation_reason']}",
        "",
        "## Primary Routes",
    ]
    for row in plan.get("primary_routes", []):
        lines.append(f"- {row['target_name']}: {row['route']} ({row['reason']})")
    lines.extend(["", "## Fallback Pool"])
    for row in plan.get("fallback_pool", []):
        lines.append(f"- {row['target_name']}: {row['use_condition']}")
    return "\n".join(lines).rstrip() + "\n"


def render_result_packet(packet: Mapping[str, Any]) -> str:
    lines = [
        "# E15A Result Packet",
        "",
        f"- current_execution_status: {packet['current_execution_status']}",
        f"- next_route_recommendation: {packet['next_route_recommendation']}",
        f"- recommendation_reason: {packet['recommendation_reason']}",
        "",
        "## Ready For Owner Send",
    ]
    for action_id in packet.get("ready_for_owner_send_actions", []):
        lines.append(f"- `{action_id}`")
    lines.extend(["", "## Routes"])
    for route_id, route in packet.get("routes", {}).items():
        lines.extend(
            [
                f"### {route_id}",
                f"- trigger: {route['trigger']}",
                f"- allowed_actions: {', '.join(route['allowed_actions'])}",
                f"- blocked_actions: {', '.join(route['blocked_actions'])}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_delivery_request(repo_root: Path) -> Path:
    allowed_files = [
        "office/mission_command/e15a_owner_execution_console.py",
        "office/mission_command/e15a_owner_confirmation_packet.py",
        "office/mission_command/e15a_ledger_transition_runtime.py",
        "office/mission_command/e15a_feedback_capture_pack.py",
        "office/mission_command/e15a_feedback_signal_evaluator.py",
        "office/mission_command/e15a_target_replacement_router.py",
        "office/mission_command/e15a_result_packet.py",
        "office/mission_command/e15a_czl_closure.py",
        "scripts/create_e15a_owner_operated_validation_execution.py",
        "operations/external_validation/e15a_owner_execution_console.json",
        "operations/external_validation/e15a_owner_execution_console.md",
        "operations/external_validation/e15a_owner_send_confirmation_template.json",
        "operations/external_validation/e15a_owner_send_confirmation_fixture.json",
        "operations/external_validation/e15a_ledger_transition_template.json",
        "operations/external_validation/e15a_ledger_state_after_owner_handoff.json",
        "operations/external_validation/e15a_feedback_capture_form.json",
        "operations/external_validation/e15a_feedback_capture_form.md",
        "operations/external_validation/e15a_feedback_signal_evaluation_fixture.json",
        "operations/external_validation/e15a_target_replacement_plan.json",
        "operations/external_validation/e15a_result_packet.json",
        "reports/integration/e15a_owner_operated_validation_execution.md",
        "reports/integration/e15a_feedback_capture_and_signal_loop.md",
        "reports/integration/e15a_target_replacement_and_next_route.md",
        "reports/integration/e15a_result_packet.md",
        "reports/integration/e15a_czl_closure.md",
        "tests/office/test_e15a_owner_execution_console.py",
        "tests/office/test_e15a_owner_confirmation_packet.py",
        "tests/office/test_e15a_ledger_transition_runtime.py",
        "tests/office/test_e15a_feedback_capture_pack.py",
        "tests/office/test_e15a_feedback_signal_evaluator.py",
        "tests/office/test_e15a_target_replacement_router.py",
        "tests/office/test_e15a_result_packet.py",
        "tests/office/test_e15a_czl_closure.py",
        "operations/repository_delivery/delivery_requests/e15a_owner_operated_validation_execution_delivery.json",
    ]
    request = {
        "request_id": "e15a_owner_operated_validation_execution_delivery",
        "milestone_id": "E15A_owner_operated_first_validation_execution_feedback_capture",
        "repo_root": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "expected_base_head": BASE_HEAD,
        "expected_result_head_optional": "",
        "commit_message": "feat: add owner-operated validation execution loop",
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
        "created_by": "Codex E15A",
        "created_at": "2026-05-03T00:00:00+00:00",
        "safety_boundary": "E15A creates owner execution console, confirmation template, ledger transition, feedback capture, signal evaluation, replacement routing, result packet, and CZL. No agent/Codex external action is executed.",
        "no_external_side_effects_statement": "E15A executes no customer contact by agent, email/message sending by agent, publication, payment, account creation, form submission, login, external validation submission, customer system access, legal/financial commitment, credential disclosure, or core brain/CIEU/memory writeback.",
        "cleanup_generated_bytecode": True,
    }
    path = repo_root / "operations" / "repository_delivery" / "delivery_requests" / "e15a_owner_operated_validation_execution_delivery.json"
    write_json(path, request)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    ops = root / "operations" / "external_validation"
    reports = root / "reports" / "integration"

    console = build_e15a_owner_execution_console(root)
    confirmation_template = build_e15a_owner_send_confirmation_template(console)
    confirmation_fixture = build_e15a_owner_send_confirmation_fixture(console)
    ledger_template = build_e15a_ledger_transition_template()
    ledger_state = build_e15a_ledger_state_after_owner_handoff(console, confirmation_fixture)
    feedback_form = build_e15a_feedback_capture_form(console)
    signal_fixture = build_e15a_feedback_signal_evaluation_fixture()
    replacement_plan = build_e15a_target_replacement_plan(console, confirmation_fixture)
    result_packet = build_e15a_result_packet(
        console=console,
        ledger_state=ledger_state,
        feedback_form=feedback_form,
        signal_fixture=signal_fixture,
        replacement_plan=replacement_plan,
    )
    closure = build_e15a_czl_closure(
        base_head=BASE_HEAD,
        console=console,
        confirmation_fixture=confirmation_fixture,
        ledger_state=ledger_state,
        feedback_form=feedback_form,
        signal_fixture=signal_fixture,
        replacement_plan=replacement_plan,
        result_packet=result_packet,
    ).to_dict()

    validation_errors = (
        validate_e15a_owner_execution_console(console)
        + validate_e15a_owner_send_confirmation_fixture(confirmation_fixture)
        + validate_e15a_ledger_state_after_owner_handoff(ledger_state)
        + validate_e15a_feedback_capture_form(feedback_form)
        + validate_e15a_feedback_signal_fixture(signal_fixture)
        + validate_e15a_target_replacement_plan(replacement_plan)
        + validate_e15a_result_packet(result_packet)
        + validate_e15a_czl_closure(closure)
    )
    if validation_errors:
        raise SystemExit("E15A validation failed:\n" + "\n".join(validation_errors))

    write_json(ops / "e15a_owner_execution_console.json", console)
    write_text(ops / "e15a_owner_execution_console.md", render_e15a_owner_execution_console(console))
    write_json(ops / "e15a_owner_send_confirmation_template.json", confirmation_template)
    write_json(ops / "e15a_owner_send_confirmation_fixture.json", confirmation_fixture)
    write_json(ops / "e15a_ledger_transition_template.json", ledger_template)
    write_json(ops / "e15a_ledger_state_after_owner_handoff.json", ledger_state)
    write_json(ops / "e15a_feedback_capture_form.json", feedback_form)
    write_text(ops / "e15a_feedback_capture_form.md", render_e15a_feedback_capture_form(feedback_form))
    write_json(ops / "e15a_feedback_signal_evaluation_fixture.json", signal_fixture)
    write_json(ops / "e15a_target_replacement_plan.json", replacement_plan)
    write_json(ops / "e15a_result_packet.json", result_packet)

    write_text(reports / "e15a_owner_operated_validation_execution.md", render_e15a_owner_execution_console(console))
    write_text(reports / "e15a_feedback_capture_and_signal_loop.md", render_feedback_signal_report(signal_fixture))
    write_text(reports / "e15a_target_replacement_and_next_route.md", render_target_replacement_report(replacement_plan, result_packet))
    write_text(reports / "e15a_result_packet.md", render_result_packet(result_packet))
    write_text(
        reports / "e15a_czl_closure.md",
        "# E15A CZL Closure\n\n```json\n" + json.dumps(closure, indent=2, ensure_ascii=False) + "\n```\n",
    )
    write_delivery_request(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
