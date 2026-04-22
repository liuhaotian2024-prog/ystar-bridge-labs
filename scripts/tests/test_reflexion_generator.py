"""Test: ReflexionGenerator — verbal episodic memory for failures.

Covers: schema init, generate + persist, recursion guard, retrieve_recent, count.
Uses tmp brain db + mock LLM fn to avoid Ollama dependency.
"""
import os
import sys
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reflexion_generator import ReflexionGenerator, ReflectionResult


def _mock_llm(prompt: str) -> str:
    return "Concrete cause: X. Missing knowledge: Y. Next-time rule: verify Z first."


def test_init_creates_schema(tmp_path):
    db = tmp_path / "test_brain.db"
    gen = ReflexionGenerator(brain_db_path=db, llm_call_fn=_mock_llm)
    assert db.exists()
    assert gen.count() == 0


def test_generate_persists_reflection(tmp_path):
    db = tmp_path / "test_brain.db"
    gen = ReflexionGenerator(brain_db_path=db, llm_call_fn=_mock_llm)
    r = gen.generate_reflection(
        cieu_event_id="evt123",
        rt_value=2,
        failure_context="Sub-agent returned Rt=2 because missing pytest evidence.",
    )
    assert r.reflection_id > 0
    assert r.cieu_event_id == "evt123"
    assert r.rt_value == 2
    assert "cause" in r.text.lower() or "next-time" in r.text.lower()
    assert gen.count() == 1


def test_recursion_guard_reflection_prefix(tmp_path):
    db = tmp_path / "test_brain.db"
    gen = ReflexionGenerator(brain_db_path=db, llm_call_fn=_mock_llm)
    r = gen.generate_reflection(
        cieu_event_id="reflection/prior_event",
        rt_value=1,
        failure_context="anything",
    )
    assert r.reflection_id == -1
    assert "recursion guard" in r.text
    assert gen.count() == 0


def test_recursion_guard_context_match(tmp_path):
    db = tmp_path / "test_brain.db"
    gen = ReflexionGenerator(brain_db_path=db, llm_call_fn=_mock_llm)
    r = gen.generate_reflection(
        cieu_event_id="evt456",
        rt_value=1,
        failure_context="reflection_generation recursion signal",
    )
    assert r.reflection_id == -1
    assert gen.count() == 0


def test_retrieve_recent_ordering(tmp_path):
    db = tmp_path / "test_brain.db"
    gen = ReflexionGenerator(brain_db_path=db, llm_call_fn=_mock_llm)
    for i in range(3):
        gen.generate_reflection(f"evt{i}", 1, f"ctx {i}")
    results = gen.retrieve_recent(limit=3)
    assert len(results) == 3
    # Most recent first
    assert results[0].cieu_event_id == "evt2"


def test_default_llm_fallback_produces_nonempty(tmp_path):
    db = tmp_path / "test_brain.db"
    gen = ReflexionGenerator(brain_db_path=db)  # no llm_call_fn → default fallback
    r = gen.generate_reflection("evt_fallback", 1, "failure context")
    assert r.reflection_id > 0
    assert len(r.text) > 50


def test_empty_llm_response_triggers_fallback(tmp_path):
    db = tmp_path / "test_brain.db"
    gen = ReflexionGenerator(brain_db_path=db, llm_call_fn=lambda _: "")
    r = gen.generate_reflection("evt_empty", 1, "failure context")
    assert r.reflection_id > 0
    assert len(r.text) > 0  # fell back to default
