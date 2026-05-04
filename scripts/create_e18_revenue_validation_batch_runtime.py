#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from office.mission_command.e18_batch_feedback_intake import (
    build_batch_feedback_intake_schema,
    build_empty_batch_feedback_intake,
    render_batch_feedback_runtime,
)
from office.mission_command.e18_batch_owner_console import build_batch_owner_console, render_batch_owner_console
from office.mission_command.e18_batch_response_classifier import build_batch_response_classification_rules
from office.mission_command.e18_batch_target_selection import build_revenue_validation_batch, render_revenue_validation_batch
from office.mission_command.e18_commercial_fit_scoring import build_commercial_fit_scores
from office.mission_command.e18_commercial_kpi import build_commercial_kpi_packet, render_commercial_kpi_packet
from office.mission_command.e18_manual_send_tracker import build_manual_send_tracker, render_manual_send_tracker
from office.mission_command.e18_offer_variant_matrix import build_offer_variant_matrix, render_offer_variant_matrix
from office.mission_command.e18_route_decision import (
    build_e18_czl_closure,
    build_e18_route_decision,
    render_czl_closure,
    render_route_decision,
)


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_score_report(scores: Dict[str, Any]) -> str:
    lines = [
        "# E18 Commercial Fit Scores",
        "",
        f"- scoring_method: {scores['scoring_method']}",
        "- external_action_executed: false",
        "",
        "| target | status | score | variant |",
        "| --- | --- | ---: | --- |",
    ]
    for item in scores["scores"]:
        lines.append(
            f"| {item['target_name']} | {item['status']} | {item['total_score']} | {item['recommended_message_variant_id']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def create_e18(repo_root: Path, output_root: Path) -> list[str]:
    c3_batch = load_json(repo_root / "operations/external_validation/c3_validation_batch.json")
    e17_queue = load_json(repo_root / "operations/external_validation/e17_next_target_expansion_queue.json")
    batch = build_revenue_validation_batch(c3_batch, e17_queue)
    scores = build_commercial_fit_scores(batch)
    variants = build_offer_variant_matrix()
    console = build_batch_owner_console(batch, scores, variants)
    tracker = build_manual_send_tracker(batch)
    feedback_schema = build_batch_feedback_intake_schema(batch)
    feedback_empty = build_empty_batch_feedback_intake(batch)
    classification = build_batch_response_classification_rules(feedback_empty)
    route = build_e18_route_decision(batch, classification)
    kpi = build_commercial_kpi_packet(batch, tracker, classification)

    artifact_paths = [
        "operations/external_validation/e18_revenue_validation_batch.json",
        "operations/external_validation/e18_commercial_fit_scores.json",
        "operations/external_validation/e18_offer_variant_matrix.json",
        "operations/external_validation/e18_batch_owner_console.json",
        "operations/external_validation/e18_manual_send_tracker.json",
        "operations/external_validation/e18_batch_feedback_intake_schema.json",
        "operations/external_validation/e18_batch_feedback_intake_empty.json",
        "operations/external_validation/e18_batch_response_classification_rules.json",
        "operations/external_validation/e18_route_decision_packet.json",
        "operations/external_validation/e18_commercial_kpi_packet.json",
        "operations/external_validation/e18_czl_closure.json",
        "operations/external_validation/e18_batch_owner_console.md",
        "reports/integration/e18_revenue_validation_batch_runtime.md",
        "reports/integration/e18_offer_variant_matrix.md",
        "reports/integration/e18_manual_send_tracker.md",
        "reports/integration/e18_batch_feedback_runtime.md",
        "reports/integration/e18_route_decision_packet.md",
        "reports/integration/e18_commercial_kpi_packet.md",
        "reports/integration/e18_czl_closure.md",
    ]
    closure = build_e18_czl_closure(batch, route, artifact_paths)

    json_outputs = {
        "operations/external_validation/e18_revenue_validation_batch.json": batch,
        "operations/external_validation/e18_commercial_fit_scores.json": scores,
        "operations/external_validation/e18_offer_variant_matrix.json": variants,
        "operations/external_validation/e18_batch_owner_console.json": console,
        "operations/external_validation/e18_manual_send_tracker.json": tracker,
        "operations/external_validation/e18_batch_feedback_intake_schema.json": feedback_schema,
        "operations/external_validation/e18_batch_feedback_intake_empty.json": feedback_empty,
        "operations/external_validation/e18_batch_response_classification_rules.json": classification,
        "operations/external_validation/e18_route_decision_packet.json": route,
        "operations/external_validation/e18_commercial_kpi_packet.json": kpi,
        "operations/external_validation/e18_czl_closure.json": closure,
    }
    for rel, data in json_outputs.items():
        write_json(output_root / rel, data)

    write_text(output_root / "operations/external_validation/e18_batch_owner_console.md", render_batch_owner_console(console))
    write_text(output_root / "reports/integration/e18_revenue_validation_batch_runtime.md", render_revenue_validation_batch(batch) + "\n" + render_score_report(scores))
    write_text(output_root / "reports/integration/e18_offer_variant_matrix.md", render_offer_variant_matrix(variants))
    write_text(output_root / "reports/integration/e18_manual_send_tracker.md", render_manual_send_tracker(tracker))
    write_text(output_root / "reports/integration/e18_batch_feedback_runtime.md", render_batch_feedback_runtime(feedback_schema, feedback_empty))
    write_text(output_root / "reports/integration/e18_route_decision_packet.md", render_route_decision(route))
    write_text(output_root / "reports/integration/e18_commercial_kpi_packet.md", render_commercial_kpi_packet(kpi))
    write_text(output_root / "reports/integration/e18_czl_closure.md", render_czl_closure(closure))
    return sorted(artifact_paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E18 revenue validation batch operating runtime artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    files = create_e18(Path(args.repo_root), Path(args.output_root))
    if args.json:
        print(json.dumps({"status": "created", "files": files}, indent=2))
    else:
        print(f"created {len(files)} E18 artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
