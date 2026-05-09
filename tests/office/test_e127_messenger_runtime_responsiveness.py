from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_messenger_server_has_runtime_watchdog_and_threaded_handler():
    root = _repo_root()
    server = root / "office/agent_native_messenger/server.py"
    text = server.read_text(encoding="utf-8")
    assert "ThreadingHTTPServer" in text
    assert "AIDEN_MESSENGER_RUNTIME_TIMEOUT_SECONDS" in text
    assert "RUNTIME_EXECUTOR.submit" in text
    assert "runtime_timeout" in text
    assert "_runtime_notice_payload" in text
    assert "/api/health" in text


def test_messenger_browser_shows_pending_timeout_and_runtime_notices():
    root = _repo_root()
    script = root / "office/agent_native_messenger/main.js"
    text = script.read_text(encoding="utf-8")
    assert "MESSENGER_REQUEST_TIMEOUT_MS" in text
    assert "AbortController" in text
    assert "human_to_agent_pending" in text
    assert "appendSystemNotice" in text
    assert "Aiden is thinking through governed retrieval" in text
    assert "no silent hang" in text


def test_messenger_styles_include_visible_busy_and_error_states():
    root = _repo_root()
    styles = root / "office/agent_native_messenger/styles.css"
    text = styles.read_text(encoding="utf-8")
    assert ".runtime-status.busy" in text
    assert ".runtime-status.error" in text
    assert ".message.pending" in text
    assert ".composer button:disabled" in text
