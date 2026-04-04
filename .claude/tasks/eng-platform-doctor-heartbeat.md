## Task: Doctor Heartbeat Detection (RFC-2026-005)
Engineer: eng-platform
Priority: P0
RFC: RFC-2026-005 (Board批准)
Due: 本周内完成

## Context

RFC-2026-005要求建立governance system心跳监控。ystar doctor命令需要新增检查项，检测治理层是否存活。

## Current State

ystar doctor现有检查项：
- Hook installation status
- Y*gov package installation
- CIEU database integrity
- Session configuration

需要新增：governance system heartbeat检查。

## Requirements

### 1. Doctor新增heartbeat检查

**位置：** ystar/cli/commands/doctor.py

**检查逻辑：**
```python
def check_governance_heartbeat(session_manager):
    """Check governance system heartbeat status"""
    from datetime import datetime, timedelta, UTC
    import sqlite3
    
    # Read timeout config from session.json
    heartbeat_config = session_manager.session.get('heartbeat', {})
    heartbeat_timeout = heartbeat_config.get('heartbeat_timeout_secs', 300)  # 默认5分钟
    governance_loop_timeout = heartbeat_config.get('governance_loop_timeout_secs', 600)  # 默认10分钟
    
    # Query CIEU database
    cieu_db_path = '.ystar_cieu.db'  # or from config
    conn = sqlite3.connect(cieu_db_path)
    cursor = conn.cursor()
    
    # Check governance_heartbeat
    cursor.execute("""
        SELECT timestamp FROM events 
        WHERE event_type = 'governance_heartbeat' 
        ORDER BY timestamp DESC LIMIT 1
    """)
    heartbeat_row = cursor.fetchone()
    
    # Check governance_loop_alive
    cursor.execute("""
        SELECT timestamp FROM events 
        WHERE event_type = 'governance_loop_alive' 
        ORDER BY timestamp DESC LIMIT 1
    """)
    loop_alive_row = cursor.fetchone()
    
    conn.close()
    
    # Analyze results
    now = datetime.now(UTC)
    
    results = []
    
    if heartbeat_row:
        last_heartbeat = datetime.fromisoformat(heartbeat_row[0])
        delta = (now - last_heartbeat).total_seconds()
        if delta < heartbeat_timeout:
            results.append(('✓', f'governance_heartbeat: 最后记录 {int(delta)}秒前'))
        else:
            results.append(('✗', f'governance_heartbeat: 最后记录 {int(delta)}秒前（超过{heartbeat_timeout}秒阈值）'))
    else:
        results.append(('✗', 'governance_heartbeat: 无记录（治理层可能未启动）'))
    
    if loop_alive_row:
        last_loop = datetime.fromisoformat(loop_alive_row[0])
        delta = (now - last_loop).total_seconds()
        if delta < governance_loop_timeout:
            results.append(('✓', f'governance_loop_alive: 最后记录 {int(delta)}秒前'))
        else:
            results.append(('✗', f'governance_loop_alive: 最后记录 {int(delta)}秒前（超过{governance_loop_timeout}秒阈值）'))
    else:
        results.append(('✗', 'governance_loop_alive: 无记录（GovernanceLoop可能未运行）'))
    
    return results
```

**集成到doctor命令：**
```python
def run_doctor(session_manager):
    """Run all doctor checks"""
    print("Y*gov Health Check\n")
    
    # ... existing checks ...
    
    # New heartbeat check
    print("\n[Governance Heartbeat]")
    heartbeat_results = check_governance_heartbeat(session_manager)
    for status, message in heartbeat_results:
        print(f"{status} {message}")
    
    # ... rest of doctor logic ...
```

### 2. 输出格式

正常状态：
```
[Governance Heartbeat]
✓ governance_heartbeat: 最后记录 45秒前
✓ governance_loop_alive: 最后记录 120秒前
```

异常状态：
```
[Governance Heartbeat]
✗ governance_heartbeat: 最后记录 380秒前（超过300秒阈值）
  → 治理层可能失联，请检查hook安装状态
✗ governance_loop_alive: 无记录（GovernanceLoop可能未运行）
  → 请运行至少50次Y*gov检查以触发GovernanceLoop
```

### 3. 错误处理

如果CIEU database不存在或表结构不对：
```python
try:
    # ... check logic ...
except sqlite3.OperationalError as e:
    return [('?', f'无法读取CIEU数据库: {e}')]
except Exception as e:
    return [('✗', f'心跳检查失败: {e}')]
```

## Acceptance Criteria

- [ ] ystar doctor有governance heartbeat检查项
- [ ] 从session.json读取timeout配置，有默认值
- [ ] 正确查询CIEU database的governance_heartbeat和governance_loop_alive
- [ ] 根据阈值判断正常/异常并输出清晰诊断
- [ ] 错误处理覆盖database不存在/表结构错误等情况
- [ ] 86个测试全部通过
- [ ] doctor命令手工测试通过

## Files in Scope

- ystar/cli/commands/doctor.py
- ystar/cli/commands/__init__.py (如需修改imports)

## Testing

手工测试流程：
```bash
# 1. 正常情况测试
# 运行一些Y*gov操作产生heartbeat记录
ystar govern "test action"  # 多次运行

# 运行doctor查看heartbeat状态
ystar doctor

# 2. 超时情况测试
# 等待超过阈值时间（或手动修改CIEU记录timestamp）
ystar doctor
# 应显示超时警告

# 3. 无记录情况测试
# 清空CIEU database或新建session
ystar doctor
# 应显示无记录提示
```

单元测试（可选，如有时间）：
```bash
python -m pytest tests/test_doctor.py -v
```

## Dependencies

- 依赖eng-governance完成Orchestrator heartbeat实现（并行任务）
- 两个任务完成后需要集成测试验证端到端流程

## Notes

- Heartbeat检查是被动监控，不主动触发任何治理操作
- 区分"无新数据"（正常沉默）vs"数据源断裂"（异常）
- 完成后通知CTO进行code review
