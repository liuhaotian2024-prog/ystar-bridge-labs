# Y*gov Post-Launch FAQ

**Version:** 0.48.0  
**Last Updated:** 2026-04-03  
**Audience:** HN readers, first-time users, enterprise evaluators

---

## Installation & Setup

### Q: `ystar hook-install` fails with "git hooks directory not found"

**A:** This usually happens in these scenarios:

1. **Not in a git repository**
   ```bash
   git init  # Initialize git first
   ystar hook-install
   ```

2. **Windows without Git Bash**
   - Install Git for Windows: https://git-scm.com/download/win
   - Run commands in Git Bash, not PowerShell/CMD
   - Or use WSL2

3. **Permissions issue**
   ```bash
   ls -la .git/hooks/  # Check if directory exists
   chmod +x .git/hooks/  # Fix permissions (Unix)
   ```

**Diagnostic command:**
```bash
ystar doctor
```
This will identify the exact blocker.

---

### Q: Installation succeeds but `ystar doctor` shows errors

**A:** Common issues:

| Error | Cause | Fix |
|-------|-------|-----|
| `Python version 3.10` | Y*gov requires >=3.11 | Upgrade: `python --version` check |
| `AGENTS.md not found` | No governance contract | Create empty `AGENTS.md` in project root |
| `Hook not executable` | Permission issue | `chmod +x .git/hooks/pre-ystar-check` |
| `SQLite not available` | Missing system library | Install sqlite3 (usually pre-installed) |

---

### Q: Can I use Y*gov in a non-git project?

**A:** Not currently. Y*gov uses git hooks as the interception mechanism. Support for non-git projects (via direct Python API) is planned for v0.49.0.

**Workaround:** Initialize a local git repo even if you don't push to remote:
```bash
git init
ystar hook-install
```

---

## Performance & Behavior

### Q: You claim governance makes agents *faster*. How is that possible?

**A:** Enforcement prevents wasted work. In EXP-001, the ungoverned agent:
- Retried a blocked command 66 times (looping on impossible task)
- Explored 3 dead-end paths that would always be denied
- Re-prompted for permissions it would never receive

With Y*gov, the first `DENY` stops the loop immediately. The agent moves on to viable work.

**Analogy:** A fence around a cliff doesn't slow you down—it prevents you from wasting time climbing back up.

---

### Q: What is the performance overhead of `check()`?

**A:** 0.042ms per tool call (42 microseconds).

**Context:**
- Microsoft AGT benchmark: 0.1ms
- LLM-based guardrail: 200-500ms (requires API call)
- Y*gov: 2.4x faster than AGT, 10,000x faster than LLM guardrails

**Why so fast?**
- Zero LLM involvement (pure AST + rule engine)
- No network calls
- Compiled regex + path normalization cached

For a typical agent task with 50 tool calls: 50 × 0.042ms = 2.1ms total overhead.

---

### Q: Does Y*gov work with GPT-4, Gemini, or open-source models?

**A:** Yes. Y*gov is **model-agnostic**. It intercepts tool calls at the runtime layer, regardless of which LLM generated them.

**Tested with:**
- Claude (Opus, Sonnet, Haiku)
- GPT-4, GPT-3.5
- Open-source (via LangChain, LlamaIndex, custom frameworks)

**Key requirement:** Your agent framework must use git hooks OR call Y*gov's Python API directly.

---

## Security & Compliance

### Q: How are CIEU records "tamper-evident"? Can't I just edit the SQLite file?

**A:** You can edit the file, but tampering is **instantly detectable**.

**Mechanism:**
1. Each CIEU record includes the SHA-256 hash of the *previous* record
2. Modifying record N breaks the hash chain at record N+1
3. `ystar verify` detects the break immediately

**Example:**
```bash
# Tamper with the database
sqlite3 .ystar_cieu.db "UPDATE cieu_records SET decision='ALLOW' WHERE seq=42"

# Verification fails
ystar verify
# Output: ❌ Chain break detected at seq=43 (expected hash abc123..., got def456...)
```

**Forensic value:** Auditors can pinpoint *exactly* which record was altered and when.

---

### Q: Is Y*gov compliant with SOC 2 / HIPAA / FINRA / FDA 21 CFR Part 11?

**A:** Y*gov provides the **enforcement and audit infrastructure** required by these frameworks. Compliance also depends on:

1. **Your governance rules** (you define what's allowed)
2. **Your operational policies** (access control, backup, retention)
3. **Your audit process** (how you review CIEU records)

**What Y*gov guarantees:**
- ✅ Tamper-evident audit trail (21 CFR Part 11 §11.10(e))
- ✅ Deterministic enforcement (no AI discretion in the compliance layer)
- ✅ Delegation chain tracking (critical for SOC 2 access control)
- ✅ Immutable record versioning (FINRA rule versioning)

**What you must provide:**
- Appropriate governance rules for your domain (e.g., HIPAA: no PII in logs)
- Secure storage of `.ystar_cieu.db` (encryption at rest, access control)
- Regular audit reviews (we recommend weekly CIEU audits)

**Compliance statement:** Y*gov is a tool for building compliant systems. It is not itself a "certified" product (no software is "HIPAA certified" — that's a common misconception).

---

### Q: What if an agent tries to disable Y*gov or delete CIEU records?

**A:** Multiple layers of defense:

**Layer 1 — Scope enforcement:**
If your governance contract forbids modifying `.ystar_cieu.db`, any attempt is blocked:
```markdown
## File Protection
Agent cannot modify: .ystar_cieu.db
```

**Layer 2 — Git hook priority:**
Y*gov hooks run *before* the agent's actions execute. The agent cannot "turn off" a hook that hasn't run yet.

**Layer 3 — Forensic detection:**
Even if an agent somehow deletes records, `ystar verify` detects the gap in the hash chain.

**Layer 4 — External backup:**
Best practice: Continuously replicate `.ystar_cieu.db` to a read-only external storage (S3, compliance logging service, etc.).

---

## Architecture & Design

### Q: Why no LLM in the enforcement layer?

**A:** Three reasons:

**1. Security:** LLMs are vulnerable to prompt injection. If the enforcement layer used an LLM, an attacker could craft a prompt that tricks it into allowing violations.

**2. Performance:** LLM calls take 200-500ms. Y*gov `check()` runs in 0.042ms because it's pure Python (AST parsing + regex + path normalization).

**3. Determinism:** Compliance frameworks require deterministic enforcement. An LLM might allow a command on Monday and deny it on Tuesday (temperature > 0, non-deterministic outputs). Y*gov guarantees: same input → same output, always.

**Where LLMs *are* used (optionally):**
- Intent extraction (converting natural language rules into contracts)
- Causal analysis (analyzing *why* a violation happened)
- Obligation synthesis (identifying implicit commitments in agent logs)

But the **enforcement decision itself** is always deterministic code.

---

### Q: Why zero external dependencies?

**A:** Supply chain security.

Every dependency is a potential attack vector:
- Malicious package injection (e.g., PyPI supply chain attacks)
- Dependency updates breaking governance (semantic versioning violations)
- Compliance risk (dependencies with incompatible licenses)

**Y*gov's approach:**
- Core runtime: stdlib only (json, sqlite3, hashlib, pathlib, ast)
- Testing: pytest (dev dependency, not in production wheel)
- Distribution: single `.whl` file (643KB, auditable)

**Audit surface:** You can review the entire enforcement codebase in ~2 hours. Try doing that with a framework that depends on 47 packages.

---

### Q: Can I use Y*gov with LangChain / AutoGPT / CrewAI / [other framework]?

**A:** Yes, via two integration paths:

**Path 1 — Git hooks (easiest):**
If your framework commits to git or runs shell commands, Y*gov hooks intercept automatically. No code changes needed.

**Path 2 — Direct Python API:**
```python
from ystar import Governance

gov = Governance.load("AGENTS.md")
result = gov.check(
    tool="bash",
    params={"command": "rm -rf /"},
    context={"agent": "cleanup_agent"}
)
if result.decision == "DENY":
    raise PermissionError(result.reason)
```

**Integration guides:** See `docs/integrations/` for LangChain, AutoGPT, and CrewAI examples.

---

## Comparisons

### Q: How is Y*gov different from LangSmith / LangFuse / Weights & Biases?

**A:** Those are **observability tools** (logging/monitoring). Y*gov is **enforcement**.

| Tool | When it acts | What it does |
|------|-------------|--------------|
| LangSmith | After execution | Logs what happened |
| Y*gov | Before execution | Prevents violations |

**Complementary, not competitive.** Best practice: Use Y*gov for enforcement + LangSmith for observability.

---

### Q: How is Y*gov different from prompt-based guardrails?

**A:** Prompts are suggestions. Y*gov is enforcement.

**Example:**
```
Prompt: "You are not allowed to read /etc/passwd"
Agent: [Reads /etc/passwd anyway — forgot, jailbroken, or prompt-injected]
```

vs.

```
Y*gov rule: "Agent cannot read /etc/"
Agent tries: cat /etc/passwd
Y*gov: DENY — /etc is not allowed
```

**EXP-001 result:** Agent without Y*gov fabricated audit records in a blog post. Agent with Y*gov could not—CIEU records are written by the enforcement engine, not the agent.

---

### Q: How is Y*gov different from OpenAI's function calling restrictions?

**A:** OpenAI's restrictions are:
1. **Model-specific** (only work with OpenAI models)
2. **Prompt-level** (agent can still ignore them)
3. **No audit trail** (you don't get immutable CIEU records)

Y*gov is:
1. **Model-agnostic** (works with any LLM)
2. **Runtime enforcement** (agent cannot bypass)
3. **Tamper-evident audit** (SHA-256 hash chain)

---

## Pricing & Licensing

### Q: Is Y*gov free?

**A:** Yes. MIT license. Use it commercially, modify it, redistribute it. No restrictions.

**Why free?**
We believe runtime governance should be infrastructure, not a luxury. We will monetize via:
- Enterprise support contracts (SLA, custom rules, integration help)
- Managed compliance service (cloud-hosted CIEU audit dashboard)
- Premium features (advanced causal analysis, multi-region replication)

**Core enforcement will always be free and open-source.**

---

### Q: Can I get enterprise support?

**A:** Yes, starting Q2 2026. Email: enterprise@ystarlabs.com

**Support tiers (planned):**
- **Community:** GitHub issues (best-effort)
- **Professional:** 48-hour response SLA, private Slack channel ($2K/year)
- **Enterprise:** 4-hour response SLA, custom rule development, compliance consulting ($25K/year)

Current status: All users get community support (GitHub issues).

---

## Roadmap & Future

### Q: What's coming in v0.49.0?

**Planned features (pending user feedback):**
1. **Direct Python API** (use Y*gov without git hooks)
2. **Delegation chain visualization** (`ystar tree` command)
3. **Performance improvements** (target: <0.03ms per check)
4. **Windows native support** (no Git Bash required)
5. **Real-time dashboard** (web UI for CIEU audit stream)

**Vote on priorities:** Open an issue with `[Feature Request]` prefix.

---

### Q: Will Y*gov support [specific feature]?

**A:** Maybe! Open a GitHub issue with:
1. Your use case (what problem does this solve?)
2. Current workaround (how are you handling it today?)
3. Proposed API (how should it work?)

**Features we're actively considering:**
- Kubernetes integration (sidecar enforcement)
- Slack/PagerDuty alerts on violations
- Policy-as-code templates (pre-built rules for HIPAA, SOC 2, etc.)
- Cross-agent causal tracing (follow a violation across 3+ agents)

---

## Troubleshooting

### Q: I get `ModuleNotFoundError: No module named 'ystar'` after installation

**A:** Python environment mismatch.

**Diagnosis:**
```bash
which python  # Check which Python is running
which pip     # Check which pip installed ystar
python -c "import ystar; print(ystar.__version__)"  # Test import
```

**Fix:**
```bash
# Use python3 explicitly
python3 -m pip install ystar
python3 -m ystar doctor

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install ystar
```

---

### Q: CIEU database grows too large (100MB+)

**A:** Normal for high-volume agents. Options:

**Option 1 — Archive old records:**
```bash
ystar archive --before 2026-03-01  # Move old records to .ystar_cieu_archive.db
```

**Option 2 — Rotate logs:**
```bash
cp .ystar_cieu.db backups/cieu_$(date +%Y%m%d).db
ystar reset  # Start fresh (loses history!)
```

**Option 3 — External replication:**
Stream CIEU records to external storage (S3, CloudWatch Logs, Splunk):
```python
# Custom integration (example)
from ystar import CIEUStream
stream = CIEUStream(".ystar_cieu.db")
for record in stream.tail(follow=True):
    send_to_s3(record)  # Your cloud storage
```

**Typical sizes:**
- 1K tool calls: ~2MB
- 10K tool calls: ~20MB
- 100K tool calls: ~200MB

---

### Q: Can I run Y*gov in CI/CD pipelines?

**A:** Yes. Common use case: Block deployments if governance violations detected.

**Example (GitHub Actions):**
```yaml
- name: Install Y*gov
  run: pip install ystar

- name: Check governance compliance
  run: |
    ystar verify  # Ensure CIEU chain is intact
    ystar report --failed  # Show any violations
    if ystar report --failed | grep DENY; then exit 1; fi
```

**GitLab CI, CircleCI, Jenkins:** Similar pattern.

---

## Getting Help

**Installation issues:** Run `ystar doctor` and paste output in GitHub issue  
**Bug reports:** https://github.com/liuhaotian2024-prog/Y-star-gov/issues  
**Feature requests:** Same link, use `[Feature Request]` prefix  
**Enterprise inquiries:** enterprise@ystarlabs.com  
**Security vulnerabilities:** security@ystarlabs.com (PGP key in repo)

---

**Did this answer your question?** If not, open an issue — we'll add it to this FAQ.
