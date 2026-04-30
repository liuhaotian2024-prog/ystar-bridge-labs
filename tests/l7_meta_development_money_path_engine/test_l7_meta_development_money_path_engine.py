import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SECRET_HELPER = ROOT / "policy" / "secret_scanner_policy.py"


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_secret_helper():
    spec = importlib.util.spec_from_file_location("secret_scanner_policy", SECRET_HELPER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_core_l7_2_outputs_exist() -> None:
    required = [
        "l7_meta_development_money_path_engine/l7_2_summary.json",
        "external_world_opportunity_map/external_world_opportunity_map.json",
        "internal_asset_and_advantage_map/internal_asset_and_advantage_map.json",
        "opportunity_asset_match_matrix/opportunity_asset_match_matrix.json",
        "commercial_path_generation/commercial_path_portfolio.json",
        "shortest_cash_realization_path/shortest_cash_path_model.json",
        "shortest_cash_realization_path/cash_path_scorecard.json",
        "shortest_cash_realization_path/first_cash_step_decision.json",
        "money_path_counterfactuals/money_path_counterfactuals.json",
        "strategic_leverage_scorecard/strategic_leverage_scorecard.json",
        "tool_gap_backpropagation/tool_gap_backpropagation.json",
        "agent_team_execution_routes/agent_team_execution_routes.json",
        "commercial_experiment_portfolio/commercial_experiment_portfolio.json",
        "meta_development_decision_packet/meta_development_decision_packet.json",
        "owner_review_packet/l7_2_money_path_owner_review_packet.json",
        "l7_2_no_action_receipt/l7_2_no_action_receipt.json",
    ]
    for rel in required:
        assert (ROOT / rel).is_file()


def test_opportunity_asset_and_path_counts() -> None:
    opportunities = load_json("external_world_opportunity_map/external_world_opportunity_map.json")
    assets = load_json("internal_asset_and_advantage_map/internal_asset_and_advantage_map.json")
    matches = load_json("opportunity_asset_match_matrix/opportunity_asset_match_matrix.json")
    paths = load_json("commercial_path_generation/commercial_path_portfolio.json")
    assert len(opportunities["opportunity_categories"]) >= 15
    assert len(assets["assets"]) >= 20
    assert len(matches["match_rows"]) >= 12
    assert len(paths["candidate_paths"]) >= 12


def test_shortest_cash_decisions_exist() -> None:
    decision = load_json("shortest_cash_realization_path/first_cash_step_decision.json")
    leverage = load_json("strategic_leverage_scorecard/strategic_leverage_scorecard.json")
    assert decision["primary_shortest_cash_path"]
    assert leverage["primary_shortest_cash_path"]
    assert leverage["primary_long_term_strategic_path"]
    assert leverage["bridge_path_between_cash_and_strategy"]
    assert "service" in decision["why_faster_than_others"].lower()


def test_money_path_rankings_are_not_single_l7_1_offer() -> None:
    paths = load_json("commercial_path_generation/commercial_path_portfolio.json")["candidate_paths"]
    ids = {path["path_id"] for path in paths}
    assert "l7_1_offer_001" not in ids
    assert "l7_1_offer_002" not in ids
    assert len(ids) >= 12
    summary = load_json("l7_meta_development_money_path_engine/l7_2_summary.json")
    assert summary["candidate_money_paths_generated"] >= 12


def test_counterfactuals_and_scorecards_exist() -> None:
    counterfactuals = load_json("money_path_counterfactuals/money_path_counterfactuals.json")
    scorecard = load_json("strategic_leverage_scorecard/strategic_leverage_scorecard.json")
    assert counterfactuals["counterfactuals"]
    assert len(scorecard["shortest_cash_ranking"]) >= 12
    assert len(scorecard["strategic_compounding_ranking"]) >= 12


def test_tool_gap_classes_exist_and_have_next_tool() -> None:
    gaps = load_json("tool_gap_backpropagation/tool_gap_backpropagation.json")
    for key in ["cash_path_blocking_tools", "cash_path_accelerators", "strategic_long_term_tools", "defer_tools"]:
        assert key in gaps
        assert gaps[key]
    assert any(item["should_build_this_week"] for item in gaps["cash_path_blocking_tools"])
    summary = load_json("l7_meta_development_money_path_engine/l7_2_summary.json")
    assert summary["next_tool_to_build"]


def test_routes_experiments_and_packets_exist() -> None:
    routes = load_json("agent_team_execution_routes/agent_team_execution_routes.json")
    experiments = load_json("commercial_experiment_portfolio/commercial_experiment_portfolio.json")
    decision = load_json("meta_development_decision_packet/meta_development_decision_packet.json")
    owner = load_json("owner_review_packet/l7_2_money_path_owner_review_packet.json")
    assert routes["routes"]
    assert experiments["experiments"]
    assert decision["shortest_cash_realization_path"]
    assert owner["primary_shortest_cash_path"]


def test_owner_review_packet_contains_shortest_cash_section() -> None:
    text = (ROOT / "owner_review_packet/l7_2_money_path_owner_review_packet.md").read_text(encoding="utf-8")
    assert "最短兑现路径 / Shortest Cash Realization Path" in text
    assert "现在最短的赚钱路径是什么" in text
    assert "Codex 下一步应该构建什么" in text


def test_no_action_receipt_and_summary_safety_flags() -> None:
    receipt = load_json("l7_2_no_action_receipt/l7_2_no_action_receipt.json")
    summary = load_json("l7_meta_development_money_path_engine/l7_2_summary.json")
    for key, value in receipt.items():
        if key.endswith("_occurred"):
            assert value is False
    for key in [
        "ask_user_url_occurred",
        "external_side_effects_occurred",
        "customer_contacted",
        "email_sent",
        "form_submitted",
        "payment_occurred",
        "publication_occurred",
        "core_writeback_occurred",
        "secret_printed_stored_in_repo",
    ]:
        assert summary[key] is False


def test_no_secret_serialization() -> None:
    helper = load_secret_helper()
    roots = [
        "l7_meta_development_money_path_engine",
        "external_world_opportunity_map",
        "internal_asset_and_advantage_map",
        "opportunity_asset_match_matrix",
        "commercial_path_generation",
        "shortest_cash_realization_path",
        "money_path_counterfactuals",
        "strategic_leverage_scorecard",
        "tool_gap_backpropagation",
        "agent_team_execution_routes",
        "commercial_experiment_portfolio",
        "meta_development_decision_packet",
        "owner_review_packet",
        "l7_2_no_action_receipt",
    ]
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for root in roots
        for path in (ROOT / root).rglob("*")
        if path.is_file() and path.suffix in {".json", ".md"}
    )
    decisions = helper.scan_text_for_secret_policy(text, file_path="tests/l7_meta_development_money_path_engine/test_l7_meta_development_money_path_engine.py")
    assert all(decision["safe_for_commit"] for decision in decisions)


def test_outputs_are_deterministic_enough() -> None:
    summary = load_json("l7_meta_development_money_path_engine/l7_2_summary.json")
    assert summary["generated_at_utc"] == "2026-04-29T00:00:00Z"
    assert summary["next_one_command_action"] == "bash scripts/run_l7_2_money_path_engine.sh --mode build"
