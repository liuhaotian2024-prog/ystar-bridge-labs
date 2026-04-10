# `pending/` — gov-order rejected translations

`scripts/gov_order.py` writes one JSON file here every time a Board NL
sentence makes it past LLM translation but **fails** the deterministic
validator (or fails earlier — JSON parse, LLM call, no provider). The
file is the audit trail for "Board said something we couldn't safely
turn into a CIEU obligation."

## Why this directory exists

`gov_order.py` never raises an exception to the Board. It always exits
0 with a clean message. But that means a failed translation could
disappear silently if we didn't archive it somewhere. So we archive
it here, and the Secretary picks it up on Monday.

## File format

```
YYYY-MM-DD-HHMMSS-rejected-{rule_id_or_unknown}.json
```

Schema (`version: "1.0"`):

```json
{
  "version": "1.0",
  "timestamp": "2026-04-09T22:00:00",
  "input_nl": "<the literal Board sentence>",
  "llm_provider": "anthropic" | "openai" | "ollama" | "lm_studio" | null,
  "llm_model": "<model id>" | null,
  "llm_raw_output": "<verbatim LLM string>" | null,
  "llm_parsed_dict": { /* parsed JSON if we got that far */ } | null,
  "validation_errors": ["..."],
  "suggested_manual_command": "python3.11 scripts/register_obligation.py ...",
  "review_status": "pending"
}
```

## Secretary's Monday review (per Q3 answer to GOV-008)

Every Monday, Secretary (Samantha) runs:

```bash
ls reports/board_proposed_changes/pending/*.json
```

For each file:

1. **Manual register** — if the LLM was nearly right, fix the
   `validation_errors` by hand and run the
   `suggested_manual_command` (or a corrected version of it).
   Mark `review_status: "registered"` and move the file to
   `reports/board_proposed_changes/reviewed/<YYYY-MM-DD>/`.
2. **Intentionally drop** — if the input was a non-task, a value
   statement, a question, or already covered by another obligation:
   set `review_status: "dropped"`, add a `drop_reason` field, and
   move to `reviewed/`.
3. **Bounce to Board** — if the input is genuinely ambiguous and
   Secretary cannot interpret it, set `review_status: "needs_board"`
   and surface it in the next Monday handoff. Do not delete.

The audit log is the whole point. **Never delete pending files** —
move them to `reviewed/` or escalate.

## Secretary writes a weekly summary

Each Monday Secretary appends a row to
`reports/secretary/gov_order_weekly_audit.md` with:

- count of pending files at start of week
- count registered / dropped / bounced
- count of `gov_order` `INTENT_RECORDED` events for the week
  (`scripts/check_intents.py --directive BOARD-* | grep RECORDED`)
- pass rate (= INTENT pass / total)
- any provider failures from `validation_errors`

This is the Q3 cadence Board confirmed in the GOV-008 answers.

## See also

- `scripts/gov_order.py` — the producer
- `scripts/gov_order_undo.py` — the rollback tool for already-registered obligations
- `reports/cto/gov_order_pipeline.md` — the full design doc
- `governance/WORKING_STYLE.md` 第七条 7.5 — the GOV-006 protocol that
  gov_order's `INTENT_RECORDED` writes piggyback on
