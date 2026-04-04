# Show HN: Y*gov — Runtime Governance for Multi-Agent AI Systems

## Title
Show HN: Y*gov – Make AI agents faster and safer by enforcing rules in code, not prompts

## Post Body

Hey HN,

I built Y*gov because I kept seeing the same pattern: teams ship multi-agent systems where the only "governance" is a paragraph in the system prompt. Then an agent reads production credentials, a subagent inherits full permissions, or someone discovers fabricated audit records in a demo — and it's too late.

**The core insight:** Rules in prompts are suggestions. Y*gov makes them laws.

Y*gov is a runtime enforcement layer that intercepts every tool call before execution (0.042ms overhead), blocks violations deterministically, and writes tamper-evident audit records that agents cannot forge.

**What you get:**
- `check()` in 0.042ms — 2.4x faster than Microsoft AGT benchmark
- Zero external dependencies, no LLM in the enforcement layer (cannot be prompt-injected)
- Tamper-evident CIEU audit chain (SHA-256 linked records)
- Delegation chain enforcement (child permissions ⊆ parent permissions)
- Obligation tracking with action-triggered omission detection

**The surprising part:** governance makes agents *faster*, not slower.

In a controlled experiment:
- Tool calls: -62% (117 → 45)
- Token consumption: -16% (186K → 156K)
- Runtime: -35% (9m19s → 6m4s)

How? Because enforcement stops agents from looping on blocked tasks, exploring dead-end paths, and re-prompting for permissions they'll never get.

**Install in 10 seconds:**
```bash
pip install ystar
ystar hook-install
ystar doctor
```

Then trigger a dangerous command in Claude Code:
```
[Y*gov] DENY — /etc is not allowed in command
CIEU record written: seq=1774555489773712
```

GitHub: https://github.com/liuhaotian2024-prog/Y-star-gov
Docs: README has the full benchmark, threat model, and architecture

This is v0.48.0 (MIT license). 559 tests passing. Zero supply chain risk.

**I'd love feedback on:**
1. Does this model of "governance as enforcement layer" resonate with your multi-agent systems?
2. What governance problems do you hit that this *doesn't* solve?
3. If you try it, what breaks? (Installation is the #1 priority to fix)

Built by one person + 4 AI agents (all governed by Y*gov itself — dogfooding since Day 1).

---

## Tags
#ai-safety #multi-agent-systems #llm-governance #runtime-enforcement #agent-frameworks

## Timing
Post during HN peak hours:
- Tuesday-Thursday
- 9-11 AM PT or 2-4 PM PT

## Follow-up Response Template

Thanks for trying it! If you hit installation issues:
1. Run `ystar doctor` and paste the output
2. Check Python >=3.11
3. Windows users: Git Bash is required for hook installation

For the "why not just use prompts" question:
→ Point to EXP-001 in README (agent fabricated audit record in blog post)
→ Prompts are bypassed by: prompt injection, jailbreaking, multi-turn manipulation, or just... forgetting

For the performance numbers:
→ Full methodology in reports/EXP-001_baseline.md
→ Same agent, same task, A/B test with/without Y*gov governance

## Soft Launch Checklist Before Posting

- [ ] PyPI 0.48.0 published (wait for Board approval)
- [ ] GitHub release v0.48.0 created with CHANGELOG
- [ ] README badges updated (✅ 559 tests)
- [ ] Installation tested on clean machine (macOS + Windows)
- [ ] `ystar demo` works for first-time users
- [ ] All links in README are correct
- [ ] CIEU audit logs are not exposed in public examples (privacy)
