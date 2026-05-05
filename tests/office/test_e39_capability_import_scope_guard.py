from office.mission_command.e39_capability_import_scope_guard import build_capability_import_scope_guard


def test_scope_guard_allows_only_internal_imports():
    guard = build_capability_import_scope_guard()
    assert "source graph schema" in guard["allowed_imports"]
    assert "provider/API execution" in guard["forbidden_actions"]
    assert guard["all_new_files_are_allowed_classes"] is True
    assert guard["external_execution_implied"] is False
    assert guard["duplicate_governance_or_execution_semantics_created"] is False
    assert guard["customer_validation_claimed"] is False
    assert guard["paid_signal_claimed"] is False
    assert {f["classification"] for f in guard["new_file_classification"]} <= {"schema", "builder", "evaluator", "delta", "report", "test"}
