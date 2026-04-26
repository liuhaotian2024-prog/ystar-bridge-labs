# Static Team Read Model Validator

This directory contains a static validator for curated console and capsule
read-model files.

It validates only JSON, docs, and index references. It must not open DBs,
WAL/SHM files, logs, active-agent markers, daemon state, runtime state, or
`__pycache__`.

This is not runtime execution, not a frontend, not hook enforcement, and not a
Y-star-gov validator implementation. It is a safety layer before future console
or runtime consumers read the model.

Run from the repository root:

```bash
python3 console_read_model/validation/validate_team_read_model.py
```

The script prints a concise PASS/FAIL report and writes no output files by
default.
