# E116 Aiden Idle Continuous Learning Runtime

E116 adds a governed idle-time learning loop for Aiden. When no explicit owner/session task is active, Aiden can collect source-dated CEO, market, strategy, product, technology, governance, and failure-residual evidence, convert it into a knowledge graph delta, write a formal CIEUStore record, and only then apply the delta to the Aiden brain database.

This reuses the existing Aiden brain, E112 freshness filter, E113 CZL/no-new-wheel principle, E114 source-dated public-read evidence path, and Y-star-gov CIEUStore. It does not create a parallel memory ledger.

Key guarantees:

- Active session work preempts idle learning.
- Stale or undated evidence cannot become durable brain knowledge.
- Y-star-gov validation is required before brain graph writes.
- CIEUStore write is required before brain graph writes.
- CZL closure requires `R_t_plus_1=0`.
- No external action, customer validation, revenue, payment, live provider execution, or K9Audit write is claimed.

The runtime supports a continuous loop, but this milestone does not start a host LaunchAgent automatically. A separate host-ops activation step should make the 24h daemon visible, auditable, and reversible.
