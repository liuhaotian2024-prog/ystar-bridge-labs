# Future Adapter Plan

| Adapter | Input class | Output | Safety guard | Status |
| --- | --- | --- | --- | --- |
| DB metadata adapter | DB_CORE, BACKUP_DB | Size/schema metadata without content extraction. | Readonly mode, no writes, no WAL mutation. | Not implemented. |
| CIEU readonly DB adapter | DB_CORE | Structured CIEU event candidates. | Explicit schema, readonly connection, CIEU review. | Not implemented. |
| Dream report bounded parser | DREAM_REPORT | Dream insight candidates. | File size limits and no bulk traversal. | Not implemented. |
| Escalation report parser | ESCALATION_REPORT | Governance incident candidates. | Bounded parse and reviewer queue. | Not implemented. |
| Drift report parser | DRIFT_REPORT | Drift signal summaries. | Bounded parse and source labeling. | Not implemented. |
| Log summarizer | LOG_RUNTIME | Health/drift/daemon summary candidates. | Size/time bounds, no raw log ingestion. | Not implemented. |
| Active-agent marker summarizer | ACTIVE_AGENT_MARKER | Role activity metadata. | Path/mtime first, content only by explicit adapter. | Not implemented. |
| Backup DB inventory adapter | BACKUP_DB | Backup inventory and retention candidates. | No DB open in first pass. | Not implemented. |
| Quarantine-to-curated-memory review queue | All eligible classes | Reviewed memory candidates. | Human/reviewer acceptance and CIEU envelope. | Not implemented. |
