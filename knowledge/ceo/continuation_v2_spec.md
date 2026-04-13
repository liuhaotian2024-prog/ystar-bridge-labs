# Session Continuation Protocol v2 — 机器语言版
# Board指示：像hook一样用代码强制执行，不依赖LLM主动性

## 设计原则
hook解决"不能做什么"（deny违规行为）
continuation解决"必须做什么"（enforce正确行为）
两者都是代码层确定性执行，不是自然语言建议

## 实现：3个文件

### 1. memory/continuation.json（session_close时自动生成）

```json
{
  "generated_at": "2026-04-11T20:30:00",
  "generated_by": "ceo",
  "campaign": {
    "name": "Y*Defuse 30天战役",
    "day": 1,
    "start_date": "2026-04-11",
    "target": "10K users + 20K stars"
  },
  "team_state": {
    "cto": {"task": "defuse MVP Level 2", "progress": "layer_4", "blocked": false},
    "cmo": {"task": "README + Show HN", "progress": "drafting", "blocked": false},
    "cso": {"task": "社区渗透计划", "progress": "planning", "blocked": false}
  },
  "action_queue": [
    {
      "seq": 1,
      "action": "check_delivery",
      "agent": "cto",
      "command": "ls /path/to/ystar-defuse/setup.py",
      "success_criteria": "file exists",
      "on_fail": "dispatch to CTO as P0"
    },
    {
      "seq": 2,
      "action": "review_quality",
      "agent": "cmo",
      "command": "head -30 content/show_hn_ystar_defuse.md",
      "success_criteria": "file exists with content",
      "on_fail": "dispatch to CMO"
    }
  ],
  "anti_patterns": [
    "report_plumbing_to_board",
    "ask_board_approval_for_decided_items",
    "list_choices_instead_of_deciding"
  ]
}
```

### 2. governance_boot.sh Step 10（解析JSON输出可执行指令）

```bash
python3 -c "
import json
with open('memory/continuation.json') as f:
    c = json.load(f)
campaign = c.get('campaign', {})
print(f'CAMPAIGN: {campaign[\"name\"]} — Day {campaign[\"day\"]}')
print(f'TARGET: {campaign[\"target\"]}')
print('ACTION QUEUE:')
for a in c.get('action_queue', []):
    print(f'  [{a[\"seq\"]}] {a[\"action\"]}: {a[\"command\"]}')
    print(f'      on_fail: {a.get(\"on_fail\", \"\")}')
print('DO NOT:', ', '.join(c.get('anti_patterns', [])))
"
```

### 3. hook_wrapper.py — continuation compliance检测

```python
def check_continuation_compliance(tool_name, tool_input, call_count):
    """Session前5个tool call必须和action_queue相关。
    如果agent在查CIEU/session.json等水管活，warn它回到action_queue。"""
    
    if call_count > 5:
        return None  # 只enforcement前5个call
    
    cont = json.load(open('memory/continuation.json'))
    anti = cont.get('anti_patterns', [])
    
    # 检测anti-pattern
    if tool_name == 'Bash':
        cmd = tool_input.get('command', '')
        if any(x in cmd.lower() for x in ['cieu', 'session.json', 'omission']):
            if 'report_plumbing_to_board' in anti:
                return {'action': 'warn', 
                        'message': '[CONTINUATION] 前5个动作应执行action_queue，不是查水管。'}
    
    return None
```

## 对比

| | v1 markdown | v2 JSON+hook |
|---|---|---|
| 格式 | 散文 | 结构化JSON |
| 强制力 | 0 | hook层warn/block |
| 解析 | LLM理解 | python3 json.load |
| anti-pattern | 当建议 | 代码检测 |
