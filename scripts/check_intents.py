#!/usr/bin/env python3.11
"""
check_intents.py — GOV-006 Intent Verification Protocol reader/confirmer.

Reads the CIEU library to list, filter, and confirm ``INTENT_RECORDED``
events. Writes the confirming ``INTENT_CONFIRMED`` / ``INTENT_ADJUSTED``
/ ``INTENT_REJECTED`` records when the reviewer acts on an intent.

Status semantics
----------------
RECORDED  — only an INTENT_RECORDED row exists; waiting for reviewer.
CONFIRMED — reviewer approved; agent may proceed with the recorded plan.
ADJUSTED  — reviewer accepted the intent but with a modification
            (notes must be present; agent must re-read before executing).
REJECTED  — reviewer rejected; agent must not execute. A new intent is
            required if the agent wants to retry.

Usage::

  python3.11 scripts/check_intents.py                          # list recent
  python3.11 scripts/check_intents.py --unconfirmed-only       # pending only
  python3.11 scripts/check_intents.py --actor cto              # by actor
  python3.11 scripts/check_intents.py --directive GOV-006      # by directive
  python3.11 scripts/check_intents.py --show intent_ab12cd34ef # full detail

  # Confirm / adjust / reject an intent:
  python3.11 scripts/check_intents.py \\
      --confirm intent_ab12cd34ef \\
      --by board \\
      --decision approve \\
      --notes "plan is clean, execute as written"
"""
import argparse
import json
import sys
import time
import uuid

from ystar.governance.cieu_store import CIEUStore

SESSION_PATH = ".ystar_session.json"
QUERY_LIMIT = 1000

# Reuse the legacy actor mapping from check_obligations so historical rows
# written under the old real-name schema still display correctly.
LEGACY_ACTOR_ALIASES = {
    "ethan_wright": "cto",
    "aiden_liu": "ceo",
    "sofia_blake": "cmo",
    "zara_johnson": "cso",
    "marco_rivera": "cfo",
    "samantha_lin": "secretary",
}

REVIEWERS = {"board", "ceo"}
DECISIONS = {"approve", "adjust", "reject"}

STATUS_RECORDED = "RECORDED"
STATUS_CONFIRMED = "CONFIRMED"
STATUS_ADJUSTED = "ADJUSTED"
STATUS_REJECTED = "REJECTED"

DECISION_TO_STATUS = {
    "approve": STATUS_CONFIRMED,
    "adjust": STATUS_ADJUSTED,
    "reject": STATUS_REJECTED,
}
DECISION_TO_EVENT_TYPE = {
    "approve": "INTENT_CONFIRMED",
    "adjust": "INTENT_ADJUSTED",
    "reject": "INTENT_REJECTED",
}


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


def canonical_actor(actor: str) -> str:
    return LEGACY_ACTOR_ALIASES.get(actor, actor)


def parse_payload(record) -> dict:
    try:
        return json.loads(record.params_json or "{}")
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {}


def collect_intents(cieu: CIEUStore) -> tuple[list, dict]:
    """Return (recorded_rows, reviews_map).

    recorded_rows: list of (record, payload) for INTENT_RECORDED
    reviews_map: intent_id -> (event_type, review_record, review_payload)
                 chosen as the most recent review for that intent.
    """
    recorded = cieu.query(event_type="INTENT_RECORDED", limit=QUERY_LIMIT)
    confirmed = cieu.query(event_type="INTENT_CONFIRMED", limit=QUERY_LIMIT)
    adjusted = cieu.query(event_type="INTENT_ADJUSTED", limit=QUERY_LIMIT)
    rejected = cieu.query(event_type="INTENT_REJECTED", limit=QUERY_LIMIT)

    reviews_map: dict = {}
    for ev_type, rows in (
        ("INTENT_CONFIRMED", confirmed),
        ("INTENT_ADJUSTED", adjusted),
        ("INTENT_REJECTED", rejected),
    ):
        for r in rows:
            payload = parse_payload(r)
            intent_id = payload.get("intent_id")
            if not intent_id:
                continue
            # Keep the latest review only (CIEU is append-only; latest by created_at wins)
            prior = reviews_map.get(intent_id)
            if prior is None or (r.created_at or 0) > (prior[1].created_at or 0):
                reviews_map[intent_id] = (ev_type, r, payload)

    recorded_rows = [(r, parse_payload(r)) for r in recorded]
    return recorded_rows, reviews_map


def status_for(intent_id: str, reviews_map: dict) -> tuple[str, dict | None]:
    review = reviews_map.get(intent_id)
    if review is None:
        return STATUS_RECORDED, None
    ev_type, _, review_payload = review
    if ev_type == "INTENT_CONFIRMED":
        return STATUS_CONFIRMED, review_payload
    if ev_type == "INTENT_ADJUSTED":
        return STATUS_ADJUSTED, review_payload
    return STATUS_REJECTED, review_payload


def build_rows(recorded_rows: list, reviews_map: dict, *,
               actor_filter: str | None,
               directive_filter: str | None,
               unconfirmed_only: bool) -> list[dict]:
    actor_canon = canonical_actor(actor_filter) if actor_filter else None
    rows = []
    for rec, payload in recorded_rows:
        intent_id = payload.get("intent_id")
        if not intent_id:
            continue
        actor_raw = payload.get("actor_id") or rec.agent_id or "?"
        actor_role = canonical_actor(actor_raw)
        directive = payload.get("directive_id") or rec.session_id or "?"
        level = payload.get("level", "?")

        if actor_canon and actor_canon != actor_role:
            continue
        if directive_filter and directive_filter != directive:
            continue

        status, review_payload = status_for(intent_id, reviews_map)
        if unconfirmed_only and status != STATUS_RECORDED:
            continue

        extra = ""
        if review_payload is not None:
            by = review_payload.get("reviewer", "?")
            notes = (review_payload.get("notes") or "")[:60]
            extra = f"by {by}: {notes}"
        else:
            age = time.time() - (payload.get("recorded_at") or rec.created_at or time.time())
            extra = f"waiting {age/60:.0f}m"

        rows.append({
            "intent_id": intent_id,
            "actor": actor_raw,
            "actor_role": actor_role,
            "directive": directive,
            "level": level,
            "status": status,
            "extra": extra,
            "created_at": payload.get("recorded_at") or rec.created_at or 0,
            "payload": payload,
        })
    # Most recent first; RECORDED on top within same timestamp bucket.
    status_rank = {STATUS_RECORDED: 0, STATUS_ADJUSTED: 1, STATUS_CONFIRMED: 2, STATUS_REJECTED: 3}
    rows.sort(key=lambda r: (status_rank.get(r["status"], 9), -r["created_at"]))
    return rows


def print_table(rows: list[dict], display_names: dict) -> None:
    if not rows:
        print("(no intents match the filter)")
        return

    header = (
        f"{'Status':<10} {'L':<3} {'Actor':<24} "
        f"{'Directive':<14} {'Intent ID':<22} Extra"
    )
    print(header)
    print("-" * 120)
    for r in rows:
        actor_display = display_names.get(r["actor_role"], r["actor"])
        print(
            f"{r['status']:<10} {str(r['level']):<3} {actor_display[:23]:<24} "
            f"{r['directive']:<14} {r['intent_id']:<22} {r['extra']}"
        )

    recorded = sum(1 for r in rows if r["status"] == STATUS_RECORDED)
    confirmed = sum(1 for r in rows if r["status"] == STATUS_CONFIRMED)
    adjusted = sum(1 for r in rows if r["status"] == STATUS_ADJUSTED)
    rejected = sum(1 for r in rows if r["status"] == STATUS_REJECTED)
    print()
    print(
        f"Total: {len(rows)}  |  recorded: {recorded}  confirmed: {confirmed}"
        f"  adjusted: {adjusted}  rejected: {rejected}"
    )


def show_one(recorded_rows: list, reviews_map: dict, intent_id: str) -> int:
    for rec, payload in recorded_rows:
        if payload.get("intent_id") != intent_id:
            continue
        status, review_payload = status_for(intent_id, reviews_map)
        source = payload.get("source")
        is_gov_order = source == "gov_order"

        print(f"Intent       : {intent_id}")
        if is_gov_order:
            print(f"Source       : gov_order (Board NL → CIEU)")
            print(f"Directive    : {payload.get('directive_id') or rec.session_id}")
            print(f"Actor        : board")
        else:
            print(f"Directive    : {payload.get('directive_id')}")
            print(f"Level        : {payload.get('level')}")
            print(f"Actor        : {payload.get('actor_id')}")
        print(f"Status       : {status}")
        print(f"Recorded at  : {time.ctime(payload.get('recorded_at') or rec.created_at or 0)}")
        print()

        if is_gov_order:
            # gov_order schema: input_nl, llm_provider, llm_model, llm_output, validation_status
            print(f"Input NL:")
            print(f"  {payload.get('input_nl')}")
            print()
            print(f"LLM provider : {payload.get('llm_provider')}")
            print(f"LLM model    : {payload.get('llm_model')}")
            print(f"Validation   : {payload.get('validation_status')}")
            errors = payload.get("validation_errors") or []
            if errors:
                print("Validation errors:")
                for e in errors:
                    print(f"  - {e}")
            llm_out = payload.get("llm_output")
            if isinstance(llm_out, dict):
                print()
                print("LLM output:")
                for k in ("owner", "entity_id", "rule_id", "rule_name",
                          "due_secs", "severity", "required_event"):
                    print(f"  {k:<14} : {llm_out.get(k)}")
                desc = (llm_out.get("description") or "").strip()
                if desc:
                    snippet = desc if len(desc) <= 200 else desc[:200] + "…"
                    print(f"  description    : {snippet}")
        else:
            # GOV-006 agent-intent schema: xt, y_star, plan, notes
            print(f"Xt (current state understanding):")
            print(f"  {payload.get('xt')}")
            print()
            print(f"Y* (target understanding):")
            print(f"  {payload.get('y_star')}")
            print()
            print("Plan:")
            for i, step in enumerate(payload.get("plan") or [], 1):
                print(f"  {i}. {step}")
            if payload.get("notes"):
                print()
                print(f"Notes: {payload.get('notes')}")
            if payload.get("source_ref"):
                print(f"Source ref: {payload.get('source_ref')}")

        if review_payload is not None:
            print()
            print("--- Review ---")
            print(f"Decision : {review_payload.get('decision')}")
            print(f"By       : {review_payload.get('reviewer')}")
            print(f"Notes    : {review_payload.get('notes')}")
            print(f"Reviewed : {time.ctime(review_payload.get('reviewed_at') or 0)}")
        return 0
    print(f"ERROR: intent_id {intent_id} not found", file=sys.stderr)
    return 1


def review_intent(cieu: CIEUStore, recorded_rows: list, intent_id: str,
                  by_actor: str, decision: str, notes: str) -> int:
    target = None
    for rec, payload in recorded_rows:
        if payload.get("intent_id") == intent_id:
            target = (rec, payload)
            break
    if target is None:
        print(f"ERROR: intent_id {intent_id} not found", file=sys.stderr)
        return 1
    rec, payload = target

    by_canon = canonical_actor(by_actor)
    if by_canon not in REVIEWERS:
        print(
            f"ERROR: --by must resolve to one of {sorted(REVIEWERS)}, "
            f"got {by_actor!r}",
            file=sys.stderr,
        )
        return 2
    if decision not in DECISIONS:
        print(
            f"ERROR: --decision must be one of {sorted(DECISIONS)}, "
            f"got {decision!r}",
            file=sys.stderr,
        )
        return 2
    # Level 3 intents MUST be reviewed by the Board. CEO cannot confirm them.
    level = payload.get("level")
    if level == 3 and by_canon != "board":
        print(
            f"ERROR: Level 3 intent can only be reviewed by --by board, "
            f"got {by_canon!r}",
            file=sys.stderr,
        )
        return 2
    if decision in ("adjust",) and not notes.strip():
        print(
            "ERROR: --notes is required with --decision adjust",
            file=sys.stderr,
        )
        return 2

    now = time.time()
    event_type = DECISION_TO_EVENT_TYPE[decision]
    new_status = DECISION_TO_STATUS[decision]

    record = {
        "event_id": str(uuid.uuid4()),
        "session_id": rec.session_id,
        "agent_id": by_canon,
        "event_type": event_type,
        "decision": "info",
        "evidence_grade": "intent",
        "created_at": now,
        "seq_global": time.time_ns() // 1000,
        "params": {
            "intent_id": intent_id,
            "directive_id": payload.get("directive_id"),
            "level": payload.get("level"),
            "actor_id": payload.get("actor_id"),
            "reviewer": by_canon,
            "decision": decision,
            "status": new_status,
            "notes": notes,
            "reviewed_at": now,
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": by_canon,
    }
    ok = cieu.write_dict(record)
    if not ok:
        print("WARN: duplicate or write failed", file=sys.stderr)
        return 1

    # Emit INTENT_FULFILLED (canonical event, k9_audit_v3 requirement) when decision=approve
    if decision == "approve":
        fulfilled_event = {
            "event_id": str(uuid.uuid4()),
            "session_id": rec.session_id,
            "agent_id": by_canon,
            "event_type": "INTENT_FULFILLED",
            "decision": "info",
            "evidence_grade": "intent",
            "created_at": time.time(),
            "seq_global": time.time_ns() // 1000,
            "params": {
                "intent_id": intent_id,
                "directive_id": payload.get("directive_id"),
                "reviewer": by_canon,
            },
            "violations": [],
            "drift_detected": False,
            "human_initiator": by_canon,
        }
        cieu.write_dict(fulfilled_event)

    print(f"OK: intent {intent_id} → {new_status}")
    print(f"    decision : {decision}")
    print(f"    by       : {by_canon}")
    print(f"    notes    : {notes}")
    return 0


def main() -> int:
    defaults = load_session_defaults()
    p = argparse.ArgumentParser(
        description="List and review INTENT_RECORDED events (GOV-006)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--db", default=defaults["cieu_db"],
                   help="CIEU database path (default: from .ystar_session.json)")
    p.add_argument("--actor", default=None,
                   help="Filter by actor_id (accepts legacy real-names too)")
    p.add_argument("--directive", default=None,
                   help="Filter by directive id (e.g. GOV-006)")
    p.add_argument("--unconfirmed-only", action="store_true",
                   help="Show only RECORDED (waiting-for-review) rows")
    p.add_argument("--show", metavar="INTENT_ID", default=None,
                   help="Show full detail for one intent")
    p.add_argument("--confirm", metavar="INTENT_ID", default=None,
                   help="Write a review event for this intent")
    p.add_argument("--by", default="",
                   help="Reviewer (board|ceo). Required with --confirm.")
    p.add_argument("--decision", default="",
                   choices=["approve", "adjust", "reject", ""],
                   help="Review decision. Required with --confirm.")
    p.add_argument("--notes", default="",
                   help="Review notes (mandatory for --decision adjust)")
    args = p.parse_args()

    cieu = CIEUStore(db_path=args.db)
    recorded_rows, reviews_map = collect_intents(cieu)

    if args.show:
        return show_one(recorded_rows, reviews_map, args.show)

    if args.confirm:
        if not args.by or not args.decision:
            print(
                "ERROR: --confirm requires --by <board|ceo> and "
                "--decision <approve|adjust|reject>",
                file=sys.stderr,
            )
            return 2
        return review_intent(
            cieu, recorded_rows, args.confirm,
            args.by, args.decision, args.notes,
        )

    rows = build_rows(
        recorded_rows, reviews_map,
        actor_filter=args.actor,
        directive_filter=args.directive,
        unconfirmed_only=args.unconfirmed_only,
    )
    print_table(rows, defaults["display_names"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
