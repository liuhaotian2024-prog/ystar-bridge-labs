# Value Hypotheses

| Artifact area | Why valuable | Why risky | Future adapter path | Direct brain ingestion? |
| --- | --- | --- | --- | --- |
| DBs | May contain CIEU events, brain state, memory graph, writeback state. | Live/sensitive structured stores; unsafe to open casually. | Readonly DB adapter with schema and review. | No. |
| WAL/SHM | May indicate live or recent DB activity. | Coupled to DB runtime state; touching may be harmful. | Metadata-only live-state signal. | No. |
| Logs | May contain daemon health, dialogue contracts, drift signals, dream cycles. | Large, noisy, private, and operationally fragile. | Bounded log summarizer. | No. |
| Dream reports | May contain consolidation insights. | Uncurated, may include speculative content. | Dream report bounded parser. | No, only after curation. |
| Escalation reports | May contain governance failures and incident evidence. | Sensitive and easy to overfit. | Escalation parser with CIEU mapping. | No. |
| Active-agent markers | May show role activity. | Ephemeral live context, not identity. | Marker summarizer. | No. |
| Pycache | Almost no semantic value. | Clutter and irrelevant binary/cache data. | Ignore/cleanup policy later. | No. |
| Backups | May preserve valuable past brain snapshots. | DB content risk and version confusion. | Backup inventory adapter first. | No. |
| Daily/drift/whitelist reports | May contain curated operational summaries. | Still needs source/risk classification. | Bounded report parser. | No, only after review. |
