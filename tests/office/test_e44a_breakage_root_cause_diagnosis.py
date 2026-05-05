from office.mission_command.e44a_breakage_root_cause_diagnosis import diagnose_capability_breakage

def test_root_cause_names_required_failure_modes():
    artifact = diagnose_capability_breakage()
    causes = {item["root_cause"] for item in artifact["root_causes"]}
    for expected in ["artifact_accessor_only", "static_artifact_not_runtime", "missing_first_class_tags", "missing_synonyms", "workflow_coverage", "test_blind_spot", "no_task_time_cascade", "no_activation_registry", "overconservative_boundary_drift"]:
        assert expected in causes
    assert artifact["no_external_action"] is True
