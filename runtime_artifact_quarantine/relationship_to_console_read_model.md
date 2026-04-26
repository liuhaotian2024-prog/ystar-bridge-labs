# Relationship to Console Read Model

`console_read_model/` reads curated generated snapshots.

`runtime_artifact_quarantine/` inventories unsafe sources so they can be
classified without becoming direct console inputs.

Future console may show counts/classes from quarantine summaries, but not raw
contents. Generated snapshots should not include DB/log direct reads.

The console remains a safe read layer. Runtime artifacts remain quarantine
inputs until adapters and review convert selected evidence into curated data.
