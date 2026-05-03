#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(DEFAULT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(DEFAULT_REPO_ROOT))

from office.mission_command.c2_action_queue import build_c2_action_queue, validate_c2_action_queue
from office.mission_command.c2_constitutional_activation import build_c2_activation_packet, validate_c2_activation_packet
from office.mission_command.c2_czl_closure import build_c2_czl_closure, validate_c2_czl_closure
from office.mission_command.c2_feedback_loop import (
    build_c2_feedback_ingestion_template,
    build_c2_signal_loop_fixture,
    validate_c2_feedback_template,
)
from office.mission_command.c2_gov_mcp_execution_control import (
    build_c2_gov_mcp_execution_control,
    validate_c2_execution_control,
)
from office.mission_command.c2_owner_handoff_capsule import (
    build_c2_owner_handoff_capsule,
    render_c2_owner_handoff_capsule,
    validate_c2_owner_handoff_capsule,
)


BASE_HEAD = "27f96e969e688422761d3e18572a3c5008298ba9"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_activation_packet(packet: dict[str, Any]) -> str:
    return f"""# C2 Constitutional Activation Packet

## 人话摘要

C2 没有把 C1 的 request 伪装成 approval。当前状态是 `{packet['activation_state']}`：系统可以模拟决策、生成 owner-handoff capsule、准备 action queue 和 feedback schema，但不能标记任何外部动作已执行。

## Boundary

- owner_approval_present: {str(packet['owner_approval_present']).lower()}
- live_external_execution_approved: {str(packet['live_external_execution_approved']).lower()}
- source_envelope_id: {packet['source_envelope_id']}
- hard_owner_gates: {', '.join(packet['owner_hard_gates'])}
"""


def render_loop_report(queue: dict[str, Any]) -> str:
    lines = [
        "# C2 Governed First Action Activation Loop",
        "",
        "## Human Summary",
        "",
        "C2 turns C1 readiness into a local, deterministic activation loop: owner constitutional boundary -> Y*gov decision -> gov-mcp execution control -> governed action queue -> owner handoff capsule -> local ledger/feedback schema -> signal evaluation -> next action recommendation.",
        "",
        "No live external action is executed in C2.",
        "",
        "## Queue",
        f"- queue_id: {queue['queue_id']}",
        f"- offer_thesis: {queue['offer_thesis']}",
        f"- primary_candidate_count: {queue['primary_candidate_count']}",
        f"- fallback_candidate_count: {queue['fallback_candidate_count']}",
        "",
        "## Candidates",
    ]
    for candidate in queue["candidates"]:
        lines.extend(
            [
                f"### {candidate['action_id']}",
                f"- target_id: {candidate['target_id']}",
                f"- priority: {candidate['priority']}",
                f"- ygov_decision: {candidate['ygov_decision']['decision']}",
                f"- gov_mcp_execution_mode: {candidate['gov_mcp_execution_mode']}",
                f"- owner_boundary_status: {candidate['owner_boundary_status']}",
                f"- external_action_executed: {str(candidate['external_action_executed']).lower()}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_execution_control_report(contracts: dict[str, Any]) -> str:
    lines = [
        "# C2 Y*gov / gov-mcp Execution Control",
        "",
        "C2 only runs `prepare_only`, `dry_run_local`, `owner_handoff`, `pending_owner_approval`, or `deny`. Future `mcp_execute_after_activation` remains a contract mode, not a live action in this milestone.",
        "",
    ]
    for item in contracts["contracts"]:
        lines.extend(
            [
                f"## {item['action_id']}",
                f"- contract_id: {item['contract_id']}",
                f"- execution_mode: {item['execution_mode']}",
                f"- ledger_write: {item['ledger_write']}",
                f"- feedback_wait_state: {item['feedback_wait_state']}",
                f"- external_action_executed: {str(item['external_action_executed']).lower()}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_feedback_report(template: dict[str, Any], fixture: dict[str, Any]) -> str:
    return f"""# C2 Owner Handoff and Feedback Loop

## Feedback Template

- public_evidence_is_not_validation_feedback: {str(template['public_evidence_is_not_validation_feedback']).lower()}
- no_response_requires_valid_action_ledger: {str(template['no_response_requires_valid_action_ledger']).lower()}

## Signal Fixture

- classification_count: {len(fixture['classifications'])}
- invalid_example_count: {len(fixture['invalid_examples'])}

Feedback can recommend follow-up, suppression, offer revision, or E15 review, but only after a valid action ledger exists.
"""


def write_delivery_request(repo_root: Path) -> Path:
    allowed_files = [
        "office/mission_command/c2_constitutional_activation.py",
        "office/mission_command/c2_ygov_action_decision.py",
        "office/mission_command/c2_gov_mcp_execution_control.py",
        "office/mission_command/c2_action_queue.py",
        "office/mission_command/c2_owner_handoff_capsule.py",
        "office/mission_command/c2_feedback_loop.py",
        "office/mission_command/c2_czl_closure.py",
        "scripts/create_c2_governed_action_activation_loop.py",
        "operations/external_validation/c2_constitutional_activation_packet.json",
        "operations/external_validation/c2_constitutional_activation_packet.md",
        "operations/external_validation/c2_ygov_decision_envelopes.json",
        "operations/external_validation/c2_gov_mcp_execution_contracts.json",
        "operations/external_validation/c2_governed_action_queue.json",
        "operations/external_validation/c2_owner_handoff_execution_capsule.json",
        "operations/external_validation/c2_owner_handoff_execution_capsule.md",
        "operations/external_validation/c2_feedback_ingestion_template.json",
        "operations/external_validation/c2_signal_loop_fixture.json",
        "reports/integration/c2_governed_first_action_activation_loop.md",
        "reports/integration/c2_y_gov_gov_mcp_execution_control.md",
        "reports/integration/c2_owner_handoff_and_feedback_loop.md",
        "reports/integration/c2_czl_closure.md",
        "tests/office/test_c2_constitutional_activation.py",
        "tests/office/test_c2_ygov_action_decision.py",
        "tests/office/test_c2_gov_mcp_execution_control.py",
        "tests/office/test_c2_action_queue.py",
        "tests/office/test_c2_owner_handoff_capsule.py",
        "tests/office/test_c2_feedback_loop.py",
        "tests/office/test_c2_czl_closure.py",
        "operations/repository_delivery/delivery_requests/c2_governed_first_action_activation_loop_delivery.json",
    ]
    request = {
        "request_id": "c2_governed_first_action_activation_loop_delivery",
        "milestone_id": "C2_governed_first_action_activation_loop",
        "repo_root": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "expected_base_head": BASE_HEAD,
        "expected_result_head_optional": "",
        "commit_message": "feat: add governed first action activation loop",
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
        "created_by": "Codex C2",
        "created_at": "2026-05-03T00:00:00+00:00",
        "safety_boundary": "C2 creates governed first action activation loop artifacts only; host_delivery_runner validates dirty set, tests, commit, push, and remote SHA confirmation. No live external action is executed.",
        "no_external_side_effects_statement": "C2 executes no customer contact, email/message sending, publication, payment, account creation, form submission, login, external validation submission, customer system access, legal/financial commitment, credential disclosure, or core brain/CIEU/memory writeback.",
        "cleanup_generated_bytecode": True,
    }
    path = repo_root / "operations" / "repository_delivery" / "delivery_requests" / "c2_governed_first_action_activation_loop_delivery.json"
    write_json(path, request)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    ops = root / "operations" / "external_validation"
    reports = root / "reports" / "integration"

    activation = build_c2_activation_packet(root).to_dict()
    queue = build_c2_action_queue(root, activation)
    decisions = [candidate["ygov_decision"] for candidate in queue["candidates"]]
    contracts = {"contracts": [build_c2_gov_mcp_execution_control(decision).to_dict() for decision in decisions]}
    capsule = build_c2_owner_handoff_capsule(queue).to_dict()
    feedback_template = build_c2_feedback_ingestion_template()
    signal_fixture = build_c2_signal_loop_fixture()
    closure = build_c2_czl_closure(
        base_head=BASE_HEAD,
        activation_packet=activation,
        action_queue=queue,
        handoff_capsule=capsule,
        feedback_template_valid=validate_c2_feedback_template(feedback_template) == [],
    ).to_dict()

    validation_errors = (
        validate_c2_activation_packet(activation)
        + validate_c2_action_queue(queue)
        + [error for contract in contracts["contracts"] for error in validate_c2_execution_control(contract)]
        + validate_c2_owner_handoff_capsule(capsule)
        + validate_c2_feedback_template(feedback_template)
        + validate_c2_czl_closure(closure)
    )
    if validation_errors:
        raise SystemExit("C2 validation failed:\n" + "\n".join(validation_errors))

    write_json(ops / "c2_constitutional_activation_packet.json", activation)
    write_text(ops / "c2_constitutional_activation_packet.md", render_activation_packet(activation))
    write_json(ops / "c2_ygov_decision_envelopes.json", {"decisions": decisions})
    write_json(ops / "c2_gov_mcp_execution_contracts.json", contracts)
    write_json(ops / "c2_governed_action_queue.json", queue)
    write_json(ops / "c2_owner_handoff_execution_capsule.json", capsule)
    write_text(ops / "c2_owner_handoff_execution_capsule.md", render_c2_owner_handoff_capsule(capsule))
    write_json(ops / "c2_feedback_ingestion_template.json", feedback_template)
    write_json(ops / "c2_signal_loop_fixture.json", signal_fixture)
    write_text(reports / "c2_governed_first_action_activation_loop.md", render_loop_report(queue))
    write_text(reports / "c2_y_gov_gov_mcp_execution_control.md", render_execution_control_report(contracts))
    write_text(reports / "c2_owner_handoff_and_feedback_loop.md", render_feedback_report(feedback_template, signal_fixture))
    write_text(
        reports / "c2_czl_closure.md",
        "# C2 CZL Closure\n\n```json\n" + json.dumps(closure, indent=2, ensure_ascii=False) + "\n```\n",
    )
    write_delivery_request(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
