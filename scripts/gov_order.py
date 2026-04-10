#!/usr/bin/env python3.11
"""
gov_order.py — Board NL → CIEU obligation auto-pipeline (GOV-008).

Translates a natural-language Board directive into a structured obligation
record and writes it to the CIEU library, with full audit trail:

    Board NL sentence
        ↓
    [1] Detect LLM provider (Anthropic / OpenAI / Ollama / LM Studio / none)
        ↓
    [2] Translate via LLM (or graceful manual fallback if no provider)
        ↓
    [3] Deterministic validator (hard schema gate)
        ↓
    [4] INTENT_RECORDED CIEU event (source='gov_order')
        ↓
    [5] register_obligation_programmatic() → OBLIGATION_REGISTERED event
        ↓
    [6] Print summary including both event_ids and obligation_id

Failures at any LLM-side step (no provider, JSON parse, schema validation,
non-task input) write a JSON file to ``reports/board_proposed_changes/pending/``
and exit cleanly with a manual fallback hint. The pipeline never raises an
exception to the Board.

Usage::

  python3.11 scripts/gov_order.py "ethan 明早 9 点前把 GOV-008 实施完"
  python3.11 scripts/gov_order.py --dry-run "..."
  python3.11 scripts/gov_order.py --no-llm "..."   # force manual fallback path

Environment variables checked (in order, first match wins):

  ANTHROPIC_API_KEY  → uses anthropic SDK if importable
  OPENAI_API_KEY     → uses openai SDK if importable
  OLLAMA_HOST        → uses local Ollama HTTP API
  LM_STUDIO_HOST     → uses local LM Studio HTTP API

Refs:
  - reports/cto/gov_order_pipeline.md (Step 1 design, GOV-008)
  - scripts/record_intent.py (GOV-006 INTENT_RECORDED schema)
  - scripts/register_obligation.py (programmatic entry point)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import sys
import time
import uuid
import warnings
from pathlib import Path
from typing import Any, Callable, Optional

# Suppress the InMemoryOmissionStore NullCIEUStore warning, same as
# register_obligation.py — persistence happens via CIEUStore.write_dict.
warnings.filterwarnings("ignore", message=".*NullCIEUStore.*")

# Make the sibling register_obligation module importable when run via CLI.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from ystar.governance.cieu_store import CIEUStore  # noqa: E402

SESSION_PATH = ".ystar_session.json"
PENDING_DIR = Path("reports/board_proposed_changes/pending")
SOURCE_TAG = "gov_order"

KNOWN_OWNERS = {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}
KNOWN_SEVERITIES = {"low", "medium", "high", "critical"}
KNOWN_EVENTS = {
    "acknowledgement_event",
    "completion_event",
    "result_publication_event",
    "status_update_event",
}
LLM_TIMEOUT_SECS = 30.0


# ───────────────────────── helpers: session config ─────────────────────────

def load_session_defaults(session_path: str = SESSION_PATH) -> dict:
    try:
        with open(session_path, "r") as f:
            data = json.load(f)
        return {
            "cieu_db": data.get("cieu_db") or ".ystar_cieu.db",
            "display_names": data.get("agent_display_names", {}),
        }
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"cieu_db": ".ystar_cieu.db", "display_names": {}}


# ────────────────────────── helpers: LLM provider ──────────────────────────

def _anthropic_call(prompt: str) -> str:
    import anthropic  # type: ignore
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        timeout=LLM_TIMEOUT_SECS,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = []
    for block in resp.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


def _openai_call(prompt: str) -> str:
    import openai  # type: ignore
    client = openai.OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o",
        timeout=LLM_TIMEOUT_SECS,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content or ""


def _ollama_call(host: str, model: str, prompt: str) -> str:
    import urllib.request
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SECS) as r:
        body = json.loads(r.read().decode("utf-8"))
    return body.get("response", "")


def _lm_studio_call(host: str, model: str, prompt: str) -> str:
    import urllib.request
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{host.rstrip('/')}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SECS) as r:
        body = json.loads(r.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def detect_llm_provider() -> Optional[tuple[str, str, Callable[[str], str]]]:
    """Return ``(provider_name, model, call_fn)`` or ``None`` if no provider
    is available. Probe-only: never makes a network call here.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic  # noqa: F401
            return ("anthropic", "claude-sonnet-4-5", _anthropic_call)
        except ImportError:
            pass

    if os.environ.get("OPENAI_API_KEY"):
        try:
            import openai  # noqa: F401
            return ("openai", "gpt-4o", _openai_call)
        except ImportError:
            pass

    ollama_host = os.environ.get("OLLAMA_HOST")
    if ollama_host or shutil.which("ollama"):
        host = ollama_host or "http://localhost:11434"
        model = os.environ.get("OLLAMA_MODEL", "llama3")
        return ("ollama", model, lambda p: _ollama_call(host, model, p))

    lm_studio_host = os.environ.get("LM_STUDIO_HOST")
    if lm_studio_host:
        model = os.environ.get("LM_STUDIO_MODEL", "default")
        return ("lm_studio", model, lambda p: _lm_studio_call(lm_studio_host, model, p))

    return None


# ────────────────────────── helpers: prompt + parse ────────────────────────

PROMPT_TEMPLATE = """\
You are translating a Y*Bridge Labs Board directive into a structured
obligation record. Output exactly one JSON object, nothing else (no prose,
no markdown fences).

Schema:
{{
  "owner": one of [ceo, cto, cmo, cso, cfo, secretary],
  "entity_id": format BOARD-YYYY-MM-DD-NNN, or reuse if Board mentions
               an existing directive ID (GOV-001, AMENDMENT-001, etc.),
  "rule_id": short snake_case identifier, e.g. "gov_008_impl_cto",
  "rule_name": human-readable obligation name,
  "description": one-paragraph description of what the agent must do
                 (>= 10 chars),
  "due_secs": deadline in seconds from now, integer or float
              ("today" = 28800, "tonight" = 14400, "this week" = 604800,
               "tomorrow morning 9am" = approximate seconds-to-tomorrow-9am,
               specific datetime → seconds from now to that datetime),
  "severity": one of [low, medium, high, critical],
  "required_event": one of [acknowledgement_event, completion_event,
                            result_publication_event, status_update_event]
}}

Rules:
1. If the Board's sentence is NOT a task (it's a deny rule, value statement,
   or question), output {{"_input_type": "non_task", "reason": "..."}}.
2. If you cannot determine a field with high confidence, use null. The
   deterministic verifier will reject null fields and route to pending.
3. owner must be a single agent role (not "all"). If Board says "all
   agents", default to "ceo" who will dispatch downstream.
4. Do not invent fields not in the schema.
5. Today is {today}. Use this to compute due_secs for relative phrases.

Input: {board_sentence}

Output JSON:
"""


def build_prompt(board_sentence: str) -> str:
    today = _dt.datetime.now().strftime("%Y-%m-%d %H:%M %Z")
    return PROMPT_TEMPLATE.format(today=today, board_sentence=board_sentence)


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(raw: str) -> dict:
    """Pull a single JSON object out of an LLM string. Raises ``ValueError``
    on failure with a description suitable for logging to pending."""
    if not raw or not raw.strip():
        raise ValueError("LLM output is empty")
    text = raw.strip()
    # Strip common markdown fences if the model added them anyway.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_BLOCK_RE.search(text)
        if not match:
            raise ValueError("no JSON object found in LLM output")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON decode failed: {exc}") from exc


# ────────────────────────── helpers: validator ─────────────────────────────

def validate_obligation_dict(d: dict) -> list[str]:
    """Return a list of validation errors. Empty list = valid.

    Hard schema gate. No LLM, no fuzzy matching. Reads
    ``.ystar_session.json`` for the cross-reference check on owner.
    """
    errors: list[str] = []
    required = {
        "owner", "entity_id", "rule_id", "rule_name",
        "description", "due_secs", "severity", "required_event",
    }
    missing = required - set(d.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")

    if d.get("owner") not in KNOWN_OWNERS:
        errors.append(
            f"owner {d.get('owner')!r} not in {sorted(KNOWN_OWNERS)}"
        )

    if d.get("severity") not in KNOWN_SEVERITIES:
        errors.append(
            f"severity {d.get('severity')!r} not in {sorted(KNOWN_SEVERITIES)}"
        )

    if d.get("required_event") not in KNOWN_EVENTS:
        errors.append(
            f"required_event {d.get('required_event')!r} not in {sorted(KNOWN_EVENTS)}"
        )

    due = d.get("due_secs")
    if not isinstance(due, (int, float)) or isinstance(due, bool) or due <= 0:
        errors.append(f"due_secs {due!r} must be a positive number")

    desc = d.get("description") or ""
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        errors.append("description must be a non-empty string >= 10 chars")

    rule_id = d.get("rule_id") or ""
    if (not isinstance(rule_id, str) or not rule_id
            or " " in rule_id
            or not rule_id.replace("_", "").isalnum()):
        errors.append(f"rule_id {rule_id!r} must be snake_case alphanumeric")

    entity_id = d.get("entity_id") or ""
    if not isinstance(entity_id, str) or not entity_id or len(entity_id) > 80:
        errors.append(f"entity_id {entity_id!r} invalid (1..80 chars)")

    rule_name = d.get("rule_name") or ""
    if not isinstance(rule_name, str) or len(rule_name.strip()) < 3:
        errors.append("rule_name must be a non-empty string >= 3 chars")

    # Cross-check owner against the live .ystar_session.json so a
    # rename of agent_display_names doesn't silently leak through.
    try:
        with open(SESSION_PATH, "r") as f:
            session = json.load(f)
        display_names = session.get("agent_display_names", {})
        if d.get("owner") and d.get("owner") not in display_names:
            errors.append(
                f"owner {d.get('owner')!r} not in .ystar_session.json "
                f"agent_display_names; available={sorted(display_names.keys())}"
            )
    except (OSError, json.JSONDecodeError):
        pass  # session file unreadable; skip the cross-check

    return errors


# ────────────────────────── helpers: pending dir ───────────────────────────

def save_pending(*, nl: str, provider: Optional[str], model: Optional[str],
                 raw_output: Any, parsed: Any,
                 errors: list[str]) -> Path:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    ts = _dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    rule_hint = "unknown"
    if isinstance(parsed, dict):
        rid = parsed.get("rule_id")
        if isinstance(rid, str) and rid:
            safe = re.sub(r"[^a-zA-Z0-9_]", "_", rid)[:30]
            if safe:
                rule_hint = safe
    fname = f"{ts}-rejected-{rule_hint}.json"
    path = PENDING_DIR / fname

    suggested = manual_fallback_message(nl, partial=parsed if isinstance(parsed, dict) else None)
    payload = {
        "version": "1.0",
        "timestamp": _dt.datetime.now().isoformat(),
        "input_nl": nl,
        "llm_provider": provider,
        "llm_model": model,
        "llm_raw_output": raw_output if isinstance(raw_output, str) else None,
        "llm_parsed_dict": parsed if isinstance(parsed, dict) else None,
        "validation_errors": errors,
        "suggested_manual_command": suggested,
        "review_status": "pending",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# ────────────────────────── helpers: manual fallback ──────────────────────

def manual_fallback_message(nl: str, partial: Optional[dict] = None) -> str:
    """Build a copy-paste register_obligation.py command line for the Board."""
    p = partial or {}
    owner = p.get("owner") or "<owner>"
    entity_id = p.get("entity_id") or "BOARD-YYYY-MM-DD-NNN"
    rule_id = p.get("rule_id") or "<rule_id>"
    rule_name = p.get("rule_name") or "<rule name>"
    description = p.get("description") or nl[:80]
    due_secs = p.get("due_secs") or 14400
    severity = p.get("severity") or "high"
    return (
        "python3.11 scripts/register_obligation.py \\\n"
        f"    --entity-id {entity_id} \\\n"
        f"    --owner {owner} \\\n"
        f"    --rule-id {rule_id} \\\n"
        f"    --rule-name {rule_name!r} \\\n"
        f"    --description {description!r} \\\n"
        f"    --due-secs {due_secs} \\\n"
        f"    --severity {severity}"
    )


# ────────────────────────── helpers: CIEU writes ───────────────────────────

def write_intent_record(cieu: CIEUStore, *, nl: str,
                        provider: Optional[str], model: Optional[str],
                        llm_dict: Optional[dict],
                        validation_status: str,
                        validation_errors: list[str],
                        entity_id: Optional[str]) -> str:
    intent_id = f"intent_{uuid.uuid4().hex[:12]}"
    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": entity_id or "BOARD-NL-INPUT",
        "agent_id": "board",
        "event_type": "INTENT_RECORDED",
        "decision": "info",
        "evidence_grade": "intent",
        "created_at": time.time(),
        "seq_global": time.time_ns() // 1000,
        "params": {
            "intent_id": intent_id,
            "source": SOURCE_TAG,
            "input_nl": nl,
            "llm_provider": provider,
            "llm_model": model,
            "llm_output": llm_dict,
            "validation_status": validation_status,
            "validation_errors": list(validation_errors),
            "subsequent_obligation_id": None,  # filled later if successful
            "recorded_at": time.time(),
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": "board",
    }
    ok = cieu.write_dict(record)
    if not ok:
        raise RuntimeError("INTENT_RECORDED CIEU write failed")
    return intent_id


def write_link_record(cieu: CIEUStore, *, intent_id: str,
                      obligation_id: str, entity_id: str) -> None:
    """Write a small ``INTENT_LINKED`` row so check_intents.py can show
    the obligation that came out of an INTENT_RECORDED. We do not mutate
    the original INTENT_RECORDED row (CIEU is append-only)."""
    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": entity_id,
        "agent_id": "board",
        "event_type": "INTENT_LINKED",
        "decision": "info",
        "evidence_grade": "intent",
        "created_at": time.time(),
        "seq_global": time.time_ns() // 1000,
        "params": {
            "intent_id": intent_id,
            "obligation_id": obligation_id,
            "linked_at": time.time(),
            "source": SOURCE_TAG,
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": "board",
    }
    cieu.write_dict(record)


# ─────────────────────────────── main flow ─────────────────────────────────

def _print_proposed(d: dict) -> None:
    print("[gov-order] LLM proposed obligation:")
    for k in ("owner", "entity_id", "rule_id", "rule_name", "due_secs",
              "severity", "required_event"):
        print(f"  {k:<14} : {d.get(k)}")
    desc = (d.get("description") or "").strip()
    if desc:
        snippet = desc if len(desc) <= 200 else desc[:200] + "…"
        print(f"  description    : {snippet}")


def main() -> int:
    defaults = load_session_defaults()
    p = argparse.ArgumentParser(
        description="Translate a Board NL directive into a CIEU obligation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("nl", help="Board's natural-language directive (one sentence)")
    p.add_argument("--db", default=defaults["cieu_db"],
                   help="CIEU database path (default: from .ystar_session.json)")
    p.add_argument("--dry-run", action="store_true",
                   help="Run translation + validation but skip the actual "
                        "OBLIGATION_REGISTERED write")
    p.add_argument("--no-llm", action="store_true",
                   help="Skip LLM detection entirely; force the manual "
                        "fallback path")
    args = p.parse_args()

    print(f"[gov-order] Input: {args.nl!r}")
    cieu = CIEUStore(db_path=args.db)

    # ── 1. LLM provider detection ────────────────────────────────────
    if args.no_llm:
        provider_tuple = None
        print("[gov-order] --no-llm given; skipping provider detection")
    else:
        provider_tuple = detect_llm_provider()

    if provider_tuple is None:
        print("[gov-order] No LLM provider detected.")
        print("[gov-order] Manual fallback — copy/paste this:")
        print()
        print(manual_fallback_message(args.nl))
        print()
        # Still record an INTENT_RECORDED so the audit trail exists.
        intent_id = write_intent_record(
            cieu, nl=args.nl, provider=None, model=None, llm_dict=None,
            validation_status="manual_fallback",
            validation_errors=["no LLM provider available"],
            entity_id=None,
        )
        print(f"[gov-order] INTENT_RECORDED (manual fallback): {intent_id}")
        return 0
    provider_name, model, call_fn = provider_tuple
    print(f"[gov-order] Using {provider_name}/{model}")

    # ── 2. LLM call ──────────────────────────────────────────────────
    prompt = build_prompt(args.nl)
    try:
        raw_output = call_fn(prompt)
    except Exception as exc:  # noqa: BLE001 — we want a graceful fallback
        path = save_pending(
            nl=args.nl, provider=provider_name, model=model,
            raw_output=None, parsed=None,
            errors=[f"LLM call failed: {type(exc).__name__}: {exc}"],
        )
        print(f"[gov-order] LLM call failed: {exc}")
        print(f"[gov-order] Saved to pending: {path}")
        write_intent_record(
            cieu, nl=args.nl, provider=provider_name, model=model,
            llm_dict=None, validation_status="llm_call_failed",
            validation_errors=[f"{type(exc).__name__}: {exc}"],
            entity_id=None,
        )
        return 0

    # ── 3. Parse JSON ────────────────────────────────────────────────
    try:
        llm_dict = extract_json(raw_output)
    except ValueError as exc:
        path = save_pending(
            nl=args.nl, provider=provider_name, model=model,
            raw_output=raw_output, parsed=None,
            errors=[f"JSON parse: {exc}"],
        )
        print(f"[gov-order] LLM output not valid JSON: {exc}")
        print(f"[gov-order] Saved to pending: {path}")
        write_intent_record(
            cieu, nl=args.nl, provider=provider_name, model=model,
            llm_dict=None, validation_status="json_parse_failed",
            validation_errors=[str(exc)], entity_id=None,
        )
        return 0

    # ── 4. Non-task detection ────────────────────────────────────────
    if isinstance(llm_dict, dict) and llm_dict.get("_input_type") == "non_task":
        reason = llm_dict.get("reason", "(no reason given)")
        print(f"[gov-order] Input classified as non-task: {reason}")
        print("[gov-order] Not registering. If this is a contract rule,")
        print("[gov-order] use governance/BOARD_CHARTER_AMENDMENTS.md flow.")
        write_intent_record(
            cieu, nl=args.nl, provider=provider_name, model=model,
            llm_dict=llm_dict, validation_status="non_task",
            validation_errors=[f"non_task: {reason}"], entity_id=None,
        )
        return 0

    # ── 5. Deterministic validation ──────────────────────────────────
    _print_proposed(llm_dict)
    errors = validate_obligation_dict(llm_dict)
    if errors:
        path = save_pending(
            nl=args.nl, provider=provider_name, model=model,
            raw_output=raw_output, parsed=llm_dict, errors=errors,
        )
        print("[gov-order] Deterministic verification: FAIL")
        for e in errors:
            print(f"  - {e}")
        print(f"[gov-order] Saved to pending: {path}")
        print("[gov-order] Manual command:")
        print(manual_fallback_message(args.nl, partial=llm_dict))
        write_intent_record(
            cieu, nl=args.nl, provider=provider_name, model=model,
            llm_dict=llm_dict, validation_status="fail",
            validation_errors=errors, entity_id=llm_dict.get("entity_id"),
        )
        return 0
    print("[gov-order] Deterministic verification: PASS")

    # ── 6. INTENT_RECORDED ───────────────────────────────────────────
    intent_id = write_intent_record(
        cieu, nl=args.nl, provider=provider_name, model=model,
        llm_dict=llm_dict, validation_status="pass",
        validation_errors=[], entity_id=llm_dict["entity_id"],
    )
    print(f"[gov-order] INTENT_RECORDED CIEU event: {intent_id}")

    if args.dry_run:
        print("[gov-order] DRY RUN — skipping OBLIGATION_REGISTERED write")
        return 0

    # ── 7. Programmatic register_obligation call ─────────────────────
    from register_obligation import register_obligation_programmatic  # local import

    try:
        written = register_obligation_programmatic(
            db_path=args.db,
            entity_id=llm_dict["entity_id"],
            owner=llm_dict["owner"],
            rule_id=llm_dict["rule_id"],
            rule_name=llm_dict["rule_name"],
            description=llm_dict["description"],
            due_secs=float(llm_dict["due_secs"]),
            severity=llm_dict["severity"],
            required_event=llm_dict["required_event"],
            initiator="board",
            directive_ref=llm_dict["entity_id"],
            verbose=True,
        )
    except RuntimeError as exc:
        # Validator passed but engine refused — e.g. duplicate.
        print(f"[gov-order] register_obligation failed: {exc}")
        save_pending(
            nl=args.nl, provider=provider_name, model=model,
            raw_output=raw_output, parsed=llm_dict,
            errors=[f"engine_failure: {exc}"],
        )
        return 0

    obligation_id = written[0] if written else None
    if obligation_id:
        write_link_record(
            cieu,
            intent_id=intent_id,
            obligation_id=obligation_id,
            entity_id=llm_dict["entity_id"],
        )
        print(f"[gov-order] OBLIGATION_REGISTERED: {obligation_id}")
        print(f"[gov-order] INTENT_LINKED: {intent_id} → {obligation_id}")
        print(f"[gov-order] Done. Run `python3.11 scripts/check_obligations.py "
              f"--actor {llm_dict['owner']}` to see it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
