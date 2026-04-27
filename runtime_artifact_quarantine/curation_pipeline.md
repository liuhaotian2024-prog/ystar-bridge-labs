# Curation Pipeline

Future pipeline:

```text
runtime artifact
→ quarantine manifest
→ class/risk assignment
→ backlog disposition routing
→ adapter eligibility
→ bounded extraction candidate
→ pending review queue entry
→ structural evidence scoring
→ undecided review decision stub
→ not-approved hint routing
→ human/reviewer inspection
→ CIEU evidence envelope
→ human/reviewer acceptance
→ curated memory candidate
→ brain writeback candidate
→ console read model update
```

No artifact becomes canonical memory without review.

Raw artifacts may be evidence sources. They are not memory, governance truth, or
brain writeback input until curated through an explicit adapter and review path.

Safe mining v0 stops at bounded extraction candidates for approved Markdown
reports. It does not create CIEU evidence envelopes or memory/writeback records.

Review queue v0 converts candidates into `pending_review` entries only. It does
not approve, ingest, or write anything to memory, brain, or CIEU.

Backlog disposition v0 covers the whole dirty artifact manifest with routing
metadata only. It prepares future adapter/evidence-scoring fields but does not
perform semantic truth scoring or ingestion.

Evidence review v0 estimates structural reuse readiness and creates undecided
decision stubs plus not-approved hint routes. It does not validate truth,
approve candidates, write CIEU records, migrate memory, or write brain state.
