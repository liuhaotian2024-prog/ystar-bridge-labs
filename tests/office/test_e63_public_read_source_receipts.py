from office.mission_command.e63_opportunity_discovery_core import build_public_read_source_receipts


class _FakeResult:
    url = "https://example.com/"
    domain = "example.com"
    status = 200
    retrieved_at = "2026-05-06T00:00:00Z"
    title = "Agent Workflow Reliability"
    text_excerpt = "Agent workflows need guardrails, tracing, evaluation, tool control, and reliable operations."
    safety_errors = []
    blocked_reason = ""
    bytes_read = 128
    external_action_executed = False


class _FakeReader:
    def read(self, _url):
        return _FakeResult()


def test_e63_receipts_can_be_created_from_controlled_public_reads_without_contact():
    data = build_public_read_source_receipts(reader=_FakeReader())
    assert data["source_receipt_count"] == data["planned_source_count"]
    assert data["live_successful_read_count"] == data["planned_source_count"]
    first = data["receipts"][0]
    assert first["retrieval_status"] == "public_read_success"
    assert first["no_contact_info_extracted"] is True
    assert first["not_customer_validation"] is True
