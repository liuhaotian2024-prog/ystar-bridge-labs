# Hook Gate Policy

The hook should remain thin. It should gate action, not imagine action.

Future hook responsibilities:

- Check whether the action risk tier requires a Pre-U packet.
- Locate the packet reference for the requested action.
- Call a Y-star-gov packet validator.
- Enforce the validator result.
- Emit or link a pre-action CIEU event.
- Block or escalate when a required packet is missing or invalid.

The hook must not:

- Generate counterfactual candidates.
- Perform complex reasoning.
- Inspect DB contents.
- Replace Y-star-gov validation.
- Treat speculative packet content as actual outcome evidence.

## Risk Tiers

| Tier | Action class | Packet policy | Expected hook behavior |
| --- | --- | --- | --- |
| Tier 0 | Trivial read-only action. | Packet optional. | Allow if normal governance allows. |
| Tier 1 | Documentation/index update. | Lightweight packet recommended. | Allow or warn depending on local policy and packet availability. |
| Tier 2 | Source code modification. | Packet required. | Deny or require revision if packet missing/invalid. |
| Tier 3 | Governance, hook, runtime script, scheduler, or enforcement change. | Packet required plus escalation. | Require validator approval and escalation path. |
| Tier 4 | DB/WAL/SHM/log/active-agent state mutation. | Packet required plus hard review; usually deny unless explicitly authorized. | Deny by default or require explicit authorization and validator approval. |

Hook output should remain a governance decision, not a cognitive essay. The
packet can hold the reasoning; the hook should enforce the boundary.
