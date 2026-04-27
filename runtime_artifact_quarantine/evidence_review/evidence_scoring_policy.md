# Evidence Scoring Policy

Evidence scoring v0 is structural only.

Allowed scoring signals:

- Candidate exists in the safe-mining index.
- Candidate is linked to a pending review queue entry.
- Candidate has a bounded snippet.
- Candidate has captured headings.
- Candidate has default intended-use suggestions.
- Candidate disposition is `safe_mined_to_review_queue`.
- Candidate artifact class is an approved report-like class.

Forbidden scoring claims:

- Semantic truth validation.
- Source correctness.
- Memory correctness.
- Governance approval.
- Brain writeback readiness.
- CIEU write readiness.

No score may approve a candidate automatically. Every generated decision remains `undecided`.
