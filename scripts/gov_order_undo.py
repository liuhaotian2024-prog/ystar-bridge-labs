#!/usr/bin/env python3.11
"""
gov_order_undo.py — Rollback for ``gov_order.py`` (GOV-008 Q4).

CIEU is append-only. "Undo" therefore means: write a new
``OBLIGATION_CANCELLED`` row that voids a previously registered
obligation, and an ``INTENT_REJECTED`` row that voids the
``INTENT_RECORDED`` row that produced it. ``check_obligations.py``
treats CANCELLED rows as terminal (not OVERDUE) so the dashboard
clears immediately.

Usage::

  # Look up by intent_id (the typical entry point — Board reads
  # the gov-order output and copies the intent_id):
  python3.11 scripts/gov_order_undo.py --intent-id intent_a3b1c2d4e5f6

  # Look up by obligation_id (if Board only has the OBLIGATION_REGISTERED id):
  python3.11 scripts/gov_order_undo.py --obligation-id <uuid>

  # Always include a reason; the audit trail is the whole point:
  python3.11 scripts/gov_order_undo.py --intent-id intent_... \\
      --reason "LLM mistranslated due_secs as 8h, actual intent was 8d"

The script refuses to undo:
  - Intents not produced by gov_order (params.source != 'gov_order')
  - Obligations that are already FULFILLED
  - Obligations that are already CANCELLED
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
import warnings
from typing import Optional

warnings.filterwarnings("ignore", message=".*NullCIEUStore.*")

from ystar.governance.cieu_store import CIEUStore  # noqa: E402

SESSION_PATH = ".ystar_session.json"
QUERY_LIMIT = 1000
SOURCE_TAG = "gov_order"


def load_db_default(path: str = SESSION_PATH) -> str:
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("cieu_db") or ".ystar_cieu.db"
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return ".ystar_cieu.db"


def parse_payload(record) -> dict:
    try:
        return json.loads(record.params_json or "{}")
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {}


def find_intent(cieu: CIEUStore, intent_id: str) -> Optional[tuple]:
    rows = cieu.query(event_type="INTENT_RECORDED", limit=QUERY_LIMIT)
    for r in rows:
        payload = parse_payload(r)
        if payload.get("intent_id") == intent_id:
            return (r, payload)
    return None


def find_link_for_intent(cieu: CIEUStore, intent_id: str) -> Optional[dict]:
    rows = cieu.query(event_type="INTENT_LINKED", limit=QUERY_LIMIT)
    for r in rows:
        payload = parse_payload(r)
        if payload.get("intent_id") == intent_id:
            return payload
    return None


def find_obligation_registered(cieu: CIEUStore, obligation_id: str
                               ) -> Optional[tuple]:
    rows = cieu.query(event_type="OBLIGATION_REGISTERED", limit=QUERY_LIMIT)
    for r in rows:
        payload = parse_payload(r)
        if payload.get("obligation_id") == obligation_id:
            return (r, payload)
    return None


def is_already_terminal(cieu: CIEUStore, obligation_id: str) -> Optional[str]:
    """Return 'FULFILLED' or 'CANCELLED' if a terminal row already exists,
    otherwise None."""
    for ev_type, label in (
        ("OBLIGATION_FULFILLED", "FULFILLED"),
        ("OBLIGATION_CANCELLED", "CANCELLED"),
    ):
        rows = cieu.query(event_type=ev_type, limit=QUERY_LIMIT)
        for r in rows:
            payload = parse_payload(r)
            if payload.get("obligation_id") == obligation_id:
                return label
    return None


def find_intent_id_for_obligation(cieu: CIEUStore, obligation_id: str
                                  ) -> Optional[str]:
    rows = cieu.query(event_type="INTENT_LINKED", limit=QUERY_LIMIT)
    for r in rows:
        payload = parse_payload(r)
        if payload.get("obligation_id") == obligation_id:
            return payload.get("intent_id")
    return None


def write_obligation_cancelled(cieu: CIEUStore, *, oblig_record,
                               oblig_payload: dict, reason: str,
                               by_actor: str = "board") -> str:
    now = time.time()
    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": oblig_record.session_id,
        "agent_id": by_actor,
        "event_type": "OBLIGATION_CANCELLED",
        "decision": "info",
        "evidence_grade": "ops",
        "created_at": now,
        "seq_global": time.time_ns() // 1000,
        "params": {
            "obligation_id": oblig_payload.get("obligation_id"),
            "rule_id": oblig_payload.get("rule_id"),
            "directive_ref": oblig_payload.get("directive_ref"),
            "actor_id": oblig_payload.get("actor_id"),
            "cancelled_by": by_actor,
            "cancelled_at": now,
            "reason": reason,
            "registered_at": oblig_payload.get("registered_at"),
            "source": SOURCE_TAG,
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": by_actor,
    }
    if not cieu.write_dict(record):
        raise RuntimeError("OBLIGATION_CANCELLED write failed")
    return record["event_id"]


def write_intent_rejected(cieu: CIEUStore, *, intent_id: str,
                          intent_record, intent_payload: dict,
                          reason: str, by_actor: str = "board") -> str:
    now = time.time()
    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": intent_record.session_id,
        "agent_id": by_actor,
        "event_type": "INTENT_REJECTED",
        "decision": "info",
        "evidence_grade": "intent",
        "created_at": now,
        "seq_global": time.time_ns() // 1000,
        "params": {
            "intent_id": intent_id,
            "directive_id": intent_payload.get("directive_id")
                            or intent_record.session_id,
            "level": intent_payload.get("level"),
            "actor_id": intent_payload.get("actor_id") or "board",
            "reviewer": by_actor,
            "decision": "reject",
            "status": "REJECTED",
            "notes": f"undone by gov_order_undo.py: {reason}",
            "reviewed_at": now,
            "source": SOURCE_TAG,
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": by_actor,
    }
    if not cieu.write_dict(record):
        raise RuntimeError("INTENT_REJECTED write failed")
    return record["event_id"]


def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "Rollback a gov_order.py registration by writing "
            "OBLIGATION_CANCELLED + INTENT_REJECTED rows."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--db", default=load_db_default(),
                   help="CIEU database path (default: from .ystar_session.json)")
    p.add_argument("--intent-id", default=None,
                   help="The intent_id printed by gov_order.py")
    p.add_argument("--obligation-id", default=None,
                   help="The obligation_id (UUID). Resolves intent_id via "
                        "INTENT_LINKED rows.")
    p.add_argument("--reason", default="",
                   help="Why we are undoing this. Required.")
    p.add_argument("--by", default="board",
                   help="Reviewer recording the undo (default: board)")
    p.add_argument("--force", action="store_true",
                   help="Override the source!=gov_order safety check")
    args = p.parse_args()

    if not args.intent_id and not args.obligation_id:
        print("ERROR: must give --intent-id or --obligation-id", file=sys.stderr)
        return 2
    if not args.reason.strip():
        print("ERROR: --reason is required", file=sys.stderr)
        return 2

    cieu = CIEUStore(db_path=args.db)

    intent_id = args.intent_id
    obligation_id = args.obligation_id

    # Resolve missing side via INTENT_LINKED
    if obligation_id and not intent_id:
        intent_id = find_intent_id_for_obligation(cieu, obligation_id)
        if not intent_id:
            print(
                f"ERROR: no INTENT_LINKED row references obligation_id "
                f"{obligation_id}",
                file=sys.stderr,
            )
            return 1
    if intent_id and not obligation_id:
        link = find_link_for_intent(cieu, intent_id)
        if not link:
            print(
                f"ERROR: no INTENT_LINKED row references intent_id {intent_id} "
                f"— did gov_order actually finish?",
                file=sys.stderr,
            )
            return 1
        obligation_id = link.get("obligation_id")

    intent_target = find_intent(cieu, intent_id) if intent_id else None
    if intent_target is None:
        print(f"ERROR: intent_id {intent_id} not found", file=sys.stderr)
        return 1
    intent_record, intent_payload = intent_target

    if intent_payload.get("source") != SOURCE_TAG and not args.force:
        print(
            f"ERROR: intent {intent_id} was not created by gov_order "
            f"(source={intent_payload.get('source')!r}). Pass --force to "
            f"override.",
            file=sys.stderr,
        )
        return 1

    oblig_target = find_obligation_registered(cieu, obligation_id)
    if oblig_target is None:
        print(
            f"ERROR: obligation_id {obligation_id} not found in "
            f"OBLIGATION_REGISTERED rows",
            file=sys.stderr,
        )
        return 1
    oblig_record, oblig_payload = oblig_target

    terminal = is_already_terminal(cieu, obligation_id)
    if terminal:
        print(
            f"ERROR: obligation {obligation_id} is already {terminal}; "
            f"refusing to undo",
            file=sys.stderr,
        )
        return 1

    cancel_event_id = write_obligation_cancelled(
        cieu, oblig_record=oblig_record, oblig_payload=oblig_payload,
        reason=args.reason, by_actor=args.by,
    )
    reject_event_id = write_intent_rejected(
        cieu, intent_id=intent_id, intent_record=intent_record,
        intent_payload=intent_payload, reason=args.reason, by_actor=args.by,
    )

    print("OK: gov_order undo recorded")
    print(f"    intent_id            : {intent_id}")
    print(f"    obligation_id        : {obligation_id}")
    print(f"    OBLIGATION_CANCELLED : {cancel_event_id}")
    print(f"    INTENT_REJECTED      : {reject_event_id}")
    print(f"    reason               : {args.reason}")
    print(f"    by                   : {args.by}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
