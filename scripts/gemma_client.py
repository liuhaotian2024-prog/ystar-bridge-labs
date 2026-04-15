#!/usr/bin/env python3
"""
Gemma 4 client with shadow mode + CIEU quality audit.

Design: Leo 510ee408 + Samantha 871b1b9e quality monitor spec.
Auto-shadow first 100 calls for A/B comparison, emit CIEU quality events.

CIEU event_type: llm_quality_audit
Path: scripts/gemma_client.py
Scope: eng-kernel (Leo Chen)
"""

import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Optional

import requests

# ── Configuration ────────────────────────────────────────────────────────────

GEMMA_ENDPOINT = os.getenv("YSTAR_GEMMA_ENDPOINT", "http://localhost:11434")
GEMMA_MODEL = "ystar-gemma:latest"
SHADOW_COUNTER_FILE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_gemma_shadow_count")
SHADOW_THRESHOLD = 100  # First 100 calls auto-shadow
CIEU_DB = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
SHADOW_LOG_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/gemma_shadow_archive")

# Quality thresholds (Samantha spec)
SIMILARITY_MIN = 0.70
KEY_INFO_RETENTION_MIN = 0.80
LENGTH_RATIO_BAND = (0.5, 2.0)

# Fallback to Claude (Anthropic API key from env)
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4.5"


# ── Shadow counter persistence ───────────────────────────────────────────────

def _get_shadow_count() -> int:
    """Read shadow counter from disk (survives session restart)."""
    if not SHADOW_COUNTER_FILE.exists():
        return 0
    try:
        return int(SHADOW_COUNTER_FILE.read_text().strip() or "0")
    except (ValueError, FileNotFoundError):
        return 0


def _bump_shadow_count() -> int:
    """Increment shadow counter and persist to disk."""
    n = _get_shadow_count() + 1
    SHADOW_COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    SHADOW_COUNTER_FILE.write_text(str(n))
    return n


# ── Gemma/Claude API calls ───────────────────────────────────────────────────

def _call_gemma(prompt: str, max_tokens: int = 500) -> dict:
    """
    Call Gemma via Ollama API.

    Returns:
        {
            "provider": "ystar-gemma:latest",
            "text": "...",
            "tokens": 172,
            "latency_ms": 6360,
            "error": None | str
        }
    """
    start = time.perf_counter()
    try:
        resp = requests.post(
            f"{GEMMA_ENDPOINT}/api/generate",
            json={
                "model": GEMMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                }
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        latency_ms = int((time.perf_counter() - start) * 1000)

        return {
            "provider": GEMMA_MODEL,
            "text": data.get("response", ""),
            "tokens": data.get("eval_count", 0),
            "latency_ms": latency_ms,
            "error": None,
        }
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "provider": GEMMA_MODEL,
            "text": "",
            "tokens": 0,
            "latency_ms": latency_ms,
            "error": str(e),
        }


def _call_claude(prompt: str, max_tokens: int = 500) -> dict:
    """
    Call Claude via Anthropic API.

    Returns:
        {
            "provider": "claude-sonnet-4.5",
            "text": "...",
            "tokens": 189,
            "latency_ms": 1820,
            "error": None | str
        }
    """
    start = time.perf_counter()
    try:
        if not CLAUDE_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        latency_ms = int((time.perf_counter() - start) * 1000)

        text = ""
        if data.get("content"):
            text = data["content"][0].get("text", "")

        return {
            "provider": CLAUDE_MODEL,
            "text": text,
            "tokens": data.get("usage", {}).get("output_tokens", 0),
            "latency_ms": latency_ms,
            "error": None,
        }
    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return {
            "provider": CLAUDE_MODEL,
            "text": "",
            "tokens": 0,
            "latency_ms": latency_ms,
            "error": str(e),
        }


# ── Quality metrics ──────────────────────────────────────────────────────────

def _compute_similarity(gemma_out: str, claude_out: str) -> float:
    """SequenceMatcher ratio (0.0-1.0)."""
    if not gemma_out or not claude_out:
        return 0.0
    return SequenceMatcher(None, gemma_out, claude_out).ratio()


def _compute_key_info_retention(gemma_out: str, claude_out: str) -> float:
    """Jaccard similarity of token sets (0.0-1.0)."""
    g_tokens = set(gemma_out.lower().split())
    c_tokens = set(claude_out.lower().split())
    if not c_tokens:
        return 1.0
    return len(g_tokens & c_tokens) / len(c_tokens)


def _compute_length_ratio(gemma_out: str, claude_out: str) -> float:
    """Length ratio: len(gemma) / len(claude)."""
    if not claude_out:
        return 0.0
    return len(gemma_out) / len(claude_out)


# ── Shadow record persistence ────────────────────────────────────────────────

def _persist_shadow_record(prompt: str, gemma_result: dict, claude_result: dict) -> None:
    """
    Write shadow record to reports/gemma_shadow_archive/YYYYMMDD/call_NNNNN.json.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    day_dir = SHADOW_LOG_DIR / date_str
    day_dir.mkdir(parents=True, exist_ok=True)

    count = _get_shadow_count()
    call_id = f"call_{count:05d}"
    record_path = day_dir / f"{call_id}.json"

    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

    record = {
        "call_id": call_id,
        "timestamp": time.time(),
        "prompt_hash": prompt_hash,
        "prompt_snippet": prompt[:200],
        "gemma": gemma_result,
        "claude": claude_result,
        "metrics": {
            "similarity": _compute_similarity(gemma_result["text"], claude_result["text"]),
            "key_info_retention": _compute_key_info_retention(gemma_result["text"], claude_result["text"]),
            "length_ratio": _compute_length_ratio(gemma_result["text"], claude_result["text"]),
        },
    }

    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)


# ── CIEU quality event emission ──────────────────────────────────────────────

def _emit_cieu_quality_event(
    prompt: str,
    gemma_result: dict,
    claude_result: Optional[dict],
) -> None:
    """
    Emit CIEU llm_quality_audit event to .ystar_cieu.db.

    Schema:
        C: llm_quality_audit
        I: {prompt_hash, gemma_*, shadow, claude_*, similarity_score, ...}
        E: quality_compared | quality_threshold_breached
        U: <active_agent>
        τ: <timestamp>
    """
    try:
        # Compute active agent
        active_agent_file = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.ystar_active_agent")
        active_agent = "leo-kernel"
        if active_agent_file.exists():
            active_agent = active_agent_file.read_text().strip() or "leo-kernel"

        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

        intent_data = {
            "prompt_hash": prompt_hash,
            "gemma_provider": gemma_result["provider"],
            "gemma_tokens": gemma_result["tokens"],
            "gemma_latency_ms": gemma_result["latency_ms"],
            "gemma_error": gemma_result["error"],
            "shadow": claude_result is not None,
        }

        if claude_result:
            intent_data.update({
                "claude_model": claude_result["provider"],
                "claude_tokens": claude_result["tokens"],
                "claude_latency_ms": claude_result["latency_ms"],
                "claude_error": claude_result["error"],
                "similarity_score": _compute_similarity(gemma_result["text"], claude_result["text"]),
                "key_info_retention": _compute_key_info_retention(gemma_result["text"], claude_result["text"]),
                "length_ratio": _compute_length_ratio(gemma_result["text"], claude_result["text"]),
            })

        # Determine event type
        event_type = "quality_compared"
        if claude_result:
            sim = intent_data["similarity_score"]
            retention = intent_data["key_info_retention"]
            if sim < SIMILARITY_MIN or retention < KEY_INFO_RETENTION_MIN:
                event_type = "quality_threshold_breached"

        # Write to CIEU DB
        conn = sqlite3.connect(CIEU_DB)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (timestamp, event_type, agent, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            time.time(),
            event_type,  # quality_compared | quality_threshold_breached
            active_agent,
            json.dumps(intent_data),
        ))
        conn.commit()
        conn.close()
    except Exception:
        # Fail-open: CIEU emission failure doesn't block inference
        pass


# ── Public API ───────────────────────────────────────────────────────────────

def generate(prompt: str, max_tokens: int = 500, force_shadow: bool = False) -> dict:
    """
    Generate via Gemma. Auto shadow-call Claude for first 100 calls OR if force_shadow=True.

    Args:
        prompt: Input prompt
        max_tokens: Max output tokens
        force_shadow: Force A/B comparison even after 100 calls

    Returns:
        {
            "provider": "ystar-gemma:latest",
            "text": "...",
            "tokens": 172,
            "latency_ms": 6360,
            "error": None | str,
            "shadowed": bool,
            "metrics": {...} | None  # only if shadowed
        }
    """
    n = _get_shadow_count()
    do_shadow = force_shadow or n < SHADOW_THRESHOLD

    # Primary: Gemma
    gemma_result = _call_gemma(prompt, max_tokens)

    # Shadow: Claude (blocking A/B comparison)
    claude_result = None
    if do_shadow and not gemma_result["error"]:
        claude_result = _call_claude(prompt, max_tokens)
        _bump_shadow_count()
        _persist_shadow_record(prompt, gemma_result, claude_result)

    # Emit CIEU quality event (every call)
    _emit_cieu_quality_event(prompt, gemma_result, claude_result)

    # Return primary result + metadata
    result = {**gemma_result, "shadowed": claude_result is not None}
    if claude_result:
        result["metrics"] = {
            "similarity": _compute_similarity(gemma_result["text"], claude_result["text"]),
            "key_info_retention": _compute_key_info_retention(gemma_result["text"], claude_result["text"]),
            "length_ratio": _compute_length_ratio(gemma_result["text"], claude_result["text"]),
        }

    return result


def fallback_to_claude(prompt: str, max_tokens: int = 500) -> dict:
    """
    Emergency fallback to Claude when Gemma is unavailable.

    Use this when Gemma returns error or when Board-facing output is required.
    """
    return _call_claude(prompt, max_tokens)


if __name__ == "__main__":
    # Self-test
    test_prompt = "Summarize Y*gov in one sentence."
    print(f"Testing Gemma client with prompt: '{test_prompt}'")
    result = generate(test_prompt, max_tokens=100)
    print(f"\nResult:")
    print(json.dumps(result, indent=2))
