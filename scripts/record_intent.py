#!/usr/bin/env python3.11
"""
record_intent.py — GOV-006 Intent Verification Protocol (option C).

Writes one ``INTENT_RECORDED`` event to the CIEU library. The event is
the agent's own pre-execution commitment to an interpretation of a
Level 2 or Level 3 directive: *what do I think the current state is,
what do I think the goal is, and what do I plan to do about it.*

GOV-009 upgrade (2026-04-10): four additional fields are now mandatory
and hard-validated at CLI-parse time:

  --meaning      why this matters + connection to company goals
                 (>= 30 chars after strip)
  --success-bar  measurable completion criteria
                 (rejects vague phrases: 做完, 做好, 完成, done, finish, ok)
  --assumptions  hidden judgments + verification status, one per flag
                 (format: "假设内容——已验证" or "假设内容——未验证")
                 (at least one required)
  --theory       theory/framework + one-line insight, one per flag
                 (format: "理论名——一句话启示", both sides non-empty)
                 (at least one required)

An intent row missing any of the four new fields is treated as
"unqualified" by the GOV-008 Gap 2 hook guard and triggers a
GOV006_VIOLATION_WARNING row (warn-only, fail-open).

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
      --meaning "这件事为什么重要，和公司目标如何连接 (>=30 chars)" \\
      --success-bar "具体可验证的完成判定标准" \\
      --assumptions "假设A——已验证" --assumptions "假设B——未验证" \\
      --theory "理论名1——一句话启示" --theory "理论名2——一句话启示" \\
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

# GOV-009 hard-coded quality-bar constants.
MEANING_MIN_CHARS = 30
VAGUE_SUCCESS_BAR_PATTERNS = (
    "做完", "做好", "完成", "搞定", "弄好",
    "done", "finish", "finished", "ok", "okay",
)
ASSUMPTION_SEPARATOR = "——"
ASSUMPTION_VALID_STATUSES = ("已验证", "未验证")
THEORY_SEPARATOR = "——"


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
            "directive. GOV-009 adds four hard-enforced quality-bar fields: "
            "--meaning, --success-bar, --assumptions, --theory."
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
    # ── GOV-009 quality-bar fields (all required) ────────────────────
    p.add_argument("--meaning", required=True,
                   help=f"Why this matters + connection to company goals "
                        f"(>= {MEANING_MIN_CHARS} chars after strip). GOV-009.")
    p.add_argument("--success-bar", required=True,
                   help="Measurable completion criteria. Rejects vague "
                        "phrases like 做完/做好/完成/done/finish/ok. GOV-009.")
    p.add_argument("--assumptions", action="append", default=[],
                   help="Hidden judgment + verification status. Format: "
                        "'假设内容——已验证' or '假设内容——未验证'. At least "
                        "one required. GOV-009.")
    p.add_argument("--theory", action="append", default=[],
                   help="Theory name + one-line insight. Format: "
                        "'理论名——一句话启示' (both sides non-empty). At "
                        "least one required. GOV-009.")
    p.add_argument("--notes", default="",
                   help="Optional freeform notes (constraints, known unknowns, "
                        "etc.)")
    p.add_argument("--source-ref", default="",
                   help="Optional back-reference to a proposal file "
                        "(e.g. reports/cto/intent_verification_proposal.md)")
    return p


def _validate_meaning(value: str) -> list[str]:
    if not value or not value.strip():
        return ["--meaning must not be empty"]
    stripped = value.strip()
    if len(stripped) < MEANING_MIN_CHARS:
        return [
            f"--meaning must be at least {MEANING_MIN_CHARS} chars after "
            f"strip (got {len(stripped)}). Describe why this task matters "
            f"and how it connects to the company's overall goal."
        ]
    return []


def _validate_success_bar(value: str) -> list[str]:
    if not value or not value.strip():
        return ["--success-bar must not be empty"]
    stripped = value.strip()
    # Reject if the ENTIRE value is a vague phrase (or a vague phrase +
    # trivial padding). A longer success-bar is allowed to contain a
    # vague word inside a larger sentence.
    lowered = stripped.lower()
    for pattern in VAGUE_SUCCESS_BAR_PATTERNS:
        pl = pattern.lower()
        if lowered == pl or lowered.strip(".。!?,，") == pl:
            return [
                f"--success-bar {value!r} is too vague. 'done' / 'finish' / "
                f"'做完' / '做好' / '完成' are not measurable. Describe a "
                f"concrete, verifiable condition (tests passing, a file "
                f"existing, a metric reaching a threshold)."
            ]
    # Also reject very short success-bars — a one-word measurable
    # criterion is almost always hiding ambiguity.
    if len(stripped) < 10:
        return [
            f"--success-bar must be at least 10 chars (got {len(stripped)}). "
            f"Short criteria hide ambiguity. Write a sentence."
        ]
    return []


def _validate_assumptions(values: list[str]) -> list[str]:
    if not values:
        return [
            "--assumptions is required at least once. Format: "
            "'内容——已验证' or '内容——未验证'. Example: "
            "--assumptions '用户会每周使用——未验证'."
        ]
    errors: list[str] = []
    for idx, raw in enumerate(values, 1):
        if not raw or not raw.strip():
            errors.append(f"--assumptions #{idx} is empty")
            continue
        stripped = raw.strip()
        if ASSUMPTION_SEPARATOR not in stripped:
            errors.append(
                f"--assumptions #{idx} {stripped!r} missing '{ASSUMPTION_SEPARATOR}' "
                f"separator. Format: '内容{ASSUMPTION_SEPARATOR}已验证' or "
                f"'内容{ASSUMPTION_SEPARATOR}未验证'."
            )
            continue
        content, _, status = stripped.rpartition(ASSUMPTION_SEPARATOR)
        if not content.strip():
            errors.append(f"--assumptions #{idx} has empty content before '{ASSUMPTION_SEPARATOR}'")
        status_clean = status.strip()
        if status_clean not in ASSUMPTION_VALID_STATUSES:
            errors.append(
                f"--assumptions #{idx} status {status_clean!r} invalid. "
                f"Must be one of {list(ASSUMPTION_VALID_STATUSES)}."
            )
    return errors


def _validate_theory(values: list[str]) -> list[str]:
    if not values:
        return [
            "--theory is required at least once. Format: "
            "'理论名——一句话启示'. Example: "
            "--theory 'Conway\u2019s law——team structure shapes system architecture'."
        ]
    errors: list[str] = []
    for idx, raw in enumerate(values, 1):
        if not raw or not raw.strip():
            errors.append(f"--theory #{idx} is empty")
            continue
        stripped = raw.strip()
        if THEORY_SEPARATOR not in stripped:
            errors.append(
                f"--theory #{idx} {stripped!r} missing '{THEORY_SEPARATOR}' "
                f"separator. Format: '理论名{THEORY_SEPARATOR}一句话启示'."
            )
            continue
        name, _, insight = stripped.partition(THEORY_SEPARATOR)
        if not name.strip():
            errors.append(f"--theory #{idx} has empty theory name before '{THEORY_SEPARATOR}'")
        if not insight.strip():
            errors.append(f"--theory #{idx} has empty insight after '{THEORY_SEPARATOR}'")
    return errors


def validate_gov009_fields(args: argparse.Namespace) -> list[str]:
    """Run all four GOV-009 validators and return the concatenated
    error list. Empty list = valid."""
    errors: list[str] = []
    errors += _validate_meaning(args.meaning)
    errors += _validate_success_bar(args.success_bar)
    errors += _validate_assumptions(args.assumptions)
    errors += _validate_theory(args.theory)
    return errors


def make_intent_record(args: argparse.Namespace, intent_id: str) -> dict:
    """Construct the CIEU row. Mirrors ``register_obligation.make_cieu_record``
    for schema consistency — downstream readers can share one parser.

    GOV-009: the four new fields (meaning, success_bar, assumptions,
    theory) are embedded in params. The hook guard's ``_intent_is_qualified``
    check reads them from this exact location.
    """
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
            # GOV-009 quality-bar fields
            "meaning": args.meaning.strip(),
            "success_bar": args.success_bar.strip(),
            "assumptions": [a.strip() for a in args.assumptions],
            "theory": [t.strip() for t in args.theory],
            # end GOV-009
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

    # GOV-009 quality-bar validation. Any error → exit 2, no CIEU write.
    gov009_errors = validate_gov009_fields(args)
    if gov009_errors:
        print("ERROR: GOV-009 quality bar failed — intent NOT written", file=sys.stderr)
        for err in gov009_errors:
            print(f"  - {err}", file=sys.stderr)
        return 2

    intent_id = f"intent_{uuid.uuid4().hex[:12]}"
    record = make_intent_record(args, intent_id)

    cieu = CIEUStore(db_path=args.db)
    ok = cieu.write_dict(record)
    if not ok:
        print("ERROR: CIEU write failed (duplicate event_id?)", file=sys.stderr)
        return 1

    # Emit INTENT_DECLARED (canonical event, k9_audit_v3 requirement)
    declared_event = {
        "event_id": str(uuid.uuid4()),
        "session_id": args.directive_id,
        "agent_id": args.actor,
        "event_type": "INTENT_DECLARED",
        "decision": "info",
        "evidence_grade": "intent",
        "created_at": time.time(),
        "seq_global": time.time_ns() // 1000,
        "params": {
            "intent_id": intent_id,
            "directive_id": args.directive_id,
            "level": args.level,
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": args.actor,
    }
    cieu.write_dict(declared_event)

    print(f"OK: intent recorded")
    print(f"    intent_id   : {intent_id}")
    print(f"    directive   : {args.directive_id}")
    print(f"    level       : {args.level}")
    print(f"    actor       : {args.actor}")
    print(f"    plan_steps  : {len(args.plan)}")
    print(f"    meaning     : {args.meaning.strip()[:60]}"
          f"{'…' if len(args.meaning.strip()) > 60 else ''}")
    print(f"    success_bar : {args.success_bar.strip()[:60]}"
          f"{'…' if len(args.success_bar.strip()) > 60 else ''}")
    print(f"    assumptions : {len(args.assumptions)} entries")
    print(f"    theory      : {len(args.theory)} entries")
    print(f"    db          : {args.db}")
    print()
    print("Next step: paste the INTENT block in the chat reply and WAIT for ")
    print("Board (Level 3) or CEO (Level 2) confirmation before any tool call.")
    print(f"After confirmation, mark status with:")
    print(f"  python3.11 scripts/check_intents.py --confirm {intent_id} "
          f"--by board --decision approve --notes '<why>'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
