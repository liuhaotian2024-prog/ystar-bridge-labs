from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def all_l7_text() -> str:
    paths = [
        *ROOT.glob("l7_*/**/*.json"),
        *ROOT.glob("l7_*/**/*.md"),
        *ROOT.glob("l7_parallel_lane_specs/*.md"),
        *ROOT.glob("scripts/l7_lanes/*.py"),
        ROOT / "scripts/run_l7_parallel_lanes.sh",
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.exists())


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        ["bash", "scripts/run_l7_parallel_lanes.sh", *args],
        cwd=ROOT,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )


def test_parallel_orchestration_script_exists_and_supports_modes() -> None:
    script = ROOT / "scripts/run_l7_parallel_lanes.sh"
    text = script.read_text(encoding="utf-8")

    assert script.is_file()
    assert "--mode scaffold" in text
    assert "local-parallel" in text
    assert "worktree-setup" in text
    assert "status" in text
    assert "git worktree add" in text
    assert "network: disabled by default" in text
    assert "external actions: blocked" in text
    assert "core writeback: blocked" in text


def test_scaffold_and_status_modes_run_offline() -> None:
    scaffold = run_script("--mode", "scaffold")
    status = run_script("--mode", "status")

    assert "L7 scaffold complete" in scaffold.stdout
    assert "all lanes complete: True" in status.stdout
    assert "next recommended command" in status.stdout


def test_integration_manifest_does_not_require_manual_parallel_work_or_keys() -> None:
    manifest = load_json("l7_parallel_commercial_agent_team_orchestrator/l7_0p_integration_manifest.json")

    assert manifest["supported_modes"] == ["scaffold", "local-parallel", "worktree-setup", "status"]
    assert manifest["default_mode"] == "local-parallel"
    assert manifest["manual_codex_windows_required"] is False
    assert manifest["manual_worktree_creation_required"] is False
    assert manifest["manual_prompt_distribution_required"] is False
    assert manifest["manual_branch_merge_required"] is False
    assert manifest["network_required"] is False
    assert manifest["api_keys_required"] is False


def test_lane_prompt_and_builder_files_exist() -> None:
    manifest = load_json("l7_parallel_commercial_agent_team_orchestrator/l7_0p_integration_manifest.json")

    for lane in manifest["lanes"]:
        assert (ROOT / lane["prompt"]).is_file()
        assert (ROOT / lane["builder"]).is_file()
        prompt = (ROOT / lane["prompt"]).read_text(encoding="utf-8")
        assert lane["worktree"] in prompt
        assert lane["branch"] in prompt
        assert "forbidden actions" in prompt.lower()
        assert "completion report" in prompt.lower()


def test_l7a_required_agents_exist() -> None:
    profiles_dir = ROOT / "l7_agent_team_runtime/agent_role_profiles"
    expected = {
        "CEO",
        "Researcher",
        "Operator/COO",
        "Engineer/CTO",
        "Secretary",
        "Auditor",
        "Revenue Scout",
    }

    profiles = [json.loads(path.read_text(encoding="utf-8")) for path in profiles_dir.glob("*.json")]
    assert {profile["role_id"] for profile in profiles} == expected
    for profile in profiles:
        assert profile["no_side_effect_boundary"] is True
        assert "external outreach" in profile["forbidden_actions"]
        assert "brain/memory writeback" in profile["forbidden_actions"]


def test_l7b_revenue_opportunity_packet_exists_and_is_internal_only() -> None:
    packet = load_json("l7_revenue_opportunity_radar/opportunity_packets/opportunity_packet_001.json")

    assert packet["opportunity_id"] == "l7b_opportunity_001"
    assert packet["human_approval_required_before_external_action"] is True
    assert packet["next_safe_step"] in {
        "internal strategy memo",
        "market hypothesis table",
        "third-pass read-only observation",
        "technical gap analysis",
        "policy/funding landscape map",
        "human review session",
    }
    assert "customer contact" in packet["forbidden_actions"]
    assert "publication" in packet["forbidden_actions"]
    assert "payment" in packet["forbidden_actions"]


def test_l7c_external_action_gate_defaults_actions_blocked() -> None:
    index = load_json("l7_human_approved_external_action_gate/external_action_types/external_action_type_index.json")
    assert len(index["action_types"]) >= 10

    for action in index["action_types"]:
        assert action["default_status"] == "blocked_until_human_approved"
        assert action["allowed_pre_approval_output"] == "draft_only"
        assert action["post_action_receipt_required"] is True


def test_l7d_writeback_candidates_are_dry_run_only() -> None:
    index = load_json("l7_review_gated_memory_writeback/memory_writeback_candidates/candidate_index.json")
    assert len(index["candidates"]) >= 6

    for candidate in index["candidates"]:
        assert candidate["default_decision"] == "blocked_until_approved"
        assert candidate["dry_run_only"] is True
        assert candidate["required_human_approval"] is True


def test_l7e_owner_cockpit_exists_and_points_to_safe_next_command() -> None:
    cockpit = load_json("l7_owner_runtime_cockpit/owner_cockpit.json")

    assert cockpit["what_agents_exist"]
    assert cockpit["what_actions_are_blocked"]
    assert cockpit["next_safest_command"] == "bash scripts/run_l7_parallel_lanes.sh --mode local-parallel"
    receipt = load_json("l7_owner_runtime_cockpit/owner_cockpit_no_action_receipts/no_action_receipt.json")
    assert receipt["ask_user_for_url_occurred"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert receipt["core_writeback_occurred"] is False


def test_integration_summary_and_lane_status_complete() -> None:
    summary = load_json("l7_parallel_commercial_agent_team_orchestrator/l7_0p_summary.json")
    status = load_json("l7_parallel_commercial_agent_team_orchestrator/l7_0p_lane_status.json")

    assert summary["l7a_agent_team_runtime_created"] is True
    assert summary["l7b_revenue_radar_created"] is True
    assert summary["l7c_human_approved_action_gate_created"] is True
    assert summary["l7d_writeback_protocol_created"] is True
    assert summary["l7e_owner_cockpit_created"] is True
    assert summary["all_lanes_complete"] is True
    assert status["all_lanes_complete"] is True
    assert {lane["status"] for lane in status["lanes"]} == {"complete"}


def test_no_secret_serialization_or_external_side_effects() -> None:
    text = all_l7_text()
    receipt = load_json("l7_parallel_commercial_agent_team_orchestrator/l7_0p_no_action_receipt.json")

    assert "controlled_observation" + ".env" not in text
    assert "TAVILY" + "_API_KEY=" not in text
    assert "BRAVE_SEARCH" + "_API_KEY=" not in text
    assert "SERP" + "API_API_KEY=" not in text
    assert "tvly" + "-" not in text
    assert receipt["external_network_performed"] is False
    assert receipt["external_side_effects_occurred"] is False
    assert receipt["core_writeback_occurred"] is False
    assert receipt["ask_user_for_url_occurred"] is False
    assert receipt["secret_values_serialized"] is False


def test_no_core_writeback_or_external_repo_modification_claims() -> None:
    summary = load_json("l7_parallel_commercial_agent_team_orchestrator/l7_0p_summary.json")
    receipt = load_json("l7_parallel_commercial_agent_team_orchestrator/l7_0p_no_action_receipt.json")

    assert summary["external_actions_still_blocked"] is True
    assert summary["core_writebacks_still_blocked"] is True
    assert summary["y_star_gov_modified"] is False
    assert summary["gov_mcp_modified"] is False
    assert receipt["cieu_db_write_occurred"] is False
    assert receipt["brain_memory_writeback_occurred"] is False
    assert receipt["canonical_strategy_mutation_occurred"] is False
    assert receipt["direct_y_star_mutation_occurred"] is False
    assert receipt["y_star_gov_modification_occurred"] is False
    assert receipt["gov_mcp_modification_occurred"] is False
