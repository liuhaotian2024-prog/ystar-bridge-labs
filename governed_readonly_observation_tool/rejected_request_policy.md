# Rejected Request Policy

The wrapper rejects an invocation before reading any requested source when:

- A requested source is not listed in the allowed source registry.
- A registry entry is not marked safe to read.
- A registry entry requires network or credentials.
- A source path is absolute, escapes the repository root, has an unsafe suffix, or points to an excluded runtime/state area.
- A source is larger than its registry `max_bytes`.
- The invocation asks for live action, external action, brain writeback, memory ingestion, or CIEU persistence.

Rejected invocations may be recorded as generated dry-run traces, but no unsafe source is read.

