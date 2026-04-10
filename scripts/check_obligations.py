#!/usr/bin/env python3.11
"""
check_obligations.py — GOV-001 Step 5

Stateless obligation status reporter. Reads the CIEU library as the single
source of truth, computes per-obligation status by comparing due_at to now
and matching OBLIGATION_FULFILLED records to OBLIGATION_REGISTERED ones.

Status semantics:
  PENDING   — registered, not yet fulfilled, now < due_at
  FULFILLED — a matching OBLIGATION_FULFILLED record exists
  OVERDUE   — registered, not fulfilled, now >= due_at

Usage:
  python3.11 scripts/check_obligations.py                       # all
  python3.11 scripts/check_obligations.py --actor ethan_wright  # filter
  python3.11 scripts/check_obligations.py --overdue-only        # only red
  python3.11 scripts/check_obligations.py --directive GOV-001   # by directive

  # Mark fulfilled (writes one OBLIGATION_FULFILLED record):
  python3.11 scripts/check_obligations.py \\
      --mark-fulfilled <OBLIGATION_ID> \\
      --by ethan_wright \\
      --evidence "git commit abc1234 + report sent to Board"
"""
import argparse
import json
import sys
import time
import uuid

from ystar.governance.cieu_store import CIEUStore


STATUS_PENDING = "PENDING"
STATUS_FULFILLED = "FULFILLED"
STATUS_OVERDUE = "OVERDUE"
STATUS_CANCELLED = "CANCELLED"

QUERY_LIMIT = 1000  # CIEU query default is 50, lift it for full audit pulls

SESSION_PATH = ".ystar_session.json"

# Legacy real-name actor IDs from GOV-001 Step 7 (before GOV-005 Part 4 unified
# the system to role-based IDs). These keep historical CIEU records readable
# without rewriting them — CIEU is append-only, so we resolve at display time.
LEGACY_ACTOR_ALIASES = {
    "ethan_wright": "cto",
    "aiden_liu": "ceo",
    "sofia_blake": "cmo",
    "zara_johnson": "cso",
    "marco_rivera": "cfo",
    "samantha_lin": "secretary",
}


def load_display_names(session_path: str = SESSION_PATH) -> dict:
    """Load agent_display_names from .ystar_session.json. Empty dict on failure."""
    try:
        with open(session_path, "r") as f:
            return json.load(f).get("agent_display_names", {})
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def canonical_actor(actor: str) -> str:
    """Map any actor ID (legacy real-name OR role) to its canonical role ID."""
    return LEGACY_ACTOR_ALIASES.get(actor, actor)


def fmt_secs(s: float) -> str:
    s = abs(float(s))
    if s < 60:
        return f"{s:.0f}s"
    if s < 3600:
        return f"{s/60:.1f}m"
    if s < 86400:
        return f"{s/3600:.1f}h"
    return f"{s/86400:.1f}d"


def parse_payload(record) -> dict:
    """Safely decode params_json into a dict; return {} on any error."""
    try:
        return json.loads(record.params_json or "{}")
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {}


def collect_obligations(cieu: CIEUStore) -> tuple[list, dict, dict]:
    """
    Return ``(registered_records, fulfilled_map, cancelled_map)``.

    ``fulfilled_map``: obligation_id -> (record, payload)
    ``cancelled_map``: obligation_id -> (record, payload) — populated by
    ``gov_order_undo.py`` writes (GOV-008 Q4) and treated as terminal.
    """
    regs = cieu.query(event_type="OBLIGATION_REGISTERED", limit=QUERY_LIMIT)
    fulfs = cieu.query(event_type="OBLIGATION_FULFILLED", limit=QUERY_LIMIT)
    cancs = cieu.query(event_type="OBLIGATION_CANCELLED", limit=QUERY_LIMIT)

    fulfilled_map = {}
    for f in fulfs:
        payload = parse_payload(f)
        ob_id = payload.get("obligation_id")
        if ob_id:
            fulfilled_map[ob_id] = (f, payload)

    cancelled_map = {}
    for c in cancs:
        payload = parse_payload(c)
        ob_id = payload.get("obligation_id")
        if ob_id:
            cancelled_map[ob_id] = (c, payload)
    return regs, fulfilled_map, cancelled_map


def build_rows(regs: list, fulfilled_map: dict, cancelled_map: dict, *,
               actor_filter: str | None = None,
               directive_filter: str | None = None,
               overdue_only: bool = False) -> list[dict]:
    now = time.time()
    rows = []
    # Normalize the filter once so the per-row comparison is cheap.
    filter_canonical = canonical_actor(actor_filter) if actor_filter else None

    for r in regs:
        payload = parse_payload(r)
        ob_id = payload.get("obligation_id")
        if not ob_id:
            continue

        actor_raw = payload.get("actor_id") or r.agent_id or "?"
        actor_role = canonical_actor(actor_raw)
        directive = payload.get("directive_ref") or payload.get("entity_id") or r.session_id or "?"

        if filter_canonical and filter_canonical != actor_role:
            continue
        if directive_filter and directive != directive_filter:
            continue

        due_at = float(payload.get("due_at") or 0)

        if ob_id in cancelled_map:
            status = STATUS_CANCELLED
            canc_payload = cancelled_map[ob_id][1]
            reason = (canc_payload.get("reason") or "")[:50]
            extra = f"by {canc_payload.get('cancelled_by', '?')}: {reason}"
        elif ob_id in fulfilled_map:
            status = STATUS_FULFILLED
            ful_payload = fulfilled_map[ob_id][1]
            extra = f"by {ful_payload.get('fulfilled_by', '?')}: {ful_payload.get('evidence', '')[:50]}"
        elif now >= due_at:
            status = STATUS_OVERDUE
            extra = f"overdue {fmt_secs(now - due_at)}"
        else:
            status = STATUS_PENDING
            extra = f"due in {fmt_secs(due_at - now)}"

        if overdue_only and status != STATUS_OVERDUE:
            continue

        rows.append({
            "obligation_id": ob_id,
            "actor": actor_raw,           # original record value (audit-faithful)
            "actor_role": actor_role,     # canonical role for display lookup
            "directive": directive,
            "type": payload.get("obligation_type") or "?",
            "status": status,
            "extra": extra,
            "severity": payload.get("severity") or "medium",
            "rule_id": payload.get("rule_id") or "?",
            "due_at": due_at,
        })

    # Sort: OVERDUE first, then PENDING by due_at, then FULFILLED, then CANCELLED last
    status_rank = {
        STATUS_OVERDUE: 0,
        STATUS_PENDING: 1,
        STATUS_FULFILLED: 2,
        STATUS_CANCELLED: 3,
    }
    rows.sort(key=lambda r: (status_rank.get(r["status"], 9), r["due_at"]))
    return rows


def print_table(rows: list[dict], display_names: dict) -> None:
    if not rows:
        print("(no obligations match the filter)")
        return

    header = (
        f"{'Status':<10} {'Sev':<8} {'Actor':<26} "
        f"{'Directive':<14} {'Rule':<18} {'OBL_ID':<14} Extra"
    )
    print(header)
    print("-" * 140)
    for r in rows:
        # Resolve display name via the canonical role; fall back to raw actor
        # if the role isn't in the map (e.g., 'doctor_agent', 'eng-kernel').
        actor_display = display_names.get(r["actor_role"], r["actor"])
        print(
            f"{r['status']:<10} {r['severity']:<8} {actor_display[:25]:<26} "
            f"{r['directive']:<14} {r['rule_id'][:16]:<18} "
            f"{r['obligation_id'][:12]:<14} {r['extra']}"
        )

    pending = sum(1 for r in rows if r["status"] == STATUS_PENDING)
    overdue = sum(1 for r in rows if r["status"] == STATUS_OVERDUE)
    fulfilled = sum(1 for r in rows if r["status"] == STATUS_FULFILLED)
    cancelled = sum(1 for r in rows if r["status"] == STATUS_CANCELLED)
    print()
    print(
        f"Total: {len(rows)}  |  pending: {pending}  overdue: {overdue}  "
        f"fulfilled: {fulfilled}  cancelled: {cancelled}"
    )


def mark_fulfilled(cieu: CIEUStore, obligation_id: str,
                   by_actor: str, evidence: str) -> int:
    # Find the registration record so we can copy session_id and validate the id.
    regs = cieu.query(event_type="OBLIGATION_REGISTERED", limit=QUERY_LIMIT)
    target = None
    for r in regs:
        payload = parse_payload(r)
        if payload.get("obligation_id") == obligation_id:
            target = (r, payload)
            break

    if target is None:
        print(f"ERROR: obligation_id {obligation_id} not found in CIEU registry",
              file=sys.stderr)
        return 1

    reg_record, reg_payload = target
    now = time.time()
    # NOTE: CIEUStore._insert_dict reads `d.get("params")` (raw dict), not
    # `d.get("params_json")`. Read-side exposes it as `params_json` string.
    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": reg_record.session_id,
        "agent_id": by_actor,
        "event_type": "OBLIGATION_FULFILLED",
        "decision": "info",
        "evidence_grade": "ops",
        "created_at": now,
        "seq_global": time.time_ns() // 1000,
        "params": {
            "obligation_id": obligation_id,
            "rule_id": reg_payload.get("rule_id"),
            "fulfilled_by": by_actor,
            "evidence": evidence,
            "fulfilled_at": now,
            "registered_at": reg_payload.get("registered_at"),
            "due_at": reg_payload.get("due_at"),
            "actor_id": reg_payload.get("actor_id"),
            "directive_ref": reg_payload.get("directive_ref"),
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": by_actor,
    }
    ok = cieu.write_dict(record)
    if not ok:
        print("WARN: duplicate or write failed", file=sys.stderr)
        return 1

    print(f"OK: marked fulfilled {obligation_id}")
    print(f"    by      : {by_actor}")
    print(f"    evidence: {evidence}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Check obligation status from CIEU library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--db", default=".ystar_cieu.db",
                   help="CIEU database path (default: .ystar_cieu.db)")
    p.add_argument("--actor", default=None,
                   help="Filter by actor_id. Accepts both new role-based IDs "
                        "(ceo/cto/cmo/cso/cfo/secretary) and legacy real-name "
                        "format (ethan_wright/aiden_liu/...). Both resolve to "
                        "the same canonical role.")
    p.add_argument("--directive", default=None,
                   help="Filter by directive reference (e.g. GOV-001)")
    p.add_argument("--overdue-only", action="store_true",
                   help="Show only OVERDUE rows")
    p.add_argument("--mark-fulfilled", metavar="OBLIGATION_ID", default=None,
                   help="Write an OBLIGATION_FULFILLED record for this obligation ID")
    p.add_argument("--by", default="",
                   help="Actor performing the fulfillment (required with --mark-fulfilled)")
    p.add_argument("--evidence", default="",
                   help="Evidence string (commit hash, file path, report URL, ...)")
    args = p.parse_args()

    cieu = CIEUStore(db_path=args.db)

    if args.mark_fulfilled:
        if not args.by:
            print("ERROR: --by is required with --mark-fulfilled", file=sys.stderr)
            return 2
        return mark_fulfilled(cieu, args.mark_fulfilled, args.by, args.evidence)

    regs, fulfilled_map, cancelled_map = collect_obligations(cieu)
    rows = build_rows(
        regs,
        fulfilled_map,
        cancelled_map,
        actor_filter=args.actor,
        directive_filter=args.directive,
        overdue_only=args.overdue_only,
    )
    display_names = load_display_names()
    print_table(rows, display_names)
    return 0


if __name__ == "__main__":
    sys.exit(main())
