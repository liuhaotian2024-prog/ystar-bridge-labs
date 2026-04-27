# CIEU Runtime Event Policy

The CIEU runtime event boundary is a schema and fixture layer only.

Allowed:

- define future event envelope fields
- generate dry-run sample events
- validate disabled write policy
- expose read-only console summaries

Forbidden:

- writing CIEU records
- opening or querying databases
- executing actions
- reading logs or active-agent markers
- writing brain or memory
- approving candidates
- treating structural fixtures as semantic truth

All generated events must keep `dry_run_only: true` and
`persistence_enabled: false`.
