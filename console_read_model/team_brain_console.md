# Team Brain Console v0

## Current Team Brain Status

The current team brain state is reference-ready, not runtime-ready. The system
has curated architecture indexes, shared Agent Brain Capsule schema, and
per-agent capsules for three evidenced agents/functions.

Known active/reference agents:

- `Aiden-CEO`: orchestration, mission alignment, Aiden brain chain, and Pre-U
  Counterfactual Packet reference path.
- `Ethan-CTO`: technical architecture, implementation reasoning, and execution
  channel boundary.
- `Samantha-Secretary`: memory continuity, curation, handoff, and secretary
  context.

## Shared Schema Status

`agent_brains/schema/` defines the shared capsule structure, required files,
reference-file schema, execution-channel schema, Pre-U packet profile schema,
and static validation policy. It is reference-only; no static validator script
exists yet.

## Aiden Chain Status

Aiden has the most complete chain:

- Base brain capsule.
- Pre-U Counterfactual Packet reference.
- Boundary alignment between labs / Y-star-gov / hook / CIEU / brain.
- Chain review and next runtime steps.

## Ethan Execution-Channel Status

Ethan has a base capsule plus explicit embodiment boundary:

- Ethan persists as a role-brain in `ystar-company`.
- Codex / Claude Code / shell / GitHub are execution substrates.
- Tool sessions do not own Ethan's identity, memory, or authority.
- Execution evidence must return through report/CIEU/curated memory pathways.

## Samantha Continuity / Secretary Status

Samantha has a base continuity-focused capsule:

- Memory continuity.
- Session handoff.
- Local secretary context.
- Report and memory hygiene.

Samantha does not yet have a Pre-U packet variant or executable curation workflow
validated here.

## Y-star-gov Validator Interface Reference

The Y-star-gov Pre-U packet validator interface is an external governance spec:

`/Users/haotianliu/.openclaw/workspace/Y-star-gov/docs/pre_u_packet_validator/`

Y-star-gov judges. It does not generate labs-side packets or own Aiden/Ethan/
Samantha brain identity.

## Ready for Future UI

- Curated agent cards.
- Team capability matrix.
- Safe data source list.
- Governance link summary.
- Runtime readiness summary.
- Open gaps list.

## Not Ready

- Frontend UI.
- Live team-state refresh.
- Static capsule validator script.
- Runtime packet generator.
- Hook enforcement.
- CIEU prediction-delta schema.
- DB-safe query adapter.

## Must Never Be Read Directly by Console

- DB/WAL/SHM files.
- Logs.
- Active-agent markers.
- Daemon state.
- `__pycache__`.
- Raw runtime state.

Future console should read curated indexes, not raw operational substrate.
