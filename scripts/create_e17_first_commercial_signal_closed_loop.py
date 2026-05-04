#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from office.mission_command.e17_feedback_intake import build_empty_feedback_intake, build_feedback_intake_schema, render_feedback_runtime
from office.mission_command.e17_offer_revision_runtime import build_offer_revision_packet
from office.mission_command.e17_owner_activation_console import (
    build_final_message_package,
    build_owner_activation_console,
    render_final_message_package,
    render_owner_activation_console,
)
from office.mission_command.e17_paid_signal_runtime import (
    build_next_target_expansion_queue,
    build_paid_signal_readiness_packet,
    render_paid_signal_and_offer_report,
)
from office.mission_command.e17_response_classifier import build_response_classification_rules, classify_e17_response
from office.mission_command.e17_route_decision import build_czl_closure, build_route_decision_packet, render_czl_closure, render_route_decision_packet


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_main_report(console: Dict[str, Any], paid_signal: Dict[str, Any], queue: Dict[str, Any]) -> str:
    ready = [item for item in queue.get("entries", []) if item.get("status") == "ready_candidate_from_existing_repo_evidence"]
    return "\n".join(
        [
            "# E17 First Commercial Signal Closed Loop Runtime",
            "",
            "E17 turns the E16C0 no-send dry-run into an owner-approval-gated commercial signal operating loop.",
            "",
            f"- selected_target: {console['target_name']}",
            f"- offer: {console['offer']}",
            f"- recommended_owner_action: {console['recommended_owner_action']}",
            f"- paid_signal_current_state: {paid_signal['current_feedback_state']}",
            f"- next_allowed_commercial_action: {paid_signal['next_allowed_commercial_action']}",
            f"- ready_next_targets_from_repo_evidence: {len(ready)}",
            "- external_action_executed: false",
            "",
            "## Revenue Relevance",
            "This does not create revenue by itself. It removes operational drag between a safe target choice and the first real customer signal: one owner decision surface, one final message, one feedback intake file, deterministic classification, and a route decision that can move toward paid diagnostic follow-up only when evidence supports it.",
        ]
    ).rstrip() + "\n"


def render_commercial_path_report(commercial: Dict[str, Any], route: Dict[str, Any], queue: Dict[str, Any]) -> str:
    return "\n".join(
        [
            "# E17 Commercial Path Assessment",
            "",
            f"- selected_target: {commercial.get('selected_target')}",
            f"- offer: {commercial.get('offer')}",
            f"- shortest_cash_path_candidate: {str(commercial.get('shortest_cash_path_candidate')).lower()}",
            f"- recommended_route: {route.get('recommended_route')}",
            "",
            "## Shortest Cash Path Logic",
            "The fastest real signal remains owner manual send first: it avoids waiting for real provider implementation while still preserving governance, feedback provenance, and do-not-contact safety. If feedback is positive, E18 can prepare paid diagnostic follow-up. If feedback is weak, E17 routes to offer or target revision instead of pretending market validation happened.",
            "",
            "## Next Target Queue",
            f"- queue_entries: {len(queue.get('entries', []))}",
            "- source_policy: existing repo evidence only; no scraping and no fake targets",
        ]
    ).rstrip() + "\n"


def create_e17(repo_root: Path, output_root: Path) -> list[str]:
    selected_pilot = load_json(repo_root / "operations/external_validation/e16c0_selected_one_action_pilot.json")
    selected_action = selected_pilot["selected_action"]
    commercial = load_json(repo_root / "operations/external_validation/e16c0_commercial_path_assessment.json")
    c3_batch = load_json(repo_root / "operations/external_validation/c3_validation_batch.json")

    message_package = build_final_message_package(selected_action)
    console = build_owner_activation_console(selected_action, message_package)
    schema = build_feedback_intake_schema(selected_action)
    empty_feedback = build_empty_feedback_intake(selected_action)
    rules = build_response_classification_rules(selected_action)
    classification = classify_e17_response(empty_feedback.to_dict())
    paid_signal = build_paid_signal_readiness_packet(selected_action, classification)
    offer_revision = build_offer_revision_packet(commercial, classification)
    next_target_queue = build_next_target_expansion_queue(c3_batch, str(selected_action.get("action_id")))
    route = build_route_decision_packet(selected_action, paid_signal, offer_revision)

    artifact_paths = [
        "operations/external_validation/e17_owner_activation_console.json",
        "operations/external_validation/e17_final_message_package.json",
        "operations/external_validation/e17_feedback_intake_schema.json",
        "operations/external_validation/e17_feedback_intake_empty.json",
        "operations/external_validation/e17_response_classification_rules.json",
        "operations/external_validation/e17_paid_signal_readiness_packet.json",
        "operations/external_validation/e17_offer_revision_packet.json",
        "operations/external_validation/e17_next_target_expansion_queue.json",
        "operations/external_validation/e17_route_decision_packet.json",
        "operations/external_validation/e17_czl_closure.json",
        "operations/external_validation/e17_owner_activation_console.md",
        "reports/integration/e17_first_commercial_signal_closed_loop.md",
        "reports/integration/e17_final_message_package.md",
        "reports/integration/e17_feedback_runtime.md",
        "reports/integration/e17_paid_signal_and_offer_revision.md",
        "reports/integration/e17_route_decision_packet.md",
        "reports/integration/e17_czl_closure.md",
    ]
    closure = build_czl_closure(route, artifact_paths)

    json_outputs = {
        "operations/external_validation/e17_owner_activation_console.json": console.to_dict(),
        "operations/external_validation/e17_final_message_package.json": message_package.to_dict(),
        "operations/external_validation/e17_feedback_intake_schema.json": schema.to_dict(),
        "operations/external_validation/e17_feedback_intake_empty.json": empty_feedback.to_dict(),
        "operations/external_validation/e17_response_classification_rules.json": rules,
        "operations/external_validation/e17_paid_signal_readiness_packet.json": paid_signal.to_dict(),
        "operations/external_validation/e17_offer_revision_packet.json": offer_revision,
        "operations/external_validation/e17_next_target_expansion_queue.json": next_target_queue,
        "operations/external_validation/e17_route_decision_packet.json": route,
        "operations/external_validation/e17_czl_closure.json": closure,
    }
    for rel, data in json_outputs.items():
        write_json(output_root / rel, data)

    write_text(output_root / "operations/external_validation/e17_owner_activation_console.md", render_owner_activation_console(console, message_package))
    write_text(output_root / "reports/integration/e17_first_commercial_signal_closed_loop.md", render_main_report(console.to_dict(), paid_signal.to_dict(), next_target_queue))
    write_text(output_root / "reports/integration/e17_final_message_package.md", render_final_message_package(message_package))
    write_text(output_root / "reports/integration/e17_feedback_runtime.md", render_feedback_runtime(schema, empty_feedback, rules))
    write_text(output_root / "reports/integration/e17_paid_signal_and_offer_revision.md", render_paid_signal_and_offer_report(paid_signal.to_dict(), offer_revision))
    write_text(output_root / "reports/integration/e17_route_decision_packet.md", render_route_decision_packet(route))
    write_text(output_root / "reports/integration/e17_czl_closure.md", render_czl_closure(closure))
    return sorted(set(artifact_paths))


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E17 first commercial signal closed loop runtime artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    written = create_e17(Path(args.repo_root), Path(args.output_root))
    if args.json:
        print(json.dumps({"status": "created", "files": written}, indent=2))
    else:
        print(f"created {len(written)} E17 artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
