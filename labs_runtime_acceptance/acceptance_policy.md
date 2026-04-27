# Labs Runtime Acceptance Policy

## Purpose

The acceptance pack proves the current labs runtime governance stack can run
end-to-end in deterministic dry-run mode.

## Allowed Inputs

The runner may invoke existing safe builders and validators that operate on:

- curated quarantine generated JSON
- safe-mining generated JSON
- review queue generated JSON
- backlog disposition generated JSON
- evidence review generated JSON
- Labs-Gov bridge generated JSON
- Pre-U governance generated JSON
- console read-model generated JSON
- role brain capsule JSON references

## Forbidden Inputs

The runner must not open DB, WAL, SHM, raw logs, active-agent marker contents,
daemon state, or dirty raw runtime artifacts.

## Non-Execution Boundary

The runner may call the Y-star-gov hook dry-run CLI through existing bridge
tools. It must not execute selected actions, write CIEU records, mutate
brain/memory, or approve candidates.

## Local Safety Wrapper

The local safety wrapper validates acceptance outputs but does not call the
full acceptance runner. This avoids acceptance-runner recursion while keeping
the acceptance summary visible to normal local checks.

