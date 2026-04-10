#!/usr/bin/env python3.11
"""
record_intent.py — GOV-006 Intent Verification Protocol (option C).

Writes one ``INTENT_RECORDED`` event to the CIEU library. The event is
the agent's own pre-execution commitment to an interpretation of a
Level 2 or Level 3 directive: *what do I think the current state is,
what do I think the goal is, and what do I plan to do about it.*

Design notes
------------
- Append-only. No blocking. No hook modification. Board confirmation
  happens in chat; the agent later marks the intent ``CONFIRMED``
  (or ``ADJUSTED`` / ``REJECTED``) via ``check_intents.py``.
- Independent of ``register_obligation.py``. This script never fires
  OmissionEngine rules — it only writes a pre-execution audit row.
- ``evidence_grade`` is ``"intent"`` so that future scans can cleanly
  separate pre-execution commitments from ``ops`` rows.
- CIEU row layout mirrors ``register_obligation.make_cieu_record`` so
  downstream tooling (``gov_doctor``, Secretary audit) can reuse the
  same parser.

Usage::

  python3.11 scripts/record_intent.py \\
      --directive-id GOV-006 \\
      --level 3 \\
      --actor cto \\
      --xt "current state I understand as ..." \\
      --y-star "goal I understand as ..." \\
      --plan "step 1" --plan "step 2" --plan "step 3" \\
      --notes "optional freeform"

Returns the generated ``intent_id`` on stdout so the agent can display
it in the chat reply and the Board can refer to it when confirming.
"""
import argparse
import json
import sys
import time
import uuid

from ystar.governance.cieu_store import CIEUStore

SESSION_PATH = ".ystar_session.json"
ROLES = {"board", "ceo", "cto", "cmo", "cso", "cfo", "secretary"}


def load_session_defaults(session_path: str = SESSION_PATH) -> dict:
    """Load ``cieu_db`` from ``.ystar_session.json`` so the default matches
    whatever layer-1 hook and gov-mcp are reading from.
    """
    try:
        with open(session_path, "r") as f:
            data = json.load(f)
        return {"cieu_db": data.get("cieu_db") or ".ystar_cieu.db"}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"cieu_db": ".ystar_cieu.db"}


def build_argparser(defaults: dict) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Record an INTENT_RECORDED CIEU event per GOV-006 protocol. "
            "Agents must call this before executing any Level 2 or Level 3 "
            "directive."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--db", default=defaults["cieu_db"],
                   help="CIEU database path (default: from .ystar_session.json)")
    p.add_argument("--directive-id", required=True,
                   help="Directive ID the intent is for, e.g. GOV-006")
    p.add_argument("--level", type=int, required=True, choices=[1, 2, 3],
                   help="Decision authority level (1 self / 2 CEO / 3 Board). "
                        "Level 1 still allowed but should be rare.")
    p.add_argument("--actor", required=True,
                   help="Actor recording the intent, e.g. cto. Must be a "
                        "known role: " + ", ".join(sorted(ROLES)))
    p.add_argument("--xt", required=True,
                   help="Agent's understanding of the current state (one line "
                        "or short paragraph)")
    p.add_argument("--y-star", required=True,
                   help="Agent's understanding of the target end state")
    p.add_argument("--plan", action="append", default=[],
                   help="Execution plan step. Repeat for multiple steps: "
                        "--plan 'step 1' --plan 'step 2'")
    p.add_argument("--notes", default="",
                   help="Optional freeform notes (constraints, assumptions, "
                        "known unknowns)")
    p.add_argument("--source-ref", default="",
                   help="Optional back-reference to a proposal file "
                        "(e.g. reports/cto/intent_verification_proposal.md)")
    return p


def make_intent_record(args: argparse.Namespace, intent_id: str) -> dict:
    """Construct the CIEU row. Mirrors ``register_obligation.make_cieu_record``
    for schema consistency — downstream readers can share one parser."""
    now = time.time()
    return {
        "event_id": str(uuid.uuid4()),
        "session_id": args.directive_id,
        "agent_id": args.actor,
        "event_type": "INTENT_RECORDED",
        "decision": "info",
        "evidence_grade": "intent",
        "created_at": now,
        "seq_global": time.time_ns() // 1000,
        "params": {
            "intent_id": intent_id,
            "directive_id": args.directive_id,
            "level": args.level,
            "actor_id": args.actor,
            "xt": args.xt,
            "y_star": args.y_star,
            "plan": list(args.plan),
            "notes": args.notes,
            "source_ref": args.source_ref,
            "status": "RECORDED",
            "recorded_at": now,
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": args.actor,
    }


def main() -> int:
    defaults = load_session_defaults()
    args = build_argparser(defaults).parse_args()

    if args.actor not in ROLES:
        print(
            f"ERROR: --actor must be one of {sorted(ROLES)}, got {args.actor!r}",
            file=sys.stderr,
        )
        return 2
    if not args.plan:
        print("ERROR: --plan is required at least once", file=sys.stderr)
        return 2

    intent_id = f"intent_{uuid.uuid4().hex[:12]}"
    record = make_intent_record(args, intent_id)

    cieu = CIEUStore(db_path=args.db)
    ok = cieu.write_dict(record)
    if not ok:
        print("ERROR: CIEU write failed (duplicate event_id?)", file=sys.stderr)
        return 1

    print(f"OK: intent recorded")
    print(f"    intent_id : {intent_id}")
    print(f"    directive : {args.directive_id}")
    print(f"    level     : {args.level}")
    print(f"    actor     : {args.actor}")
    print(f"    plan_steps: {len(args.plan)}")
    print(f"    db        : {args.db}")
    print()
    print("Next step: paste the INTENT block in the chat reply and WAIT for ")
    print("Board (Level 3) or CEO (Level 2) confirmation before any tool call.")
    print(f"After confirmation, mark status with:")
    print(f"  python3.11 scripts/check_intents.py --confirm {intent_id} "
          f"--by board --decision approve --notes '<why>'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
