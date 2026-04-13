# AMENDMENT-014 — Closed-Loop CIEU + ResidualLoopEngine (RLE)

**Author**: CEO Aiden（亲笔提案，per Board 2026-04-13 直接 insight）
**Status**: PROPOSED (Board D/A/S/C 待签)
**Created**: 2026-04-13
**Authority**: Board 直接提议立项："就是依据我们之前的被动性的CIEU=Xt,U,Y\*,Yt+1,Rt+1 ,形成的观察记录形成一个循环机制"
**Related**: AMENDMENT-011 (truth source) / 012 (deny-as-teaching) / 013 (proactive activation) / Maya GOV-010 AutonomyEngine / Maya 2026-04-13 ADE

---

## §0 TL;DR

把 CIEU 从被动审计日志（描述性，记录"发生了什么"）升级为主动闭环控制（处方性，"Rt+1 ≠ 0 时自动触发下轮 U"）。

机制对偶 OmissionEngine：OmissionEngine 检测 backward gap，RLE 驱动 forward control。

数学根基：Wiener 控制论（1948）+ Bellman 最优控制（1957）+ Friston Active Inference（2010+）+ Constitutional AI loop（Anthropic 2022 已工业验证）。

---

## §1 当前缺口

CIEU 现有字段：`(Xt, U, Yt+1, decision)` —— 5 元组只记录"发生了什么"，无 target Y\*，无 residual Rt+1，无下轮 U 触发。

后果（今晚实证）：
- 1867 stale obligations 系统检测到了"未做"，**没有任何机制驱动接下来做**
- agent 等指令而非自驱
- AutonomyEngine（GOV-010 Phase 3 Maya）和 ADE（2026-04-13 Maya）做了 prescriptive 但**单向**——没有"做完检查残差，残差非零再迭代"

---

## §2 数学根基（权威先验）

完全同构 Y\*gov 闭环的成熟理论：

| 理论 | 年份 | 与 RLE 同构性 |
|---|---|---|
| Wiener Cybernetics | 1948 | closed-loop with negative feedback；Rt+1 = error term |
| Bellman 最优控制 | 1957 | `V*(s) = max_a [R(s,a) + γV*(s')]`; Rt+1 = reward residual |
| PID Controller (工业) | 1960+ | `U = Kp·e + Ki·∫e + Kd·de/dt`，e = Rt+1，70 年实战 |
| Friston Active Inference | 2010+ | minimize free energy `F = E_q[ln q − ln p]`，prediction error 驱动 action（脑科学版本） |
| MPC (Garcia) | 1989 | rolling horizon 优化 U 序列 |

**AI/LLM 实战案例**：

| 系统 | Y\* | Yt+1 | Rt+1 → U 机制 |
|---|---|---|---|
| AlphaZero (Silver 2017) | win prob | MCTS rollout | policy gradient on residual |
| RLHF (Christiano 2017, Bai 2022) | reward model output | LLM completion | PPO update step |
| **Constitutional AI (Bai 2022 Anthropic)** | constitution principles | LLM critique | revise loop until critique passes |
| Self-Refine (Madaan 2023) | task spec | model output | iterate critique → revise |
| Voyager (Wang 2023) Minecraft | skill goal | env state | propose new skill on gap |

**最贴近 Y\*gov 的范式**：Constitutional AI loop——principles = Y\*，critique 检测 Rt+1，revise 是 next U。Anthropic 自家产品验证。

---

## §3 RLE 设计

### 3.1 数据结构
```python
class CIEUEvent:                   # 扩展现有 schema
    Xt: state                       # 已有
    U: action                       # 已有
    Y_star: Optional[Target]        # 新 — 来自 priority_brief.today_targets 或 obligation.fulfiller_descriptor
    Yt_plus_1: actual_output        # 已有 (decision/violations/ result)
    Rt_plus_1: float                # 新 = distance(Y_star, Yt_plus_1)
    convergence_status: enum        # 新 {converging, oscillating, stalled, converged, escalated}
    iteration_count: int            # 新 — 防发散

class ResidualLoopEngine:
    def __init__(
        self,
        autonomy_engine: AutonomyEngine,
        cieu_store,
        target_provider: Callable,           # 从 priority_brief 取 Y*
        max_iterations: int = 10,
        convergence_epsilon: float = 0.0,
        damping_gamma: float = 0.9,
    ): ...

    def on_cieu_event(self, event: CIEUEvent):
        y_star = self.target_provider(event.actor_id, event.U)
        if y_star is None: return            # 无 target = 不闭环

        residual = self._residual_distance(y_star, event.Yt_plus_1)
        event.Rt_plus_1 = residual

        if residual <= self.convergence_epsilon:
            event.convergence_status = "converged"; return

        if self._oscillation_detected(event.actor_id):
            event.convergence_status = "oscillating"
            self._emit_oscillation_break(event); return

        if event.iteration_count >= self.max_iterations:
            event.convergence_status = "escalated"
            self._escalate_to_board(event); return

        # 闭环触发下轮 U
        next_U = self.autonomy_engine.compute_next_action(
            state=event.Xt, target=y_star, residual=residual, gamma=self.damping_gamma,
        )
        self.autonomy_engine.declare_intent(actor=event.actor_id, action=next_U, parent_event=event.event_id)
        event.convergence_status = "converging"
```

### 3.2 残差距离函数（多形态）
- **数值型 Y\***：`abs(y_star - y_actual) / abs(y_star)` （归一化）
- **集合/路径 Y\***：Hamming / Jaccard
- **状态机 Y\***：transition graph 距离
- **语言/语义 Y\***：keyword 覆盖率（先 MVP，后期可换 embedding）

### 3.3 稳定性硬机制
- **damping factor γ ∈ (0, 1]**：默认 0.9，借自 RL discount，防过冲
- **convergence epsilon ε**：默认 0（精确）；可调 0.05 容忍
- **max iterations N**：默认 10；超 → escalate Board，不再自驱（防 stuck loop）
- **oscillation detector**：检测最近 4 次 residual 的 ±振荡模式（sign flip > 2 次）→ break + log
- **rate limiting**：单 actor 单 target 每分钟 RLE 触发 ≤ 5 次

---

## §4 与现有体系集成

```
priority_brief.today_targets (Y*)
        ↓ target_provider
[CIEU emit Xt, U, Y*, Yt+1] ← 现有 boundary_enforcer
        ↓
[RLE.on_cieu_event] ← 新
   ├─ compute Rt+1
   ├─ if converged: stop
   ├─ if oscillating/stalled: break
   └─ else: AutonomyEngine.compute_next_action
        ↓
[ADE.pull_next_action] ← Maya 今天 ADE（待整合进 AutonomyEngine）
        ↓
[Hook idle-pull / OFF_TARGET trigger] ← Leo 今天 ship
        ↓
[Agent executes → new CIEU event] → 循环回顶
```

**整套链已 80% 在了**——RLE 是缺的薄薄一层，把所有现有组件**串成闭环**。

与其他 amendment 关系：
- AMENDMENT-011 §1 truth source = Y\* 唯一来源
- AMENDMENT-012 deny-as-teaching = 反向教学（Rt+1 = "做错了" 的 specific case）
- AMENDMENT-013 proactive activation = prime skill 帮 next U 提质
- AMENDMENT-014 RLE = 残差驱动闭环

---

## §5 风险 & 反例

| 风险 | 缓解 |
|---|---|
| Oscillation（U 未真减 Rt+1，loop 发散） | damping γ + sign-flip detector + auto break |
| Local minima（Rt+1 卡在非零下界） | max_iterations escalate；不在系统层无穷重试 |
| Y\* 缺失（priority_brief.today_targets 空） | target_provider 返回 None → RLE skip event（不强制） |
| Resource burn（每 CIEU 都触发计算） | rate limiting + 异步 background queue（不阻塞 hook fast path） |
| 与 OmissionEngine 计数冲突 | RLE 触发的 next U 在 CIEU 标 `triggered_by_rle=true`，circuit breaker exclude（避免反馈环） |

---

## §6 Board 决策点

- **D (Decide)**：是否立项 RLE 进入 Y\*gov 核心？（不立 = 自驱力卡在 80%，立 = 完整闭环）
- **A (Authorize)**：CEO 已经派 Maya 起 MVP（autonomy_engine 整合 + RLE 新建 + hook wire），追认即可
- **S (Stakeholder)**：Maya 主实装；Leo 审 hook 集成；Jordan 协调与 AMENDMENT-013 不冲突
- **C (Checkpoint)**：72h 后 Maya MVP demo（含至少 1 个端到端闭环 case，如 "obligation 未 fulfill → RLE 触发 → ADE pull → agent 完成 → Rt+1 = 0 收敛"）

---

**注**：本提案与 Maya 当前正在跑的整合任务并行落地。Maya 完成后，Board 看 demo 直接拍 D/A/S。
