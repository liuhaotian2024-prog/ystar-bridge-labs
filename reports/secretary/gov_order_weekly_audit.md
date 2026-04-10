# gov-order Weekly Audit Log

**Owner**: Secretary (Samantha Lin)
**Cadence**: Every Monday morning ET (per Board GOV-008 Q3 answer)
**Source files**:
- `scripts/check_intents.py` — INTENT_RECORDED events from CIEU
- `reports/board_proposed_changes/pending/*.json` — failed translations
- `scripts/check_obligations.py` — OBLIGATION_REGISTERED rows tagged `gov_order`

This log captures one entry per week. Each entry is a snapshot of how
well the natural-language → CIEU pipeline worked, what failed, and
what Secretary did about it.

## Secretary's Monday checklist

```bash
# 1. List the week's pending failures
ls reports/board_proposed_changes/pending/*.json

# 2. Pull all gov_order INTENT_RECORDED events for the week
python3.11 scripts/check_intents.py --directive BOARD-* 2>/dev/null

# 3. Pull obligations registered in the last 7 days
python3.11 scripts/check_obligations.py | head -50

# 4. For each pending file, decide: register / drop / bounce
#    (see reports/board_proposed_changes/pending/README.md)

# 5. Move processed files to reviewed/<YYYY-MM-DD>/
mkdir -p reports/board_proposed_changes/reviewed/$(date +%Y-%m-%d)
mv reports/board_proposed_changes/pending/<processed>.json \
   reports/board_proposed_changes/reviewed/$(date +%Y-%m-%d)/

# 6. Append a row to this file (template below)
```

## Weekly entry template

```markdown
### Week of YYYY-MM-DD (Monday review YYYY-MM-DD)

**Pending count at start**: N
**INTENT_RECORDED count (gov_order source)**: N
**OBLIGATION_REGISTERED count (gov_order tag)**: N
**Pass rate**: M / N (= REGISTERED / total INTENT_RECORDED)

**Disposition of pending files**:
- registered: K — list
- dropped: K — list with drop_reason
- bounced to Board: K — list with reason

**Provider failure breakdown**:
- anthropic 401: 0
- anthropic 429: 0
- openai timeout: 0
- ollama unreachable: 0
- json parse: 0
- non_task: 0
- validator schema: 0

**Notable misinterpretations**:
- (e.g., "明早" interpreted as 7am instead of 9am — Board prefers 9am)

**Recommendations to CTO** (if any):
- (e.g., prompt should mention "明早" defaults to 9am ET)
```

## Entries

(Empty until first Monday after gov_order ships. First entry expected
2026-04-13 if gov-order is in production by then.)

---

**Why this log exists**: GOV-008 Q3 — Board confirmed Secretary
handles weekly Monday audit of `pending/`. This file is the canonical
audit log so future readers can trace whether the gov_order pipeline
is healthy without re-running the analysis.

**See also**:
- `reports/board_proposed_changes/pending/README.md` — pending file schema
- `reports/cto/gov_order_pipeline.md` — gov_order design doc
- `scripts/gov_order.py` / `scripts/gov_order_undo.py` — the tools
- `agents/Secretary.md` — the GOV-008 weekly audit duty in岗位宪法
