# Show HN: Y*Defuse - We don't detect the bomb, we defuse it

I built Y*Defuse after realizing that every existing prompt injection defense is playing the wrong game.

Everyone's trying to detect malicious prompts by scanning inputs. Problem: attackers can always disguise their payloads as songs, jokes, or base64. Traditional defenses are an arms race we can't win.

Y*Defuse takes a different approach: we don't care what the input says. We only enforce what actions your AI agent can execute.

How it works:
- Hook into every tool call before execution
- Block anything not in the auto-learned whitelist
- Hard rules (Level 1) that users cannot override: .env files, SSH keys, rm -rf commands
- Smart whitelist (Level 2) learned from 24h of normal agent behavior

Install takes 10 seconds:
```bash
pip install ystar-defuse
ystar-defuse start
```

The killer feature: delayed injection detection. Attackers plant innocent-looking data in session 1, then trigger malicious execution 50 turns later. Y*Defuse tracks cross-session behavior chains (CIEU format) - when session 50 tries to execute that planted payload, we correlate it back to session 1 and deny it.

No AI in the loop. No false positives. 100% deterministic. Latency under 10ms.

Core protection is free forever. We're giving away the solution to delayed prompt injection because we want CIEU to become the standard audit format.

Built this for Claude Code initially, but the enforcement engine works with any Python-based agent. Would love feedback from the HN community - especially if you've seen prompt injection attacks in production.

GitHub: https://github.com/liuhaotian2024-prog/ystar-defuse
Docs: Full README with attack examples and performance benchmarks

---
## Submission Notes
- Title: Show HN: Y*Defuse - We don't detect the bomb, we defuse it
- URL: https://github.com/liuhaotian2024-prog/ystar-defuse
- Best posting time: Tuesday 10:00-11:00 AM EST (HN traffic peak, technical audience most active, avoids Monday noise and Friday dropoff)
- Backup time: Wednesday 9:00-10:00 AM EST if Tuesday slot is too competitive
