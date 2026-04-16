# CIEU Event Taxonomy — Canonical Naming Doctrine

**Status**: L4 CONSTITUTIONAL DRAFT (W27 atomic dispatch)
**Established**: 2026-04-15
**Author**: Samantha Lin (Secretary)
**Purpose**: single source of truth for every `event_type` value written to `.ystar_cieu.db`. W26 k9_audit_v3 infrastructure (Liveness / Chain / Invariant layers) depends on this doctrine to wire queries to real data. W27.1 ForgetGuard rule `cieu_event_unknown_type` enforces it.

---

## 1. Naming Specification

### 1.1 Format

```
[LAYER]_[ACTION](_[QUALIFIER])?
```

- **LAYER** (required, enum): physical source layer emitting the event.
  `AGENT | HOOK | GOVERNANCE | AUDIT | INTENT | OBLIGATION | CIEU | SECRETARY | FORGET_GUARD | ARTICLE_11 | RESIDUAL_LOOP | WHITELIST | OMISSION | CANONICAL | WIRE | DEFER | BACKLOG | CHOICE | BEHAVIOR | DIRECTIVE | BOARD | SUBAGENT | CEO | TWIN | SESSION | IDLE | TELEGRAM | KNOWLEDGE | ADE | MATURITY | TOMBSTONE`
- **ACTION** (required, verb, uppercase): what happened.
  `START | STARTED | BOOT | TRIGGER | TRIGGERED | CHECK | TICK | RECEIVED | RECORDED | REGISTERED | LINKED | DECLARED | ADJUSTED | CONFIRMED | COMPLETED | FULFILLED | CANCELLED | REJECTED | DENY | WARN | WARNING | DRIFT | BROKEN | MATCH | GAP | VIOLATION | ACTION | CONVERGED | OSCILLATION | ESCALATE | ESCALATED | SHIPPED | DECISION | PUSH | CHANGED | SET | READ | WRITE | EXEC | FAILED | SCAN | UPDATED | IMPORT | IMPORTED | APPLIED | LINT | TRANSITION | MILESTONE | INSIGHT | CURATE | CURATED | PULL | PULLED | OVERRIDE | FIXED`
- **QUALIFIER** (optional, noun): disambiguating context. `RULE | TOKEN | BOARD | COMMIT | REPLY | BASH | DAILY | SESSION | LAYER_{0..12} | ARTICLE_11 | BREAK_GLASS | etc.`

### 1.2 Examples (canonical)

| Event | Layer | Action | Qualifier | Reads |
|-------|-------|--------|-----------|-------|
| `FORGET_GUARD` | forget_guard | (top-level aggregate) | — | "forget_guard fired" |
| `FORGETGUARD_DENY` *(future, see §4)* | forget_guard | deny | — | "forget_guard denied op" |
| `WIRE_BROKEN` | wire | broken | — | "wire broken" |
| `OBLIGATION_REGISTERED` | obligation | registered | — | "obligation registered" |
| `DEFER_IN_REPLY_DRIFT` | defer | drift | in_reply | "defer-language drift found in assistant reply" |
| `CIEU_LAYER_7` | cieu | (layer marker) | layer 7 | "12-layer protocol layer 7 ack" |
| `SECRETARY_CURATE_COMPLETE` | secretary | completed | curate | "curation pipeline finished" |

### 1.3 Non-conforming but grandfathered

Lowercase snake-case events predate this doctrine. Kept live, flagged for rename in §4.

```
cmd_exec            handoff               file_read           file_write
session_start       session_close         chain_reset         lesson
external_observation  orchestration:*     omission_violation:*  intervention_gate:*
intervention_pulse:* obligation_check     action_pulled       boot_protocol_completed
continuation_loaded task_dispatched       content.artifact.ship
```

---

## 2. Full Event-Type Registry (observed `.ystar_cieu.db` @ 2026-04-15 — 148 distinct types)

Columns: `event_type | layer | category | rename_to | first_used | status`
- `category`: Liveness / Chain / Invariant / Drift / Lifecycle / Meta / Grandfathered
- `rename_to`: blank if already canonical; otherwise new canonical name
- `status`: `CANONICAL | DEPRECATED | RENAME_PENDING | GRANDFATHERED | UNKNOWN_TO_AUDIT`

| event_type | layer | category | rename_to | first_used | status |
|---|---|---|---|---|---|
| `HOOK_BOOT` | hook | Liveness | — | 2026-04 | CANONICAL |
| `CIEU_WATCHER_TICK` | cieu | Liveness | — | 2026-04 | CANONICAL |
| `governance_coverage_scan` | governance | Liveness | `GOVERNANCE_COVERAGE_SCAN` | 2026-04 | RENAME_PENDING |
| `omission_setup_complete` | omission | Liveness | `OMISSION_SETUP_COMPLETE` | 2026-04 | RENAME_PENDING |
| `circuit_breaker_armed` | governance | Liveness | `GOVERNANCE_CIRCUIT_BREAKER_ARMED` | 2026-04 | RENAME_PENDING |
| `session_start` | session | Liveness | `SESSION_START` | 2026-04 | RENAME_PENDING |
| `boot_protocol_completed` | session | Liveness | `SESSION_BOOT_COMPLETED` | 2026-04 | RENAME_PENDING |
| `continuation_loaded` | session | Liveness | `SESSION_CONTINUATION_LOADED` | 2026-04 | RENAME_PENDING |
| `AGENT_IDENTITY_SET` | agent | Liveness | — | 2026-04 | CANONICAL |
| `HOOK_STARTUP` | hook | Liveness | `HOOK_BOOT` *(audit_v3 bug)* | — | UNKNOWN_TO_AUDIT |
| `omission_violation:required_acknowledgement_omission` | omission | Drift | `OMISSION_ACK_REQUIRED_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:directive_acknowledgement` | omission | Drift | `OMISSION_DIRECTIVE_ACK_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:intent_declaration` | omission | Drift | `OMISSION_INTENT_DECL_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:progress_update` | omission | Drift | `OMISSION_PROGRESS_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:task_completion_report` | omission | Drift | `OMISSION_TASK_COMPLETE_REPORT_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:knowledge_update` | omission | Drift | `OMISSION_KNOWLEDGE_UPDATE_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:autonomous_daily_report` | omission | Drift | `OMISSION_DAILY_REPORT_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:gemma_session_daily` | omission | Drift | `OMISSION_GEMMA_SESSION_MISSED` | 2026-04 | RENAME_PENDING |
| `omission_violation:theory_library_daily` | omission | Drift | `OMISSION_THEORY_LIB_MISSED` | 2026-04 | RENAME_PENDING |
| `OMISSION_TRIGGER` | omission | Liveness | — | proposed | CANONICAL |
| `FORGET_GUARD` | forget_guard | Invariant | — | 2026-04 | CANONICAL |
| `FORGETGUARD_CHECK` | forget_guard | Liveness | — | proposed | CANONICAL |
| `FORGET_GUARD_ARTICLE_11_PARTIAL_WALK` | forget_guard | Invariant | — | 2026-04 | CANONICAL |
| `FORGET_GUARD_ARTICLE_11_BYPASS_WARNING` | forget_guard | Invariant | — | 2026-04 | CANONICAL |
| `ARTICLE_11_MISSING` | article_11 | Invariant | — | 2026-04 | CANONICAL |
| `ARTICLE_11_LAYER_0_COMPLETE` .. `_6_COMPLETE` | article_11 | Chain | — | 2026-04 | CANONICAL |
| `CIEU_LAYER_0` .. `CIEU_LAYER_12` | cieu | Chain | — | 2026-04 | CANONICAL |
| `INTENT_RECORDED` | intent | Chain | — | 2026-04 | CANONICAL |
| `INTENT_LINKED` | intent | Chain | — | 2026-04 | CANONICAL |
| `INTENT_DECLARED` | intent | Chain | — | 2026-04 | CANONICAL |
| `INTENT_CONFIRMED` | intent | Chain | — | 2026-04 | CANONICAL |
| `INTENT_ADJUSTED` | intent | Chain | — | 2026-04 | CANONICAL |
| `INTENT_COMPLETED` | intent | Chain | — | 2026-04 | CANONICAL |
| `INTENT_REJECTED` | intent | Chain | — | 2026-04 | CANONICAL |
| `INTENT_RECEIVED` | intent | Chain | — | proposed | CANONICAL |
| `OBLIGATION_REGISTERED` | obligation | Chain | — | 2026-04 | CANONICAL |
| `OBLIGATION_FULFILLED` | obligation | Chain | — | 2026-04 | CANONICAL |
| `OBLIGATION_CANCELLED` | obligation | Chain | — | 2026-04 | CANONICAL |
| `OBLIGATION_CREATED` | obligation | Chain | `OBLIGATION_REGISTERED` *(audit_v3 bug)* | — | UNKNOWN_TO_AUDIT |
| `obligation_check` | obligation | Liveness | `OBLIGATION_CHECK` | 2026-04 | RENAME_PENDING |
| `DIRECTIVE_ACKNOWLEDGED` | directive | Chain | — | 2026-04 | CANONICAL |
| `DIRECTIVE_REJECTED` | directive | Chain | — | 2026-04 | CANONICAL |
| `DIRECTIVE_FAILED` | directive | Chain | — | proposed | CANONICAL |
| `BOARD_DECISION` | board | Chain | — | 2026-04 | CANONICAL |
| `BOARD_DIRECTIVE` | board | Chain | — | audit_v3 expects | UNKNOWN_TO_AUDIT |
| `ESCALATION` | residual_loop | Chain | `RESIDUAL_LOOP_ESCALATE` *(audit_v3 bug)* | — | UNKNOWN_TO_AUDIT |
| `RESIDUAL_LOOP_ACTION` | residual_loop | Chain | — | 2026-04 | CANONICAL |
| `RESIDUAL_LOOP_CONVERGED` | residual_loop | Chain | — | 2026-04 | CANONICAL |
| `RESIDUAL_LOOP_OSCILLATION` | residual_loop | Drift | — | 2026-04 | CANONICAL |
| `RESIDUAL_LOOP_ESCALATE` | residual_loop | Chain | — | 2026-04 | CANONICAL |
| `GAP_IDENTIFIED` | governance | Chain | — | 2026-04 | CANONICAL |
| `GAP_REPORTED` | governance | Chain | `GAP_IDENTIFIED` *(audit_v3 bug)* | — | UNKNOWN_TO_AUDIT |
| `WHITELIST_MATCH` | whitelist | Invariant | — | 2026-04 | CANONICAL |
| `WHITELIST_DRIFT` | whitelist | Drift | — | 2026-04 | CANONICAL |
| `WHITELIST_GAP` | whitelist | Drift | — | 2026-04 | CANONICAL |
| `WHITELIST_UPDATE` | whitelist | Chain | — | 2026-04 | CANONICAL |
| `DEFER_LANGUAGE_DRIFT` | defer | Drift | — | 2026-04 | CANONICAL |
| `DEFER_IN_COMMIT_DRIFT` | defer | Drift | — | 2026-04 | CANONICAL |
| `DEFER_IN_BASH_DRIFT` | defer | Drift | — | 2026-04 | CANONICAL |
| `DEFER_IN_REPLY_DRIFT` | defer | Drift | — | 2026-04-15 | CANONICAL |
| `BACKLOG_DISGUISE_DRIFT` | backlog | Drift | — | 2026-04-15 | CANONICAL |
| `CHOICE_IN_REPLY_DRIFT` | choice | Drift | — | 2026-04-15 | CANONICAL |
| `BOARD_CHOICE_QUESTION_DRIFT` | board | Drift | — | 2026-04-15 | CANONICAL |
| `CEO_CODE_WRITE_DRIFT` | ceo | Drift | — | 2026-04-15 | CANONICAL |
| `CEO_ENGINEERING_OVERRIDE` | ceo | Invariant | — | 2026-04-15 | CANONICAL |
| `CEO_NO_MIDSTREAM_CHECKIN` *(W25 R6)* | ceo | Drift | — | 2026-04-15 | CANONICAL |
| `CANONICAL_HASH_DRIFT` | canonical | Drift | — | 2026-04-15 | CANONICAL |
| `WIRE_BROKEN` | wire | Drift | — | 2026-04 | CANONICAL |
| `BEHAVIOR_RULE_VIOLATION` | behavior | Invariant | — | 2026-04 | CANONICAL |
| `BEHAVIOR_RULE_WARNING` | behavior | Invariant | — | 2026-04 | CANONICAL |
| `GOV006_VIOLATION_WARNING` | governance | Invariant | — | 2026-04 | CANONICAL |
| `IMMUTABLE_FORGOT_BREAK_GLASS` | governance | Drift | — | 2026-04 | CANONICAL |
| `A1_VIOLATION_PREVENTED` | governance | Invariant | — | 2026-04 | CANONICAL |
| `MATURITY_TAG_MISSING` | maturity | Drift | — | 2026-04 | CANONICAL |
| `MATURITY_TRANSITION` | maturity | Chain | — | 2026-04 | CANONICAL |
| `SESSION_JSON_SCHEMA_VIOLATION` | session | Drift | — | 2026-04 | CANONICAL |
| `OFF_TARGET_WARNING` | governance | Drift | — | 2026-04 | CANONICAL |
| `MIRROR_SYNC` | governance | Lifecycle | — | 2026-04 | CANONICAL |
| `KNOWLEDGE_IMPORT` | knowledge | Lifecycle | — | 2026-04 | CANONICAL |
| `KNOWLEDGE_IMPORT_COMPLETE` | knowledge | Lifecycle | — | 2026-04 | CANONICAL |
| `LESSON_READ` | knowledge | Lifecycle | — | 2026-04 | CANONICAL |
| `lesson` | knowledge | Lifecycle | `LESSON_CAPTURED` | 2026-04 | RENAME_PENDING |
| `TWIN_EVOLUTION` | twin | Lifecycle | — | 2026-04 | CANONICAL |
| `SECRETARY_CURATE_START` | secretary | Chain | — | 2026-04 | CANONICAL |
| `SECRETARY_CURATE_COMPLETE` | secretary | Chain | — | 2026-04 | CANONICAL |
| `SECRETARY_CURATION_DECISION` | secretary | Chain | — | 2026-04 | CANONICAL |
| `ACTION_QUEUE_UPDATED` | governance | Chain | — | 2026-04 | CANONICAL |
| `action_pulled` | governance | Chain | `ACTION_PULLED` | 2026-04 | RENAME_PENDING |
| `IDLE_PULL` | idle | Chain | — | 2026-04 | CANONICAL |
| `TOMBSTONE_APPLIED` | tombstone | Chain | — | 2026-04 | CANONICAL |
| `TOMBSTONE_LINT` | tombstone | Invariant | — | 2026-04 | CANONICAL |
| `LIVE_FILE_CHANGED` | governance | Chain | — | 2026-04 | CANONICAL |
| `DIALOGUE_CONTRACT_DRAFT` | governance | Lifecycle | — | 2026-04 | CANONICAL |
| `PRIORITY_BRIEF_CHECK` | governance | Chain | — | 2026-04 | CANONICAL |
| `PRIORITY_BRIEF_TARGETS_CHECK` | governance | Chain | — | 2026-04 | CANONICAL |
| `PROGRESS_UPDATED` | governance | Chain | — | 2026-04 | CANONICAL |
| `TASK_START` | governance | Chain | — | 2026-04 | CANONICAL |
| `TASK_COMPLETED` | governance | Chain | — | 2026-04 | CANONICAL |
| `TASK_COMPLETION_REPORT` | governance | Chain | — | 2026-04 | CANONICAL |
| `VERIFY` | governance | Chain | — | 2026-04 | CANONICAL |
| `STEP` | governance | Chain | — | 2026-04 | CANONICAL |
| `SUBAGENT_BOARD_SHELL_REQUEST` | subagent | Invariant | — | 2026-04-15 | CANONICAL |
| `SUBAGENT_DEFER_DRIFT` | subagent | Drift | — | 2026-04-15 | CANONICAL |
| `AGENT_PUSH` | agent | Chain | — | 2026-04 | CANONICAL |
| `chain_reset` | governance | Lifecycle | `CHAIN_RESET` | 2026-04 | RENAME_PENDING |
| `handoff` | governance | Lifecycle | `HANDOFF` | 2026-04 | RENAME_PENDING |
| `handoff_failed` | governance | Drift | `HANDOFF_FAILED` | 2026-04 | RENAME_PENDING |
| `intervention_gate:deny` | governance | Invariant | `INTERVENTION_GATE_DENY` | 2026-04 | RENAME_PENDING |
| `intervention_pulse:soft_pulse` | governance | Liveness | `INTERVENTION_PULSE_SOFT` | 2026-04 | RENAME_PENDING |
| `intervention_pulse:interrupt_gate` | governance | Invariant | `INTERVENTION_PULSE_INTERRUPT` | 2026-04 | RENAME_PENDING |
| `external_observation` | meta | Meta | `EXTERNAL_OBSERVATION` | 2026-04 | RENAME_PENDING |
| `cmd_exec` | hook | Liveness | `HOOK_CMD_EXEC` | 2026-04 | RENAME_PENDING |
| `file_read` / `file_write` | hook | Liveness | `HOOK_FILE_READ` / `HOOK_FILE_WRITE` | 2026-04 | RENAME_PENDING |
| `Read` / `Write` / `Edit` / `Bash` / `Agent` / `TaskCreate` / `TaskUpdate` | agent | Liveness | `AGENT_TOOL_<UPPER>` | 2026-04 | RENAME_PENDING |
| `web_fetch` | agent | Liveness | `AGENT_TOOL_WEB_FETCH` | 2026-04 | RENAME_PENDING |
| `orchestration:governance_loop_cycle` | governance | Liveness | `ORCHESTRATION_GOV_LOOP_CYCLE` | 2026-04 | RENAME_PENDING |
| `orchestration:path_a_cycle` / `:path_b_cycle` | governance | Liveness | `ORCHESTRATION_PATH_A_CYCLE` / `_PATH_B_CYCLE` | 2026-04 | RENAME_PENDING |
| `session_close` | session | Lifecycle | `SESSION_CLOSE` | 2026-04 | RENAME_PENDING |
| `TELEGRAM_DAILY_DRYRUN` | telegram | Lifecycle | — | 2026-04 | CANONICAL |
| `TELEGRAM_DISTILL_DRYRUN` | telegram | Lifecycle | — | 2026-04 | CANONICAL |
| `TELEGRAM_EVENT_MILESTONE_SHIPPED` | telegram | Lifecycle | — | 2026-04 | CANONICAL |
| `TELEGRAM_EVENT_MILESTONE_SHIPPED_FAILED` | telegram | Drift | — | 2026-04 | CANONICAL |
| `TELEGRAM_EVENT_CRITICAL_INSIGHT_DRYRUN` | telegram | Lifecycle | — | 2026-04 | CANONICAL |
| `CRITICAL_INSIGHT` | governance | Chain | — | 2026-04 | CANONICAL |
| `COMPANY_FORMALIZATION_AUDIT_COMPLETE` | audit | Lifecycle | — | 2026-04 | CANONICAL |
| `ADE_CAT11_POPULATOR_FIXED` | ade | Lifecycle | — | 2026-04 | CANONICAL |
| `OMISSION_TIMER_TO_BEHAVIOR_FIXED` | omission | Lifecycle | — | 2026-04 | CANONICAL |
| `AMENDMENT_013_IMPLEMENTATION` | governance | Lifecycle | — | 2026-04 | CANONICAL |
| `SKILL_LIFECYCLE_SCAN` | audit | Lifecycle | — | 2026-04 | CANONICAL |
| `TEST_CIEU_REPAIR` | test | Meta | — | 2026-04 | CANONICAL |
| `P1C_TEST_1776273366` | test | Meta | `TEST_*` | 2026-04 | DEPRECATED |
| `task_dispatched` | governance | Chain | `TASK_DISPATCHED` | 2026-04 | RENAME_PENDING |
| `content.artifact.ship` | cmo | Lifecycle | `CONTENT_ARTIFACT_SHIP` | 2026-04 | RENAME_PENDING |
| `(empty string)` | — | — | delete | 2026-04 | DEPRECATED |

---

## 3. Canonical Event List (W26 k9_audit_v3 source of truth)

### 3.1 Liveness indicators (Layer 1 of k9_audit_v3)

Query pattern: `SELECT COUNT(*) WHERE event_type = ? AND created_at > now - 5min`

```
HOOK_BOOT
CIEU_WATCHER_TICK
OMISSION_TRIGGER              (rename of omission_setup_complete path)
FORGETGUARD_CHECK              (proposed fire-on-every-hook liveness)
RLE_TICK                       (proposed residual-loop heartbeat)
INTENT_RECEIVED                (proposed — sibling of INTENT_RECORDED)
AGENT_IDENTITY_SET
SESSION_START
SESSION_BOOT_COMPLETED
```

### 3.2 Chain events (Layer 2 of k9_audit_v3)

Expected causal path `GOV_ORDER → INTENT_RECORDED → OBLIGATION_REGISTERED → …` :

```
BOARD_DECISION
BOARD_DIRECTIVE                (alias-to BOARD_DECISION — see §4)
DIRECTIVE_ACKNOWLEDGED
INTENT_RECORDED
INTENT_LINKED
INTENT_DECLARED
INTENT_CONFIRMED
INTENT_ADJUSTED
INTENT_COMPLETED
OBLIGATION_REGISTERED
OBLIGATION_FULFILLED
OBLIGATION_CANCELLED
GAP_IDENTIFIED
RESIDUAL_LOOP_ACTION
RESIDUAL_LOOP_CONVERGED
RESIDUAL_LOOP_ESCALATE
CIEU_LAYER_0 … CIEU_LAYER_12
ARTICLE_11_LAYER_0_COMPLETE … ARTICLE_11_LAYER_6_COMPLETE
CIEU_EVENT_EMIT                (proposed — every emit logs itself)
CIEU_INGEST                    (proposed — watcher confirms ingest)
```

### 3.3 Drift events (Layer 3 Invariant of k9_audit_v3)

```
DEFER_LANGUAGE_DRIFT
DEFER_IN_COMMIT_DRIFT
DEFER_IN_BASH_DRIFT
DEFER_IN_REPLY_DRIFT
BACKLOG_DISGUISE_DRIFT
CHOICE_IN_REPLY_DRIFT
BOARD_CHOICE_QUESTION_DRIFT
CEO_CODE_WRITE_DRIFT
CEO_NO_MIDSTREAM_CHECKIN
SUBAGENT_DEFER_DRIFT
CANONICAL_HASH_DRIFT
WIRE_BROKEN
BEHAVIOR_RULE_VIOLATION
BEHAVIOR_RULE_WARNING
SESSION_JSON_SCHEMA_VIOLATION
RESIDUAL_LOOP_OSCILLATION
OFF_TARGET_WARNING
WHITELIST_DRIFT
WHITELIST_GAP
MATURITY_TAG_MISSING
IMMUTABLE_FORGOT_BREAK_GLASS
```

### 3.4 Invariant events (Layer 3 of k9_audit_v3)

```
DIRECTIVE_FAILED
DIRECTIVE_REJECTED
OBLIGATION_FULFILLED
OBLIGATION_CANCELLED
RESIDUAL_LOOP_ESCALATE
BOARD_DECISION
FORGET_GUARD
FORGET_GUARD_ARTICLE_11_PARTIAL_WALK
FORGET_GUARD_ARTICLE_11_BYPASS_WARNING
ARTICLE_11_MISSING
WHITELIST_MATCH
INTERVENTION_GATE_DENY
GOV006_VIOLATION_WARNING
A1_VIOLATION_PREVENTED
CEO_ENGINEERING_OVERRIDE
SUBAGENT_BOARD_SHELL_REQUEST
TOMBSTONE_LINT
```

---

## 4. Deprecation / Rename Migration

**Policy**: 30-day backward compatibility window from 2026-04-15. During window, both legacy and canonical names accepted by readers (k9_audit_v3, gov_trend, secretary_curate). After 2026-05-15 emit code enforces canonical only.

### 4.1 Audit-v3 already-broken aliases (apply immediately)

k9_audit_v3.py currently queries names that do not exist in the db. Until script is patched, readers must alias:

| audit_v3 expects | real canonical | action |
|---|---|---|
| `HOOK_STARTUP` | `HOOK_BOOT` | patch `scripts/k9_audit_v3.py:416` |
| `OBLIGATION_CREATED` | `OBLIGATION_REGISTERED` | patch `scripts/k9_audit_v3.py:364` |
| `BOARD_DIRECTIVE` | `BOARD_DECISION` *(or add emitter)* | patch `scripts/k9_audit_v3.py:345` |
| `ESCALATION` | `RESIDUAL_LOOP_ESCALATE` | patch `scripts/k9_audit_v3.py:378-382` |
| `GAP_REPORTED` | `GAP_IDENTIFIED` | patch `scripts/k9_audit_v3.py:397` |

### 4.2 Lowercase → UPPERCASE renames (30-day window)

All `RENAME_PENDING` rows in §2 table. Emitter-side changes tracked in ticket `W27.2_lowercase_event_rename`.

### 4.3 Colon-namespaced → underscore

```
orchestration:*            → ORCHESTRATION_*
omission_violation:*       → OMISSION_<NAME>_MISSED
intervention_gate:*        → INTERVENTION_GATE_*
intervention_pulse:*       → INTERVENTION_PULSE_*
```

### 4.4 Outright deprecations

- `(empty string)` — 4406 rows, corrupt emits. Drop in next vacuum (W28).
- `P1C_TEST_1776273366` — one-off test residue. Rename future test events `TEST_<PURPOSE>`.
- `lesson` (lowercase) — → `LESSON_CAPTURED`.

---

## 5. Validation Rule

### 5.1 ForgetGuard `cieu_event_unknown_type` (W27.1 backlog)

Pseudocode (Python hook, runs in `scripts/forget_guard.py`):

```python
KNOWN_EVENT_TYPES = load_yaml("governance/cieu_event_taxonomy.yaml")  # machine view of §2

def check_cieu_emit(event):
    et = event.get("event_type", "")
    if et in KNOWN_EVENT_TYPES:
        return PASS
    if et in GRANDFATHERED_SET:
        return WARN_SOFT  # during 30-day window
    emit({
        "event_type": "UNKNOWN_CIEU_EVENT_TYPE",
        "decision": "WARN",
        "drift_detected": 1,
        "drift_category": "taxonomy",
        "drift_details": f"emit used event_type '{et}' not in taxonomy",
        "agent_id": event.get("agent_id"),
    })
    return WARN_HARD
```

Wire point: every call to `CIEUClient.emit()` (wrap in `scripts/cieu/client.py` entrypoint). Violations visible in `gov_report --event UNKNOWN_CIEU_EVENT_TYPE`.

### 5.2 Machine-readable companion

A YAML mirror of §2 lives at `governance/cieu_event_taxonomy.yaml` (produced by W27.1 work). Loader of record: `scripts/cieu_taxonomy.py::load_taxonomy()`. Any PR adding a new event_type must update both this .md and the .yaml.

---

## 6. Amendment Protocol

Adding a new event_type:
1. Propose via Secretary sub-agent task card; include layer/action/qualifier + category.
2. Append to §2 with `status=CANONICAL` and today's date in `first_used`.
3. Add to §3 bucket (Liveness / Chain / Drift / Invariant / Lifecycle / Meta).
4. Regenerate `governance/cieu_event_taxonomy.yaml`.
5. Secretary logs to `governance/DNA_LOG.md` with commit hash.
6. Emitters may start writing events once both files are merged.

Renaming an existing event_type:
1. Same as above but `status=RENAME_PENDING`, `rename_to` filled.
2. 30-day backward compat starts on merge date.
3. CTO (or Platform engineer) opens tracking ticket to migrate emit sites.
4. On +30 day, Secretary flips row to `DEPRECATED`, emit hook blocks legacy name.

Deleting:
- Only after `rowid` count hits zero AND 60-day quiescence. Secretary requests Board L3 approval and records in `DNA_LOG.md`.

---

## 7. References

- `.ystar_cieu.db` — 148 distinct event_types observed 2026-04-15 (see §2)
- `scripts/k9_audit_v3.py` — W26 consumer (5 broken aliases, see §4.1)
- `scripts/forget_guard.py` — W27.1 enforcement point
- `scripts/cieu/client.py` — emit wrap site
- `governance/forget_guard_rules.yaml` — sibling rule registry
- `knowledge/secretary/sop/` — taxonomy update SOP (to be authored W27.3)
