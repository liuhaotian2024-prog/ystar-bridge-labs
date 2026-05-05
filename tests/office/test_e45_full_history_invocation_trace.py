from office.mission_command.e45_full_history_invocation_trace import build_full_history_actual_invocation_trace

def test_actual_invocation_trace_has_real_records():
    trace = build_full_history_actual_invocation_trace()
    assert trace["actual_invocation_family_count"] >= 8
    assert trace["assertion_invoked_requires_result_data"] is True
    families = {r["family"] for r in trace["actual_invocation_records"]}
    for expected in ["Article 11 / CEO OS", "Working memory / LRS", "Wisdom search / CEO wisdom corpus", "Commercial / plugin / sales assets", "Notification / Board loop", "K9 / CIEU / CZL audit context", "E42 / E44A / E43 activated runtime"]:
        assert expected in families
    assert trace["no_external_action"] is True
