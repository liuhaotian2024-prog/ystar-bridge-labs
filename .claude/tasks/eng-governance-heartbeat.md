## Task: Orchestrator Governance Heartbeat (RFC-2026-005)
Engineer: eng-governance
Priority: P0
RFC: RFC-2026-005 (Board批准)
Due: 本周内完成

## Context

RFC-2026-005要求建立三层闭环治理架构。当前阶段第一个任务：在Orchestrator实现第5个子系统 — governance_heartbeat。

## Current State

Orchestrator现有4个子系统：
1. InterventionEngine scan（每10次调用或60s）
2. GovernanceLoop + Path A（每50次调用或5min）
3. CausalEngine advisory（高风险工具触发）
4. Coverage scan（每200次调用或30min）

需要新增第5个子系统。

## Requirements

### 1. 新增governance_heartbeat子系统

**位置：** ystar/governance/orchestrator.py的_run_cycle()方法

**实现逻辑：**
```python
# 在_run_cycle()中添加第5个子系统检查
if self.call_count % self.heartbeat_interval == 0:
    self._write_governance_heartbeat()
```

**heartbeat方法实现：**
```python
def _write_governance_heartbeat(self):
    """Write governance system heartbeat to CIEU"""
    heartbeat_event = {
        'event_type': 'governance_heartbeat',
        'timestamp': datetime.now(UTC).isoformat(),
        'call_count': self.call_count,
        'orchestrator_status': 'alive',
        'subsystems_active': ['intervention', 'governance_loop', 'causal', 'coverage', 'heartbeat']
    }
    # 写入CIEU database
    self.cieu_recorder.record_event(heartbeat_event)
```

### 2. 参数配置化（不硬编码）

**session.json新增字段：**
```json
{
  "heartbeat": {
    "interval_calls": 100,
    "governance_loop_timeout_secs": 600,
    "heartbeat_timeout_secs": 300
  }
}
```

**Orchestrator读取配置：**
```python
def __init__(self, session_manager):
    # ... existing code ...
    heartbeat_config = session_manager.session.get('heartbeat', {})
    self.heartbeat_interval = heartbeat_config.get('interval_calls', 100)  # 默认100次调用
```

### 3. GovernanceLoop.tighten()写alive记录

**位置：** ystar/governance/path_a/governance_loop.py的tighten()方法

每次tighten()执行时写governance_loop_alive：
```python
def tighten(self):
    # ... existing logic ...
    
    # 在方法末尾添加alive记录
    self._write_alive_signal()

def _write_alive_signal(self):
    """Write governance loop alive signal to CIEU"""
    alive_event = {
        'event_type': 'governance_loop_alive',
        'timestamp': datetime.now(UTC).isoformat(),
        'cycle_count': self.cycle_count  # if exists
    }
    self.cieu_recorder.record_event(alive_event)
```

## Acceptance Criteria

- [ ] Orchestrator有_write_governance_heartbeat()方法
- [ ] heartbeat_interval从session.json读取，有默认值100
- [ ] 每N次调用写governance_heartbeat到CIEU
- [ ] GovernanceLoop.tighten()写governance_loop_alive到CIEU
- [ ] CIEU database能查询到这两种event_type
- [ ] 86个测试全部通过
- [ ] 不修改GovernanceLoop核心逻辑（只在末尾添加alive记录）

## Files in Scope

- ystar/governance/orchestrator.py
- ystar/governance/path_a/governance_loop.py
- ystar/session.py (如需修改session.json schema)

## Testing

执行后验证：
```bash
# 运行测试
python -m pytest --tb=short -q

# 查询CIEU heartbeat记录
sqlite3 .ystar_cieu.db "SELECT * FROM events WHERE event_type = 'governance_heartbeat' ORDER BY timestamp DESC LIMIT 5"

# 查询governance_loop_alive记录
sqlite3 .ystar_cieu.db "SELECT * FROM events WHERE event_type = 'governance_loop_alive' ORDER BY timestamp DESC LIMIT 5"
```

## Dependencies

- 需要eng-platform完成doctor检测heartbeat功能（并行任务）
- 不依赖其他RFC任务，可独立执行

## Notes

- GovernanceLoop.tighten()是HIGH风险方法，只在末尾添加代码，不改核心逻辑
- heartbeat是基础设施，为后续Layer 3 MetaLearning Hub做准备
- 完成后通知CTO进行code review
