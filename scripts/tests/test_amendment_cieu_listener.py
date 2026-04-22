"""Test: AMENDMENT CIEU listener — polls proposals jsonl, updates inbox."""
import json
import os
import sys
import time
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_listener_handles_no_log_file(tmp_path, monkeypatch):
    import amendment_cieu_listener as mod
    monkeypatch.setattr(mod, "PROPOSALS_LOG", tmp_path / "nope.jsonl")
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")
    monkeypatch.setattr(mod, "INBOX", tmp_path / "inbox.md")
    assert mod.main() == 0


def test_listener_processes_new_proposals(tmp_path, monkeypatch):
    import amendment_cieu_listener as mod
    log = tmp_path / "proposals.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        for i, tier in enumerate(["low", "medium"]):
            f.write(json.dumps({
                "event_type": "SELF_MOD_PROPOSAL",
                "timestamp": time.time(),
                "amendment_id": f"AMEND_TEST_{i}",
                "tier": tier,
                "title": f"Test {i}",
                "draft_path": f"/tmp/draft_{i}.md",
            }) + "\n")

    monkeypatch.setattr(mod, "PROPOSALS_LOG", log)
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")
    monkeypatch.setattr(mod, "INBOX", tmp_path / "inbox.md")
    mod.main()
    assert (tmp_path / "inbox.md").exists()
    text = (tmp_path / "inbox.md").read_text()
    assert "AMEND_TEST_0" in text
    assert "AMEND_TEST_1" in text


def test_listener_idempotent(tmp_path, monkeypatch):
    import amendment_cieu_listener as mod
    log = tmp_path / "proposals.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        f.write(json.dumps({
            "event_type": "SELF_MOD_PROPOSAL",
            "timestamp": time.time(),
            "amendment_id": "IDEM",
            "tier": "low",
            "title": "idem",
            "draft_path": "/tmp/x.md",
        }) + "\n")

    inbox = tmp_path / "inbox.md"
    monkeypatch.setattr(mod, "PROPOSALS_LOG", log)
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")
    monkeypatch.setattr(mod, "INBOX", inbox)
    mod.main()
    first = inbox.stat().st_size
    mod.main()
    assert inbox.stat().st_size == first


def test_listener_ignores_non_self_mod_events(tmp_path, monkeypatch):
    import amendment_cieu_listener as mod
    log = tmp_path / "proposals.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        f.write(json.dumps({
            "event_type": "SOMETHING_ELSE",
            "timestamp": time.time(),
            "amendment_id": "NOPE",
        }) + "\n")

    inbox = tmp_path / "inbox.md"
    monkeypatch.setattr(mod, "PROPOSALS_LOG", log)
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")
    monkeypatch.setattr(mod, "INBOX", inbox)
    mod.main()
    assert not inbox.exists()


def test_listener_inbox_has_czl159_header(tmp_path, monkeypatch):
    import amendment_cieu_listener as mod
    log = tmp_path / "proposals.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        f.write(json.dumps({
            "event_type": "SELF_MOD_PROPOSAL",
            "timestamp": time.time(),
            "amendment_id": "A",
            "tier": "low",
            "title": "t",
            "draft_path": "/tmp/x.md",
        }) + "\n")

    inbox = tmp_path / "inbox.md"
    monkeypatch.setattr(mod, "PROPOSALS_LOG", log)
    monkeypatch.setattr(mod, "SENTINEL", tmp_path / "sentinel.json")
    monkeypatch.setattr(mod, "INBOX", inbox)
    mod.main()
    text = inbox.read_text()
    assert "Audience:" in text
    assert "Research basis:" in text
    assert "Synthesis:" in text
    assert "Purpose:" in text
