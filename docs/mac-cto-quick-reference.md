# MAC CTO Workstation — Quick Reference

## Daily Operations

### Start CTO Session
```bash
# From Windows (via Telegram)
python C:/Users/liuha/OneDrive/桌面/ystar-company/scripts/telegram_bridge.py "cd ~/workspace/Y-star-gov && tmux new -d -s cto 'claude --agent cto'"

# Or via SSH (if key is set up)
ssh liuha@haotians-mac-mini.local "cd ~/workspace/Y-star-gov && tmux new -d -s cto 'claude --agent cto'"
```

### Check CTO Status
```bash
python telegram_bridge.py "tmux ls"
python telegram_bridge.py "tmux capture-pane -t cto -p | tail -30"
```

### Stop CTO Session
```bash
python telegram_bridge.py "tmux kill-session -t cto"
```

### Pull Latest Code
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git pull && cd ~/workspace/ystar-bridge-labs && git pull"
```

### Run Tests
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -m pytest --tb=short -q"
```

### Check Test Count
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -m pytest --collect-only -q | grep 'test session starts'"
```

### Run Doctor
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && ystar doctor"
```

### View Recent Commits
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git log --oneline -10"
```

### Check CTO Reports
```bash
python telegram_bridge.py "ls -lt ~/workspace/ystar-bridge-labs/reports/autonomous/ | head -10"
python telegram_bridge.py "cat ~/workspace/ystar-bridge-labs/reports/autonomous/\$(ls -t ~/workspace/ystar-bridge-labs/reports/autonomous/ | head -1)"
```

## Common Tasks

### Assign Task to CTO
1. On Windows, create task file in ystar-bridge-labs:
```bash
cd C:/Users/liuha/OneDrive/桌面/ystar-company
echo "Fix hook installation bug" > .claude/tasks/cto-001-fix-hook.md
git add .claude/tasks/cto-001-fix-hook.md
git commit -m "task: CTO fix hook installation"
git push
```

2. Pull on MAC:
```bash
python telegram_bridge.py "cd ~/workspace/ystar-bridge-labs && git pull"
```

3. CTO will read and execute on next session start

### Retrieve CTO Work Results
1. CTO commits to Y-star-gov and writes report to ystar-bridge-labs
2. Pull from Windows:
```bash
cd C:/Users/liuha/OneDrive/桌面/Y-star-gov
git pull
cd C:/Users/liuha/OneDrive/桌面/ystar-bridge-labs
git pull
cat reports/autonomous/2026-04-01-cto-*.md
```

### Update Y*gov on MAC
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git pull && pip3 install -e ."
```

### Rebuild Package
```bash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -m build && ls -lh dist/"
```

## SSH Setup (One-Time)

### Add Windows SSH Key to MAC
```bash
# Step 1: Copy key (from Windows)
cat ~/.ssh/id_ed25519.pub
# Copy output: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMHwNNUicBvHo5hy8iEqCTt5e9HIyf9FgjLvoVB+QJE1

# Step 2: Add to MAC authorized_keys
python telegram_bridge.py "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
python telegram_bridge.py "echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMHwNNUicBvHo5hy8iEqCTt5e9HIyf9FgjLvoVB+QJE1 liuha@zippolyon' >> ~/.ssh/authorized_keys"
python telegram_bridge.py "chmod 600 ~/.ssh/authorized_keys"

# Step 3: Test from Windows
ssh liuha@haotians-mac-mini.local "whoami"
```

After SSH setup, you can skip Telegram for most operations.

## Troubleshooting

### Telegram Bridge Not Working
```bash
# Check session file exists
ls C:/Users/liuha/OneDrive/桌面/ystar-company/ystar_telegram_session.session

# Re-authenticate if needed
cd C:/Users/liuha/OneDrive/桌面/ystar-company/scripts
python telegram_bridge.py
```

### CTO Session Not Responding
```bash
# Check if tmux session exists
python telegram_bridge.py "tmux ls"

# Attach to session to see what's happening
python telegram_bridge.py "tmux capture-pane -t cto -p"

# Kill and restart
python telegram_bridge.py "tmux kill-session -t cto"
python telegram_bridge.py "cd ~/workspace/Y-star-gov && tmux new -d -s cto 'claude --agent cto'"
```

### Git Sync Issues
```bash
# Check status
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git status"

# Stash changes
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git stash"

# Pull
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git pull"

# Pop stash
python telegram_bridge.py "cd ~/workspace/Y-star-gov && git stash pop"
```

### Tests Failing
```bash
# Run with verbose output
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -m pytest -v --tb=short tests/test_hook.py 2>&1 | head -50"

# Run specific test
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -m pytest tests/test_hook.py::test_hook_install -v"

# Check imports
python telegram_bridge.py "cd ~/workspace/Y-star-gov && python -c 'import ystar; print(ystar.__file__)'"
```

## Monitoring Commands

### System Resources
```bash
python telegram_bridge.py "top -l 1 | head -20"
python telegram_bridge.py "df -h | grep -E '(Filesystem|/System/Volumes/Data)'"
```

### Process List
```bash
python telegram_bridge.py "ps aux | grep claude"
python telegram_bridge.py "ps aux | grep python"
```

### Network
```bash
python telegram_bridge.py "ifconfig en0 | grep inet"
python telegram_bridge.py "curl -s ifconfig.me"  # Public IP
```

## Configuration Files

### ~/.clauderc (on MAC)
```json
{
  "apiKey": "sk-ant-api03-...",
  "defaultModel": "claude-sonnet-4-5"
}
```

### ~/workspace/ystar-bridge-labs/.claude/agents/cto.md
CTO agent definition (see full setup guide)

### ~/workspace/ystar-bridge-labs/.claude/settings.json
Y*gov hook configuration (created by `ystar hook-install`)

## Quick Diagnostic

```bash
# One command to check everything
python telegram_bridge.py "cd ~/workspace/Y-star-gov && echo '=== Git Status ===' && git status --short && echo '=== Ystar Version ===' && ystar --version && echo '=== Test Count ===' && python -m pytest --collect-only -q 2>&1 | tail -1 && echo '=== Doctor ===' && ystar doctor 2>&1 | grep -E '(PASS|FAIL|WARN)'"
```

## File Locations

| Item | MAC Path | Windows Path |
|------|----------|--------------|
| Y*gov source | ~/workspace/Y-star-gov | C:/Users/liuha/OneDrive/桌面/Y-star-gov |
| Company repo | ~/workspace/ystar-bridge-labs | C:/Users/liuha/OneDrive/桌面/ystar-company |
| Telegram bridge | N/A | C:/Users/liuha/OneDrive/桌面/ystar-company/scripts/telegram_bridge.py |
| CTO tasks | ~/workspace/ystar-bridge-labs/.claude/tasks/ | C:/Users/liuha/OneDrive/桌面/ystar-company/.claude/tasks/ |
| CTO reports | ~/workspace/ystar-bridge-labs/reports/autonomous/ | C:/Users/liuha/OneDrive/桌面/ystar-company/reports/autonomous/ |

---

Updated: 2026-04-01
Platform Engineer: Y*gov Team
