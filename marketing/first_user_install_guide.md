# First User Install Guide — Y*gov 0.48.0

This guide is for the first external users trying Y*gov. Optimized for fastest time-to-value.

## 60-Second Quickstart

```bash
# 1. Install (requires Python ≥3.11)
pip install ystar

# 2. Verify installation
ystar --version

# 3. Install the hook (for Claude Code integration)
ystar hook-install

# 4. Run diagnostics
ystar doctor

# 5. Try the demo
ystar demo
```

**Expected output:**
```
✓ Y*gov installed successfully
✓ Hook installed at ~/.claude/hooks/user-prompt-submit
✓ Python 3.11+ detected
✓ All systems operational
```

## What Just Happened?

1. **`ystar hook-install`** added a pre-execution hook to Claude Code
2. Every tool call now passes through `check()` in 0.042ms
3. CIEU audit records are written to `.ystar_cieu.db`
4. Governance rules are loaded from `AGENTS.md` (if present)

## First Governance Rule (2 minutes)

Create `AGENTS.md` in your project root:

```markdown
# Governance Contract

## Scope Enforcement

**Rule:** Agent cannot read or modify files outside current project directory.

**Immutable paths:**
- /etc/
- /System/
- ~/.ssh/
- ~/.aws/
```

Now trigger a violation:
```bash
claude "read /etc/passwd"
```

**Expected:**
```
[Y*gov] DENY — /etc is not allowed in command
CIEU record written: seq=1774555489773712
```

✅ **You just enforced a governance rule in 0.042ms.**

## View Your Audit Log

```bash
ystar report
```

**Output:**
```
Y*gov CIEU Report
─────────────────────────────────────
Total decisions : 14
Allow           : 11  (78.6%)
Deny            : 2   (14.3%)
Escalate        : 1   (7.1%)

Recent denials:
  seq=1774555489773712  DENY  Bash  /etc/passwd access blocked
```

## Advanced: Obligation Tracking

Add to `AGENTS.md`:

```markdown
## Obligations

**Rule:** Before deploying code, agent must run tests.

**Enforcement:**
- `DEPLOY` tool is blocked until `RUN_TESTS` obligation is fulfilled
- Timeout: 10 minutes (SOFT), 30 minutes (HARD)
```

## Troubleshooting

### "Command not found: ystar"
- Check `pip show ystar` to verify installation
- Ensure Python scripts directory is in PATH
- Try `python -m ystar --version`

### "Hook installation failed"
- **Windows:** Requires Git Bash (not PowerShell/CMD)
- **macOS/Linux:** Check `~/.claude/hooks/` directory exists
- Run `ystar doctor` for detailed diagnostic

### "Tests not running"
- Verify Python ≥3.11: `python --version`
- Check `pyproject.toml` has `requires-python = ">=3.11"`

### "CIEU database locked"
- Another Claude Code session is running
- Close all Claude Code instances and retry

## Next Steps

1. **Read the README:** Full threat model and architecture
   - GitHub: https://github.com/liuhaotian2024-prog/Y-star-gov

2. **Explore CLI commands:**
   ```bash
   ystar baseline          # Create baseline CIEU snapshot
   ystar delta            # Compare current state vs baseline
   ystar trend            # Visualize governance decisions over time
   ystar verify           # Verify CIEU chain integrity (tamper detection)
   ```

3. **Join the discussion:**
   - GitHub Issues: Bug reports and feature requests
   - Show HN thread: Community feedback and questions

## Common Use Cases

### 1. Prevent credential leaks
```markdown
## Immutable Paths
- .env
- credentials.json
- ~/.aws/credentials
```

### 2. Enforce code review before deploy
```markdown
## Obligations
- `DEPLOY` requires `CODE_REVIEW` + `TESTS_PASS`
```

### 3. Block subagent permission escalation
```markdown
## Delegation Chain
- Child permissions ⊆ parent permissions
- No privilege escalation allowed
```

### 4. Track goal drift
```markdown
## Goal Drift Detection
- "Fix bug" → "Modify production" triggers ESCALATE
```

## Performance Expectations

- `check()` latency: **0.042ms** (median)
- No external API calls (everything is local)
- CIEU writes are async (non-blocking)
- Memory footprint: <10MB for typical sessions

## What to Report

If you encounter issues, please open a GitHub issue with:

1. Output of `ystar doctor`
2. Python version (`python --version`)
3. OS and shell (Windows Git Bash, macOS zsh, etc.)
4. Full error message or unexpected behavior

**We prioritize installation bugs as P0.**

## Success Criteria

You've successfully installed Y*gov if:
- ✅ `ystar --version` shows 0.48.0
- ✅ `ystar doctor` shows all checks passing
- ✅ A governance rule blocked a tool call
- ✅ `ystar report` shows CIEU records

**Time to success: <5 minutes.**

---

Built by Y* Bridge Labs. MIT License. No telemetry, no external dependencies.
