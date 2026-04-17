---
name: CEO Autonomous Loop (Board 静默时自主循环算法)
type: meta
discovered: 2026-04-16
trigger: Board "给自己写一个钩子 — 当 Board 三分钟没有指令后，开始思考下一步"
depth: foundational
---

## Claim
CEO 不需要 Board 每条消息都给指令。Board 静默 = CEO 自主循环的触发器，不是"等待"的信号。

## Algorithm (CEO Autonomous Operation Loop)

```python
def ceo_autonomous_loop():
    """当 Board 静默 ≥ 3 分钟时自动启动"""
    
    while mission_function_M(t) > 0:  # 使命未完成 = 永远循环
        
        # 1. 评估当前状态 Xt
        xt = assess_current_state()
        #   - AC score / HP score / K9 violations
        #   - 16 维度各维度得分
        #   - 哪些 enforce live / 哪些断裂
        #   - 哪些 sub-agent 在飞 / 哪些 idle
        
        # 2. 盘点资源
        resources = inventory_resources()
        #   - 人员: 谁 free? 谁在飞?
        #   - 机制: 哪些 hook/daemon/cron LIVE?
        #   - 数据: CIEU 事件 / wisdom / MEMORY
        #   - 代码: Y*gov 模块 / adapter / scripts
        
        # 3. 推导 Y* (从使命子目标函数)
        y_star = derive_next_subgoal(mission_M_t, xt)
        #   - M(t) 哪个维度最弱?
        #   - 弱维度的依赖前置满足了吗?
        #   - 满足 → Y* = 提升这个维度
        #   - 不满足 → Y* = 先提升前置维度
        
        # 4. 决定 U (用 U-action workflow 5 步)
        u = u_action_workflow(y_star, xt, resources)
        #   - research → learn → synthesize → match → decide
        #   - 谁做? CEO 不做 System 2-3
        #   - 怎么做? CZL 5-tuple dispatch
        
        # 5. 执行
        execute(u)  # dispatch via whiteboard / direct if urgent
        
        # 6. 记录实际结果
        yt_plus_1 = observe_outcome()
        
        # 7. 计算 Rt+1
        rt_plus_1 = measure_delta(y_star, yt_plus_1)
        
        # 8. 如果 Rt+1 > 0: 反事实修正
        if rt_plus_1 > 0:
            counterfactual_u = counterfactual_reason(u, yt_plus_1)
            # "如果换个 U 会 Rt+1=0 吗?" → 调整 → 重做
            u = counterfactual_u
            continue  # 回到 step 5
        
        # 9. Rt+1 = 0: 存 wisdom + cascade 下一目标
        save_wisdom_if_novel(xt, u, yt_plus_1)
        next_y_star = trigger_cascade(y_star)  # DAG 下一节点
        # 循环 → step 1 with new Xt
```

## Board 的原话
"当 board 三分钟没有指令后，我就开始思考我下一步的 U 是什么？Xt 是什么，我有什么样的针对于这个任务的资源...然后行动，记录下来实际结果 Yt+1, Rt+1 是否是 0？再推进一步，用反事实铆钉为 Rt+1=0...循环下一步"

## Implementation Path
1. 当前: 作为 CEO 思维方法论 (手动执行 loop)
2. 短期: governance_boot.sh 加 "idle-check" (Board 最后消息 > 3min → inject action queue reminder)
3. 中期: ADE autonomy_driver.py 升级 (pull_next_action 消费 mission sub-goal DAG)
4. 终极: cron + daemon 自动跑 loop (无 Board 也推进 → Level 3 真自驱)

## Connections
→ three_level_drive.md (this IS Level 3 implementation)
→ u_action_workflow.md (Step 4 的展开)
→ mission function M(t) (Step 3 的驱动源)
→ ADE autonomy_driver.py (Step 3 的 infrastructure)
→ Path A meta_agent.py (同构: GovernanceSuggestion → IntentContract → execute → judge)
