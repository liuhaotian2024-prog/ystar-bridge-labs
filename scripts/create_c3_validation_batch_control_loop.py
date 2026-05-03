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

from office.mission_command.c3_action_ledger_state import (
    build_c3_action_ledger_state_fixture,
    build_c3_action_ledger_state_template,
    validate_c3_action_ledger_state_fixture,
)
from office.mission_command.c3_czl_closure import build_c3_czl_closure, validate_c3_czl_closure
from office.mission_command.c3_decision_replay import replay_c3_decisions, validate_c3_decision_replay_report
from office.mission_command.c3_dry_run_execution_receipts import build_c3_dry_run_receipts, validate_c3_dry_run_receipts
from office.mission_command.c3_e15_next_action_packet import build_c3_e15_next_action_packet, validate_c3_e15_next_action_packet
from office.mission_command.c3_feedback_intake_runtime import (
    build_c3_feedback_intake_template,
    build_c3_feedback_signal_fixture,
    validate_c3_feedback_intake_template,
)
from office.mission_command.c3_narrow_constitutional_envelope import (
    build_c3_narrow_envelope,
    validate_c3_narrow_envelope,
)
from office.mission_command.c3_owner_handoff_execution_batch import (
    build_c3_owner_handoff_batch,
    render_c3_owner_handoff_batch,
    validate_c3_owner_handoff_batch,
)
from office.mission_command.c3_validation_batch_selector import build_c3_validation_batch, validate_c3_validation_batch


BASE_HEAD = "73d0f9513b2481ba0693ee355736094a05b30563"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_narrow_envelope(envelope: Mapping[str, Any]) -> str:
    return f"""# C3 Narrow Constitutional Activation

## 人话摘要

C3 没有伪造 owner approval。当前 envelope 是 `{envelope['status']}`，只允许 owner-handoff 和 local dry-run。它不允许 agent 直接发送消息，也不允许 login / form submission / publication / account creation / payment / contract / core writeback。

## Scope

- allowed_scope: {', '.join(envelope['allowed_scope'])}
- allowed_execution_modes: {', '.join(envelope['allowed_execution_modes'])}
- agent_direct_execution_allowed: {str(envelope['agent_direct_execution_allowed']).lower()}
- external_action_executed: {str(envelope['external_action_executed']).lower()}
"""


def render_batch_report(batch: Mapping[str, Any]) -> str:
    lines = [
        "# C3 First Governed Validation Batch",
        "",
        "C3 selects the first owner-handoff validation batch from the C2 action queue. It does not send anything.",
        "",
        f"- batch_id: {batch['batch_id']}",
        f"- offer_thesis: {batch['offer_thesis']}",
        f"- primary_count: {batch['primary_count']}",
        f"- fallback_count: {batch['fallback_count']}",
        f"- suppression_candidate_count: {batch['suppression_candidate_count']}",
        f"- excluded_count: {batch['excluded_count']}",
        "",
    ]
    for action in batch["actions"]:
        lines.extend(
            [
                f"## {action['action_id']}",
                f"- role: {action['role']}",
                f"- target: {action['target_name']} ({action['target_id']})",
                f"- mode: {action['gov_mcp_execution_mode']}",
                f"- ledger_id: {action['ledger_id']}",
                f"- feedback_event_id: {action['feedback_event_id']}",
                f"- route: {action['next_action_route']}",
                f"- reason: {action['selection_reason']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_replay_report(report: Mapping[str, Any]) -> str:
    lines = [
        "# C3 Decision Replay and Consistency",
        "",
        f"- all_consistent: {str(report['all_consistent']).lower()}",
        f"- external_action_executed: {str(report['external_action_executed']).lower()}",
        "",
    ]
    for record in report["records"]:
        lines.extend(
            [
                f"## {record['action_id']}",
                f"- replay_decision: {record['replay_decision']}",
                f"- mode: {record['gov_mcp_execution_mode']}",
                f"- owner_handoff_only: {str(record['owner_handoff_only']).lower()}",
                f"- reason_codes: {', '.join(record['deterministic_reason_codes'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_feedback_report(template: Mapping[str, Any], fixture: Mapping[str, Any]) -> str:
    return f"""# C3 Feedback Intake and Signal Loop

## Template Boundary

- public_evidence_is_not_feedback: {str(template['public_evidence_is_not_feedback']).lower()}
- no_response_requires_valid_action_ledger: {str(template['no_response_requires_valid_action_ledger']).lower()}

## Fixture

- examples: {len(fixture['examples'])}

The feedback runtime normalizes owner-later feedback into signal strength, sales implication, governance implication, next action, offer revision, suppression, and owner escalation flags.
"""


def render_e15_packet(packet: Mapping[str, Any]) -> str:
    lines = [
        "# C3 E15 Next-Action Decision Packet",
        "",
        f"- recommended_route: {packet['recommended_route']}",
        f"- why_recommended: {packet['why_recommended']}",
        "",
    ]
    for route_id, route in packet["routes"].items():
        lines.extend(
            [
                f"## {route_id}: {route['name']}",
                f"- trigger_condition: {route['trigger_condition']}",
                f"- owner_involvement_level: {route['owner_involvement_level']}",
                f"- expected_next_repository_milestone: {route['expected_next_repository_milestone']}",
                f"- allowed_actions: {', '.join(route['allowed_actions'])}",
                f"- blocked_actions: {', '.join(route['blocked_actions'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_delivery_request(repo_root: Path) -> Path:
    allowed_files = [
        "office/mission_command/c3_narrow_constitutional_envelope.py",
        "office/mission_command/c3_validation_batch_selector.py",
        "office/mission_command/c3_decision_replay.py",
        "office/mission_command/c3_owner_handoff_execution_batch.py",
        "office/mission_command/c3_dry_run_execution_receipts.py",
        "office/mission_command/c3_action_ledger_state.py",
        "office/mission_command/c3_feedback_intake_runtime.py",
        "office/mission_command/c3_e15_next_action_packet.py",
        "office/mission_command/c3_czl_closure.py",
        "scripts/create_c3_validation_batch_control_loop.py",
        "operations/external_validation/c3_narrow_constitutional_envelope.json",
        "operations/external_validation/c3_narrow_constitutional_envelope.md",
        "operations/external_validation/c3_validation_batch.json",
        "operations/external_validation/c3_decision_replay_report.json",
        "operations/external_validation/c3_owner_handoff_validation_batch.json",
        "operations/external_validation/c3_owner_handoff_validation_batch.md",
        "operations/external_validation/c3_dry_run_execution_receipts.json",
        "operations/external_validation/c3_action_ledger_state_template.json",
        "operations/external_validation/c3_action_ledger_state_fixture.json",
        "operations/external_validation/c3_feedback_intake_template.json",
        "operations/external_validation/c3_feedback_signal_fixture.json",
        "operations/external_validation/c3_e15_next_action_decision_packet.json",
        "reports/integration/c3_narrow_constitutional_activation.md",
        "reports/integration/c3_first_governed_validation_batch.md",
        "reports/integration/c3_decision_replay_and_consistency.md",
        "reports/integration/c3_owner_handoff_execution_batch.md",
        "reports/integration/c3_feedback_intake_and_signal_loop.md",
        "reports/integration/c3_e15_next_action_decision_packet.md",
        "reports/integration/c3_czl_closure.md",
        "tests/office/test_c3_narrow_constitutional_envelope.py",
        "tests/office/test_c3_validation_batch_selector.py",
        "tests/office/test_c3_decision_replay.py",
        "tests/office/test_c3_owner_handoff_execution_batch.py",
        "tests/office/test_c3_dry_run_execution_receipts.py",
        "tests/office/test_c3_action_ledger_state.py",
        "tests/office/test_c3_feedback_intake_runtime.py",
        "tests/office/test_c3_e15_next_action_packet.py",
        "tests/office/test_c3_czl_closure.py",
        "operations/repository_delivery/delivery_requests/c3_validation_batch_control_loop_delivery.json",
    ]
    request = {
        "request_id": "c3_validation_batch_control_loop_delivery",
        "milestone_id": "C3_narrow_constitutional_activation_first_validation_batch",
        "repo_root": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "expected_base_head": BASE_HEAD,
        "expected_result_head_optional": "",
        "commit_message": "feat: add first governed validation batch control loop",
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
        "created_by": "Codex C3",
        "created_at": "2026-05-03T00:00:00+00:00",
        "safety_boundary": "C3 creates owner-handoff-only validation batch control loop artifacts; host_delivery_runner validates dirty set, tests, commit, push, and remote SHA confirmation. No live external action is executed.",
        "no_external_side_effects_statement": "C3 executes no customer contact, email/message sending, publication, payment, account creation, form submission, login, external validation submission, customer system access, legal/financial commitment, credential disclosure, or core brain/CIEU/memory writeback.",
        "cleanup_generated_bytecode": True,
    }
    path = repo_root / "operations" / "repository_delivery" / "delivery_requests" / "c3_validation_batch_control_loop_delivery.json"
    write_json(path, request)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    ops = root / "operations" / "external_validation"
    reports = root / "reports" / "integration"

    envelope = build_c3_narrow_envelope(root).to_dict()
    batch = build_c3_validation_batch(root)
    replay = replay_c3_decisions(batch, envelope)
    handoff = build_c3_owner_handoff_batch(batch)
    receipts = build_c3_dry_run_receipts(batch, replay)
    ledger_template = build_c3_action_ledger_state_template()
    ledger_fixture = build_c3_action_ledger_state_fixture(batch, receipts)
    feedback_template = build_c3_feedback_intake_template()
    feedback_fixture = build_c3_feedback_signal_fixture()
    e15_packet = build_c3_e15_next_action_packet(batch=batch, replay_report=replay, handoff_batch=handoff, feedback_fixture=feedback_fixture)
    closure = build_c3_czl_closure(
        base_head=BASE_HEAD,
        envelope=envelope,
        batch=batch,
        replay_report=replay,
        dry_run_receipts=receipts,
        ledger_fixture=ledger_fixture,
        e15_packet=e15_packet,
    ).to_dict()

    validation_errors = (
        validate_c3_narrow_envelope(envelope)
        + validate_c3_validation_batch(batch)
        + validate_c3_decision_replay_report(replay)
        + validate_c3_owner_handoff_batch(handoff)
        + validate_c3_dry_run_receipts(receipts)
        + validate_c3_action_ledger_state_fixture(ledger_fixture)
        + validate_c3_feedback_intake_template(feedback_template)
        + validate_c3_e15_next_action_packet(e15_packet)
        + validate_c3_czl_closure(closure)
    )
    if validation_errors:
        raise SystemExit("C3 validation failed:\n" + "\n".join(validation_errors))

    write_json(ops / "c3_narrow_constitutional_envelope.json", envelope)
    write_text(ops / "c3_narrow_constitutional_envelope.md", render_narrow_envelope(envelope))
    write_json(ops / "c3_validation_batch.json", batch)
    write_json(ops / "c3_decision_replay_report.json", replay)
    write_json(ops / "c3_owner_handoff_validation_batch.json", handoff)
    write_text(ops / "c3_owner_handoff_validation_batch.md", render_c3_owner_handoff_batch(handoff))
    write_json(ops / "c3_dry_run_execution_receipts.json", receipts)
    write_json(ops / "c3_action_ledger_state_template.json", ledger_template)
    write_json(ops / "c3_action_ledger_state_fixture.json", ledger_fixture)
    write_json(ops / "c3_feedback_intake_template.json", feedback_template)
    write_json(ops / "c3_feedback_signal_fixture.json", feedback_fixture)
    write_json(ops / "c3_e15_next_action_decision_packet.json", e15_packet)
    write_text(reports / "c3_narrow_constitutional_activation.md", render_narrow_envelope(envelope))
    write_text(reports / "c3_first_governed_validation_batch.md", render_batch_report(batch))
    write_text(reports / "c3_decision_replay_and_consistency.md", render_replay_report(replay))
    write_text(reports / "c3_owner_handoff_execution_batch.md", render_c3_owner_handoff_batch(handoff))
    write_text(reports / "c3_feedback_intake_and_signal_loop.md", render_feedback_report(feedback_template, feedback_fixture))
    write_text(reports / "c3_e15_next_action_decision_packet.md", render_e15_packet(e15_packet))
    write_text(
        reports / "c3_czl_closure.md",
        "# C3 CZL Closure\n\n```json\n" + json.dumps(closure, indent=2, ensure_ascii=False) + "\n```\n",
    )
    write_delivery_request(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
