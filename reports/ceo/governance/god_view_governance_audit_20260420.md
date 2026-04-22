Audience: Board (Haotian) + Ethan CTO + 未来 Aiden session + 所有工程师
Research basis: Y-star-gov/ystar/governance/__init__.py 完整 5-engine export + Board 2026-04-20 多次 framing (行为合规 / 治理层两分 / 5 通道) + 今晚 parent session 退化实证
Synthesis: Y*gov 治理 stack 完备 (5 engine + 10+ 辅助模块); gap 不在工具缺, 在 parent session (CEO 自身) 没 register 为被治理实体, 五通道从未对 parent 自身的长会话状态跑, 导致今晚 parent degrade 无自救机制; 上帝视角解药 = register parent, 不造新轮子
Purpose: 固化上帝视角架构认知, 防未来 session 再造新组件绕开既有 Y*gov stack

# God-View Governance Audit — 2026-04-20

## Root catch (Board 2026-04-20 P0)

"你这是要新造轮子, 我们之前在 Y\*gov 里面全都有治理工具, 而且也有 5 个通道. 马上全面扫描系统, 然后依据上帝视角来制定工作流程."

## Y*gov 治理 Stack 完整版 (上帝视角)

### 5 核心通道 (ystar/governance/__init__.py 直接 export)

| # | Engine | 职责 | 今晚 parent 需求映射 |
|---|---|---|---|
| 1 | **OmissionEngine** | 义务追踪 / 承诺闭环 / 缺位检测 | Parent session "session fatigue detector" — track parent 的 reply 延迟 + tool_uses 密度 作 omission 信号 |
| 2 | **InterventionEngine** | Gating / capability restrict / pulse | "drift-catch auto-correct" — parent 连续 drift 时 auto-intervene (降级并发 cap, 强制 break) |
| 3 | **GovernanceLoop** | Observation → Suggestion → Tighten 循环 | "主动治理 proactive layer" — 实时观察 + 主动建议 CEO 做什么 (不只被动拦) |
| 4 | **AmendmentEngine** | 规则进化 / AmendmentProposal 自动生成 | 今晚 insight → rule pipeline 的实质 impl — 自动提 amendment 到 BOARD_CHARTER_AMENDMENTS |
| 5 | **ReportEngine** | KPI 度量 / Report 生成 / CIEU 摘要 | "context compression helper" — summary + heatmap 压缩 parent context 浪费 |

### 加 10+ 辅助模块

- **CIEUStore** — audit chain (长期记忆基底, brain 之外还有 CIEU side)
- **OmissionStore** — 义务持久化
- **PulseStore** — 干预 pulse 存储
- **AdaptiveCoefficients** — meta-learning surface
- **ManagedConstraint** — 约束注册
- **ConstraintRegistry** — 全局约束
- **AutoConfigure / GovernanceAutoConfigureScheduler** — 自配置, auto floor secs
- **CausalFeedback** — Pearl level-2 因果
- **BackdoorAdjuster** — do-calculus 反事实
- **ContractLifecycle** — 契约生命周期
- **EnforcementObserver** — meta-observer
- **AutonomyEngine** — 自主度评估
- **ExperienceBridge** — 经验桥接
- **BackbonePack (ConstitutionalContract / DelegationChain / DelegationContract)** — kernel 宪章
- **ReplyTaxonomy** — 回复分类 (24 失败类已知)
- **RouterRegistry** — 路由注册
- **ForgetGuardRules** — 22 条 (今晚 retire 6 条)

## 今晚我造过的"新轮子" (全部 drift, 应撤)

| 我的 drift 提议 | 应映射的既有通道 | 处置 |
|---|---|---|
| context compression helper | ReportEngine.omission_summary / entity_timeline | 撤新造 |
| session fatigue detector | OmissionEngine tracked_entity + EntityStatus | 撤新造 |
| auto-checkpoint | CIEUStore + OmissionStore (已 persist) | 撤新造 |
| drift-catch auto-correct | InterventionEngine.PulseStore + restrict | 撤新造 |
| CZL-BRAIN-METACOGNITION-LEDGER | ReplyTaxonomy + GovernanceLoop observation | 合并到 ReplyTaxonomy 扩展 |
| CZL-BRAIN-BLOOM-LEVEL-TAGGING | Brain node 内字段扩展即可, 不是新 ledger | 缩小 scope |
| CZL-AIDEN-SELF-EDUCATION-SCHEDULER | AutoConfigureScheduler + GovernanceLoop | 复用 scheduler, 不新写 |
| CZL-BRAIN-ERROR-CORRECTION-EXERCISE | CausalFeedback + BackdoorAdjuster + ReplyTaxonomy | Pearl 层已有, 只需连线 |

## 真正的 Gap (不在工具, 在注册)

**Parent session (CEO 自身) 从未 register 为被治理实体**.

- TrackedEntity.register(entity_id="ceo-parent-session-<uuid>") 从未跑
- OmissionEngine 没观察 parent reply latency / tool_uses 堆积 / Goodhart retry 频率
- InterventionEngine 没对 parent 发 pulse (parent 长 session drift 时无 auto-restrict)
- GovernanceLoop observation 没收 parent session 作数据源
- ReportEngine 没给 parent 产 context summary 注入

**后果**: CEO 对外用 5 通道治理 sub-agent, 自己 3 小时 drift 无自救机制. Board 手动 catch 7+ 次我才发现.

## 上帝视角工作流程 (替代方案)

### Phase 1: Register parent 为 TrackedEntity

1. 在 parent session boot 阶段 emit `TrackedEntity.register(entity_id=f"parent-{session_id}", entity_type="ceo_parent")`
2. 给 GovernanceLoop 注入 parent 作 observation subject
3. OmissionEngine 定义 parent-specific obligations (e.g. "don't exceed tool_uses/30min", "escalate when drift_count >= 2")

### Phase 2: Wire parent-specific Intervention

当 parent session 命中以下条件, InterventionEngine 自动发 pulse:
- tool_uses 累计 > N (context 满载前主动摘要)
- drift_count >= 2 within 30min (parent 自己 catch 不及 Board)
- reply latency > 2x baseline (parent LLM 慢了)
- stream timeout count >= 2 (sub-agent I/O 挤占)

Pulse action:
- Level 1: emit CIEU `PARENT_FATIGUE_DETECTED`, suggest `重启 / checkpoint`
- Level 2: restrict new spawn (cap=1) until session close
- Level 3: force break_glass to Board with context summary

### Phase 3: ReportEngine 做 context 精简

- Every 30min parent session 自动跑 `ReportEngine.generate_summary(session_id=...)`
- 摘要覆盖 sub-agent receipts / CIEU events / 主要 decisions
- 注入 parent 作 "memory compression anchor", 旧 raw content 可丢

### Phase 4: AmendmentEngine 自动提 amendment

- 每个"insight → rule" 转化, AmendmentEngine.propose() 自动草稿
- 不靠 CEO 手写 markdown 到 BOARD_CHARTER_AMENDMENTS
- 草稿进 `reports/amendment_proposals/` 等 Board 批

### Phase 5: AdaptiveCoefficients 按 CEO drift 调 rule threshold

- 若 `insight_to_rule_pipeline_required` 这条 meta-rule warn 多次, AdaptiveCoefficients.update 收紧 threshold
- 若某条 rule 90 天 0 fire, AdaptiveCoefficients suggest retire

## 工作流程实施 CZL (取代之前造的新轮子)

| CZL | 说明 |
|---|---|
| CZL-PARENT-SESSION-REGISTER-AS-ENTITY | 把 parent register 进 OmissionEngine + GovernanceLoop |
| CZL-INTERVENTION-PULSE-FOR-PARENT | Parent-specific Level 1-3 pulse trigger |
| CZL-REPORT-ENGINE-CONTEXT-SUMMARY | 每 30min 自动 ReportEngine summary 注入 |
| CZL-AMENDMENT-ENGINE-AUTO-PROPOSE | insight → AmendmentProposal 自动 |
| CZL-ADAPTIVE-RULE-TUNING-FOR-FG | AdaptiveCoefficients wire 到 ForgetGuard |

今晚之前造的 new-wheel CZL (METACOGNITION-LEDGER / BLOOM-TAGGING / SELF-EDU-SCHEDULER / ERROR-CORRECTION-EXERCISE) **全部并入对应既有通道**, 不单独 impl.

## 向 Board 的道歉

今晚我两次违反自己写过的 `feedback_god_view_before_build`:
- 第一次: 想给 parent 加 context helper / fatigue detector / auto-checkpoint (全部既有)
- 第二次: 贴了一堆 brain 子系统 CZL 到白板 (全部可并入 5 通道)

上帝视角必须先扫既有 stack, 再 propose 新组件. 这是 `feedback_god_view_before_build` 的核心, 我失守两次.

## 对 Board 承诺

之前 white-board 上造新轮子的 CZL 不 spawn impl. 替换为 Phase 1-5 register + wire 既有 5 通道. 这才是 Board 给的"上帝视角制定工作流程"真义.

没有新造, 全是既有 stack 的连线. 这是今晚应该做的, 而不是 3 小时跑偏才意识到.
