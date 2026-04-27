# Open Gaps

- Static validator only.
- No JSON Schema validation library used.
- No live runtime validation.
- No DB-safe adapter.
- No hook/Y-star-gov integration.
- No frontend.
- No automatic report artifact.
- No CI wiring yet.
- Generated snapshots are static and not live runtime truth.
- CLI behavior is smoke-tested manually, not deeply validated by the static validator.
- Quarantine validation checks summary wiring only, not artifact contents or mining correctness.
- Capsule schema alignment is lightweight and does not use a full JSON Schema engine.
- Aiden's older v0 profile still lacks the newer recommended `role_specific_focus` field.
