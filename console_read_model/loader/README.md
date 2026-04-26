# Team Console Snapshot Loader

This directory contains a safe static loader/generator for the curated team
console read model.

It reads only curated JSON and Markdown references from `console_read_model/`
and selected capsule index files. It must not read DBs, logs, active-agent
markers, daemon state, raw runtime reports, or `__pycache__`.

It is not runtime execution, not a frontend, not hook enforcement, not a
Y-star-gov validator implementation, and not DB ingestion.

Run from the repository root:

```bash
python3 console_read_model/loader/build_team_console_snapshot.py
```

Outputs are written under `console_read_model/generated/`.
