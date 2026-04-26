# Forbidden Direct Reads

Do not directly read:

- DB/WAL/SHM contents.
- `scripts/.logs/*`.
- Active-agent markers.
- Daemon pid/state files.
- `__pycache__`.
- Raw runtime reports in bulk.
- Backup DB contents.

Console must not read these directly. Agent brains must not ingest these
directly. Future mining requires an explicit adapter, a manifest, and CIEU-backed
review.
