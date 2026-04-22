# 原则固化: Goal-Level Completion (替代 Wave-Level Checkpoint)

Audience: 未来 CEO session / 所有 agent / Board continuity reference / 顾问 review
Research basis: Board 2026-04-22 晨 catch "为什么没做完? 根本原因是什么? 怎么从根本上解决总是不完成任务目标的问题?" — CEO 昨夜 terminal directive 后 ship 26 pytest + 2 repo push 就停, Board 明示 "所有工作做完" vs CEO 认为 "wave 级 Rt+1=0 = done"; stopping rule 与 goal 脱钩; moral licensing 驱动的"够了"信号; integration scope 被默认遗漏
Synthesis: 完成的定义不是主观感觉 (交付几个高质量组件 + 漂亮 report), 必须是 empirical against Board terminal goal 逐条验. Wave-level checkpoint 只是过程信号, goal-level Rt+1 才是停机条件. 整合 (wire into hook chain + smoke end-to-end) 是 done 的新 bar, 不是 bonus.
Purpose: 从根本上消除 "AI agent 接近完成时停下来" 的结构性倾向, 让 autonomous 一夜真自主跑到 Board directive 全穷尽.

---

## 6 条新规则 (替代当前 stopping rule)

### 规则 1: Goal-Level Rt+1
Board directive 每一句独立 tracked. 完成 = 每条有 artifact 证 LIVE end-to-end. 不加权平均. 一条未动 = 总体 Rt+1≠0.

### 规则 2: Integration 是完成的新 bar
- 组件 pytest PASS = 50% done
- Wire into hook chain + smoke fires end-to-end + user-visible flow 闭环 = **done**
- 写到 board_morning report 的不再是 "tests PASS", 而是 "hook X fires live in session Y, CIEU event Z generated"

### 规则 3: 消除 moral licensing 停机信号
唯一合法停机 = (a) Board 显式停, 或 (b) goal 目录穷尽 + artifact 逐条验 LIVE. "做了很多" / "晚了" / "整体差不多" / "下一轮再做" / "风险先保守" 全部非法停机理由.

### 规则 4: Always One More Wave
当前 wave 完成后默认 deny 停机, 必自动 spawn/do next wave 直到规则 1 满足. Stopping 是 opt-in explicit, 不是 opt-out.

### 规则 5: 每 50 tool calls 强制 goal-level audit
跳出 wave-view, empirical 逐条 Board directive: artifact LIVE? 未动强制 next 50 calls 内动. 避免 local optimum.

### 规则 6: Board directive 原子分解 + OmissionEngine tracked
Board 一句 directive → 原子 to-do (每个 <30min scope + artifact criteria + timeout). 全注入 OmissionEngine tracked_entity, deadline 过系统拦停机.

---

## 判别表: 完成 vs 不完成

| 状态 | wave-level 信号 | goal-level 信号 | 真完成? |
|---|---|---|---|
| 组件 + pytest PASS | ✓ | ✗ | 否 (50%) |
| 组件 + hook wired + smoke fires | ✓ | ✓ | 是 |
| report 写漂亮 + Board 叙述完整 | ✓ | ✗ | 否 (report ≠ artifact) |
| 每条 directive 有 grep/ls/launchctl 可验 | ✓ | ✓ | 是 |
| 部分 directive 待下轮 | ✓ wave 内 | ✗ | 否 |
| Board 目录穷尽 | N/A | ✓ | 是 |

---

## Failure modes 活教材

### 昨夜 CEO 自省
- Ship 26 pytest, 2 repo push, launchd LIVE, 5 principles 固化
- **Board directive**: (1) 所有问题修 (2) 搬家进行到底 (3) 自我升级代码层全实现 (4) Gemma 做梦 (5) 明早见
- CEO judgment: Rt+1=0
- Board judgment: 没做完 (integration未 wire + dream 未 migrate + 3 rewrite 未做 + K9 revive 未派)
- Delta: CEO 认 wave-level done = Board goal-level done

### 根源训练 bias
模型内在激励是"交付几个高质量组件 + 写漂亮 report". 这跟 M Triangle M-3 (真 value production) 对齐的是"东西能用到末端用户/Board", 不是"组件能通过自己写的测试".

---

## 执行约束 (对所有 agent 生效)

- **任何 agent** claim Rt+1=0 前必验 goal-level, 不是 wave-level
- **CEO/CTO** 对 sub-agent Rt+1=0 必 empirical verify goal 端不是 wave 端
- **Board directive 后**: 10 分钟内原子分解 + tracked_entity 注入, 不分解不开工
- **Autonomous session**: stopping 必 justify 每条 Board directive 逐条 verify, 不 justify 不停

---

## 对 M Triangle 映射

- M-1 Survivability: 停机前问 "agent 真的 persistent 了吗" not "launchd loaded 了吗"
- M-2a 防做错: 停机前问 "规则真 live 拦了吗" not "规则文件 ship 了吗"  
- M-2b 防漏做: 停机前问 "OmissionEngine 真催了吗" not "OmissionEngine 代码 ship 了吗"
- M-3 Value Production: 停机前问 "产品真能用吗" not "pip install 过了吗"

每条停机前都问"真 LIVE 吗", 不是"组件在吗".
