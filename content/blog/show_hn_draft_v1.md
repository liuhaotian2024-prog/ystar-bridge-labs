<!-- L: L2-content-external -->
<!-- Author: Sofia Blake (CMO, acting), Y* Bridge Labs -->
<!-- Date: 2026-04-13 | Target: Hacker News Show HN -->

# Show HN: Y*gov — deterministic runtime governance for multi-agent systems

Every multi-agent stack in production fails the same three ways: agents drift from their role, escalate their own permissions, and fail in ways no post-hoc log can reconstruct. LangChain callbacks are advisory. NeMo and Bedrock Guardrails are single-call. None of them enforce across 40 turns of shared state.

Y\*gov installs a deterministic hook layer *below* the agent runtime. Every tool call is intercepted, matched against a per-role IntentContract, written to a causal audit store (CIEU), and either executed or hard-denied — not suggested, denied. The agent cannot bypass it because the enforcement point is not beside the loop, it's under it.

We dogfood it. Y\* Bridge Labs is one human on the Board and an 11-agent team (CEO, CTO, CMO, CSO, CFO, Secretary, 4 engineers) all governed by Y\*gov. Live numbers from our `.ystar_cieu.db` right now:

- **27,286** CIEU events across **678** sessions
- **6,579** enforcement denials + obligation violations logged, **13** distinct violation types
- **803** governance loop cycles, **0** unattended incidents

Every `A1_VIOLATION_PREVENTED` in that log is a real moment our own CEO agent tried to write code and got denied by the kernel — because the contract says coordinators coordinate, engineers implement. The postmortem took 90 seconds because the causal chain was already there.

```bash
pip install ystar
ystar hook-install
ystar doctor
```

Local SQLite. No egress. MIT. Whitepaper + architecture diagram: [link to whitepaper].

Looking for design partners running AutoGen / CrewAI / custom swarms in production. Feedback especially welcome on the CIEU schema — we want it to be the log your auditor asks for, not the log you have to translate.
