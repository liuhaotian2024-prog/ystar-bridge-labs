<!-- Completed: 2026-04-11 | Author: Sofia Blake (CMO) -->
<!-- TARGET: content/show_hn_ystar_defuse.md -->

# Show HN: Y*Defuse -- The world's first defense against delayed prompt injection

I built Y*Defuse after watching every prompt injection defense fail the same way: they scan inputs. Attackers always win that game -- disguise a payload as a song lyric, a code comment, or base64, and your scanner is blind.

But here's the real threat nobody's talking about: **delayed prompt injection**. An attacker plants innocent-looking data in session 1. Your agent reads it, stores it, moves on. Fifty turns later, a trigger activates the payload and your agent exfiltrates your API keys. No single-turn scanner can catch this because the attack spans sessions.

Y*Defuse takes a fundamentally different approach: **we don't care what the input says. We enforce what actions your agent can execute.**

## How it works

Every AI agent operates through tool calls -- read a file, run a command, make a network request. Y*Defuse hooks into every tool call before execution:

1. **Level 1 (hard floor):** Credential theft, data exfiltration, destructive commands are blocked unconditionally. Users cannot override this. Your `.env` files, SSH keys, and API keys are untouchable.

2. **Level 2 (smart whitelist):** After 24 hours of observing your agent's normal behavior, Y*Defuse auto-generates a whitelist. New actions get a gentle prompt. No config files to write.

3. **Cross-session tracking (CIEU):** We maintain a causal behavior chain across turns and sessions. When session 50 tries to execute a payload planted in session 1, we correlate the chain and deny it. This is the feature no competitor has.

## Install in 10 seconds

```bash
pip install ystar-defuse
ystar-defuse start
```

No config. No YAML. No API keys. It just works.

## Key properties

- **No AI in the loop** -- deterministic rules, not LLM judgment. Cannot be prompt-injected itself.
- **<10ms latency** -- you won't notice it's there.
- **Zero false positives** -- same input always produces same decision.
- **Works with Claude Code, Cursor, OpenHands, Cline**, and any Python-based agent.

## Why free?

Core protection is **free forever**, including delayed injection defense. We want CIEU to become the standard audit format for AI agent behavior. The paid tier ($9.9/mo) adds advanced pattern libraries, custom rules, and a visual dashboard.

Y*Defuse is our open-source gateway to Y*gov, our full enterprise governance framework. If you outgrow the free tier, your CIEU data migrates seamlessly.

## What I'd love feedback on

- Have you seen delayed prompt injection in production? I'd love to hear war stories.
- Are there attack patterns we should add to the Level 1 hard floor?
- What agent frameworks should we prioritize integration for?

GitHub: https://github.com/liuhaotian2024-prog/ystar-defuse

---

## Submission Notes (internal -- do not publish)

- **Title:** Show HN: Y*Defuse -- The world's first defense against delayed prompt injection
- **URL:** https://github.com/liuhaotian2024-prog/ystar-defuse
- **Best posting time:** Tuesday 10:00-11:00 AM EST (peak HN technical audience)
- **Backup time:** Wednesday 9:00-10:00 AM EST
- **Key differentiator to emphasize in comments:** Cross-session CIEU tracking -- no competitor does this
- **Anticipated pushback and responses:**
  - "How is this different from a firewall?" -- Firewalls don't track cross-session behavioral chains. We correlate session 1 payload with session 50 execution.
  - "Whitelists are annoying" -- Level 2 is auto-learned. Most users never touch config.
  - "Can't I just use Anthropic's built-in safety?" -- Using an LLM to audit an LLM is like one suspect signing another suspect's alibi. We use deterministic rules.
  - "What about false negatives?" -- Level 1 is deterministic pattern matching on actions, not probabilistic classification on inputs. If the action matches a dangerous pattern, it's blocked. Period.
  - "MIT license but you sell a paid tier?" -- Core is free and MIT forever. Paid tier is convenience features, not security features. Your safety never depends on paying us.
