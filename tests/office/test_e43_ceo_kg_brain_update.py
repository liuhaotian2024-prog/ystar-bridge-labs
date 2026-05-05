from office.mission_command.e43_ceo_brain_live_work_loop_update import build_ceo_brain_live_work_loop_update
from office.mission_command.e43_ceo_kg_live_work_loop_feedback import build_ceo_kg_live_work_loop_feedback


def test_e43_ceo_kg_and_brain_update_are_delta_only():
    brain = build_ceo_brain_live_work_loop_update()
    kg = build_ceo_kg_live_work_loop_feedback()
    assert brain["live_company_work_loop_completed"] is True
    assert brain["second_CEO_brain_created"] is False
    assert brain["second_CEO_KG_created"] is False
    assert kg["node_count"] >= 5
    assert kg["paid_signal_claimed"] is False
