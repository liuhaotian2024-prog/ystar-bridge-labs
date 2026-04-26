# Agent Brain Capsule Schema

This directory defines the shared schema/reference standard for per-agent brain
capsules.

It is based on the existing Aiden-CEO, Ethan-CTO, and Samantha-Secretary
reference capsules. It is not runtime implementation, does not open DBs, does
not move memory, and does not create new agents.

Purpose:

- Prevent future capsule drift.
- Keep per-agent capsules consistent without copying Aiden/Ethan/Samantha by hand.
- Preserve the boundary between persistent role-brain identity and execution tools.
- Provide a stable reference for future static validation.

A per-agent brain capsule is the persistent identity/read-model for an agent.
Tool sessions are execution substrates, not identity owners. CIEU evidence and
curated memory nourish the persistent brain.
