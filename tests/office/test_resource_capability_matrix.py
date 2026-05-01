from pathlib import Path

from office.mission_command.resource_capability_matrix import (
    build_behavior_capability_matrix,
    build_resource_inventory,
    find_behavior_capability,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_resource_matrix_contains_y_star_gov_gov_mcp_aiden_mission_command():
    resources = build_resource_inventory(REPO_ROOT)
    names = {item["resource"] for item in resources}
    assert "Y-star-gov" in names
    assert "gov-mcp" in names
    assert "Aiden CEO Meeting Room" in names
    assert "Mission Command" in names


def test_behavior_matrix_separates_autonomous_from_owner_approved_actions():
    matrix = build_behavior_capability_matrix(REPO_ROOT)
    by_name = {item["capability"]: item for item in matrix}
    assert by_name["internal analysis"]["autonomous_now"] is True
    assert by_name["customer contact"]["autonomous_now"] is False
    assert by_name["customer contact"]["requires_owner_approval"] is True


def test_behavior_matrix_marks_customer_contact_as_approval_required():
    item = find_behavior_capability(REPO_ROOT, "contact customer")
    assert item["current_status"] == "approval_required"
    assert item["external_side_effect"] is True


def test_behavior_matrix_marks_core_writeback_as_review_gated():
    item = find_behavior_capability(REPO_ROOT, "core memory writeback")
    assert item["current_status"] == "review_gated"
    assert item["requires_owner_approval"] is True


def test_no_external_side_effects():
    matrix = build_behavior_capability_matrix(REPO_ROOT)
    assert all("executed" not in item["current_status"] for item in matrix)


def test_no_customer_contact():
    item = find_behavior_capability(REPO_ROOT, "customer contact")
    assert item["autonomous_now"] is False


def test_no_email():
    item = find_behavior_capability(REPO_ROOT, "email/message sending")
    assert item["requires_owner_approval"] is True


def test_no_payment():
    item = find_behavior_capability(REPO_ROOT, "payment")
    assert item["current_status"] == "blocked_or_review_gated"


def test_no_publication():
    item = find_behavior_capability(REPO_ROOT, "publication")
    assert item["requires_owner_approval"] is True


def test_no_core_db_writeback():
    item = find_behavior_capability(REPO_ROOT, "core writeback")
    assert item["current_status"] == "review_gated"
