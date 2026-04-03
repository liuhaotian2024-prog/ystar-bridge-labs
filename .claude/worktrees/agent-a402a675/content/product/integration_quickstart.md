# Y*gov Integration Quick-Start

Three paths, shortest first. Pick the one that matches your stack.

---

## Path 1: Claude Code (3 commands)

```bash
pip install ystar-gov
ystar hook-install          # installs Claude Code pre-tool-use hook
ystar doctor                # verifies installation + runs self-check
```

**Expected output** (doctor):
```
[ok] ystar-gov 0.42.0
[ok] hook installed at ~/.claude/hooks/pre-tool-use
[ok] kernel check() ... 8 dimensions active
[ok] CIEU store ... writable
All systems nominal.
```

**What just happened**: Every Claude Code tool call (file write, bash, web fetch)
now passes through `check()` before execution. Violations are blocked in real time.
CIEU records every decision for audit.

---

## Path 2: OpenClaw (5 lines of Python)

```python
from ystar.integrations.base import LiveWorkloadConfig
from ystar.integrations.openclaw import OpenClawConnector
from ystar.integrations import WorkloadRunner

config = LiveWorkloadConfig(endpoint_url="http://localhost:9000/events")
result = WorkloadRunner.run(OpenClawConnector(config))
```

**Expected output**:
```
WorkloadResult(events_processed=42, denied=3, escalated=1, elapsed=12.4s)
```

**What just happened**: Y*gov connected to your OpenClaw runtime via SSE,
checked every agent action against its contract in real time, and injected
allow/deny decisions back into OpenClaw. Three unsafe actions were blocked.

---

## Path 3: Any Python Agent (10 lines)

```python
from ystar.kernel.dimensions import IntentContract
from ystar.kernel.engine import check

# Define what your agent is allowed to do
contract = IntentContract(
    name="my_agent_policy",
    deny=["/etc", "/root", "~/.ssh"],
    deny_commands=["rm -rf", "sudo", "eval("],
    only_domains=["api.example.com", "cdn.example.com"],
)

# Before every action, check it
result = check(contract, {"file_path": "/etc/passwd"})
print(result.passed)    # False
print(result.summary()) # VIOLATION: Path '/etc/passwd' is under denied path '/etc'

result = check(contract, {"url": "https://api.example.com/data"})
print(result.passed)    # True
```

**Expected output**:
```
False
VIOLATION: Path '/etc/passwd' is under denied path '/etc'
True
```

**What just happened**: You created a contract (8 constraint dimensions available),
then used `check()` to enforce it. Same function, same deterministic logic that
runs inside Claude Code hooks and OpenClaw connectors. Zero ML in the critical path.

---

*Full API docs*: `python -m ystar --help` | *304 tests* | *MIT License*
