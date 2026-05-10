# E94 — Strategic Input Ingestion Pipeline Spec

**Status**: Spec for owner review (not yet implemented)
**Author**: Owner research session (sandbox, Claude)
**Target consumer**: CEO / CTO when scheduling implementation
**Type**: Engineering spec, not strategy memo
**Date**: 2026-05-09

---

## 1. The problem this spec solves

When the owner writes a strategic memo (`STRAT-002`, `STRAT-003`, etc.) and stores it under `knowledge/ceo/strategy/`, Aiden cannot read it.

When Aiden runs `e90_market_grounded_strategy_run`, the route candidates it scores come from a hardcoded list of 6 routes inside `_route_candidates()` — they do not come from any of:

- Owner strategic memos under `knowledge/ceo/strategy/STRAT-*.md`
- Aiden's own prior milestone artifacts under `operations/external_validation/e*_*.json`
- Earlier deep-strategy run outputs (e32 / e34 / e90 readbacks)
- Mission GO asset inventory (the 248K LOC across `Y-star-gov/`, `gov-mcp/`, `office/`)

The result: each new strategy run rediscovers the same 6 routes, scores them against the same frozen 5/4 evidence snapshot, and outputs a near-identical recommendation. New owner inputs do not change the outcome because they never enter the cognition pipeline.

E94 is the smallest pipeline that fixes this. Its goal is **not** to make Aiden smarter. Its goal is to make every new strategic memo and every prior milestone output **reachable** by `e90_market_grounded_strategy_run` and its successors, so subsequent runs can produce different conclusions when input changes.

---

## 2. What E94 is and is not

### Is

- A read-only ingestion module: `office/mission_command/e94_strategic_input_ingestion.py`
- A serialization format that turns owner memos and prior artifacts into a single structured input packet that `e90` and its successors can consume
- A deterministic loader that runs at the start of every deep-strategy run
- A small extension to `_route_candidates()` and `_route_scoring()` so they read from the input packet instead of hardcoding

### Is not

- A new cognition layer. It does not "interpret" memos or generate new opinions.
- A natural language to structured data converter. The owner memo format must already be structured enough to ingest (frontmatter + numbered sections, per the STRAT-001 / STRAT-002 convention).
- A live search runner. It only ingests what is already in the file system.
- A trigger to publish, contact, or send anything externally.

---

## 3. The data flow E94 enables

```
knowledge/ceo/strategy/STRAT-*.md         ─┐
operations/external_validation/e34_*.json  ├─→ e94 ingestion ─→ structured packet ─→ e90 (or successor)
office/mission_command/e32_*_inventory.py  ├─→
prior e90 readback reports                 ─┘
```

The structured packet replaces today's hardcoded `_route_candidates()` and `_route_scoring()` constants. e90's existing 14-dimension scoring and benchmark logic stay unchanged.

---

## 4. Module contract

**Path**: `office/mission_command/e94_strategic_input_ingestion.py`

**Public functions**:

```python
def build_strategic_input_packet(
    repo_root: Path | None = None,
    include_strategy_memos: bool = True,
    include_e34_artifacts: bool = True,
    include_prior_milestone_inventories: bool = True,
    include_dead_paths: bool = True,
) -> dict[str, Any]:
    """
    Returns a single dict containing all structured inputs for downstream
    deep-strategy runs. Read-only. No side effects.
    """

def extract_route_candidates_from_packet(
    packet: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Pulls route_id / name / description / route_type entries from
    ingested artifacts. Replaces e90._route_candidates() if packet is provided.
    """

def extract_evidence_pool_from_packet(
    packet: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Pulls evidence items (verified / unverified / corrected) from STRAT memos
    and e-number artifacts. Each evidence item carries its source path,
    verification status, and freshness timestamp.
    """

def extract_constraint_set_from_packet(
    packet: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Pulls owner-imposed constraints from STRAT memos (the 'Constraints Aiden
    Must Respect' sections) and dead_path documents (forbidden patterns).
    Used by e90 / e91 doctrine enforcement.
    """
```

**Returned packet shape**:

```python
{
    "packet_id": "e94_strategic_input_packet_<utc_iso>",
    "generated_at": "<utc_iso>",
    "sources": {
        "strategy_memos": [
            {
                "archive_id": "STRAT-001",
                "path": "knowledge/ceo/strategy/STRAT-001_governance_moat_vs_bounty_speed_20260416.md",
                "frontmatter": {...},     # parsed YAML-style frontmatter
                "sections": {...},         # heading -> body text
                "claims": [...],           # extracted from §3-style verified evidence
                "constraints": [...],      # extracted from 'must respect' sections
                "open_questions": [...],   # extracted from §8-style open-question sections
            },
            {... STRAT-002 ...}
        ],
        "e34_artifacts": [
            {
                "artifact_id": "e34_institutional_void_mapper",
                "path": "operations/external_validation/e34_institutional_void_mapper.json",
                "voids": [...],
                "most_important_void": "agent_action_authority"
            },
            {... e34_non_obvious_opportunity_spaces with 22 spaces ...}
        ],
        "milestone_inventories": [
            {
                "milestone_id": "e32",
                "path": "office/mission_command/e32_existing_learning_strategy_wheel_inventory.py",
                "frozen_at": "2026-05-04T22:30:00Z",
                "monetization_paths": [...],   # extracted from ARTIFACTS dict
                "scoring_summary": {...}
            }
        ],
        "dead_paths": [
            {
                "path_id": "premature_external_launch_ystar_defuse",
                "forbidden_patterns": [...],
                "revival_conditions": [...]
            }
        ],
    },
    "synthesized_views": {
        "merged_route_candidates": [...],
        "merged_evidence_pool": [...],
        "active_constraints": [...],
        "active_open_questions": [...],
        "freshness_warnings": [...]
    }
}
```

---

## 5. Parsing rules

For E94 to work without an LLM, the source files must be machine-parseable. Two of three input types already are. The third needs minor convention.

**5.1 STRAT-*.md memos** — already parseable.

The STRAT-001 / STRAT-002 convention provides:
- YAML-ish frontmatter (Archive ID, Date, Author, Type, Status, Related)
- Numbered sections (1, 2, 3...) with predictable headings
- §3 "Hard Evidence vs Unverified Claims" subsections (3.1, 3.2, 3.3) — mappable to `claims[].verification_status`
- §2 "Constraints" — mappable to `constraints[]`
- §8 "Open Questions" — mappable to `open_questions[]`

E94 parses these with a small markdown-section walker. No NLP.

**5.2 e34 / operations JSON artifacts** — already parseable.

These are JSON. E94 reads them and pulls predictable keys (`voids[]`, `opportunity_spaces[]`, `most_important_void`).

**5.3 Milestone inventories like e32** — needs convention.

Today, e32 stores its 5MB JSON inside a `.py` file as `ARTIFACTS = json.loads(r"""...""")`. E94 imports the module and reads `ARTIFACTS` directly. This works as-is.

For future milestones, the convention is: any milestone that produces a strategic snapshot exposes a top-level `ARTIFACTS: dict` constant or a `get_artifact(name) -> dict` function. e34 already follows this pattern (`from .e34_ceo_decision_failure_diagnosis import get_artifact`). e32 already follows the `ARTIFACTS` constant pattern.

E94 attempts both interfaces and skips modules that expose neither.

---

## 6. Integration into e90

**Change to** `office/mission_command/e90_market_grounded_strategy_run.py`:

Replace this:
```python
def _route_candidates() -> list[dict[str, Any]]:
    return [
        {"route_id": "governed_ops_blueprint_cieu_audit_wedge", ...},
        {"route_id": "cieu_audit_module", ...},
        ...
    ]
```

With this:
```python
from office.mission_command.e94_strategic_input_ingestion import (
    build_strategic_input_packet,
    extract_route_candidates_from_packet,
)

def _route_candidates(repo_root: Path | None = None) -> list[dict[str, Any]]:
    packet = build_strategic_input_packet(repo_root=repo_root)
    candidates = extract_route_candidates_from_packet(packet)
    if not candidates:
        # fallback to baseline 6 if ingestion produces nothing
        return _baseline_route_candidates()
    return candidates

def _baseline_route_candidates() -> list[dict[str, Any]]:
    # the current hardcoded list, kept as fallback only
    return [...]
```

**Same pattern** for `_route_scoring()`: it reads scoring weights from packet, falls back to hardcoded only when packet is empty.

**Doctrine integration**: `e91_ceo_doctrine_enforced_runtime_session.build_e90_doctrine_action_context()` accepts a new `constraints` parameter sourced from `extract_constraint_set_from_packet(packet)`. STRAT-001 trust-race thesis, STRAT-002 8 owner constraints, dead_path forbidden patterns all become enforced doctrine, not memos that Aiden never sees.

---

## 7. Test plan

The deliverable includes tests that verify E94 actually changes outputs:

**Test 1 — STRAT-002 visibility**:
Without E94: run `e90_market_grounded_strategy_run` against current branch. Capture output route list. Confirm "x402", "agent_to_agent_payment", "Mission GO" never appear in routes.
With E94: same run after spec implemented. Confirm at least one route originates from STRAT-002 §5 / §8 content (e.g., a route candidate matching e34 void #10).

**Test 2 — e34 propagation**:
Confirm `extract_route_candidates_from_packet()` includes at least 5 of the 22 e34 opportunity spaces as candidate routes.

**Test 3 — STRAT-001 doctrine enforcement**:
Confirm any candidate route classified as "speed-race" (e.g., 30-min hackathon-shaped) is filtered out by the constraint set extracted from STRAT-001.

**Test 4 — fallback safety**:
With `knowledge/ceo/strategy/` empty, confirm e90 still runs using the baseline 6-route hardcoded fallback. No regression.

**Test 5 — freshness warnings**:
Confirm e32's 2026-05-04 frozen snapshot is flagged as stale relative to STRAT-002's 2026-05-09 verified evidence, surfaced in `synthesized_views.freshness_warnings`.

---

## 8. Engineering scope

The spec describes scope only. No time estimates.

**Files created**:
- `office/mission_command/e94_strategic_input_ingestion.py`
- `tests/mission_command/test_e94_strategic_input_ingestion.py`

**Files modified**:
- `office/mission_command/e90_market_grounded_strategy_run.py` (`_route_candidates`, `_route_scoring`)
- `office/mission_command/e91_ceo_doctrine_enforced_runtime_session.py` (constraint injection)

**Files unchanged**:
- All STRAT-*.md memos (the format is already correct)
- All e34_*.json artifacts (already JSON)
- All e32-style frozen-inventory milestones (interface already exposed)
- `gov-mcp/` (no payment / no external action — this is read-only ingestion)
- `Y-star-gov/` (this lives in `office/mission_command/`, not in governance kernel)

**Permissions / boundaries**:
- E94 has read-only access to repo file system
- E94 does not write to brain.db, .ystar_cieu.db, or any DB
- E94 does not call external services or networks
- E94 is sandbox-promotable through the existing `gov-mcp/outbound/` state machine if ever needed, but does not require live promotion to function (it is internal)

---

## 9. What this enables next

After E94 is shipped:

1. **STRAT-002 finally lands**. The next `e90_market_grounded_strategy_run` reads it. The 7 open questions in STRAT-002 §8 become structured `open_questions[]` that the run produces specific responses for.
2. **e34 voids and opportunity spaces re-enter cognition**. Aiden's own April work stops being orphaned.
3. **STRAT-001 trust-race doctrine becomes enforced**, not just declared. Any future speed-race candidate gets filtered automatically.
4. **Subsequent STRAT-003+ memos can change strategy**. The owner's writing becomes a real input lever, not a wall to talk at.

After E94, the next work is the actual deep-strategy investigation that STRAT-002 asks for: x402 economy × Mission GO asset matching, with Aiden using its own 14-dimension benchmark and the now-ingested input packet.

---

## 10. What this does NOT enable

- Does not give Aiden the ability to autonomously act externally
- Does not give Aiden multi-tenant runtime
- Does not connect frontend-v2 chat box to mission_command (still separate)
- Does not modify aiden_meeting_room (the 11-template stub stays as-is — fixing it is a different project)
- Does not change patent claim scope
- Does not commit Y* to any external action

---

## 11. Risk and kill criteria

**Risks**:
- Markdown parsing of STRAT memos could miss content if section heading conventions drift. Mitigation: a strict parser that emits warnings on malformed input rather than silently dropping content.
- Extracting "candidate routes" from owner memos could produce non-actionable items (an open question is not a route). Mitigation: the extractor only promotes content explicitly marked as a candidate (e.g., §5 / §8 content), and degrades gracefully to "candidate observation" rather than "candidate route" when uncertain.
- The packet could grow large enough that e90 slows down. Mitigation: include a size cap with an explicit overflow flag; force the deep-strategy run to acknowledge truncation rather than silently dropping.

**Kill criteria** (decide after first real run):
- If the post-E94 strategy run output is materially the same as pre-E94 → either E94 is parsing wrong, or e90's downstream scoring discards the packet content. Either way, root-cause before adding more inputs.
- If owner reads three consecutive post-E94 strategy runs and they still feel "frozen" → the problem is not ingestion, it is scoring. Move to a separate spec for `_route_scoring()`.
- If parsing STRAT memos produces noticeably wrong claims attribution → switch to requiring explicit `<claim>` / `<constraint>` / `<open_question>` markers in memos, narrowing the parser scope.

---

## 12. Open question for owner

E94 is structured around the assumption that **Aiden's deep-strategy run (`e90`) is the right consumer** for ingested strategic input. If the owner intends `frontend-v2` (the 8784 dashboard) to also reflect ingested STRAT memos in real time, that requires a separate frontend-side change — not part of E94. Owner should decide whether to scope frontend integration as E95 or defer it.

---

**Filed as engineering spec for owner review. No implementation has occurred. No external action authorized.**
