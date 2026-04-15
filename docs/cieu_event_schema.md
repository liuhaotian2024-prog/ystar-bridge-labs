# CIEU Event Schema — Telegram-Pushed Event Types

**Owner**: Samantha Lin (Secretary)
**Established**: 2026-04-15 (Board directive — close auto-trigger gap on
telegram_notify)
**Referenced by**: `scripts/cieu_event_watcher.py`, `scripts/telegram_notify.py`

---

## Purpose

Declarative contract between agents (emitters) and the Secretary-owned
watcher daemon. Any row written to `cieu_events` with an `event_type` in this
document is automatically pushed to the Board Telegram channel within ~60s by
`cieu_event_watcher.py` (cron every minute).

If you emit one of these event_types outside the contract below, you will
wake the Board. Don't.

---

## Pushed event_types

### 1. `CRITICAL_INSIGHT`

| Field | Value |
|---|---|
| When to emit | Agent (during work) uncovers a non-obvious truth that changes a strategic assumption or reveals a hidden failure mode. Must be surfaced to Board within the day. |
| Who may emit | CEO, CTO, CMO, CSO, CFO, any engineer sub-agent, Secretary. |
| Must NOT emit for | Routine progress, task completion, "I learned a small thing", debugging breadcrumbs. Use agent-local lessons dir instead. |
| Required CIEU fields | `event_type='CRITICAL_INSIGHT'`, `agent_id`, `task_description` (the insight headline, ≤140 chars), `violations` optional (JSON context). |
| Telegram surface | 💡 icon, title = `task_description`, detail = agent_id + file_path + command + violations. |
| Frequency budget | ≤ 3 / day across entire team. If you're about to be the 4th, downgrade to lesson file. |

**Example headline**: `"Scenario C (CROBA inject) is the real USP — Scenario A is break-glass audit only"`

---

### 2. `MAJOR_INCIDENT`

| Field | Value |
|---|---|
| When to emit | System failure with data-loss risk, governance breach, production customer impact, financial misstep, or any condition requiring Board decision to unblock. |
| Who may emit | Any agent detecting the condition. Prefer earliest detector (don't wait to escalate up the C-suite chain). |
| Must NOT emit for | Expected test failures, recoverable transient errors, anything auto-healed within the same session. |
| Required CIEU fields | `event_type='MAJOR_INCIDENT'`, `agent_id`, `task_description` (what broke, ≤140 chars), `file_path` or `command` if applicable, `violations` JSON with `{severity, blast_radius, rollback_available}`. |
| Telegram surface | 🚨 icon, immediate push, no batching. |
| Frequency budget | Unbounded (by definition these are rare). If >2 in a single day, CEO runs post-mortem. |

**Example headline**: `"CIEU DB wal corruption — 47 events lost since 02:14 UTC, no backup"`

---

### 3. `MILESTONE_SHIPPED` *(already wired pre-2026-04-15, not watcher-pushed)*

Documented here for completeness. MILESTONE_SHIPPED is emitted inline by the
shipping agent via `telegram_notify.send_event(...)` directly. The watcher
**does not** re-push these to avoid duplicate Board messages.

---

## Non-pushed reference types (read-only via `gov_report`)

- `CIEU_WATCHER_TICK` — self-emitted by `cieu_event_watcher.py` every cron tick
  for audit. Do not filter on these for dashboards; they are noisy by design.
- `TELEGRAM_*` — emitted by `telegram_notify._emit_cieu()` as a send-receipt.
  One per send attempt (success or fail).

---

## Emitter-side discipline (Iron Rule 1.6)

When an agent inserts one of the pushed event_types, they MUST also:

1. Populate `task_description` with a human-readable ≤140-char headline (the
   watcher uses this as the Telegram title).
2. Populate `agent_id` with their canonical role (`samantha-secretary`,
   `ethan-cto`, etc.), never `"unknown"`.
3. For `MAJOR_INCIDENT`: include `violations` JSON with severity assessment.

Violations of this discipline produce low-quality Board pushes and will be
flagged by `MATURITY_TAG_MISSING` sweep (AMENDMENT-019).

---

## Change log

| Date | Change | Author |
|---|---|---|
| 2026-04-15 | Initial — wire watcher for CRITICAL_INSIGHT + MAJOR_INCIDENT | Samantha Lin |
