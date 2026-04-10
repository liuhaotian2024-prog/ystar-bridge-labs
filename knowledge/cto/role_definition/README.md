# CTO (Ethan Wright) — role_definition/

Long-lived knowledge about **the role itself**, not about individual tasks.
This directory is built once (then updated as the role evolves) and read
whenever the agent needs to orient to its own purpose.

## What goes here

- **`world_class_standard.md`** — What does "world-class at this role"
  look like? Core competencies, evaluation criteria, behavioral signatures.
  Not our self-description; the outside world's standard.
- **`role_heroes.md`** — Who are the top-tier practitioners of this role
  (named individuals, companies, frameworks)? How do they actually work?
  What can we observe and copy, what is inimitable?
- **`task_type_map.md`** — Self-decomposition of the role into at least
  8 distinct task types, each with: description, core verbs (2-4),
  priority, frequency. This file is the **input** to the `theory/`
  directory — each task type gets one theory library file.

## How it is used

- At session boot, the agent reads `task_type_map.md` to know what
  kinds of work its role covers.
- When a new directive arrives, the agent matches it to a task type
  from this map and pulls the matching `theory/<task_type>.md`.
- The `world_class_standard.md` and `role_heroes.md` files are the
  aspiration reference — consulted when the agent is deciding whether
  its own work meets the bar.

## Owned by

The role itself. The current holder of this role drafts, revises, and
owns these files. When the role transitions, the files transition
with it.

## Source

Board capability system directive (2026-04-10). First populated per
the `role_definition/` priority of the idle learning loop defined in
`AGENTS.md` and `governance/WORKING_STYLE.md` 第九条.
