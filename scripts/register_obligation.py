#!/usr/bin/env python3.11
"""
register_obligation.py — GOV-001 Step 5

Register an obligation lifecycle event in the CIEU library.

Design (Y*Bridge Labs flavor):
  - Uses an EMPTY RuleRegistry — Y*gov default rules (e.g. rule_a_delegation
    that auto-creates a delegation obligation on every ENTITY_CREATED) are
    intentionally suppressed. Only the explicit rule passed via CLI fires.
  - The OmissionEngine is built fresh per invocation; in-memory state is
    discarded after the script exits. The CIEU library is the single source
    of truth for obligation persistence.
  - Each new obligation produced by `engine.ingest_event` is written to CIEU
    as one record with event_type='OBLIGATION_REGISTERED'. The full obligation
    payload (obligation_id, due_at, rule_id, etc.) lives in params_json.

Usage:
  python3.11 scripts/register_obligation.py \\
      --entity-id GOV-001 \\
      --owner ethan_wright \\
      --rule-id gov_001_ack \\
      --rule-name "GOV-001 acknowledgement" \\
      --description "Engineering team must acknowledge GOV-001 within 4h" \\
      --due-secs 14400 \\
      --severity high
"""
import argparse
import sys
import time
import uuid
import warnings

# Suppress OmissionEngine's NullCIEUStore warning. The warning is misleading
# in our design: we intentionally don't pass `cieu_store=` to OmissionEngine.
# Persistence happens directly via `cieu.write_dict()` in `make_cieu_record()`,
# not through the engine's internal CIEU path. The script DOES persist —
# the warning's "CIEU events will NOT be persisted" is wrong for our usage.
warnings.filterwarnings("ignore", message=".*NullCIEUStore.*")

from ystar import (  # noqa: E402  (intentional after warnings filter)
    BUILTIN_RULES,
    EntityStatus,
    GEventType,
    GovernanceEvent,
    InMemoryOmissionStore,
    OmissionEngine,
    OmissionRule,
    TrackedEntity,
)
from ystar.governance.cieu_store import CIEUStore
from ystar.governance.omission_engine import RuleRegistry
from ystar.governance.omission_models import Severity


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Register an obligation lifecycle event in the CIEU library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--db", default=".ystar_cieu.db",
                   help="CIEU database path (default: .ystar_cieu.db)")
    p.add_argument("--entity-id", required=True,
                   help="Entity (typically a directive) ID, e.g. GOV-001")
    p.add_argument("--owner", required=True,
                   help="Actor ID who owes the obligation, e.g. ethan_wright")
    p.add_argument("--rule-id", required=True,
                   help="Rule ID, e.g. gov_001_ack")
    p.add_argument("--rule-name", required=True,
                   help="Human-readable rule name")
    p.add_argument("--description", required=True,
                   help="What this obligation is about")
    p.add_argument("--obligation-type", default="required_acknowledgement_omission",
                   help="Y*gov OmissionType value (default: required_acknowledgement_omission)")
    p.add_argument("--required-event", default="acknowledgement_event",
                   help="Event type that fulfills this obligation "
                        "(default: acknowledgement_event)")
    p.add_argument("--due-secs", type=float, required=True,
                   help="Soft deadline in seconds from now")
    p.add_argument("--severity", default="high",
                   choices=["low", "medium", "high", "critical"],
                   help="Severity (default: high)")
    p.add_argument("--initiator", default="board",
                   help="Who issued the entity (default: board)")
    p.add_argument("--directive-ref", default="",
                   help="Reference back to the originating directive "
                        "(default: same as --entity-id)")
    return p


def build_engine_and_rule(args: argparse.Namespace) -> tuple[OmissionEngine, OmissionRule]:
    """Build a fresh OmissionEngine with an empty registry + the single CLI rule.

    NOTE: `RuleRegistry()` is NOT empty by construction — its `__init__`
    deep-copies all `BUILTIN_RULES` (rule_a_delegation, rule_b_acknowledgement,
    rule_c_status_update, rule_d_result_publication, rule_e_upstream_notification,
    rule_f_escalation, rule_g_closure) into `_rules`. We must explicitly
    `unregister()` each builtin to honor Decision B (Y*Bridge Labs only fires
    explicit rules; Y*gov defaults are intentionally suppressed at this layer).
    """
    registry = RuleRegistry()
    for builtin in BUILTIN_RULES:
        registry.unregister(builtin.rule_id)

    rule = OmissionRule(
        rule_id=args.rule_id,
        name=args.rule_name,
        description=args.description,
        trigger_event_types=[GEventType.ENTITY_CREATED],
        entity_types=["directive"],
        obligation_type=args.obligation_type,
        required_event_types=[args.required_event],
        due_within_secs=args.due_secs,
        severity=Severity(args.severity),
    )
    registry.register(rule)
    engine = OmissionEngine(store=InMemoryOmissionStore(), registry=registry)
    return engine, rule


def _build_cieu_record(ob, *, entity_id: str, rule_id: str, rule_name: str,
                       description: str, due_within_secs: float,
                       directive_ref: str, initiator: str) -> dict:
    """Build a CIEU record dict for one ObligationRecord.

    NOTE on schema: CIEUStore._insert_dict reads `d.get("params")` (raw dict),
    not `d.get("params_json")`. CIEU serializes internally via _sanitize_json.
    Same asymmetry for "result". Read-side returns it as `params_json` string.
    """
    now = time.time()
    return {
        "event_id": str(uuid.uuid4()),
        "session_id": entity_id,
        "agent_id": ob.actor_id,
        "event_type": "OBLIGATION_REGISTERED",
        "decision": "info",
        "evidence_grade": "ops",
        "created_at": now,
        "seq_global": time.time_ns() // 1000,
        "params": {
            "obligation_id": ob.obligation_id,
            "rule_id": rule_id,
            "rule_name": rule_name,
            "obligation_type": ob.obligation_type,
            "required_event_types": list(ob.required_event_types),
            "due_at": ob.due_at,
            "due_within_secs": due_within_secs,
            "severity": ob.severity.value if hasattr(ob.severity, "value") else str(ob.severity),
            "actor_id": ob.actor_id,
            "entity_id": ob.entity_id,
            "directive_ref": directive_ref or entity_id,
            "description": description,
            "trigger_event_id": ob.trigger_event_id,
            "registered_at": now,
        },
        "violations": [],
        "drift_detected": False,
        "human_initiator": initiator,
    }


def make_cieu_record(ob, args: argparse.Namespace) -> dict:
    """Backward-compat wrapper for the original ``args``-based call site."""
    return _build_cieu_record(
        ob,
        entity_id=args.entity_id,
        rule_id=args.rule_id,
        rule_name=args.rule_name,
        description=args.description,
        due_within_secs=args.due_secs,
        directive_ref=args.directive_ref,
        initiator=args.initiator,
    )


def register_obligation_programmatic(
    *,
    db_path: str,
    entity_id: str,
    owner: str,
    rule_id: str,
    rule_name: str,
    description: str,
    due_secs: float,
    severity: str = "high",
    obligation_type: str = "required_acknowledgement_omission",
    required_event: str = "acknowledgement_event",
    initiator: str = "board",
    directive_ref: str = "",
    verbose: bool = True,
) -> list[str]:
    """Register one obligation in the CIEU library, callable from Python code.

    This is the GOV-008 Step 2a refactor target. ``main()`` below is a thin
    argparse wrapper around this function. Both call sites land in the same
    write path so unit tests can exercise the function directly without
    spawning a subprocess.

    Returns a list of obligation_ids actually written (one per
    ``OmissionEngine`` rule firing — typically 1).
    """
    # Build a synthetic argparse.Namespace so build_engine_and_rule can stay
    # untouched (it only reads args.* fields and not anything else).
    ns = argparse.Namespace(
        db=db_path,
        entity_id=entity_id,
        owner=owner,
        rule_id=rule_id,
        rule_name=rule_name,
        description=description,
        obligation_type=obligation_type,
        required_event=required_event,
        due_secs=due_secs,
        severity=severity,
        initiator=initiator,
        directive_ref=directive_ref,
    )

    cieu = CIEUStore(db_path=db_path)
    engine, _rule = build_engine_and_rule(ns)

    entity = TrackedEntity(
        entity_id=entity_id,
        entity_type="directive",
        initiator_id=initiator,
        current_owner_id=owner,
        status=EntityStatus.CREATED,
        goal_summary=description,
    )
    engine.register_entity(entity)

    ev = GovernanceEvent(
        event_type=GEventType.ENTITY_CREATED,
        entity_id=entity_id,
        actor_id=initiator,
        source="register_obligation_programmatic",
        payload={"directive_ref": directive_ref or entity_id},
    )
    result = engine.ingest_event(ev)

    if not result.new_obligations:
        raise RuntimeError(
            f"rule {rule_id!r} did not produce any obligation; "
            f"check rule fields"
        )

    written: list[str] = []
    for ob in result.new_obligations:
        record = _build_cieu_record(
            ob,
            entity_id=entity_id,
            rule_id=rule_id,
            rule_name=rule_name,
            description=description,
            due_within_secs=due_secs,
            directive_ref=directive_ref,
            initiator=initiator,
        )
        ok = cieu.write_dict(record)
        if ok:
            written.append(ob.obligation_id)
            if verbose:
                due_in = ob.due_at - time.time()
                print(f"  registered: {ob.obligation_id}")
                print(f"    actor    : {ob.actor_id}")
                print(f"    rule     : {rule_id}")
                print(f"    type     : {ob.obligation_type}")
                print(f"    due_in   : {due_in/3600:.1f}h ({due_in:.0f}s)")
                print(f"    severity : "
                      f"{ob.severity.value if hasattr(ob.severity, 'value') else ob.severity}")
        else:
            print(
                f"  WARN: duplicate or write failed for {ob.obligation_id}",
                file=sys.stderr,
            )
    return written


def main() -> int:
    args = build_argparser().parse_args()
    try:
        written = register_obligation_programmatic(
            db_path=args.db,
            entity_id=args.entity_id,
            owner=args.owner,
            rule_id=args.rule_id,
            rule_name=args.rule_name,
            description=args.description,
            due_secs=args.due_secs,
            severity=args.severity,
            obligation_type=args.obligation_type,
            required_event=args.required_event,
            initiator=args.initiator,
            directive_ref=args.directive_ref,
            verbose=True,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    cieu = CIEUStore(db_path=args.db)
    print()
    print(f"OK: wrote {len(written)} obligation(s) to {args.db}")
    print(f"    total CIEU records now: {cieu.count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
