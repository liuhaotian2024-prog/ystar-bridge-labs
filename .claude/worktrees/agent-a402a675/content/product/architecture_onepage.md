# Y*gov Architecture Overview

```
                        Human Intent (natural language)
                                  |
                                  v
  ┌─────────────────────────────────────────────────────────────┐
  │                   INTENT COMPILATION LINE                   │
  │         NL policy  ──>  IntentContract (8 dimensions)       │
  │         "Do not touch /etc"  ──>  deny: ["/etc"]            │
  └───────────────────────────┬─────────────────────────────────┘
                              |
          ┌───────────────────┼───────────────────┐
          v                   v                   v
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │   PATH  A    │   │   KERNEL     │   │   PATH  B    │
  │  Internal    │   │  Foundation  │   │  External    │
  │  Meta-Gov    │   │  Engine      │   │  Gov Loop    │
  │              │   │              │   │              │
  │ Governs the  │   │ check():     │   │ Governs AI  │
  │ governor     │   │ contract vs  │   │ agents in   │
  │ itself.      │   │ actual call. │   │ production. │
  │ Single-track │   │ Deterministic│   │ Multi-agent │
  │ fail-closed. │   │ pure function│   │ delegation. │
  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │                    GOVERNANCE SERVICES                      │
  │  Omission Engine  |  Intervention Engine  |  Causal Engine  │
  │  Obligation track |  Gate check (deny/    |  Pearl L2-3     │
  │  + escalation     |  allow/escalate)      |  do-calculus    │
  └───────────────────────────┬─────────────────────────────────┘
                              |
  ┌─────────────────────────────────────────────────────────────┐
  │                      CIEU AUDIT TRAIL                       │
  │  SQLite WAL  |  SHA-256 sealed sessions  |  FTS5 search     │
  │  Every check() writes one immutable record. Tamper-evident. │
  └───────────────────────────┬─────────────────────────────────┘
                              |
          ┌───────────────────┼───────────────────┐
          v                   v                   v
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │ Claude Code  │   │  OpenClaw    │   │  Any Python  │
  │   Adapter    │   │  Connector   │   │    Agent     │
  └──────────────┘   └──────────────┘   └──────────────┘
```

**One foundation**: Kernel engine -- deterministic `check()` with 8 constraint dimensions.
Same contract + same params = same result, every time. Zero ML in the critical path.

**Three lines**: Intent Compilation (NL to contract), Governance Services
(omission/intervention/causal), and CIEU audit trail (immutable, sealed, searchable).

**Bridge**: Adapter layer connects any AI runtime -- Claude Code hooks, OpenClaw SSE/webhook,
or raw Python `import ystar` -- to the same governance backbone.

| Metric | Value |
|---|---|
| Test coverage | 304 tests, all passing |
| CIEU audit records | 830+ in production |
| Causal reasoning | Pearl Level 2-3 (do-calculus, counterfactuals) |
| Patent filings | 3 provisional (governance loop, causal engine, omission detection) |
