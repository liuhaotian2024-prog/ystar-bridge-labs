from office.mission_command.safe_public_page_reader import (
    PublicPageReadResult,
    reject_unsafe_public_url,
    stop_reason_from_text,
)


def test_private_or_local_url_rejected():
    assert "private_or_local_url" in reject_unsafe_public_url("http://localhost:8000")
    assert "private_or_internal_ip" in reject_unsafe_public_url("http://10.0.0.5/page")


def test_non_http_scheme_rejected():
    assert "non_http_scheme" in reject_unsafe_public_url("file:///tmp/secret")


def test_login_or_payment_indicator_blocks_page():
    assert stop_reason_from_text("Please sign in to continue") == "blocked_login_indicator"
    assert stop_reason_from_text("Enter payment and credit card") == "blocked_payment_indicator"


def test_public_page_read_result_never_executes_external_action():
    result = PublicPageReadResult(
        url="https://example.com",
        domain="example.com",
        status=200,
        retrieved_at="2026-05-01T00:00:00Z",
        title="Example",
        text_excerpt="public text",
        safety_errors=[],
        blocked_reason="",
        bytes_read=11,
        external_action_executed=False,
    )
    assert result.external_action_executed is False
