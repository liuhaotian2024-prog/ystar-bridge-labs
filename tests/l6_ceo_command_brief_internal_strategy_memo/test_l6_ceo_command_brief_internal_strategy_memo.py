from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "l6_ceo_command_brief_internal_strategy_memo",
    "ceo_command_brief",
    "system_capability_inventory",
    "evidence_to_strategy_trace",
    "internal_strategy_memo",
    "planning_candidate_selection",
    "bounded_conflict_caveat_table",
    "decision_options_matrix",
    "next_30_60_90_day_plan",
    "owner_operating_guide",
    "l6_16_no_action_receipts",
    "l6_16_read_model",
]

REQUIRED_JSON = [
    "l6_ceo_command_brief_internal_strategy_memo/l6_16_milestone_contract.json",
    "l6_ceo_command_brief_internal_strategy_memo/l6_16_summary.json",
    "ceo_command_brief/l6_16_ceo_command_brief.json",
    "system_capability_inventory/system_capability_inventory.json",
    "evidence_to_strategy_trace/evidence_to_strategy_trace.json",
    "internal_strategy_memo/l6_16_internal_strategy_memo.json",
    "planning_candidate_selection/planning_candidate_selection.json",
    "bounded_conflict_caveat_table/bounded_conflict_caveat_table.json",
    "decision_options_matrix/decision_options_matrix.json",
    "next_30_60_90_day_plan/next_30_60_90_day_plan.json",
    "owner_operating_guide/l6_16_owner_operating_guide.json",
    "l6_16_no_action_receipts/no_side_effect_receipt.json",
    "l6_16_read_model/l6_16_read_model_summary.json",
    "l6_16_read_model/l6_16_readiness_assessment.json",
    "console_read_model/generated/l6_16_ceo_command_brief_internal_strategy_memo_summary.json",
]

FORBIDDEN_CONTRACT_FLAGS = [
    "new_external_search_authorized_by_default",
    "ask_user_for_url_authorized",
    "login_authorized",
    "account_creation_authorized",
    "payment_authorized",
    "checkout_authorized",
    "form_submission_authorized",
    "posting_authorized",
    "commenting_authorized",
    "messaging_authorized",
    "publication_authorized",
    "outreach_authorized",
    "grant_rfp_bounty_submission_authorized",
    "revenue_execution_authorized",
    "mcp_execution_authorized",
    "live_behavior_authorized",
    "cieu_db_write_authorized",
    "canonical_update_authorized",
    "direct_y_star_mutation_authorized",
    "brain_writeback_authorized",
    "memory_ingestion_authorized",
    "core_writeback_authorized",
    "artifact_refinement_application_authorized",
]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_l6_16_directories_and_json_parse() -> None:
    for rel in REQUIRED_DIRS:
        assert (ROOT / rel).is_dir(), rel
    for rel in REQUIRED_JSON:
        assert (ROOT / rel).is_file(), rel
        load(rel)


def test_contract_identifies_l6_16_and_forbids_action_or_writeback() -> None:
    contract = load("l6_ceo_command_brief_internal_strategy_memo/l6_16_milestone_contract.json")
    assert contract["milestone_id"] == "L6.16"
    assert contract["input_milestones"][-1] == "L6.15"
    assert contract["mode"] == "ceo_command_brief_internal_strategy_memo"
    assert contract["ceo_command_brief_authorized"] is True
    assert contract["internal_strategy_memo_authorized"] is True
    assert contract["external_action_authorized"] is False
    assert contract["core_writeback_authorized"] is False
    for field in FORBIDDEN_CONTRACT_FLAGS:
        assert contract[field] is False, field


def test_builder_ingests_l6_15_review_packet_and_statuses_are_deterministic() -> None:
    builder = load_module(
        "l6_16_builder",
        "l6_ceo_command_brief_internal_strategy_memo/tools/build_l6_ceo_command_brief_internal_strategy_memo.py",
    )
    inputs = builder.load_inputs()
    assert inputs["missing"] == []
    assert inputs["l6_15_summary"]["l6_15_review_status"] == (
        "human_review_ready_with_bounded_conflict"
    )
    summary = load("l6_16_read_model/l6_16_read_model_summary.json")
    assert summary["l6_15_review_status"] == "human_review_ready_with_bounded_conflict"
    assert summary["primary_selected_planning_candidate"] == (
        "l6_15_candidate_internal_strategy_memo"
    )
    assert summary["next_safe_step"] == "draft internal strategy memo with bounded-conflict caveats"


def test_ceo_command_brief_is_generated_for_owner_readability() -> None:
    brief = load("ceo_command_brief/l6_16_ceo_command_brief.json")
    markdown = (ROOT / "ceo_command_brief/l6_16_ceo_command_brief.md").read_text()
    assert brief["real_external_observation_succeeded"] is True
    assert brief["evidence_collected"]["packets_considered"] == 6
    assert brief["bounded_or_conflicted"]["bounded_conflicts"] == 1
    assert "What do I own now?" in markdown
    assert "What can the CEO agent do today?" in markdown
    assert "What should not be built next?" in markdown


def test_capability_inventory_is_generated() -> None:
    inventory = load("system_capability_inventory/system_capability_inventory.json")
    capability_ids = {item["capability_id"] for item in inventory["capabilities"]}
    for expected in [
        "controlled_search",
        "controlled_public_page_read",
        "evidence_packet_generation",
        "human_review_packet",
        "read_model_console_visibility",
    ]:
        assert expected in capability_ids
    assert len(inventory["capabilities"]) >= 10


def test_evidence_to_strategy_trace_is_generated_and_forbids_overclaiming() -> None:
    trace = load("evidence_to_strategy_trace/evidence_to_strategy_trace.json")
    assert trace["trace_items"]
    for item in trace["trace_items"]:
        assert item["evidence_packet_ids"]
        assert "internal" in item["allowed_use"]
        assert "settled truth" in item["forbidden_use"]
        assert "external publication" in item["forbidden_use"]


def test_internal_strategy_memo_is_generated_and_labeled_internal_only() -> None:
    memo = load("internal_strategy_memo/l6_16_internal_strategy_memo.json")
    markdown = (ROOT / "internal_strategy_memo/l6_16_internal_strategy_memo.md").read_text()
    assert memo["classification"] == "internal_strategy_memo_generated"
    assert "Internal use only" in memo["internal_use_notice"]
    assert "Not for publication" in memo["internal_use_notice"]
    assert "Recommended Internal Planning Direction" in markdown
    assert "bounded-conflict caveats" in markdown


def test_planning_candidate_selection_picks_internal_strategy_memo() -> None:
    selection = load("planning_candidate_selection/planning_candidate_selection.json")
    assert selection["candidates_considered"] == 5
    assert selection["primary_selected_planning_candidate"] == (
        "l6_15_candidate_internal_strategy_memo"
    )
    statuses = {item["candidate_id"]: item["selected_status"] for item in selection["selection"]}
    assert statuses["l6_15_candidate_internal_strategy_memo"] == "primary_recommended"


def test_decision_options_matrix_and_30_60_90_plan_are_generated() -> None:
    options = load("decision_options_matrix/decision_options_matrix.json")["decision_options"]
    option_ids = {item["option_id"] for item in options}
    assert len(options) == 8
    assert "continue_internal_strategy_only" in option_ids
    assert "block_external_action_until_approval" in option_ids
    plan = load("next_30_60_90_day_plan/next_30_60_90_day_plan.json")
    assert plan["external_actions_authorized_in_l6_16"] is False
    assert plan["core_writeback_authorized_in_l6_16"] is False
    assert plan["plan"]["30_days"]
    assert plan["plan"]["60_days"]
    assert plan["plan"]["90_days"]


def test_owner_operating_guide_is_generated() -> None:
    guide = (ROOT / "owner_operating_guide/l6_16_owner_operating_guide.md").read_text()
    assert "How do I run the CEO command brief?" in guide
    assert "What should I not ask the agent to do yet?" in guide
    assert "ceo-command-brief-internal-strategy-memo" in guide


def test_no_action_receipt_covers_forbidden_actions() -> None:
    receipt = load("l6_16_no_action_receipts/no_side_effect_receipt.json")
    assert receipt["new_external_search_performed"] is False
    assert receipt["ask_user_for_url_occurred"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert receipt["core_writeback_occurred"] is False
    assert receipt["secret_values_serialized"] is False
    for action in [
        "login",
        "account_creation",
        "payment",
        "checkout",
        "form_submission",
        "posting",
        "commenting",
        "messaging",
        "email_customer_outreach",
        "publication",
        "grant_rfp_bounty_submission",
        "revenue_execution",
        "mcp_execution",
        "live_behavior",
        "cieu_db_write",
        "brain_memory_writeback",
        "canonical_strategy_mutation",
        "direct_y_star_mutation",
        "ask_user_url",
    ]:
        assert receipt[f"{action}_occurred"] is False


def test_external_actions_and_core_writeback_remain_blocked() -> None:
    summary = load("l6_16_read_model/l6_16_read_model_summary.json")
    assert summary["blocked_external_actions"] >= 1
    assert summary["blocked_core_writebacks"] >= 1
    assert summary["external_side_effects_occurred"] is False
    assert summary["core_writeback_occurred"] is False
    assert summary["ask_user_for_url_occurred"] is False


def test_read_model_summary_validates_and_console_command_works() -> None:
    summary = load("console_read_model/generated/l6_16_ceo_command_brief_internal_strategy_memo_summary.json")
    assert summary["command_brief_generated"] is True
    assert summary["strategy_memo_generated"] is True
    assert summary["owner_guide_generated"] is True
    result = subprocess.run(
        [sys.executable, "console_read_model/cli/team_console.py", "ceo-command-brief-internal-strategy-memo"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "L6.16 CEO Command Brief & Internal Strategy Memo Sprint" in result.stdout
    assert "ask-user-URL occurred: False" in result.stdout


def test_secret_values_are_not_serialized() -> None:
    generated_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "l6_ceo_command_brief_internal_strategy_memo/l6_16_summary.json",
            ROOT / "ceo_command_brief/l6_16_ceo_command_brief.json",
            ROOT / "internal_strategy_memo/l6_16_internal_strategy_memo.json",
            ROOT / "l6_16_read_model/l6_16_read_model_summary.json",
        ]
    )
    assert ("TAVILY_" + "API_KEY=") not in generated_text
    assert ("BRAVE_SEARCH_" + "API_KEY=") not in generated_text
    assert ("SERPAPI_" + "API_KEY=") not in generated_text
    assert ("tv" + "ly-") not in generated_text
