from office.mission_command.e45_real_local_first_value_demo_runner import run_real_local_first_value_demo

def test_local_first_value_demo_attempts_safe_commands():
    result = run_real_local_first_value_demo()
    assert result["entrypoints"]["gov_mcp"] is True
    assert result["entrypoints"]["ystar"] is True
    labels = {item["label"] for item in result["commands_attempted"]}
    assert "gov_mcp_server_help" in labels
    assert "gov_mcp_status" in labels
    assert "ystar_demo" in labels
    assert result["commands_passed_count"] >= 3
    assert result["local_demo_readiness_class"] in {"ready_for_owner_review", "blocked_by_docs", "blocked_by_cli", "blocked_by_local_env", "blocked_by_cross_repo_patch", "blocked_by_unknown"}
    assert result["no_internet_install"] is True
    assert result["no_external_action"] is True
