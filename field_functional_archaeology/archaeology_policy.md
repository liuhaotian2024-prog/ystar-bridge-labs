# Archaeology Policy

- Search safe source, schema, and documentation files before creating new design.
- Scan only explicitly allowed repositories and optional roots that exist.
- Exclude runtime stores, logs, active-agent markers, report runtime dumps, caches,
  virtual environments, and database-shaped files.
- Store only bounded metadata and snippets no longer than 240 characters.
- Classify old assets into reuse, wrap, rewrite, concept-reference, or do-not-absorb
  decisions using deterministic lexical rules.
- Keep all live action, external action, persistence, writeback, ingestion, and
  network flags disabled.

