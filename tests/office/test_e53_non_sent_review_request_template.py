from office.mission_command.e53_non_sent_review_request_template import build_non_sent_review_request_template

def test_template_is_not_sent_and_has_no_contact():
    data = build_non_sent_review_request_template()
    assert data["sent"] is False
    assert data["contact_identified"] is False
    assert data["contact_info_collected"] is False
    assert data["owner_approval_required_before_send"] is True
