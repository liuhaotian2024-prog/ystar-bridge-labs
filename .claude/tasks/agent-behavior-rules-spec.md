# Agent Behavior Rules Engine — CTO执行规范
**日期**: 2026-04-10
**优先级**: P1 — 下一sprint重点
**批准人**: Board
**执行人**: CTO (Ethan Wright)

---

## 目标

将每个agent md中的可验证行为规则提取出来，通过boundary_enforcer适配器强制执行。
不是硬编码，是session config中的可配置规则（和cognitive_profiles/immutable_paths同一架构）。

## 架构

```
agent md中的规则 → 分类 → 行为规则（适配器强制）
                        → 输出规则（gov_precheck间接强制）
                        → 思维规则（不可强制，靠学习进化）
```

## 需要从agent md中提取的行为规则

### CTO (Ethan Wright)
- pre_commit_requires_test: commit前必须跑测试全过
- source_first_fixes: bug fix必须在Y-star-gov源码做，不能改site-packages
- fix_log_required: 每次fix后写reports/cto_fix_log.md

### CEO (Aiden Liu)
- directive_decompose_within_minutes: 10 — Board指令10分钟内分解
- must_dispatch_via_cto: true — 工程任务必须通过CTO，不能直接指挥工程师
- session_close_required: true — session结束必须运行session_close_yml.py
- twin_evolution_on_board_session: true — Board参与的session必须运行twin_evolution

### Secretary (Samantha Lin)
- weekly_audit_required: true — 每周一审计6岗位义务履约率
- audit_day: "monday"
- dna_distillation_requires_sources: true — DNA蒸馏必须附来源

### CMO (Sofia Blake)
- content_length_check: true — 发布前检查平台字数限制
- board_approval_before_publish: true — 外部发布需Board批准

### CFO (Marco Rivera)
- no_fabricated_data: true — 不能编造成本数据
- data_source_required: true — 每个数字必须有来源

### CSO (Zara Johnson)
- real_conversation_count: true — 日报必须包含真实外部对话数量

## Session Config格式

```json
"agent_behavior_rules": {
    "cto": {
        "pre_commit_requires_test": true,
        "source_first_fixes": true,
        "fix_log_required": true
    },
    "ceo": {
        "directive_decompose_within_minutes": 10,
        "must_dispatch_via_cto": true,
        "session_close_required": true,
        "twin_evolution_on_board_session": true
    },
    "secretary": {
        "weekly_audit_required": true,
        "audit_day": "monday"
    },
    "cmo": {
        "content_length_check": true,
        "board_approval_before_publish": true
    },
    "cfo": {
        "no_fabricated_data": true,
        "data_source_required": true
    },
    "cso": {
        "real_conversation_count": true
    }
}
```

## 适配器改动

boundary_enforcer.py新增 `_check_behavior_rules()` 函数：
- 从session config读取agent_behavior_rules
- 根据当前agent_id和tool_name，检查对应规则
- 例：ceo尝试spawn eng-kernel → 检查must_dispatch_via_cto → 如果是true且target不是cto → DENY

## 产品通用化

和cognitive_profiles/immutable_paths一样：
- Y*gov核心库提供规则引擎（通用）
- 每个客户在session config中配置自己的规则（个性化）
- JSON Schema文档供用户参考
- 默认值为空（不配就不检查）

## 完成标准

1. 所有agent md的可验证规则提取到session config
2. boundary_enforcer.py新增规则检查函数
3. 至少10个测试覆盖核心规则
4. 现有测试不回归
5. JSON Schema文档
