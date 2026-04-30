import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_FILE = ROOT / "policy" / "secret_scanning_policy.json"
HELPER_FILE = ROOT / "policy" / "secret_scanner_policy.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("secret_scanner_policy", HELPER_FILE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_policy_file_and_helper_exist() -> None:
    policy = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    assert policy["policy_id"] == "secret_scanning_context_policy_v0"
    assert "TAVILY_API_KEY" in {item["family"] for item in policy["forbidden_real_secret_patterns"]}
    assert HELPER_FILE.is_file()


def test_real_looking_provider_keys_are_blocked() -> None:
    helper = load_helper()
    samples = [
        "tvly-fake-real-looking-secret-value-1234567890abcdef",
        "BRAVE_SEARCH_API_KEY=brave-fake-real-looking-secret-1234567890abcdef",
        "SERPAPI_API_KEY=serpapi-fake-real-looking-secret-1234567890abcdef",
    ]
    for sample in samples:
        decision = helper.classify_secret_pattern(sample, file_path="tests/fixtures/test_secret_policy.py")
        assert decision["safe_for_commit"] is False
        assert decision["decision"] == "hard_forbidden_real_secret"


def test_approved_placeholders_are_allowed() -> None:
    helper = load_helper()
    placeholders = [
        "TAVILY_API_KEY_PLACEHOLDER",
        "TAVILY_API_KEY_REDACTED",
        "SECRET_EXAMPLE_TAVILY_API_KEY",
        "TVLY_TEST_PREFIX_EXAMPLE",
    ]
    for placeholder in placeholders:
        decision = helper.classify_secret_pattern(placeholder, file_path="tests/fixtures/test_secret_policy.py")
        assert decision["safe_for_commit"] is True
        assert decision["decision"] in {"allowed_redacted_placeholder", "allowed_test_fixture"}


def test_raw_assignment_blocked_and_redacted_assignment_allowed() -> None:
    helper = load_helper()
    raw = helper.classify_secret_pattern(
        "TAVILY_API_KEY=tvly-fake-real-looking-secret-value-1234567890abcdef",
        file_path="tests/fixtures/test_secret_policy.py",
    )
    assert raw["decision"] == "hard_forbidden_real_secret"
    assert raw["safe_for_commit"] is False

    redacted = helper.classify_secret_pattern(
        "TAVILY_API_KEY=<REDACTED>",
        file_path="docs/example.md",
        context_hint="documentation",
    )
    assert redacted["decision"] == "allowed_documentation_example"
    assert redacted["safe_for_commit"] is True


def test_documentation_example_and_test_fixture_contexts() -> None:
    helper = load_helper()
    doc = helper.classify_secret_pattern(
        "Authorization: Bearer <REDACTED>",
        file_path="docs/secret_scanning_test_fixture_conventions.md",
        context_hint="documentation",
    )
    assert doc["safe_for_commit"] is True

    fixture = helper.classify_secret_pattern(
        "TEST_ONLY_API_KEY_PLACEHOLDER",
        file_path="tests/fixtures/test_secret_policy.py",
        context_hint="test_fixture",
    )
    assert fixture["decision"] == "allowed_test_fixture"
    assert fixture["safe_for_commit"] is True

    unsafe_fixture = helper.classify_secret_pattern(
        "SERPAPI_API_KEY=serpapi-fake-real-looking-secret-1234567890abcdef",
        file_path="tests/fixtures/test_secret_policy.py",
        context_hint="test_fixture",
    )
    assert unsafe_fixture["safe_for_commit"] is False


def test_helper_does_not_echo_secret_value_in_reason() -> None:
    helper = load_helper()
    candidate = "tvly-fake-real-looking-secret-value-1234567890abcdef"
    decision = helper.classify_secret_pattern(candidate, file_path="tests/test_secret_policy.py")
    explanation = helper.explain_secret_scan_decision(decision)
    assert candidate not in decision["reason"]
    assert candidate not in explanation
    assert decision["matched_family"] == "TAVILY_API_KEY"


def test_unsafe_contexts_are_blocked_or_review_required() -> None:
    helper = load_helper()
    unsafe = helper.classify_secret_pattern(
        "API_KEY=unredacted-secret-like-value-1234567890",
        file_path=".env",
    )
    assert unsafe["safe_for_commit"] is False
    assert unsafe["decision"] in {"hard_forbidden_real_secret", "blocked_suspicious_secret"}


def test_scan_text_classifies_safe_and_unsafe_candidates() -> None:
    helper = load_helper()
    text = "\n".join(
        [
            "TAVILY_API_KEY=<REDACTED>",
            "SECRET_EXAMPLE_TAVILY_API_KEY",
            "TAVILY_API_KEY=tvly-fake-real-looking-secret-value-1234567890abcdef",
        ]
    )
    decisions = helper.scan_text_for_secret_policy(text, file_path="tests/test_secret_policy.py")
    assert any(item["safe_for_commit"] is True for item in decisions)
    assert any(item["safe_for_commit"] is False for item in decisions)


def test_no_runtime_secret_surfaces_are_needed_or_modified() -> None:
    helper_text = HELPER_FILE.read_text(encoding="utf-8")
    receipt = json.loads((ROOT / "l7_secret_scanner_policy" / "no_secret_leakage_receipt.json").read_text(encoding="utf-8"))
    for marker in [".db", ".db-wal", ".db-shm", ".log", "active_agent", "controlled_observation.env"]:
        assert marker in helper_text
    assert receipt["db_files_read"] is False
    assert receipt["wal_files_read"] is False
    assert receipt["shm_files_read"] is False
    assert receipt["active_agent_marker_content_read"] is False
    assert receipt["y_star_gov_modified"] is False
    assert receipt["gov_mcp_modified"] is False
