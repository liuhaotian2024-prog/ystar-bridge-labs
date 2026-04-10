#!/usr/bin/env python3.11
"""
local_learn.py — local-Gemma learning assistant for the capability system.

Three CLI modes that call a local Gemma model (via the Ollama HTTP API)
to help agents break out of their own cognitive closed loops:

  --mode questions   generate an uncertainty-point list for a task
                     (used in theory-calibration step 1 / step 3, and
                     in idle learning priority 2)
  --mode tasks       generate a fictional role task scenario
                     (used in idle learning priority 3 counterfactual
                     simulation)
  --mode eval        generate a first-draft self-evaluation against a
                     provided success_bar (used in layer 11 fulfillment
                     prep — the agent MUST revise and confirm before
                     using it as a real self-eval)

Design principles (all three non-negotiable):

  1. Gemma is a Socratic questioner, not a decision authority. It is
     NEVER called from the hook path or from any governance decision
     code. It is only called from this CLI and only by agents doing
     their own learning work.

  2. Fail-open end-to-end. No reachable endpoint → print a clear
     message, exit 0, no exception propagates. Governance must not
     depend on Gemma being up.

  3. Every invocation writes one JSONL line to
     knowledge/{canonical_actor}/gaps/gemma_sessions.log. Secretary's
     weekly Monday audit reads this log as separate evidence from the
     48-hour freshness check (per Board GOV-CAPABILITY Q2 answer).

Endpoints are read from .ystar_session.json's "gemma_endpoints" list,
probed in order. First to respond to /api/tags wins. Model is read
from "gemma_default_model" (default "gemma3:4b").

Usage::

  python3.11 scripts/local_learn.py --mode questions --actor cto \\
      --task "design a new CIEU event type for silent-overdue directives"

  python3.11 scripts/local_learn.py --mode tasks --actor cmo

  python3.11 scripts/local_learn.py --mode eval --actor secretary \\
      --task "distill GOV-009 into 第七条 7.5" \\
      --success-bar "CLI template updated with four new fields" \\
      --result "commit 256ccf1 pushed with 7 file updates"
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_PATH = REPO_ROOT / ".ystar_session.json"
ROLES = {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}
LEGACY_ACTOR_ALIASES = {
    "ethan_wright": "cto",
    "aiden_liu": "ceo",
    "sofia_blake": "cmo",
    "zara_johnson": "cso",
    "marco_rivera": "cfo",
    "samantha_lin": "secretary",
}

DEFAULT_ENDPOINTS = [
    "http://localhost:11434",
    "http://192.168.1.225:11434",
    "http://192.168.1.228:11434",
]
DEFAULT_MODEL = "ystar-gemma"
PROBE_TIMEOUT = 2.0
GENERATE_TIMEOUT = 60.0


# ────────────────────────── config + actor helpers ──────────────────────────

def canonical_actor(actor: str) -> str:
    return LEGACY_ACTOR_ALIASES.get(actor, actor)


def load_config() -> dict:
    """Read gemma endpoints and model from .ystar_session.json, with
    sensible fallbacks so the script still runs if the session file is
    unreadable (fail-open even on config)."""
    try:
        with open(SESSION_PATH, "r") as f:
            data = json.load(f)
        endpoints = data.get("gemma_endpoints") or DEFAULT_ENDPOINTS
        model = data.get("gemma_default_model") or DEFAULT_MODEL
    except (OSError, json.JSONDecodeError):
        endpoints = DEFAULT_ENDPOINTS
        model = DEFAULT_MODEL
    # Normalize endpoints: strip trailing slash, ensure scheme.
    normed = []
    for ep in endpoints:
        ep = ep.strip().rstrip("/")
        if ep and not ep.startswith("http"):
            ep = f"http://{ep}"
        if ep:
            normed.append(ep)
    return {"endpoints": normed, "model": model}


# ───────────────────────── endpoint probe + call ────────────────────────────

def probe_endpoint(url: str, timeout: float = PROBE_TIMEOUT) -> bool:
    """True if GET {url}/api/tags returns a valid JSON body. Never raises."""
    try:
        req = urllib.request.Request(f"{url}/api/tags")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8")
        json.loads(body)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError,
            json.JSONDecodeError, TimeoutError, OSError):
        return False


def find_endpoint(endpoints: list[str]) -> str | None:
    for ep in endpoints:
        if probe_endpoint(ep):
            return ep
    return None


def generate(endpoint: str, model: str, prompt: str,
             timeout: float = GENERATE_TIMEOUT) -> str:
    """Call Ollama /api/generate with stream=false. Raises on error so
    the caller can log and fail open at its own layer."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{endpoint}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.loads(r.read().decode("utf-8"))
    return body.get("response", "")


# ──────────────────────────── prompt templates ──────────────────────────────

PROMPT_QUESTIONS = """\
You are a Socratic tutor helping a role-specific AI agent surface what
it does NOT know before starting a task. The agent has described the
task below. Your job is NOT to solve the task. Your job is to produce
a numbered list of 5 to 8 specific uncertainty points — concrete,
answerable questions the agent should resolve before acting.

Good uncertainty points:
- Factual questions whose answer would materially change the plan
- Assumptions the agent is likely making without noticing
- Definitional ambiguities in the task statement
- Dependencies on facts the agent would need to verify externally
- Edge cases that would break a naive approach

Bad uncertainty points:
- Generic "what if things change" hand-waving
- Questions that are really suggestions ("have you considered X")
- Questions the task statement already answers

Format: plain numbered list, one question per line, no extra text.

Role: __ROLE__
Task: __TASK__

Numbered uncertainty list:
"""

PROMPT_TASKS = """\
You are a scenario generator producing fictional but realistic task
scenarios for a __ROLE__ to practice against. The scenario should be
specific enough that a reasonable agent could walk through a decision
framework on it, but not so detailed that it dictates the answer.

Output format (strict, no extra text):

SCENARIO TITLE: <short phrase>

BACKGROUND (3-5 sentences):
<context setting the situation>

CONSTRAINTS:
- <constraint 1>
- <constraint 2>
- <constraint 3>

SUCCESS CRITERIA:
- <measurable criterion 1>
- <measurable criterion 2>

OPEN QUESTIONS FOR THE AGENT:
- <question 1>
- <question 2>

Generate exactly one such scenario. Make the role-specific flavor
obvious. The scenario must be solvable but not trivial.
"""

PROMPT_EVAL = """\
You are producing a first-draft self-evaluation for an AI agent that
just executed a task. Your job is NOT to pass judgment on the agent's
work — the agent itself will revise this draft before submitting it.
Your job is to produce a structured first cut so the agent has
something concrete to react to.

Format (strict):

AGAINST SUCCESS CRITERION:
1. <criterion text from success_bar>
   - Judgment: 达到 / 未达到 / 部分达到
   - Reason: <one sentence>
2. ...continue for each criterion...

IDENTIFIED GAPS:
- <gap 1: what did the agent overlook?>
- <gap 2: ...>

LESSONS WORTH RECORDING:
- <lesson 1>
- <lesson 2>

TASK: __TASK__

STATED SUCCESS BAR: __SUCCESS_BAR__

EXECUTION RESULT SUMMARY: __RESULT__

First-draft self-evaluation:
"""


def _rag_context(query: str, top_k: int = 3) -> str:
    """Retrieve relevant context from RAG index. Fail-open: returns empty
    string if index missing or query fails."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_rag_index import query_index
        results = query_index(query, top_k=top_k)
        if not results:
            return ""
        lines = ["\n[Relevant context from knowledge base:]"]
        for r in results:
            source = r.get("source", "?")
            text = r.get("text", "")[:400]
            lines.append(f"--- {source} ---\n{text}")
        return "\n".join(lines) + "\n"
    except Exception:
        return ""


def build_prompt(mode: str, *, role: str = "", task: str = "",
                 success_bar: str = "", result: str = "") -> str:
    # RAG: inject relevant context for question and eval modes
    rag = ""
    if mode in ("questions", "eval") and task:
        rag = _rag_context(task)

    if mode == "questions":
        return (rag + PROMPT_QUESTIONS
                .replace("__ROLE__", role or "general agent")
                .replace("__TASK__", task or "(no task given)"))
    if mode == "tasks":
        return PROMPT_TASKS.replace("__ROLE__", role or "general agent")
    if mode == "eval":
        return (rag + PROMPT_EVAL
                .replace("__TASK__", task or "(no task given)")
                .replace("__SUCCESS_BAR__", success_bar or "(no success bar given)")
                .replace("__RESULT__", result or "(no result given)"))
    raise ValueError(f"unknown mode: {mode}")


# ──────────────────────────── JSONL session log ─────────────────────────────

def write_session_log(*, canonical: str, mode: str, actor: str,
                      endpoint: str | None, model: str,
                      input_summary: str, output_text: str,
                      question_count: int | None) -> Path | None:
    """Append one JSONL line to knowledge/{canonical}/gaps/gemma_sessions.log.
    Fails silently (returns None) if the directory is missing — but it
    should always exist because the Ethan infrastructure commit creates
    all 6 gaps/ directories.
    """
    log_dir = REPO_ROOT / "knowledge" / canonical / "gaps"
    if not log_dir.is_dir():
        return None
    log_path = log_dir / "gemma_sessions.log"
    entry = {
        "timestamp": _dt.datetime.now().isoformat(),
        "mode": mode,
        "actor": actor,
        "endpoint": endpoint,
        "model": model,
        "input_summary": input_summary[:200],
        "question_count": question_count,
        "output_hash": hashlib.sha256(
            (output_text or "").encode("utf-8")
        ).hexdigest()[:16],
        "output_length": len(output_text or ""),
    }
    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        return None
    return log_path


# ────────────────────────── main CLI entrypoint ─────────────────────────────

def count_questions(text: str) -> int:
    """Rough count of numbered-list items in a 'questions' output."""
    import re
    matches = re.findall(r"^\s*\d+[.)、]\s*\S", text, re.MULTILINE)
    return len(matches)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Socratic Gemma assistant for capability-system learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--mode", required=True,
                   choices=["questions", "tasks", "eval"],
                   help="questions: uncertainty list; tasks: simulated "
                        "scenario; eval: self-eval first draft")
    p.add_argument("--actor", required=True,
                   help="Role asking for help. Must be in ROLES whitelist: "
                        + ", ".join(sorted(ROLES)))
    p.add_argument("--task", default="",
                   help="Task description (required for --mode questions "
                        "and --mode eval)")
    p.add_argument("--success-bar", default="",
                   help="Success criterion text (required for --mode eval)")
    p.add_argument("--result", default="",
                   help="Execution result summary (required for --mode eval)")
    p.add_argument("--model", default=None,
                   help="Override the default model (from .ystar_session.json)")
    args = p.parse_args()

    canonical = canonical_actor(args.actor)
    if canonical not in ROLES:
        print(
            f"ERROR: --actor must resolve to one of {sorted(ROLES)}, "
            f"got {args.actor!r} → {canonical!r}",
            file=sys.stderr,
        )
        return 2

    # Validate mode-specific args
    if args.mode in ("questions", "eval") and not args.task.strip():
        print(f"ERROR: --task is required for --mode {args.mode}",
              file=sys.stderr)
        return 2
    if args.mode == "eval":
        if not args.success_bar.strip() or not args.result.strip():
            print("ERROR: --mode eval requires --success-bar and --result",
                  file=sys.stderr)
            return 2

    cfg = load_config()
    model = args.model or cfg["model"]
    endpoints = cfg["endpoints"]

    # ── endpoint probe ──────────────────────────────────────────────
    endpoint = find_endpoint(endpoints)
    if endpoint is None:
        print("[local-learn] No reachable Gemma endpoint found.")
        print(f"[local-learn] Probed in order: {endpoints}")
        print("[local-learn] This is fail-open — exit 0, no exception.")
        print("[local-learn] Check that Ollama is running "
              "(ollama serve) and a gemma model is pulled.")
        # Still write a log line so Secretary can see the attempt
        write_session_log(
            canonical=canonical, mode=args.mode, actor=args.actor,
            endpoint=None, model=model,
            input_summary=(args.task or "(tasks mode, no --task)")[:200],
            output_text="",
            question_count=None,
        )
        return 0
    print(f"[local-learn] Using {endpoint}  model={model}  "
          f"mode={args.mode}  actor={canonical}", file=sys.stderr)

    # ── build prompt ────────────────────────────────────────────────
    prompt = build_prompt(
        args.mode,
        role=canonical,
        task=args.task,
        success_bar=args.success_bar,
        result=args.result,
    )

    # ── generate ────────────────────────────────────────────────────
    t0 = time.time()
    try:
        output = generate(endpoint, model, prompt)
    except Exception as exc:  # noqa: BLE001 — fail-open
        print(f"[local-learn] Gemma call failed: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        print("[local-learn] fail-open — exit 0")
        write_session_log(
            canonical=canonical, mode=args.mode, actor=args.actor,
            endpoint=endpoint, model=model,
            input_summary=(args.task or "(tasks mode, no --task)")[:200],
            output_text="",
            question_count=None,
        )
        return 0
    dt = time.time() - t0
    print(f"[local-learn] generated in {dt:.1f}s", file=sys.stderr)

    # ── emit to stdout + log ────────────────────────────────────────
    print(output)

    q_count = count_questions(output) if args.mode == "questions" else None
    log_path = write_session_log(
        canonical=canonical, mode=args.mode, actor=args.actor,
        endpoint=endpoint, model=model,
        input_summary=(args.task or "(tasks mode, no --task)")[:200],
        output_text=output,
        question_count=q_count,
    )
    if log_path:
        print(f"[local-learn] logged to {log_path.relative_to(REPO_ROOT)}",
              file=sys.stderr)
    else:
        print("[local-learn] WARN: could not write gemma_sessions.log "
              f"(knowledge/{canonical}/gaps/ missing?)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
