from office.mission_command.e57_commercial_route_candidates import build_commercial_route_candidates


def test_route_candidates_include_required_routes_and_deny_outreach():
    data = build_commercial_route_candidates()
    assert data["route_count"] == 12
    routes = {r["route_id"]: r for r in data["routes"]}
    assert routes["direct_customer_outreach_now"]["allowed_action_type"] == "denied"
    assert routes["controlled_single_first_user_review_after_owner_approval"]["allowed_action_type"] == "owner_approval_required"
    assert all(not r["customer_validation_dependency"] or r["owner_approval_required"] for r in routes.values())

