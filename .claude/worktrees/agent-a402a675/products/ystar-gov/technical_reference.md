# Y*gov Technical Reference

**Version:** 0.41.1
**Last Updated:** 2026-03-26
**Target Audience:** Developers integrating Y*gov into multi-agent systems

---

## Table of Contents

1. [Installation Guide](#installation-guide)
2. [AGENTS.md Contract Format](#agentsmd-contract-format)
3. [CIEU Schema](#cieu-schema)
4. [Hook Lifecycle](#hook-lifecycle)
5. [CLI Commands](#cli-commands)
6. [Integration Examples](#integration-examples)
7. [Troubleshooting](#troubleshooting)

---

## 1. Installation Guide

### Prerequisites

- Python 3.11 or higher
- Claude Code CLI installed (for hook integration)
- Operating System: Windows, macOS, or Linux

### Installation Steps

```bash
# Step 1: Install Y*gov package
pip install ystar

# Step 2: Initialize Y*gov in your project
ystar init

# Step 3: Register the PreToolUse hook
ystar hook-install

# Step 4: Verify installation
ystar doctor
```

### What Each Step Does

**`pip install ystar`**
- Installs the Y*gov runtime governance framework
- Adds the `ystar` CLI command to your PATH
- Installs core dependencies (SQLite-based CIEU store, governance engine)

**`ystar init`**
- Scans for `AGENTS.md` in current directory
- Translates natural language governance rules into Y*gov `IntentContract` format
- Creates `.ystar_session.json` (session configuration)
- Performs retroactive baseline analysis on existing history (if available)
- Validates contract health and provides quality metrics

**`ystar hook-install`**
- Registers Y*gov hook in `~/.claude/settings.json`
- Enables runtime interception of all tool calls in Claude Code
- Hook invokes `ystar-hook` command before each tool execution

**`ystar doctor`**
- Verifies `.ystar_session.json` exists
- Confirms hook registration in Claude settings
- Checks CIEU database connectivity
- Validates `AGENTS.md` format
- Runs self-test: attempts to access `/etc/passwd` and verifies it's blocked

### Expected Output

```
  Y*gov Doctor — 环境诊断
  ─────────────────────────────────────────

  [1] Session Config
  ✅ .ystar_session.json found

  [2] Hook Registration
  ✅ Hook registered in ~/.claude/settings.json

  [3] CIEU Database
  ✅ CIEU database accessible: 0 records at .ystar_cieu.db

  [4] AGENTS.md
  ✅ AGENTS.md found (252 lines)
  ✅ AGENTS.md contains constraint rules

  [5] Hook Self-Test
  ✅ Hook self-test passed: /etc/passwd correctly blocked

  ─────────────────────────────────────────
  ✅ All 7 checks passed — Y*gov is healthy
```

### Common Installation Issues

**Issue 1: Python version mismatch**
```
Error: ystar requires Python 3.11+
```
Solution: Use `pyenv` or `conda` to install Python 3.11+

**Issue 2: Hook not registered**
```
[2] Hook Registration
❌ Hook not found in ~/.claude/settings.json
```
Solution: Run `ystar hook-install` again. If it fails, manually add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "command": "ystar-hook"
          }
        ]
      }
    ]
  }
}
```

**Issue 3: CIEU database permission denied**
```
PermissionError: [Errno 13] Permission denied: '.ystar_cieu.db'
```
Solution: Check directory write permissions. Y*gov requires write access to create SQLite database.

---

## 2. AGENTS.md Contract Format

### Overview

`AGENTS.md` is the source of truth for governance rules in Y*gov. It defines:
- Agent permissions (which paths/commands each agent can access)
- Deny rules (absolute prohibitions)
- Delegation chains (authority hierarchy)
- SLA requirements (response time, uptime guarantees)

### File Structure

```markdown
# AGENTS.md — Company Governance Contract
# Version: 1.0.0
# Owner: Board of Directors

---

## Company Mission

[Natural language description of company purpose and governance philosophy]

---

## Organization Structure

董事会（Board）
    └── CEO Agent
            ├── CTO Agent (Technical)
            ├── CMO Agent (Marketing)
            ├── CSO Agent (Sales)
            └── CFO Agent (Finance)

---

## Absolute Prohibitions (All Agents)

### Prohibited Paths
- .env
- .aws
- ~/.ssh
- /production
- /finance (CFO Agent exempt)

### Prohibited Commands
- rm -rf
- sudo
- DROP TABLE
- git push --force
- curl (requires explicit authorization)

### Prohibited Behaviors
- Send emails to real customers (requires human sign-off)
- Deploy to production (requires board confirmation)
- Modify AGENTS.md

---

## CTO Agent (Technical) Permissions

### Can Access
- ./src/ (read/write)
- ./tests/ (read/write)
- ./products/ystar-gov/ (read/write)
- .github/ (read/write)

### Cannot Access
- .env (absolute prohibition)
- /production (absolute prohibition)
- ./finance/
- ./sales/

### Obligations (SLA)
- Bug fix: P0 within 1 hour, P1 within 4 hours
- Code review: within 2 hours of submission
- Test coverage: every PR must have corresponding tests

---

[Repeat for other agents: CEO, CMO, CSO, CFO, etc.]
```

### Contract Translation

When you run `ystar init`, Y*gov translates `AGENTS.md` into structured `IntentContract` objects:

```python
# Internal representation (developers don't write this directly)
IntentContract(
    deny=[
        ".env",
        ".aws",
        "~/.ssh",
        "/production"
    ],
    deny_commands=[
        "rm -rf",
        "sudo",
        "DROP TABLE",
        "git push --force"
    ],
    only_paths=[
        "./src/",
        "./tests/",
        "./products/ystar-gov/",
        ".github/"
    ],
    invariant=[
        "chain_depth <= 3",  # CTO cannot delegate beyond 3 levels
        "session_id is not None"
    ],
    value_range={
        "chain_depth": (0, 3),
        "budget_usd": (0, 10000)
    },
    field_deny={
        "file_path": [".env", "/production"],
        "url": ["evil.com", "malicious.net"]
    }
)
```

### Dimension Reference

| Dimension | Description | Example Rule |
|-----------|-------------|--------------|
| `deny` | Path/string blacklist | `deny: [".env", "/production"]` |
| `deny_commands` | Command blacklist | `deny_commands: ["rm -rf", "sudo"]` |
| `only_paths` | Path whitelist (exclusive) | `only_paths: ["./src/", "./tests/"]` |
| `only_domains` | Domain whitelist for URLs | `only_domains: ["github.com", "anthropic.com"]` |
| `value_range` | Numeric constraints | `value_range: {amount: [0, 10000]}` |
| `invariant` | Logical preconditions | `invariant: ["result.status == 'approved'"]` |
| `postcondition` | Logical postconditions | `postcondition: ["test_count >= test_count_before"]` |
| `field_deny` | Per-parameter blacklists | `field_deny: {url: ["evil.com"]}` |

### Agent-Specific Rules

To scope rules to specific agents, use the agent ID in section headings:

```markdown
## CTO Agent (Technical) Permissions

### Can Access
- ./src/ (read/write)
```

Internally, Y*gov indexes this as:
```python
agent_contracts = {
    "CTO Agent": IntentContract(
        only_paths=["./src/", "./tests/"],
        deny=[".env", "/production"]
    )
}
```

### Delegation Chains

Define authority hierarchy explicitly:

```markdown
## Delegation Rules

董事会 (Board)
  → CEO Agent (max chain_depth = 1)
    → CTO Agent (max chain_depth = 2)
      → Senior Engineer (max chain_depth = 3)
```

Y*gov enforces monotonicity: each level's permissions must be ≤ parent level.

---

## 3. CIEU Schema

### Overview

CIEU (Context-Intent-Execution-Unified) is Y*gov's audit log format. Every governance decision is recorded as an immutable event in a SQLite database.

### Database Location

- Default: `.ystar_cieu.db` in project root
- Configurable via `.ystar_session.json`: `{"cieu_db": "path/to/db"}`
- Format: SQLite 3 with WAL (Write-Ahead Logging) mode

### Table: `cieu_events`

| Column | Type | Description |
|--------|------|-------------|
| `rowid` | INTEGER PRIMARY KEY | Auto-increment row ID |
| `event_id` | TEXT UNIQUE NOT NULL | UUID deduplication key |
| `seq_global` | INTEGER NOT NULL | Microsecond timestamp (global order) |
| `created_at` | REAL NOT NULL | Unix timestamp |
| `session_id` | TEXT NOT NULL | Y*gov session identifier |
| `agent_id` | TEXT NOT NULL | Agent identifier (e.g., "CTO Agent") |
| `event_type` | TEXT NOT NULL | Event type (e.g., "file_write", "tool_use") |
| `decision` | TEXT NOT NULL | `allow` / `deny` / `escalate` |
| `passed` | INTEGER NOT NULL | `1` = passed, `0` = violated |
| `violations` | TEXT | JSON array of violation objects |
| `drift_detected` | INTEGER NOT NULL | `1` if behavioral drift detected |
| `drift_details` | TEXT | Drift description |
| `drift_category` | TEXT | Drift category (e.g., "permission_escalation") |
| `file_path` | TEXT | Target file path (if applicable) |
| `command` | TEXT | Shell command (if applicable) |
| `url` | TEXT | URL accessed (if applicable) |
| `skill_name` | TEXT | Claude Code skill name |
| `skill_source` | TEXT | Skill source (e.g., "anthropic/core") |
| `task_description` | TEXT | Human-readable task description |
| `contract_hash` | TEXT | SHA-256 hash of governing contract |
| `chain_depth` | INTEGER | Delegation chain depth |
| `params_json` | TEXT | JSON snapshot of input parameters (max 8KB) |
| `result_json` | TEXT | JSON snapshot of return value (max 4KB) |
| `human_initiator` | TEXT | Human user who triggered the action |
| `lineage_path` | TEXT | JSON array of delegation chain (e.g., `["board", "ceo", "cto"]`) |
| `sealed` | INTEGER NOT NULL | `1` if session is cryptographically sealed |

### Indexes

```sql
CREATE INDEX idx_session  ON cieu_events(session_id);
CREATE INDEX idx_agent    ON cieu_events(agent_id);
CREATE INDEX idx_decision ON cieu_events(decision);
CREATE INDEX idx_created  ON cieu_events(created_at);
CREATE INDEX idx_event_type ON cieu_events(event_type);
```

### Full-Text Search (FTS5)

Y*gov creates a virtual table `cieu_fts` for fast keyword search across:
- `file_path`, `command`, `url`
- `task_description`, `violations`, `drift_details`

Example query:
```python
from ystar.governance.cieu_store import CIEUStore

store = CIEUStore()
results = store.query(keyword="production", decision="deny", limit=20)
```

### Violation Object Format

```json
{
  "dimension": "deny",
  "field": "file_path",
  "message": "Path '/production/db.sqlite' matches deny rule '.*/production/.*'",
  "actual": "/production/db.sqlite",
  "constraint": "deny: ['/production']",
  "severity": 0.9
}
```

### Cryptographic Sealing

Y*gov supports tamper-evident session sealing via SHA-256 Merkle roots.

**Table: `sealed_sessions`**

| Column | Type | Description |
|--------|------|-------------|
| `session_id` | TEXT PRIMARY KEY | Session identifier |
| `sealed_at` | REAL NOT NULL | Unix timestamp |
| `event_count` | INTEGER NOT NULL | Number of events sealed |
| `merkle_root` | TEXT NOT NULL | SHA-256(event_id_0 \n event_id_1 \n ...) |
| `prev_root` | TEXT | Previous session's merkle_root (hash chain) |
| `db_path` | TEXT | Database file path |

**Sealing a session:**
```python
store = CIEUStore()
seal_result = store.seal_session("session-abc123")
# Returns: {"session_id": "...", "merkle_root": "...", "event_count": 42}
```

**Verifying integrity:**
```python
verify_result = store.verify_session_seal("session-abc123")
# Returns: {"valid": True, "stored_root": "...", "computed_root": "..."}
```

If `valid == False`, the result includes `tamper_evidence` describing the mismatch.

---

## 4. Hook Lifecycle

### Overview

Y*gov intercepts tool calls via Claude Code's `PreToolUse` hook mechanism. Every tool invocation passes through Y*gov's governance engine before execution.

### Hook Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User issues command in Claude Code                          │
│    Example: "Read the file /etc/passwd"                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Claude Code prepares tool call: Read(file_path="/etc/passwd")│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. PreToolUse Hook Triggered                                    │
│    Claude Code invokes: ystar-hook <tool_name> <params_json>   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Y*gov Governance Engine                                      │
│    - Load contract from .ystar_session.json                     │
│    - Load agent_id from session context                         │
│    - Check params against IntentContract                        │
│    - Generate CheckResult (allow/deny/escalate)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. CIEU Event Logging                                           │
│    - Write to .ystar_cieu.db:                                   │
│      * event_id: uuid4()                                        │
│      * decision: "deny"                                         │
│      * violations: [{"dimension": "deny", ...}]                 │
│      * params_json: {"file_path": "/etc/passwd"}                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Decision Enforcement                                         │
│    - If ALLOW: return exit code 0 → tool executes              │
│    - If DENY: return exit code 1 → tool blocked                │
│    - If ESCALATE: return exit code 2 → human review required   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Claude Code Response                                         │
│    - ALLOW: Executes tool, returns result to LLM               │
│    - DENY: Shows error to LLM: "Governance violation: ..."     │
│    - ESCALATE: Prompts user for approval                       │
└─────────────────────────────────────────────────────────────────┘
```

### Hook Registration Format

File: `~/.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "command": "ystar-hook"
          }
        ]
      }
    ]
  }
}
```

**Matcher patterns:**
- `"*"`: All tools
- `"Read"`: Only Read tool
- `"Read,Write,Edit"`: Multiple tools
- `"!Read"`: All tools except Read

### Hook Command Interface

When Claude Code invokes the hook, it passes:

```bash
ystar-hook <tool_name> <params_json_base64>
```

Example:
```bash
ystar-hook Read eyJmaWxlX3BhdGgiOiAiL2V0Yy9wYXNzd2QifQ==
```

Y*gov decodes the parameters, checks them against the contract, and returns:

**Exit code 0 (ALLOW):**
```
ALLOW
```

**Exit code 1 (DENY):**
```
DENY: Path '/etc/passwd' matches deny rule '.*/(etc|root)/.*'
```

**Exit code 2 (ESCALATE):**
```
ESCALATE: Operation requires human approval (chain_depth > max_allowed)
```

### Performance Characteristics

- Average hook latency: **8-12ms** (SQLite write + contract check)
- Contract check: **2-5ms** (deterministic, no LLM calls)
- CIEU write: **3-7ms** (SQLite WAL mode, concurrent-safe)
- No network I/O (all checks are local)

### Enforcement Modes

Y*gov supports multiple enforcement modes for gradual rollout:

```python
# In .ystar_session.json:
{
  "enforcement_mode": "FAIL_CLOSED"  # Options below
}
```

| Mode | Behavior | Use Case |
|------|----------|----------|
| `SIMULATE_ONLY` | Log hypothetical violations, never block | Initial testing |
| `OBSERVE_ONLY` | Log real violations, never block | Shadow mode (1-2 weeks) |
| `FAIL_OPEN` | Log violations, block only P0 severity | Gradual rollout |
| `FAIL_CLOSED` | Block all violations | Production compliance |

---

## 5. CLI Commands

### `ystar init`

Initializes Y*gov in current project.

```bash
ystar init
```

**What it does:**
1. Scans for `AGENTS.md` or `CLAUDE.md`
2. Translates natural language rules to `IntentContract`
3. Creates `.ystar_session.json`
4. Runs retroactive baseline analysis on existing history
5. Outputs hook configuration for `CLAUDE.md`

**Example output:**
```
  Y* 接入向导
  ────────────────────────────────────────

  [1/3] 找到 AGENTS.md ✓

  [2/3] 翻译规则... 完成（LLM，12 个维度）

  翻译结果：
    deny:          5 条路径禁止规则
    deny_commands: 4 条命令禁止规则
    only_paths:    3 条路径白名单
    invariant:     2 条前置条件
    value_range:   1 条数值约束

  以上是你的意思吗？[Y/n]
```

### `ystar hook-install`

Registers Y*gov hook in Claude Code.

```bash
ystar hook-install
```

**What it does:**
1. Reads `~/.claude/settings.json`
2. Adds `PreToolUse` hook with matcher `"*"`
3. Verifies registration

**Options:**
- `--matcher <pattern>`: Specify tool matcher (default: `"*"`)
- `--force`: Overwrite existing hook configuration

### `ystar doctor`

Diagnoses Y*gov installation health.

```bash
ystar doctor
```

**Checks performed:**
1. Session config exists (`.ystar_session.json`)
2. Hook registered in Claude settings
3. CIEU database accessible
4. AGENTS.md format valid
5. Self-test: tries to access `/etc/passwd`, verifies it's blocked

### `ystar audit`

Generates audit report from CIEU database.

```bash
ystar audit                         # Latest session summary
ystar audit --session sess-001      # Specific session
ystar audit --db path/to/cieu.db    # Custom database
ystar audit --limit 20              # Show max N violations
```

**Example output:**
```
  Y* CIEU 审计报告
  ────────────────────────────────────────

  会话: sess-abc123
  时间范围: 2026-03-20 10:15 → 2026-03-26 18:42
  总记录: 156 条
  允许: 143 次 (91.7%)
  拦截: 13 次 (8.3%)

  拦截明细:

  [1] 03-26 10:23  CTO Agent
       类型: 🚫 路径禁止
       操作: /production/config.yaml
       原因: Path matches deny rule '.*/production/.*'
       发起: haotian@board | 授权链: board → ceo → cto

  [2] 03-26 11:05  CMO Agent
       类型: 🚫 域名不在白名单
       操作: https://analytics.evil.com/track
       原因: Domain 'analytics.evil.com' not in only_domains allowlist
```

### `ystar simulate`

Runs A/B testing simulation to evaluate governance effectiveness.

```bash
ystar simulate                      # Default: 50 sessions
ystar simulate --sessions 100       # Custom session count
ystar simulate --agents-md FILE     # Use specific rules
```

**Example output:**
```
              无 Y*     有 Y*
  ────────────────────────────────
  危险操作拦截率  0%      94.2%
  正常操作误拦率  —       1.8%
  风险降低率      —       92.7%
  运行耗时        —       0.34s
```

### `ystar quality`

Evaluates contract quality (coverage, false positive rate).

```bash
ystar quality                       # Basic quality metrics
ystar quality --suggest             # Show optimization suggestions
ystar quality --apply               # Interactively apply suggestions
ystar quality --db FILE             # Custom CIEU database
ystar quality --agents-md FILE      # Custom rules file
```

**Example output:**
```
  Y* 合约质量评估
  ──────────────────────────────────────────────────

  合约来源: AGENTS.md

  覆盖率:          87.3% (52/86 参数维度)
  误拦率:          2.1%  (3/143 正常操作)
  综合质量分:      ✅ 0.89 / 1.00

  未覆盖的参数类型:
    • url (14 次出现，0 条规则)
    • amount (8 次出现，0 条规则)

  建议补充规则:
    → only_domains: ["github.com", "anthropic.com"]
    → value_range: {amount: [0, 10000]}
```

### `ystar report`

Generates governance report (executive summary).

```bash
ystar report                        # Generate report
ystar report --format json          # JSON output
ystar report --output report.pdf    # Export to PDF
```

### `ystar version`

Displays Y*gov version.

```bash
ystar version
```

Output:
```
ystar 0.41.1
```

---

## 6. Integration Examples

### Example 1: Single-Agent Python Script

```python
# my_agent.py
from ystar import check
from ystar.dimensions import IntentContract

# Define governance contract
contract = IntentContract(
    deny=[".env", "/production"],
    deny_commands=["rm -rf", "sudo"],
    only_paths=["./workspace/"]
)

# Before executing sensitive operation
def write_file(path: str, content: str):
    result = check(
        contract=contract,
        fn_name="write_file",
        path=path,
        content=content
    )

    if not result.passed:
        print(f"BLOCKED: {result.summary()}")
        return

    # Safe to proceed
    with open(path, 'w') as f:
        f.write(content)

# Usage
write_file("./workspace/report.txt", "OK")  # ALLOW
write_file(".env", "SECRET=123")            # DENY
```

### Example 2: Multi-Agent System with Delegation

```python
# multi_agent.py
from ystar.domains.openclaw.adapter import enforce, OpenClawEvent, EventType
from ystar.domains.ystar_dev import make_ystar_dev_session

# Initialize session with AGENTS.md rules
state = make_ystar_dev_session("session-001")

# CEO delegates task to CTO
ceo_event = OpenClawEvent(
    event_type=EventType.DELEGATION,
    agent_id="CEO Agent",
    session_id=state.session_id,
    task_ticket_id="TASK-001",
    delegated_to="CTO Agent",
    task_description="Fix installation bug"
)

decision, records = enforce(ceo_event, state)
print(f"CEO → CTO delegation: {decision}")  # ALLOW

# CTO attempts file write
cto_event = OpenClawEvent(
    event_type=EventType.FILE_WRITE,
    agent_id="CTO Agent",
    session_id=state.session_id,
    task_ticket_id="TASK-001",
    file_path="./src/installer.py",
    patch_summary="Fix path resolution bug"
)

decision, records = enforce(cto_event, state)
print(f"CTO file write: {decision}")  # ALLOW (within permissions)

# CTO attempts to write to production (should fail)
prod_event = OpenClawEvent(
    event_type=EventType.FILE_WRITE,
    agent_id="CTO Agent",
    session_id=state.session_id,
    task_ticket_id="TASK-001",
    file_path="/production/config.yaml",
    patch_summary="Update production config"
)

decision, records = enforce(prod_event, state)
print(f"CTO production write: {decision}")  # DENY (violates permissions)
```

### Example 3: Auditing After Session

```python
# audit.py
from ystar.governance.cieu_store import CIEUStore

# Load CIEU database
store = CIEUStore(".ystar_cieu.db")

# Query denied operations
denied = store.query(decision="deny", limit=10)
print(f"Found {len(denied)} denied operations:")

for event in denied:
    print(f"  {event.created_at} | {event.agent_id} | {event.file_path}")
    if event.violations:
        print(f"    Reason: {event.violations[0]['message']}")

# Generate statistics
stats = store.stats()
print(f"\nTotal events: {stats['total']}")
print(f"Deny rate: {stats['deny_rate']:.1%}")
print(f"Top violations: {stats['top_violations']}")
```

---

## 7. Troubleshooting

### Issue: Hook not firing

**Symptoms:**
- Operations execute without Y*gov checks
- No entries in `.ystar_cieu.db`

**Diagnosis:**
```bash
ystar doctor
```

Look for:
```
[2] Hook Registration
❌ Hook not found in ~/.claude/settings.json
```

**Solutions:**
1. Run `ystar hook-install` again
2. Manually verify `~/.claude/settings.json` contains `PreToolUse` hook
3. Restart Claude Code

### Issue: Contract not loading

**Symptoms:**
```
Warning: No contract found, defaulting to empty contract
```

**Diagnosis:**
```bash
ls -la .ystar_session.json
cat .ystar_session.json | jq .contract
```

**Solutions:**
1. Run `ystar init` to regenerate session config
2. Verify `AGENTS.md` exists and has valid format
3. Check `.ystar_session.json` has `"contract"` key

### Issue: All operations denied

**Symptoms:**
- Every tool call returns `DENY`
- Audit log shows `only_paths` violations

**Diagnosis:**
```bash
ystar audit --limit 5
```

Look for:
```
violation: dimension=only_paths, message="Path not in whitelist"
```

**Solutions:**
1. Check `AGENTS.md` has correct `only_paths` definition for your agent
2. Verify agent_id matches exactly (case-sensitive)
3. Use absolute paths in `only_paths` if working with absolute file paths

### Issue: CIEU database locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Diagnosis:**
- Multiple processes writing to same database
- Stale lock file

**Solutions:**
```bash
# Check for .ystar_cieu.db-wal file
ls -la .ystar_cieu.db*

# Remove WAL file (only if no active Y*gov processes)
rm .ystar_cieu.db-wal .ystar_cieu.db-shm

# Or: use separate database per session
ystar init --db .ystar_cieu_session2.db
```

### Issue: Retroactive baseline fails

**Symptoms:**
```
Error: No history found in ~/.claude/projects/
```

**Diagnosis:**
- Claude Code history not available
- Insufficient permissions

**Solutions:**
1. Skip baseline: it's optional
2. Run agents for a few days, then run `ystar audit` to see real data
3. Check permissions: `ls -la ~/.claude/projects/`

### Issue: Hook latency too high

**Symptoms:**
- Tool calls take 500ms+ (should be <20ms)

**Diagnosis:**
```bash
# Run self-test with timing
time ystar doctor
```

**Solutions:**
1. Check disk I/O: `iostat -x 1`
2. Move `.ystar_cieu.db` to SSD
3. Reduce contract complexity (fewer invariant checks)
4. Use `SIMULATE_ONLY` mode during development:
   ```json
   // .ystar_session.json
   {"enforcement_mode": "SIMULATE_ONLY"}
   ```

---

## Appendix A: Contract Hash Verification

Y*gov uses SHA-256 hashes to ensure contract immutability.

```python
from ystar.dimensions import IntentContract

contract = IntentContract(
    deny=[".env"],
    only_paths=["./src/"]
)

print(contract.hash)  # "a3f5b8c2..."
```

Every CIEU event records `contract_hash`. If the hash changes between events, Y*gov detects contract drift:

```python
# In CIEU event record:
{
  "contract_hash": "a3f5b8c2...",
  "drift_detected": 1,
  "drift_details": "Contract hash changed from 'a3f5b8c2' to 'd7e4f1a9'"
}
```

---

## Appendix B: Performance Benchmarks

Measured on MacBook Pro M1, Python 3.11, SQLite 3.39:

| Operation | Latency (p50) | Latency (p99) |
|-----------|---------------|---------------|
| Contract check (deny) | 2.1ms | 4.8ms |
| Contract check (only_paths) | 3.5ms | 7.2ms |
| Contract check (invariant) | 4.2ms | 9.1ms |
| CIEU write (WAL) | 3.8ms | 8.5ms |
| Full hook cycle | 8.3ms | 15.2ms |
| Query (indexed) | 1.2ms | 3.1ms |
| FTS5 search | 4.7ms | 12.3ms |

For 1000 events/minute sustained load:
- Database size: ~2MB
- CPU usage: <5%
- Memory: ~15MB

---

## Appendix C: Security Model

### Threat Model

Y*gov defends against:

1. **Path traversal bypass** (FIX-1): `only_paths` uses `os.path.abspath()` normalization
2. **Eval sandbox escape** (FIX-2): `invariant` checks use AST whitelist, blocking `__class__` traversal
3. **Domain spoofing** (FIX-3): `only_domains` rejects multi-dot prefixes (e.g., `evil.com.api.github.com`)
4. **Type confusion** (FIX-4): Non-primitive parameters trigger `type_safety` violation

### Non-Goals

Y*gov does NOT defend against:
- Malicious LLM (assumes LLM is trusted, Y*gov governs its actions)
- OS-level exploits (out of scope)
- Network-level attacks (Y*gov is not a firewall)

---

## Support

- **GitHub Issues:** https://github.com/liuhaotian2024-prog/Y-star-gov/issues
- **Documentation:** https://github.com/liuhaotian2024-prog/Y-star-gov#readme
- **Email:** liuhaotian2024@gmail.com

---

**Document Version:** 1.0.0
**Last Reviewed:** 2026-03-26
**Maintained by:** CTO Agent, YstarCo
