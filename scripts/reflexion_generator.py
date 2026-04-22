#!/usr/bin/env python3
"""Reflexion Generator — verbal episodic memory for failure events.

Reflexion pattern (arxiv 2303.11366): when an agent fails, generate a
concise verbal reflection on what went wrong, store it as episodic memory,
inject into next similar context. No weight updates, just episodic guidance.

Y*gov integration:
  - Triggered by OmissionEngine tracked_entity overdue OR CIEU event Rt+1 > 0
  - LLM call routes through aiden_cluster_daemon local Gemma (tier: reflection_generation → ystar-gemma)
  - Writes brain node of type `reflection/<cieu_event_id>` into aiden_brain.db
  - Provenance = system:reflection; excluded from future L2 co-activation to avoid recursion

M-tag: M-2a (learn from failure, commission prevention) + M-2b (reduce reactive loops).

Not wired into hook chain yet — standalone callable module, integration
happens in Wave 3 (settings.json UserPromptSubmit + omission_engine callback).
"""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

AIDEN_BRAIN_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/aiden_brain.db")


REFLECTION_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS reflections (
    reflection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cieu_event_id TEXT NOT NULL,
    rt_value INTEGER,
    failure_context TEXT,
    reflection_text TEXT NOT NULL,
    tier TEXT DEFAULT 'episodic',
    created_at REAL NOT NULL,
    provenance TEXT DEFAULT 'system:reflection'
);
CREATE INDEX IF NOT EXISTS idx_reflections_event ON reflections(cieu_event_id);
CREATE INDEX IF NOT EXISTS idx_reflections_created ON reflections(created_at);
"""


@dataclass
class ReflectionResult:
    reflection_id: int
    cieu_event_id: str
    text: str
    rt_value: int
    created_at: float


class ReflexionGenerator:
    """Generate + persist verbal reflections on failure events."""

    def __init__(self, brain_db_path: Path = AIDEN_BRAIN_PATH,
                 llm_call_fn=None):
        """llm_call_fn: callable(prompt: str) -> str. If None, uses simple deterministic
        fallback so tests / offline use can still produce reflections."""
        self.brain_db_path = brain_db_path
        self.llm_call_fn = llm_call_fn or self._default_llm_fallback
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        conn = sqlite3.connect(str(self.brain_db_path), timeout=5)
        conn.executescript(REFLECTION_TABLE_SCHEMA)
        conn.commit()
        conn.close()

    def _default_llm_fallback(self, prompt: str) -> str:
        """Offline fallback: structural reflection without LLM.
        Used when aiden_cluster_daemon is unavailable (e.g. pytest, offline)."""
        return (
            "[offline reflection] Event failed. Reviewing action chain "
            "to extract lessons: (1) what tool sequence led to failure, "
            "(2) what state was missing, (3) what the next attempt should "
            "verify first. Apply Iron Rule 3 (empirical verify) and P-12 "
            "(先查后造) next attempt."
        )

    def _build_prompt(self, cieu_event_id: str, rt_value: int,
                      failure_context: str) -> str:
        return (
            f"You are the reflection layer of a governed AI agent.\n"
            f"An action just completed with Rt+1={rt_value} (≥1 = imperfect).\n"
            f"CIEU event id: {cieu_event_id}\n\n"
            f"Failure context (raw):\n{failure_context[:1200]}\n\n"
            f"Produce a 3-5 sentence verbal reflection covering:\n"
            f"1) What went wrong (concrete cause, not feelings)\n"
            f"2) What the agent knew but did not apply\n"
            f"3) Next-time rule (one actionable, not vague)\n"
            f"Output ONLY the reflection text. No preamble, no apology."
        )

    def generate_reflection(self, cieu_event_id: str, rt_value: int,
                            failure_context: str) -> ReflectionResult:
        """Generate + persist reflection. Skip if event is itself a reflection
        (anti-recursion guard, per CEO v2 Section 3.3 self-ref exclusion)."""
        if cieu_event_id.startswith("reflection/") or "reflection_generation" in failure_context:
            return self._skip_recursion(cieu_event_id)

        prompt = self._build_prompt(cieu_event_id, rt_value, failure_context)
        text = self.llm_call_fn(prompt).strip()
        if not text:
            text = self._default_llm_fallback(prompt).strip()

        created = time.time()
        conn = sqlite3.connect(str(self.brain_db_path), timeout=5)
        cur = conn.execute(
            "INSERT INTO reflections (cieu_event_id, rt_value, failure_context, "
            "reflection_text, tier, created_at, provenance) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cieu_event_id, rt_value, failure_context[:2000], text,
             "episodic", created, "system:reflection")
        )
        rid = cur.lastrowid or 0
        conn.commit()
        conn.close()

        return ReflectionResult(
            reflection_id=rid, cieu_event_id=cieu_event_id,
            text=text, rt_value=rt_value, created_at=created,
        )

    def _skip_recursion(self, cieu_event_id: str) -> ReflectionResult:
        return ReflectionResult(
            reflection_id=-1, cieu_event_id=cieu_event_id,
            text="[skipped: recursion guard]", rt_value=0, created_at=time.time(),
        )

    def retrieve_recent(self, limit: int = 5) -> list[ReflectionResult]:
        conn = sqlite3.connect(str(self.brain_db_path), timeout=5)
        rows = conn.execute(
            "SELECT reflection_id, cieu_event_id, reflection_text, rt_value, created_at "
            "FROM reflections ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return [ReflectionResult(*r) for r in rows]

    def count(self) -> int:
        conn = sqlite3.connect(str(self.brain_db_path), timeout=5)
        n = conn.execute("SELECT COUNT(*) FROM reflections").fetchone()[0]
        conn.close()
        return n


def _llm_via_cluster_daemon(prompt: str) -> str:
    """Production LLM call routing through aiden_cluster_daemon (local Gemma)."""
    try:
        from aiden_cluster_daemon import AgentWorker, pick_tier
        model = pick_tier("reflection_generation")
        w = AgentWorker(agent_id="ceo", model=model)
        w.load_identity()
        result = w.call_ollama(prompt, timeout=60)
        return result.get("response", "")
    except Exception as e:
        return f"[fallback: ollama unavailable: {type(e).__name__}]"


if __name__ == "__main__":
    gen = ReflexionGenerator(llm_call_fn=_llm_via_cluster_daemon)
    r = gen.generate_reflection(
        cieu_event_id="test/cli",
        rt_value=1,
        failure_context="CLI smoke: no real failure, just testing reflection pipeline."
    )
    print(f"[reflexion] created id={r.reflection_id} text={r.text[:200]!r}")
    print(f"[reflexion] total reflections in brain: {gen.count()}")
