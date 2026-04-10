# CFO (Marco Rivera) — sop/

Standard Operating Procedures — the operational manuals that
accumulate as this role repeats task types. SOPs are born from cases,
refined into theory, and distilled back into concrete procedures
that the next execution can follow without starting from scratch.

## What goes here

One file per task type (matches the entries in
`role_definition/task_type_map.md` and the files in `../theory/`):

```markdown
# SOP — <task type name>

## When to apply
Conditions under which this procedure is the right starting point.
Scope boundaries.

## Preconditions
What must be true before executing (data, authorizations, tool
state, upstream dependencies).

## Procedure
Concrete numbered steps. Not "consider X" but "do X, then verify
Y, then do Z." If a step is conditional, split into sub-SOPs.

## Theories invoked
References to `../theory/` entries that ground this procedure.
Why these steps in this order, not an arbitrary order.

## Known failure modes
What typically goes wrong, early warning signs, and what to do
when the warning fires.

## Exit criteria
How we know the procedure is complete. Must be concrete and
testable (per GOV-009 success_bar rules).

## Last updated / revision history
Who, when, why.
```

## How SOPs evolve

1. First execution of a task type: no SOP exists. Agent runs the
   full 12-layer framework cold, records the case in `../cases/`,
   drafts the initial SOP here.
2. Second execution: agent reads the SOP, follows it, adjusts based
   on what is different, updates the SOP if the divergence was
   systematic.
3. Third execution: SOP is now the starting point; 12-layer framework
   runs in condensed form because most of the work is captured.
4. Nth execution: SOP is the primary reference; the framework only
   re-runs in full when the situation is meaningfully new.

## Versioning

Every non-trivial revision gets a line in the revision history at
the bottom of the SOP file. SOPs can be "deprecated" by marking the
top of the file, but files are never deleted (append-only audit).

## Source

Board capability system directive (2026-04-10);
`governance/WORKING_STYLE.md` 第九条.
