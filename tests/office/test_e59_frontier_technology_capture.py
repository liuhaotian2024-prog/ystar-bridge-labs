from office.mission_command.e59_frontier_technology_capture import run_frontier_technology_capture


def test_frontier_technology_and_academic_learning_capture_exists_without_contact():
    data = run_frontier_technology_capture()
    assert data["idea_count"] >= 4
    assert data["academic_technical_learning_capture_valid"] is True
    assert data["no_author_contact"] is True
    assert data["no_expert_feedback_claim"] is True
    assert all(idea["requires_human_contact"] is False for idea in data["captured_ideas"])

