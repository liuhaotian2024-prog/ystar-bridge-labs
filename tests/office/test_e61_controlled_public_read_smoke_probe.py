from urllib.error import URLError

from office.mission_command.e61_live_public_read_core import controlled_public_read_smoke_probe


class _FakeResponse:
    status = 200
    headers = {"Content-Type": "text/html; charset=utf-8"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _max_bytes):
        return b"<html><title>Example Domain</title><body>Example public read only fixture.</body></html>"


class _SuccessOpener:
    def open(self, request, timeout):
        return _FakeResponse()


class _NetworkDownOpener:
    def open(self, request, timeout):
        raise URLError("temporary failure in name resolution")


def test_e61_smoke_probe_can_pass_with_controlled_fake_public_page():
    data = controlled_public_read_smoke_probe(["https://example.com/"], opener=_SuccessOpener())
    assert data["controlled_public_read_smoke_probe_passed"] is True
    assert data["final_status"] == "live_public_read_adapter_repaired_and_smoke_passed"
    assert data["receipts"][0]["retrieval_status"] == "public_read_success"
    assert data["receipts"][0]["no_contact_info_extracted"] is True


def test_e61_smoke_probe_classifies_network_unavailable_without_faking_success():
    data = controlled_public_read_smoke_probe(["https://example.com/"], opener=_NetworkDownOpener())
    assert data["controlled_public_read_smoke_probe_passed"] is False
    assert data["final_status"] == "live_public_read_code_repaired_but_host_network_unavailable"
    assert data["receipts"][0]["retrieval_status"] == "fetch_failed"
    assert data["receipts"][0]["failure_classification"] in {"DNS_unavailable", "host_network_unavailable"}


def test_e61_smoke_probe_blocks_non_allowlisted_or_login_sources():
    data = controlled_public_read_smoke_probe(["https://example.com/login"], opener=_SuccessOpener())
    assert data["receipts"][0]["retrieval_status"] == "policy_denied"
    assert "url_not_in_e61_allowlist" in data["receipts"][0]["safety_errors"]
