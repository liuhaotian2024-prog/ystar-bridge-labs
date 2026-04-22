#!/usr/bin/env python3
"""
Aiden Cluster Daemon (Milestone 12, 2026-04-21).

v0.4 §24.1 Track C — master daemon + per-agent asyncio workers that route
inference to local Ollama (Gemma) instead of Claude Code API. Makes Aiden
survive Claude Code session close, and lets the whole 9-agent team think
locally.

Architecture:
    AidenClusterMaster (single Python process)
      ├─ AgentWorker("ceo")        — reads WHO_I_AM.md as system prompt
      ├─ AgentWorker("ethan")       — reads WHO_I_AM_ETHAN.md
      ├─ AgentWorker("samantha")    — WHO_I_AM_SAMANTHA.md
      └─ ... 7 more (leo/maya/ryan/jordan/sofia/zara/marco)
    │
    └─ shared resources:
       - Ollama HTTP (localhost:11434) for inference
       - per-agent brain.db for context retrieval + write-back
       - czl_bus for commitment/dispatch publish

POC scope (this milestone):
    - AgentWorker class with identity + Ollama HTTP call
    - Master coordinator with dispatch(agent_id, prompt) API
    - Fallback model selection: ystar-gemma → gemma4:e4b (whichever exists)
    - pytest covers: worker init, identity prepend, HTTP call, response non-empty

Out of scope (next milestones):
    - launchd plist for 24/7 (M13)
    - per-agent brain.db context injection + writeback (M14 — integrates with
      cieu_brain_daemon existing pipeline)
    - Multi-agent concurrency + priority queue (M15, per v0.4 §24.1 guard 4)

M-tag: M-1 (Aiden survives session close) + M-3 (local-first Layer 3).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")

# Per-agent WHO_I_AM paths (mirror hook_who_i_am_staleness.WHO_I_AM_MAP)
WHO_I_AM_MAP = {
    "ceo":       WORKSPACE / "knowledge/ceo/wisdom/WHO_I_AM.md",
    "ethan":     WORKSPACE / "knowledge/cto/wisdom/WHO_I_AM_ETHAN.md",
    "samantha":  WORKSPACE / "knowledge/secretary/wisdom/WHO_I_AM_SAMANTHA.md",
    # 7 other agents: WHO_I_AM files pending CZL-MISSING-WHO-I-AM-7-AGENTS
}

def _resolve_ollama_url() -> str:
    """Ollama client URL. OLLAMA_HOST env is server listen addr (e.g. 0.0.0.0)
    which is not valid for client; normalize to localhost + explicit scheme."""
    raw = os.environ.get("OLLAMA_CLIENT_URL") or os.environ.get("OLLAMA_HOST") or ""
    raw = raw.strip()
    # If env is listen addr or empty → hard default to localhost
    if not raw or raw.startswith("0.0.0.0"):
        return "http://127.0.0.1:11434"
    # Force scheme
    if "://" not in raw:
        raw = f"http://{raw}"
    # Force port if missing
    tail = raw.rstrip("/").rsplit(":", 1)[-1]
    if not tail.isdigit():
        raw = f"{raw.rstrip('/')}:11434"
    return raw


OLLAMA_HOST = _resolve_ollama_url()
DEFAULT_MODEL_CANDIDATES = ["ystar-gemma", "gemma4:e4b"]


@dataclass
class AgentWorker:
    """One worker per agent. Loads identity from WHO_I_AM file."""
    agent_id: str
    model: str = "ystar-gemma"
    who_i_am_snippet: str = ""
    request_count: int = 0
    last_request_at: float = 0.0

    def load_identity(self, max_chars: int = 2500) -> None:
        """Load WHO_I_AM snippet (trimmed) into system prompt."""
        md = WHO_I_AM_MAP.get(self.agent_id)
        if md and md.exists():
            text = md.read_text(encoding="utf-8", errors="replace")
            self.who_i_am_snippet = text[:max_chars]
        else:
            # Fallback for 7 missing agents: use role name only
            self.who_i_am_snippet = (
                f"You are the {self.agent_id} agent of Y* Bridge Labs. "
                f"Your detailed WHO_I_AM file is pending; for now, apply "
                f"M Triangle (M-1 Survivability / M-2a 防做错 / M-2b 防漏做 / "
                f"M-3 Value Production) and WORK_METHODOLOGY 14 principles."
            )

    def build_full_prompt(self, user_prompt: str) -> str:
        """Prepend identity to user prompt (Gemma doesn't have native system-role)."""
        return (
            f"=== AGENT IDENTITY ({self.agent_id}) ===\n"
            f"{self.who_i_am_snippet}\n\n"
            f"=== USER REQUEST ===\n"
            f"{user_prompt}\n"
        )

    def call_ollama(self, user_prompt: str, *,
                    stream: bool = False,
                    timeout: float = 90.0) -> dict:
        """Synchronous HTTP POST to Ollama /api/generate. Returns raw dict."""
        if not self.who_i_am_snippet:
            self.load_identity()
        full = self.build_full_prompt(user_prompt)
        payload = json.dumps({
            "model": self.model,
            "prompt": full,
            "stream": stream,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Ollama HTTP error: {e}") from e
        dur = time.time() - start
        self.request_count += 1
        self.last_request_at = time.time()
        data = json.loads(body)
        data["_y_elapsed_sec"] = dur
        data["_y_agent_id"] = self.agent_id
        return data


def pick_tier(task_type: str = None) -> str:
    """Pick Gemma model by task tier. env YSTAR_TIER_DEFAULT overrides."""
    BG_SCAN_TASKS = {"bounty_scan", "daily_report", "health_check",
                     "k9_patrol", "memory_compress", "document_analysis",
                     "dialogue_compression"}
    DECISION_TASKS = {"ceo_reply", "cto_ruling", "engineer_impl",
                      "amendment_proposal", "reflection_generation"}
    override = os.environ.get("YSTAR_TIER_DEFAULT", "").lower()
    if override == "bg_scan":
        return "gemma4:e4b"
    if override == "decision":
        return "ystar-gemma"
    if task_type in BG_SCAN_TASKS:
        return "gemma4:e4b"
    if task_type in DECISION_TASKS:
        return "ystar-gemma"
    return "ystar-gemma"  # default decision


class AidenClusterMaster:
    """Coordinator: registers workers, dispatches prompts to target agent."""

    def __init__(self, model: str = None):
        self.workers: dict[str, AgentWorker] = {}
        self.model = model or _pick_first_available_model()

    def register(self, agent_id: str) -> AgentWorker:
        w = AgentWorker(agent_id=agent_id, model=self.model)
        w.load_identity()
        self.workers[agent_id] = w
        return w

    def register_all_known(self) -> list[str]:
        """Register all 10 known agents (aiden + ethan + 8 minted in M8b)."""
        agents = ["ceo", "ethan", "samantha",
                  "leo", "maya", "ryan", "jordan",
                  "sofia", "zara", "marco"]
        for a in agents:
            self.register(a)
        return agents

    def dispatch(self, agent_id: str, user_prompt: str, **kwargs) -> dict:
        """Sync-dispatch a prompt to target agent worker, return Ollama response."""
        if agent_id not in self.workers:
            self.register(agent_id)
        w = self.workers[agent_id]
        return w.call_ollama(user_prompt, **kwargs)

    def stats(self) -> dict:
        return {
            "workers": len(self.workers),
            "model": self.model,
            "agent_ids": sorted(self.workers.keys()),
            "total_requests": sum(w.request_count for w in self.workers.values()),
        }


def _ollama_list_models() -> list[str]:
    """Query Ollama for available models."""
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


def _pick_first_available_model() -> str:
    """Prefer ystar-gemma; fallback to gemma4:e4b; else first Gemma seen."""
    available = _ollama_list_models()
    # Strip trailing :latest for normalized compare
    normalized = {m.split(":")[0]: m for m in available}
    for candidate in DEFAULT_MODEL_CANDIDATES:
        key = candidate.split(":")[0]
        if key in normalized:
            return normalized[key]
    for m in available:
        if "gemma" in m.lower():
            return m
    # Final fallback (will error on call if truly nothing)
    return DEFAULT_MODEL_CANDIDATES[0]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="ceo", help="which agent to dispatch to")
    ap.add_argument("--prompt", default="Confirm you're running locally in one sentence.")
    ap.add_argument("--stats", action="store_true",
                    help="print cluster stats only, no dispatch")
    args = ap.parse_args()

    master = AidenClusterMaster()
    master.register_all_known()

    if args.stats:
        print(json.dumps(master.stats(), indent=2))
        return 0

    print(f"[cluster] dispatching to {args.agent} via {master.model}")
    result = master.dispatch(args.agent, args.prompt)
    print(f"[cluster] response ({result.get('_y_elapsed_sec', 0):.1f}s):")
    print(result.get("response", "(empty)"))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
