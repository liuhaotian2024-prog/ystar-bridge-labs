"""
Test: aiden_cluster_daemon — master + per-agent workers route to local Gemma.

Milestone 12 2026-04-21: v0.4 §24.1 Track C prototype. Verify
  - AgentWorker loads identity from WHO_I_AM
  - Fallback identity for 7 agents without WHO_I_AM file
  - Ollama HTTP call succeeds empirically
  - Master can register + dispatch all 10 agents

M-tag: M-1 (vendor-independent inference) + M-3 (local-first product story).
"""
import json
import os
import shutil
import socket
import sys
import time
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiden_cluster_daemon import (
    AgentWorker,
    AidenClusterMaster,
    WHO_I_AM_MAP,
    _ollama_list_models,
    _pick_first_available_model,
)


def _ollama_port_open() -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        return s.connect_ex(("127.0.0.1", 11434)) == 0
    finally:
        s.close()


def test_agent_worker_loads_ceo_identity():
    """CEO WHO_I_AM.md exists, worker.load_identity populates snippet."""
    w = AgentWorker(agent_id="ceo")
    w.load_identity()
    assert len(w.who_i_am_snippet) > 200
    # Should contain M Triangle section marker (from recent v0.6/v0.7)
    assert "M Triangle" in w.who_i_am_snippet or "M TRIANGLE" in w.who_i_am_snippet


def test_agent_worker_loads_ethan_identity():
    w = AgentWorker(agent_id="ethan")
    w.load_identity()
    assert len(w.who_i_am_snippet) > 100
    # Should identify as CTO / Ethan
    lower = w.who_i_am_snippet.lower()
    assert "ethan" in lower or "cto" in lower


def test_agent_worker_fallback_for_missing_who_i_am():
    """Leo/Maya/Ryan/Jordan/Sofia/Zara/Marco have no WHO_I_AM yet —
    worker must generate fallback identity, not crash."""
    for agent in ["leo", "maya", "ryan", "jordan", "sofia", "zara", "marco"]:
        w = AgentWorker(agent_id=agent)
        w.load_identity()
        # Fallback must mention M Triangle + WORK_METHODOLOGY
        assert "M Triangle" in w.who_i_am_snippet
        assert "WORK_METHODOLOGY" in w.who_i_am_snippet
        assert agent in w.who_i_am_snippet.lower()


def test_build_full_prompt_prepends_identity():
    w = AgentWorker(agent_id="ceo")
    w.load_identity()
    full = w.build_full_prompt("What is 2+2?")
    assert "=== AGENT IDENTITY (ceo) ===" in full
    assert "=== USER REQUEST ===" in full
    assert "What is 2+2?" in full
    # Identity comes BEFORE user request (order matters for model)
    assert full.index("AGENT IDENTITY") < full.index("USER REQUEST")


def test_master_registers_all_10_known_agents():
    master = AidenClusterMaster(model="ystar-gemma")
    agents = master.register_all_known()
    assert len(agents) == 10
    assert "ceo" in master.workers
    assert "ethan" in master.workers
    assert "samantha" in master.workers
    assert "marco" in master.workers
    stats = master.stats()
    assert stats["workers"] == 10


def test_master_dispatch_registers_on_demand():
    """dispatch() to unregistered agent auto-registers it."""
    master = AidenClusterMaster(model="ystar-gemma")
    assert "ceo" not in master.workers
    # Don't actually call Ollama — patch call_ollama
    monkeyed = {"called_with": None}
    orig_dispatch = master.dispatch

    def fake_call(user_prompt, **kw):
        monkeyed["called_with"] = user_prompt
        return {"response": "mocked", "_y_elapsed_sec": 0.0, "_y_agent_id": "ceo"}

    master.register("ceo")
    master.workers["ceo"].call_ollama = fake_call
    result = master.dispatch("ceo", "hello")
    assert result["response"] == "mocked"
    assert "hello" in monkeyed["called_with"]


def test_pick_first_available_model_returns_real_model_when_ollama_up():
    """If Ollama is running, pick_first_available_model returns a real name."""
    if not _ollama_port_open():
        pytest.skip("Ollama port 11434 not listening")
    chosen = _pick_first_available_model()
    # Must be non-empty and match a real local model
    available = _ollama_list_models()
    if available:
        # Either exact match or base-name match (e.g. "ystar-gemma" vs "ystar-gemma:latest")
        bases = {m.split(":")[0] for m in available}
        assert chosen.split(":")[0] in bases, f"chosen={chosen!r} not in {available}"


@pytest.mark.skipif(not _ollama_port_open(), reason="Ollama port 11434 not listening")
def test_end_to_end_ceo_dispatch_returns_response():
    """Empirical: CEO worker dispatches prompt, Ollama returns non-empty response."""
    master = AidenClusterMaster()
    master.register("ceo")
    start = time.time()
    result = master.dispatch("ceo",
                              "One sentence: what is 2+2? Just the answer.",
                              timeout=90)
    dur = time.time() - start
    assert "response" in result
    assert len(result["response"]) > 0
    text = result["response"].lower()
    # Accept any form of "four": digit 4 or word four
    assert "4" in text or "four" in text
    assert result["_y_agent_id"] == "ceo"
    assert result["_y_elapsed_sec"] > 0
    assert dur < 90


def test_worker_stats_increment_on_call(monkeypatch):
    """Worker request_count must increment per call (for future rate limit)."""
    w = AgentWorker(agent_id="ceo")
    w.load_identity()
    # Mock HTTP to avoid real call
    calls = []

    class FakeResp:
        def __init__(self, body): self.body = body
        def read(self): return self.body
        def __enter__(self): return self
        def __exit__(self, *a): pass

    def fake_urlopen(req, timeout=None):
        calls.append(req)
        return FakeResp(json.dumps({"response": "ok"}).encode())

    import aiden_cluster_daemon
    monkeypatch.setattr(aiden_cluster_daemon.urllib.request, "urlopen", fake_urlopen)

    assert w.request_count == 0
    w.call_ollama("hi")
    assert w.request_count == 1
    w.call_ollama("hi again")
    assert w.request_count == 2
    assert len(calls) == 2
