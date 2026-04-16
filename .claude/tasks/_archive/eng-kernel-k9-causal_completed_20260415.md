## Task: K9 CausalChainAnalyzer 迁移到 Y*gov CIEU

Engineer: eng-kernel (Leo Chen)
Priority: P0
Assigned: 2026-04-15 20:52 UTC
Deadline: ≤3h wall clock

## Context

K9Audit repo 的 `k9log/causal_analyzer.py::CausalChainAnalyzer` 实现了 CIEU 因果链追踪。
需要提取该 pattern 适配 Y*gov CIEU schema，用于白皮书 Scenario C 演示。

## Acceptance Criteria

- [ ] Clone K9Audit repo（如不存在）:`git clone https://github.com/liuhaotian2024-prog/K9Audit /tmp/K9Audit`
- [ ] 提取 `k9log/causal_analyzer.py::CausalChainAnalyzer` pattern
- [ ] 新写 `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/causal_chain_analyzer.py`
- [ ] 适配 Y*gov CIEU schema (event_id/seq_global/created_at/session_id/agent_id/event_type/drift_details)
- [ ] E2E test: 对任意一条 FORGETGUARD_DENY event 输出其前驱-后继因果链
- [ ] 三层 evidence：grep / production call / E2E verify
- [ ] Commit + push (Y-star-gov repo)

## Files in Scope

- `/tmp/K9Audit/k9log/causal_analyzer.py` (read-only reference)
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/causal_chain_analyzer.py` (new)
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/test_causal_chain_analyzer.py` (new)

## Technical Notes

K9Audit schema (legacy):
```python
k9_event = {
    "event_id": str,
    "timestamp": float,
    "agent": str,
    "event_type": str,
    "metadata": dict,
}
```

Y*gov CIEU schema:
```python
cieu_event = {
    "event_id": str,
    "seq_global": int,
    "created_at": float,
    "session_id": str,
    "agent_id": str,
    "event_type": str,
    "drift_details": str (JSON),
    # ...
}
```

Mapping:
- K9 `timestamp` → CIEU `created_at`
- K9 `agent` → CIEU `agent_id`
- K9 `metadata` → CIEU `drift_details` (JSON.parse)

## Expected Output

```python
from ystar.governance.causal_chain_analyzer import CausalChainAnalyzer

analyzer = CausalChainAnalyzer("/path/to/.ystar_cieu.db")
chain = analyzer.trace_event("fg_1713216000000_123")
# Output: {"predecessors": [...], "event": {...}, "successors": [...]}
```

## Evidence Format

Commit message 必须包含：
- CIEU 5-tuple (Y*/Xt/U/Yt+1/Rt+1)
- Evidence Layer 1: grep CausalChainAnalyzer 相关代码行数
- Evidence Layer 2: production call 对真实 FORGETGUARD_DENY 输出因果链
- Evidence Layer 3: E2E test 验证前驱-后继链完整

## License Compliance

K9Audit 是 AGPL-3.0，Y*gov 是 MIT。提取 pattern 时：
- 不直接 copy code，理解逻辑后重写
- 注释中 credit K9Audit 作为灵感来源
- Commit message 注明 "inspired by K9Audit causal_analyzer.py"

## Execution Notes

- Y-star-gov repo 路径: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/`
- 先 cd 到该 repo 再 git commit/push
- 如遇 daemon 锁死，自救：`pkill -9 -f hook_daemon; rm -f /tmp/ystar_hook*.sock`

## Report Back

完成后立刻 commit + push，不等 CTO 确认。遇 blocker 先自救。
