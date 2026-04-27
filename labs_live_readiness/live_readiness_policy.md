# Live Readiness Policy

## Purpose

Live readiness is a gate, not an activation mechanism. It records what is ready
in dry-run governance and what must exist before any minimal live governed loop.

## Allowed Inputs

The builder may read curated/generated JSON from:

- cross-repo alignment
- labs runtime acceptance
- Labs-Gov bridge
- multi-role Pre-U governance
- runtime artifact disposition
- evidence review and hint routing
- console read model
- role brain capsule JSON references

## Forbidden Behavior

The builder must not execute actions, run hooks, write CIEU, ingest memory,
write brain capsules, approve candidates, open DB/WAL/SHM files, parse logs, or
read active-agent/daemon state.

## Required Output Stance

Until explicit live boundary harnesses exist, all live write/execution flags
must remain false and `minimal_live_loop_status` must remain
`blocked_until_required_gates_exist`.

