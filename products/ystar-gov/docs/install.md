# Y*gov Installation Guide

Version: 0.48.0 | Last updated: 2026-04-23

---

## 1. Prerequisites

**Python**: 3.11 or later (3.12, 3.13, 3.14 also supported).

```bash
python3 --version
# Must show 3.11+
```

**Operating Systems**: macOS (darwin), Linux, Windows. Y*gov is pure Python with zero compiled dependencies -- it runs anywhere CPython runs.

**Required system tools** (for full governance pipeline):

- `git` -- Y*gov reads `.git/` metadata for audit trail context
- `sqlite3` -- ships with Python stdlib; used for CIEU database storage

No external C libraries or build tools are needed. `pip install` is sufficient.

---

## 2. Installation

Install from PyPI:

```bash
pip install ystar
```

For isolated environments (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
pip install ystar
```

Verify the package installed correctly:

```bash
python3 -m ystar version
```

Expected output:

```
ystar 0.48.0
```

---

## 3. Post-Install Check

### Verify the CLI entry point

```bash
ystar version
```

If the `ystar` command is not found, the script directory may not be on your PATH. Fall back to:

```bash
python3 -m ystar version
```

### Run the environment diagnostic

```bash
ystar doctor
```

`ystar doctor` runs two layers of checks:

- **Layer 1** -- zero-dependency health checks (core governance infrastructure: session file, CIEU database, contract presence)
- **Layer 2** -- dependency checks (Python environment, git availability, hook registration, test suite)

A healthy environment produces:

```
  [✓] .ystar_session.json exists
  [✓] CIEU database reachable
  [✓] Contract file found
  ...
  ============================================================
  All N checks passed -- Y*gov is healthy
```

You can run individual layers:

```bash
ystar doctor --layer1    # Only infrastructure checks
ystar doctor --layer2    # Only dependency checks (requires Layer 1 pass)
```

---

## 4. First-Run Setup

Y*gov governance requires two setup steps after installation.

### Step 1: Generate session configuration

```bash
ystar setup
```

This interactive command creates `.ystar_session.json` in the current directory. It prompts for:

- **Project name** -- defaults to the current directory name
- **CIEU DB path** -- defaults to `.ystar_cieu.db`
- **Deny paths** -- filesystem paths the governance layer blocks (default: `/etc`, `/root`, `/production`)
- **Deny commands** -- shell commands the governance layer blocks (default: `rm -rf`, `sudo`, `DROP TABLE`)

For non-interactive use (CI/CD pipelines):

```bash
ystar setup --yes
```

Files created:

| File | Purpose |
|------|---------|
| `.ystar_session.json` | Governance session configuration (193 constraint fields, 11 categories) |
| `.ystar_cieu.db` | CIEU audit event database (SQLite) |
| `.ystar_cieu_omission.db` | Omission tracking database |

### Step 2: Register the governance hook

```bash
ystar hook-install
```

This registers Y*gov as a `PreToolUse` hook in your Claude Code environment. Every tool call (Bash, Read, Write, Edit) passes through Y*gov's enforcement engine before execution.

After hook installation, the governance pipeline is active. All tool invocations are evaluated against your session contract and logged to the CIEU database.

### Step 3: Define your governance contract

Create an `AGENTS.md` file in your project root that declares agent identities, permission boundaries, and behavioral rules. Y*gov reads this file to determine enforcement policy.

```bash
ystar init
```

This generates a `policy.py` contract template as a starting point.

---

## 5. Troubleshooting

### Problem: `command not found: ystar`

**Cause**: The Python scripts directory is not on your system PATH.

**Fix**:

```bash
# Option 1: Use the module invocation instead
python3 -m ystar version

# Option 2: Add the scripts directory to PATH
# Find where pip installed scripts:
python3 -c "import sysconfig; print(sysconfig.get_path('scripts'))"
# Add that path to your shell profile (.zshrc / .bashrc)
```

### Problem: `ystar doctor` reports Layer 1 failures

**Cause**: Missing `.ystar_session.json` or unreachable CIEU database.

**Fix**:

```bash
# Generate the session file
ystar setup --yes

# Verify the CIEU database was created
ls -la .ystar_cieu.db

# Re-run doctor to confirm
ystar doctor --layer1
```

### Problem: Hook not intercepting tool calls after `ystar hook-install`

**Cause**: The hook registration may conflict with existing hooks, or the Claude Code instance needs a restart to pick up the new hook configuration.

**Fix**:

```bash
# 1. Verify hook is registered
ystar doctor --layer2

# 2. Check that .ystar_session.json exists in the project working directory
ls .ystar_session.json

# 3. Restart Claude Code to reload hook configuration
# (hooks are read at session start, not hot-reloaded)

# 4. If still failing, re-install the hook
ystar hook-install
```

---

## 6. Verification

Confirm the full governance pipeline works end-to-end by checking that tool calls produce CIEU audit records.

### Run the built-in demo

```bash
ystar demo
```

This executes a 5-second demonstration that triggers a governance event and displays the result.

### Check CIEU records

After running any governed session, inspect the audit trail:

```bash
ystar audit
```

This displays the causal audit report -- every tool call, its intent classification, and the allow/deny decision.

### View governance metrics

```bash
ystar report
```

For a delta comparison against a previous state:

```bash
ystar baseline    # Capture current state as reference
# ... run your agent session ...
ystar delta       # Compare current state against baseline
```

### View event trends

```bash
ystar trend
```

Displays a 7-day breakdown of total events, deny counts, and deny rate with trend indicators.

If `ystar audit` shows events and `ystar doctor` passes all checks, the installation is complete and governance is active.
