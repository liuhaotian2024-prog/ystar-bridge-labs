---
name: CEO Crisis Management — Cynefin Chaotic + Incident Response (学习笔记 Round 12)
type: ceo_learning
discovered: 2026-04-17
source: Cynefin chaotic domain + ISO 22361 + CEO incident response
depth: medium
---

## Cynefin Chaotic Domain — CEO 危机响应模型

### Act → Sense → Respond (不是 Sense → Analyze → Respond)
- **Chaotic ≠ Complex**: Complex 可以 probe → sense → respond。Chaotic 没时间 probe。
- **Chaotic 第一步 = ACT**: 先做决定稳住局面，对不对之后再说
- **然后 SENSE**: 行动后看哪里稳了哪里没稳
- **最后 RESPOND**: 把局面从 Chaotic 推到 Complex (可管理)

### Y* Labs 危机场景 + Playbook

| 危机场景 | Act (先做) | Sense (观察) | Respond (推到 Complex) |
|---|---|---|---|
| **API 挂 (Anthropic 服务中断)** | 切到 cached 回复 + 告 Board | API 多久恢复? 哪些任务受阻? | 降级模式 (Gemma local fallback) |
| **Board 不可达 >24h** | 按 mission function M(t) 自主推进 | Board 是暂离还是永久? | ADE pull_next_action 驱动 |
| **数据泄露 (Y*gov 含 Labs 数据 push 到 GitHub)** | 立即 `git revert` + force push 清除 | 谁拉过? 影响范围? | pre-commit hook 加固 + 全量审计 |
| **CTO hallucination 级联 (整个 session 基于假数据)** | 暂停所有 dispatch + freeze state | 从 CIEU event log 重建真实状态 | cieu_replay_recovery.py 修复 |
| **K9 + AC 全死 (监控全盲)** | 手动 4-daemon restart | 为什么全死? API 费用超限? 机器重启? | daemon 互相 watchdog |

### 危机管理 5 原则 (from ISO 22361 + Cynefin)

1. **速度 > 完美**: 80% 对的决定 NOW > 100% 对的决定 LATER
2. **稳住 → 理解 → 修复**: 不在 chaos 中分析根因 → 先止血
3. **沟通 > 沉默**: 告诉 Board "我们有问题 + 正在处理" > 等修好了再说
4. **事后复盘 ≠ 事后追责**: 复盘找系统因，不找个人错 (Antifragile: 从失败学习)
5. **每次危机 → 1 wisdom entry**: 危机后必存 wisdom (reasoning chain + counterfactual + prevention)

## CEO 危机方法论 v0.1

```python
def handle_crisis(crisis):
    # 1. Classify: 是真 Chaotic 还是只是 Complex?
    if can_probe_safely():
        return handle_as_complex()  # 不是危机，是复杂问题
    
    # 2. ACT FIRST (Cynefin Chaotic)
    immediate_action = best_guess_stabilization(crisis)
    execute(immediate_action)  # 不等完美方案
    
    # 3. SENSE
    stable_areas = identify_what_stabilized()
    unstable_areas = identify_remaining_chaos()
    
    # 4. RESPOND → push to Complex
    for area in unstable_areas:
        apply_known_pattern_or_experiment(area)
    
    # 5. POST-CRISIS
    write_wisdom_entry(crisis, actions, outcome)
    update_playbook(crisis.type)
    board_debrief(transparent=True)
```

## 与 Operating Manual 的集成
- Part 4 Decision Framework 的 Cynefin Chaotic 分支现在有详细 playbook
- Part 7 Risk 的 Black Swan section 每个场景现在有 Act-Sense-Respond 行动方案
- 新增: CEO 有权在 Chaotic 域 bypass 正常审批流程 (速度 > 流程)，事后补审
