#!/usr/bin/env python3
"""Build L7D review-gated memory/writeback protocol artifacts."""

from __future__ import annotations

from common import artifact_ref, base_no_action_receipt, lane_summary, simple_md, write_json, write_text


LANE_ID = "L7D"
LANE_NAME = "Review-Gated Memory / Brain Writeback Protocol"
OUTPUT_DIR = "l7_review_gated_memory_writeback"

TARGET_LAYERS = [
    ("agent_working_memory", "agent working memory"),
    ("secretary_archive", "secretary archive"),
    ("ceo_brain_profile", "CEO brain/profile"),
    ("capability_registry", "capability registry"),
    ("canonical_strategy", "canonical strategy"),
    ("cieu_db", "CIEU DB"),
]


def candidate(candidate_id: str, target_layer: str, source_ref: str, proposed_update: str) -> dict[str, object]:
    return {
        "schema_version": "v0",
        "candidate_id": candidate_id,
        "source_evidence_or_review_packet": artifact_ref(source_ref),
        "proposed_update": proposed_update,
        "target_layer": target_layer,
        "reason": "Capture L6.13-L6.16 learning only after human review.",
        "risk": "wrong or overbroad writeback could distort future agent behavior",
        "required_human_approval": True,
        "default_decision": "blocked_until_approved",
        "dry_run_only": True,
        "expected_value": "make reviewed commercial learning reusable",
        "possible_harm_if_wrong": "premature strategy mutation, memory pollution, or governance bypass",
    }


def build() -> None:
    artifacts: list[str] = []
    candidates = [
        candidate(
            f"l7d_candidate_{idx:03d}",
            target_layer,
            "human_review_packet/l6_15_human_review_packet.json",
            f"Review-gated update candidate for {label}.",
        )
        for idx, (target_layer, label) in enumerate(TARGET_LAYERS, start=1)
    ]

    directories = [
        "evidence_delta_candidates",
        "strategy_delta_candidates",
        "agent_capability_delta_candidates",
        "memory_writeback_candidates",
        "brain_update_candidates",
        "canonical_strategy_update_candidates",
    ]
    for directory, item in zip(directories, candidates):
        path = f"{OUTPUT_DIR}/{directory}/{item['candidate_id']}.json"
        write_json(path, item)
        artifacts.append(path)

    write_json(
        f"{OUTPUT_DIR}/memory_writeback_candidates/candidate_index.json",
        {"schema_version": "v0", "candidates": candidates},
    )
    artifacts.append(f"{OUTPUT_DIR}/memory_writeback_candidates/candidate_index.json")

    gate = {
        "schema_version": "v0",
        "lane_id": LANE_ID,
        "default_decision": "blocked_until_approved",
        "no_actual_writeback_in_l7_0p": True,
        "approval_required_for_targets": [layer for layer, _ in TARGET_LAYERS],
        "required_review_fields": [
            "candidate_id",
            "source_evidence_or_review_packet",
            "proposed_update",
            "target_layer",
            "risk",
            "human_approval_record",
        ],
    }
    write_json(f"{OUTPUT_DIR}/human_review_writeback_gate/human_review_writeback_gate.json", gate)
    artifacts.append(f"{OUTPUT_DIR}/human_review_writeback_gate/human_review_writeback_gate.json")

    receipt = base_no_action_receipt(LANE_ID, LANE_NAME)
    receipt["writeback_candidates_dry_run_only"] = True
    write_json(f"{OUTPUT_DIR}/writeback_dry_run_receipts/no_writeback_receipt.json", receipt)
    artifacts.append(f"{OUTPUT_DIR}/writeback_dry_run_receipts/no_writeback_receipt.json")

    summary = lane_summary(
        LANE_ID,
        LANE_NAME,
        OUTPUT_DIR,
        artifacts,
        "review dry-run writeback candidates before any memory or strategy update",
        {"writeback_candidates": len(candidates), "all_candidates_dry_run_only": True},
    )
    write_json(f"{OUTPUT_DIR}/l7d_review_gated_memory_writeback_summary.json", summary)
    write_text(f"{OUTPUT_DIR}/l7d_review_gated_memory_writeback_summary.md", simple_md("L7D Review-Gated Memory Writeback", summary))


if __name__ == "__main__":
    build()
