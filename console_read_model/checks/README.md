# Local Safety Checks

`run_local_safety_checks.py` is a single safe local command for the Y* company
read-model stack.

It runs the existing curated-source checks:

- runtime artifact path-only manifest builder
- team console snapshot generator
- generated JSON validity checks
- static team read model validator
- lightweight capsule schema-alignment checks through the static validator
- team console `validate-local`
- read-only CLI smoke checks for quarantine, evidence review, governance bridge,
  Pre-U governance, and sources

Run from the repository root:

```bash
python3 console_read_model/checks/run_local_safety_checks.py
```

This is not CI wiring, not runtime execution, not artifact mining, not cleanup,
and not DB/log/report parsing. It is a local confidence pass for the safe
read-model layer.

The wrapper also runs the Labs-Gov dry-run bridge. That bridge calls only the
Y-star-gov hook contract dry-run CLI and records a generated decision snapshot;
it does not execute actions or write CIEU.

The wrapper also runs the multi-role Pre-U generator flow. That flow generates
dry-run packets for Aiden, Ethan, and Samantha, converts them to hook envelopes,
and calls Y-star-gov dry-run judgment without executing actions.

The wrapper validates generated labs runtime acceptance reports and exposes a
`labs-acceptance` CLI smoke check. It does not call the full acceptance runner,
which avoids recursive acceptance-wrapper execution.

The wrapper also validates generated cross-repo alignment reports and exposes a
`cross-repo-alignment` CLI smoke check. It does not call the full cross-repo
alignment acceptance runner, which avoids long recursive cross-repo checks.

The wrapper builds the live-readiness gate report, validates its generated
JSON, and exposes a `live-readiness` CLI smoke check. This is deliberately
non-recursive and does not enable live execution.

Optional flags:

- `--no-rebuild`: validate existing generated files without rebuilding them.
- `--verbose`: print full command output.
- `--continue-on-failure`: run every check before reporting failure.
