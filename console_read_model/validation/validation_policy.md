# Validation Policy

The static validator checks curated console and capsule read-model structure.

It checks:

- JSON syntax for curated JSON files.
- Required console read-model files.
- Required capsule files for Aiden, Ethan, and Samantha.
- Shared schema presence.
- Required agent coverage.
- Loader and generated snapshot file presence.
- CLI file presence.
- Generated JSON validity.
- Generated quarantine summary presence and required fields.
- Generated team snapshot contains `quarantine_summary`.
- Lightweight capsule schema alignment for agent brain profiles and ref files.
- Ethan execution channels keep execution substrates separate from identity.
- Aiden Pre-U packet schema contains core Y*/Xt/U/Yt+1/Rt+1/CIEU concepts.
- Generated snapshot coverage for Aiden, Ethan, and Samantha.
- Generated manifest source safety.
- Safety boundary between curated read model and unsafe runtime files.
- `safe_to_read` does not list direct DB/log/runtime source patterns.
- `unsafe_to_read_directly` lists DB/log/runtime categories.

It does not check:

- DB contents.
- Runtime truth.
- Live daemon state.
- Hook behavior.
- CIEU actual event correctness.
- Y-star-gov validator implementation.
- Frontend rendering.
- Semantic truth of every Markdown claim.
- Runtime freshness of generated snapshots.
- CLI command behavior beyond static file presence.
- Runtime artifact contents behind quarantine paths.
- Full JSON Schema validation through third-party libraries.
- Runtime cognition or executable brain behavior.

The validator should remain read-only and standard-library-only until the schema
stabilizes.
