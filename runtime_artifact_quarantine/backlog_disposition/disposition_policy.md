# Disposition Policy

Backlog disposition applies the seven-layer safety method to the dirty artifact backlog:

1. Quarantine: dirty files do not directly enter the system.
2. Safe mining: only approved Markdown reports may be bounded-read by safe adapters.
3. Candidate only: candidate assets are not facts and not memory.
4. Review queue: mined candidates remain `pending_review` and `not_ingested`.
5. Evidence scoring: disposition prepares `not_started` fields only.
6. Schema validation: future approvals must match architecture schemas.
7. No direct brain writeback: no artifact may directly write brain, memory, policy, or CIEU.

The disposition builder must not open raw artifact contents. It reads only curated generated indexes and produces routing decisions.
