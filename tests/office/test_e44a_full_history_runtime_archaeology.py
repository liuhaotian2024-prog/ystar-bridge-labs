from office.mission_command.e44a_full_history_runtime_archaeology import build_full_history_runtime_archaeology

def test_full_history_archaeology_names_pre_e31_families():
    artifact = build_full_history_runtime_archaeology()
    rows = artifact["resources"]
    families = {row["capability_family"] for row in rows}
    for expected in ["live_runtime_enforcement", "session_lifecycle_memory", "ceo_wisdom_and_cognition", "commercial_and_value_production", "execution_and_delivery", "governance_and_audit", "notification_and_board_loop"]:
        assert expected in families
    assert any(row["path"] == "scripts/article_11_tracker.py" and row["still_callable_now"] for row in rows)
    assert any(row["path"] == "scripts/working_memory_snapshot.py" and row["still_callable_now"] for row in rows)
    assert any(row["path"] == "scripts/wisdom_search.py" and row["real_task_specific_computation"] for row in rows)
    assert any(row["misleading_runtime_name"] and row["artifact_accessor_only"] for row in rows)
