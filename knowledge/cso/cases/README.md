# CSO (Zara Johnson) — cases/

Case history: concrete past executions in this role that the agent
learned from. **Not a scratchpad** — cases are added after execution,
as a deliberate distillation, not during.

## What goes here

One file per case, filename: `YYYY-MM-DD-<short_slug>.md`.

Each file contains:

```markdown
## Context (Xt)
What was the situation, what was the directive, what were the
constraints.

## Decision pattern
What decision shape did we apply? Not "what did we do" (that is the
execution record) but "what pattern guided what we did." Patterns
are reusable; events are not.

## What worked
Behaviors, judgments, tools that produced the good parts of the
outcome.

## What did not work
The specific failure modes that were surfaced. Be concrete — vague
"we could have done better" is not learning.

## Theory connection
Which entries in `../theory/` framed this case? If none: flag it as
a gap and write to `../gaps/` so the next idle cycle can build the
theory.

## Transferable lesson
One sentence. What would we tell our next-session self about this
class of situation?
```

## How it is used

- When a new directive in a similar shape arrives, the agent greps
  `cases/` to see if we've been here before
- Pattern extraction > event replay: the agent pulls the decision
  pattern, not the literal text
- Gaps surfaced by cases feed the theory-library-building priority
  of the idle learning loop

## Difference from `gaps/`

Cases are **executed**. Gaps are **simulated but not yet closed**.
A case has an outcome to reflect on; a gap is a known unknown the
agent noticed but has not worked through yet.

## Source

Board capability system directive (2026-04-10); distillation
protocol from `governance/WORKING_STYLE.md` 第七条 and 第九条.
