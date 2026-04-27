# Discovery Policy

Discovery is bounded repository archaeology.

Allowed:

- scan approved repository roots read-only
- inspect source, docs, schema, and config-like text files
- classify by file path, file name, and bounded snippets
- generate inventory summaries under this directory

Forbidden:

- executing discovered tools
- importing discovered modules dynamically
- reading database, sidecar, log, active marker, backup, cache, or raw report contents
- writing outside `ystar-company`
- network access
- semantic truth scoring
