# Tool Policy

Allowed:

- Run `git status --short` to read path/status information.
- Inspect path strings, file extensions, and `os.stat` metadata.
- Write generated manifest and summary files under
  `runtime_artifact_quarantine/generated/`.

Forbidden:

- Opening DB/WAL/SHM/log contents.
- Reading daemon state contents.
- Reading active-agent marker contents.
- Reading raw runtime report contents.
- Computing checksums.
- Moving, deleting, renaming, archiving, or cleaning artifacts.
- Calling project runtime scripts.
