#!/usr/bin/env python3.11
"""
reject_directive.py — GOV-008 Gap 3 / 第八条 义务拒绝协议.

Writes one ``DIRECTIVE_REJECTED`` event to the CIEU library. An agent
that receives a Level 2 or Level 3 directive and judges that it
cannot or should not execute MUST call this script within the
agreed SLA (2 hours by default, see ``WORKING_STYLE.md`` 第八条)
instead of staying silent. Silence is not a legal end state —
every directive must close in ``COMPLETED``, ``REJECTED``, or still
be explicitly ``PENDING``.

The script mirrors ``record_intent.py`` so the two look like
siblings: same ROLES whitelist, same schema-version constants, same
session-config-driven CIEU path.

Usage::

  python3.11 scripts/reject_directive.py \\
      --directive-id GOV-010 \\
      --actor cto \\
      --reason "plan assumes a subprocess model that conflicts with Claude Code's turn-based session; see reports/cto/gov010_pushback.md for the counterfactual"

Rules enforced:
  - ``--actor`` must be a known role
  - ``--reason`` must be non-empty after strip
  - ``--directive-id`` must be non-empty
  - ``--reason`` must be at least 20 characters
    (no "don't want to" brushoffs — we need the actual analysis)

Returns the rejection event_id so it can be referenced in follow-ups.
"""
import argparse
import json
import sys
import time
import uuid

from ystar.governance.cieu_store import CIEUStore

SESSION_PATH = ".ystar_session.json"
ROLES = {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}
MIN_REASON_CHARS = 20


def load_session_defaults(session_path: str = SESSION_PATH) -> dict:
    try:
        with open(session_path, "r") as f:
            data = json.load(f)
        return {"cieu_db": data.get("cieu_db") or ".ystar_cieu.db"}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"cieu_db": ".ystar_cieu.db"}


def build_argparser(defaults: dict) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Write a DIRECTIVE_REJECTED CIEU event. Used when an agent "
            "cannot or should not execute a Level 2/3 directive. Silence "
            "is not a legal end state; use this script to close the loop."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--db", default=defaults["cieu_db"],
                   help="CIEU database path (default: from .ystar_session.json)")
    p.add_argument("--directive-id", required=True,
                   help="Directive being rejected, e.g. GOV-010 or BOARD-2026-04-09-007")
    p.add_argument("--actor", required=True,
                   help="Actor doing the rejecting. Must be a known role: "
                        + ", ".join(sorted(ROLES)))
    p.add_argument("--reason", required=True,
                   help="Why the directive is being rejected. Mandatory, "
                        f"must be at least {MIN_REASON_CHARS} chars after strip.")
    p.add_argument("--source-ref", default="",
                   help="Optional back-reference to a counter-proposal, "
                        "pushback report, or chat turn that explains the rejection")
    p.add_argument("--obligation-id", default="",
                   help="Optional linked obligation_id if the rejected directive "
                        "already had one registered by register_obligation.py")
    return p


def make_rejection_record(args: argparse.Namespace, rejection_id: str) -> dict:
    now = time.time()
    return {
        "event_id": str(uuid.uuid4()),
        "session_id": args.directive_id,
        "agent_id": args.actor,
        "event_type": "DIRECTIVE_REJECTED",
        "decision": "info",
        "evidence_grade": "decision",
        "created_at": now,
        "seq_global": time.time_ns() // 1000,
        "params": {
            "rejection_id": rejection_id,
            "directive_id": args.directive_id,
            "actor_id": args.actor,
            "reason": args.reason.strip(),
            "source_ref": args.source_ref,
            "obligation_id": args.obligation_id or None,
            "status": "REJECTED",
            "rejected_at": now,
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

    if not args.directive_id.strip():
        print("ERROR: --directive-id must be non-empty", file=sys.stderr)
        return 2

    reason_stripped = args.reason.strip()
    if not reason_stripped:
        print("ERROR: --reason must be non-empty", file=sys.stderr)
        return 2
    if len(reason_stripped) < MIN_REASON_CHARS:
        print(
            f"ERROR: --reason must be at least {MIN_REASON_CHARS} chars "
            f"after strip (got {len(reason_stripped)}). This script refuses "
            f"one-word brushoffs — explain the actual reasoning.",
            file=sys.stderr,
        )
        return 2

    rejection_id = f"reject_{uuid.uuid4().hex[:12]}"
    record = make_rejection_record(args, rejection_id)

    cieu = CIEUStore(db_path=args.db)
    if not cieu.write_dict(record):
        print("ERROR: CIEU write failed (duplicate event_id?)", file=sys.stderr)
        return 1

    print("OK: directive rejected")
    print(f"    rejection_id : {rejection_id}")
    print(f"    directive    : {args.directive_id}")
    print(f"    actor        : {args.actor}")
    print(f"    reason       : {reason_stripped[:100]}"
          f"{'…' if len(reason_stripped) > 100 else ''}")
    print(f"    db           : {args.db}")
    print()
    print("Next step: tell Board in chat that you rejected this directive ")
    print("and point at the rejection_id. Board can override by issuing a ")
    print("new directive that supersedes the rejected one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
