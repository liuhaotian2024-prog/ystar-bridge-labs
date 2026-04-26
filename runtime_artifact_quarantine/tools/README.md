# Runtime Artifact Manifest Tool

`build_runtime_artifact_manifest.py` builds a path-level manifest of dirty
runtime-like artifacts.

It reads `git status --short` output, classifies paths, and records file
metadata such as extension and size. It does not open DBs, logs, active-agent
markers, daemon state, or reports.

Generated outputs are written under `runtime_artifact_quarantine/generated/`.
