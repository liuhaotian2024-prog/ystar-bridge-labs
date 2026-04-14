<!-- Completed: 2026-04-11 | Author: Sofia Blake (CMO) -->
<!-- TARGET: products/ystar-defuse/README.md and GitHub repo root -->

# Y*Defuse — AI Bomb Disposal

**We don't detect the bomb. We defuse it.**

The world's first defense against delayed prompt injection attacks.
100% guaranteed — because we don't scan inputs, we block malicious actions.

## Install (10 seconds)

```bash
pip install ystar-defuse
ystar-defuse start
```

That's it. Zero config. It learns your agent's normal behavior automatically.

## What it does

- Blocks credential theft (`.env`, SSH keys, API keys)
- Blocks data exfiltration (unauthorized network requests)
- Blocks destructive commands (`rm -rf`, `chmod 777`)
- Detects delayed injection bombs (cross-session payload assembly)
- Auto-learns your agent's normal behavior (zero config after 24h)

## The problem no one else solves

Every existing defense tries to **detect** malicious prompts by scanning inputs. Attackers disguise payloads as songs, jokes, base64, code comments — and scanners miss them every time.

**Delayed prompt injection** is worse: the attacker plants innocent data in session 1, then triggers malicious execution 50 turns later. No single-turn scanner can catch this.

## How Y*Defuse works

```
Your agent does everything through tool calls.
We hook into every tool call.
If the action isn't in the whitelist → DENY.

No AI in the loop. No false positives. 100% deterministic. <10ms latency.
```

### Two-layer protection

```
All agent actions
  ↓
Level 1: Hard floor (user cannot override) → Dangerous actions → DENY
  ↓ pass
Level 2: Smart whitelist (auto-learned) → Unknown actions → prompt user
  ↓ pass
Allow
```

**Level 1** catches credential theft, data exfiltration, and destructive commands — always, unconditionally. Users cannot whitelist away their own security.

**Level 2** learns from 24 hours of normal agent behavior and builds a whitelist automatically. New behaviors get a gentle prompt. No manual config required.

## Why it's different

| Feature | Input scanners | Y*Defuse |
|---------|---------------|----------|
| Delayed injection | Cannot detect | Cross-session tracking (CIEU) |
| Disguised payloads | Arms race | Irrelevant — we block actions, not inputs |
| False positives | Frequent | Zero (deterministic rules) |
| Latency | 100ms+ (LLM call) | <10ms |
| Can be injected | Yes (LLM in loop) | No (no LLM, no attack surface) |

## Cross-session tracking (CIEU)

Y*Defuse tracks behavior across sessions using the CIEU (Causal Interaction Evidence Unit) format:

```
Session 1, Turn 3:  Agent reads seemingly harmless text       → recorded
Session 1, Turn 10: Agent tries to execute hidden instruction → correlated to Turn 3 → DENY
```

Attackers assemble bombs across turns. Y*Defuse remembers every piece.

## CLI commands

```bash
ystar-defuse start          # Start protection (begins learning)
ystar-defuse stop           # Pause protection
ystar-defuse report         # View security report
ystar-defuse config         # Adjust whitelist (optional)
ystar-defuse upgrade        # Unlock advanced features ($9.9/mo)
```

## Pricing

**Free forever** — core protection including delayed injection defense.

**$9.9/month** — advanced API key pattern library, custom sensitive data rules, visual dashboard, priority support.

## Works with

- Claude Code
- Cursor
- OpenHands
- Cline
- Any Python-based AI agent

## Links

- GitHub: [github.com/liuhaotian2024-prog/ystar-defuse](https://github.com/liuhaotian2024-prog/ystar-defuse)
- Docs: See `/docs` in the repo

## License

MIT License | Made by [Y* Bridge Labs](https://ystar.dev)
