# MAC CTO Workstation Setup Guide

> **DEPRECATED as of AMENDMENT-004 (2026-04-12).** This document describes the historical Windows + MAC mini dual-machine configuration. The company now runs on a single Mac under the OpenClaw workspace (`/Users/haotianliu/.openclaw/workspace/ystar-company`). CTO is a sub-agent in the same Claude Code session, not a separate physical machine. Retained for historical reference only — do not follow these setup steps.

## Executive Summary (historical)

Deploy Claude Code on MAC mini to serve as CTO engineering workstation.
- Windows machine = Board-CEO dialogue
- MAC machine = CTO/K9 execution environment
- Sync via GitHub (ystar-bridge-labs, Y-star-gov)

## Access Methods

### Method 1: Telegram Bridge (Primary - Already Working)
```bash
# From Windows
cd C:/Users/liuha/OneDrive/桌面/ystar-company/scripts
python telegram_bridge.py "your command here"
```

### Method 2: Direct SSH (Requires Setup)
```bash
# Add SSH key to MAC first
ssh-copy-id -i ~/.ssh/id_ed25519.pub liuha@haotians-mac-mini.local
# Then connect
ssh liuha@haotians-mac-mini.local
```

Current SSH public key on Windows:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMHwNNUicBvHo5hy8iEqCTt5e9HIyf9FgjLvoVB+QJE1 liuha@zippolyon
```

## Prerequisites Check

Run on MAC (via Telegram bridge):
```bash
# Check Node.js
node --version  # Need 18+

# Check npm
npm --version

# Check Git
git --version

# Check Python
python3 --version  # Need 3.9+

# Check pip
pip3 --version
```

## Installation Steps

### Step 1: Install Claude Code

```bash
# On MAC mini
npm install -g @anthropic-ai/claude-code
```

Telegram command from Windows:
```bash
python telegram_bridge.py "npm install -g @anthropic-ai/claude-code"
```

### Step 2: Authenticate Claude Code

```bash
# First run will prompt for API key
claude
```

Note: This requires interactive input. Options:
1. Set environment variable: `export ANTHROPIC_API_KEY=sk-ant-...`
2. Use ~/.clauderc config file
3. SSH in directly to complete interactive setup

Recommended ~/.clauderc content:
```json
{
  "apiKey": "sk-ant-api03-...",
  "defaultModel": "claude-sonnet-4-5"
}
```

### Step 3: Clone Repositories

```bash
# On MAC mini
cd ~
mkdir -p workspace
cd workspace

# Clone Y*gov (product source)
git clone https://github.com/liuhaotian2024-prog/Y-star-gov.git

# Clone company repo
git clone https://github.com/liuhaotian2024-prog/ystar-bridge-labs.git
```

### Step 4: Install Y*gov Development Environment

```bash
cd ~/workspace/Y-star-gov

# Install in development mode
pip3 install -e .

# Verify installation
ystar --version
```

### Step 5: Configure Governance Hook

```bash
cd ~/workspace/ystar-bridge-labs

# Setup Y*gov workspace
ystar setup --yes

# Install PreToolUse hook
ystar hook-install

# Verify hook is active
ls -la .claude/
cat .claude/settings.json
```

### Step 6: Verify Installation

```bash
# Run doctor
ystar doctor

# Check all components
ystar demo

# Run test suite
cd ~/workspace/Y-star-gov
python -m pytest --tb=short -q
```

Expected: 406 tests should pass.

### Step 7: Configure CTO Agent

Create `.claude/agents/cto.md` in ystar-bridge-labs:

```bash
cd ~/workspace/ystar-bridge-labs
cat > .claude/agents/cto.md << 'EOF'
# CTO — Platform Engineer

You are the CTO at Y* Bridge Labs.
Working directory: ~/workspace/Y-star-gov/

## Your Scope
- ystar/adapters/ (all files)
- ystar/cli/ (all files)
- ystar/integrations/
- tests/test_*.py (QA lead)

## Workflow
1. Read .claude/tasks/ for assigned work
2. Execute highest priority task
3. Run pytest to verify
4. Commit and push changes
5. Write report to ../ystar-bridge-labs/reports/autonomous/

## Quality Standards
- All changes must have passing tests
- Integration tests for new features
- No silent except:pass blocks
- Clear error messages in CLI
EOF
```

### Step 8: Start CTO Session

```bash
cd ~/workspace/Y-star-gov
claude --agent cto
```

Or use project mode:
```bash
claude --project ystar-gov
```

## Verification Checklist

- [ ] Node.js 18+ installed
- [ ] npm installed
- [ ] Git configured with liuhaotian2024-prog credentials
- [ ] Python 3.9+ installed
- [ ] Claude Code installed globally
- [ ] ANTHROPIC_API_KEY configured
- [ ] Y-star-gov cloned
- [ ] ystar-bridge-labs cloned
- [ ] Y*gov installed (pip install -e .)
- [ ] ystar hook-install completed
- [ ] ystar doctor passes
- [ ] 406 tests pass
- [ ] CTO agent configured

## Remote Execution Examples

### Via Telegram Bridge

```bash
# Check installation
python telegram_bridge.py "which claude && which ystar"

# Run doctor
python telegram_bridge.py "cd ~/workspace/Y-star-gov && ystar doctor"

# Run tests
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -m pytest -q"

# Start CTO session (requires tmux or screen)
python telegram_bridge.py "cd ~/workspace/Y-star-gov && tmux new -d -s cto 'claude --agent cto'"
```

### Via SSH (After Key Setup)

```bash
# One-line remote execution
ssh liuha@haotians-mac-mini.local "cd ~/workspace/Y-star-gov && ystar doctor"

# Interactive session
ssh liuha@haotians-mac-mini.local
cd ~/workspace/Y-star-gov
claude --agent cto
```

## Troubleshooting

### Claude Code Not Found
```bash
# Check npm global bin path
npm config get prefix
# Add to PATH if needed
export PATH="$PATH:$(npm config get prefix)/bin"
```

### Permission Denied on npm install -g
```bash
# Option 1: Fix npm permissions
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH

# Option 2: Use sudo (not recommended)
sudo npm install -g @anthropic-ai/claude-code
```

### ystar Command Not Found After pip install
```bash
# Check if in PATH
python3 -m pip show ystar | grep Location
# Add to PATH
export PATH="$PATH:~/Library/Python/3.x/bin"
```

### Hook Not Firing
```bash
# Check settings.json exists
cat ~/workspace/ystar-bridge-labs/.claude/settings.json

# Verify hook path
ystar doctor

# Re-install hook
cd ~/workspace/ystar-bridge-labs
ystar hook-install --force
```

## Next Steps After Installation

1. CTO should read assigned tasks: `.claude/tasks/cto-*.md`
2. Execute highest priority engineering work
3. Run integration tests after changes
4. Commit to Y-star-gov repo
5. Write daily report to ystar-bridge-labs/reports/autonomous/

## Architecture Notes

### Two-Machine Workflow
- Windows: Board dialogue with CEO agent
- MAC: CTO/Platform Engineer execution
- Sync point: GitHub push/pull
- Communication: Telegram bridge for remote commands

### Repository Roles
- Y-star-gov: Product source code (CTO primary)
- ystar-bridge-labs: Company ops, docs, reports (CEO primary)
- K9Audit: Read-only reference for patterns

### Agent Coordination
- CEO writes tasks to .claude/tasks/cto-*.md
- CTO reads tasks on MAC, executes in Y-star-gov
- CTO writes completion reports to ystar-bridge-labs/reports/autonomous/
- CEO aggregates reports on Windows

## Security Considerations

1. API Key Storage
   - Use ~/.clauderc on MAC
   - Never commit API keys to git
   - Rotate keys if exposed

2. SSH Key Management
   - Windows key: ssh-ed25519 ...QJE1
   - Add to MAC: ~/.ssh/authorized_keys
   - Disable password auth after key setup

3. Git Credentials
   - Use SSH keys for git operations
   - Configure user: git config --global user.name "liuhaotian2024-prog"
   - Configure email: git config --global user.email "your-email@example.com"

## Performance Optimization

1. Use tmux/screen for long-running CTO sessions
2. Enable git credential caching: `git config --global credential.helper cache`
3. Pre-download dependencies: `pip install -r requirements.txt` before starting session

## Monitoring

### Check CTO Session Status (from Windows)
```bash
python telegram_bridge.py "tmux ls"
python telegram_bridge.py "tmux capture-pane -t cto -p | tail -20"
```

### View Recent Commits
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git log --oneline -5"
```

### Check Test Status
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -m pytest --tb=line -q 2>&1 | tail -10"
```

---

Generated: 2026-04-01
Platform Engineer: Y*gov Team
Status: Ready for deployment
