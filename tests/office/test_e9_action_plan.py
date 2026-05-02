from office.mission_command.e9_action_plan import action_plan_respects_budget, build_e9_validation_action_plan
from office.mission_command.e9_draft_binding import E9DraftBinding


def test_e9_action_plan_respects_autonomy_budget():
    plan = build_e9_validation_action_plan(None, [], [E9DraftBinding("d1", "h1", "path", "email", True, True, False, [])])
    assert action_plan_respects_budget(plan, 3)
    assert "missing_manifest" in plan.blocker_reasons
