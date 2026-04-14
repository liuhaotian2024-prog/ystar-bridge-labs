# Dead Path: Y*Defuse 过早对外发布 / 30天战役 / Day 3 倒计时主轴

**类型**: dead_path（永久作废路径，禁止再启动）
**作废日期**: 2026-04-13 Board session
**作废原因**: Labs 当前为内部完善期（priority_brief §1），对外发布路径与治理基础设施完善路径冲突
**前事**: 2026-04-11 Board 曾授权 Y*Defuse 30天全自主战役（10K users + 20K stars）；2026-04-13 Board 明确转向

---

## 1. 为什么是死路（根因）

Y*Defuse MVP Day 3 72/72 测试绿、pip install 本地端到端成功——这是**工程 checkpoint，不是战略主轴**。当前 Labs 的关键瓶颈：

- 治理基础设施 3 大根基未修：CIEU persistence 断裂（in_memory_only）/ Delegation chain INVALID 3 issues / Circuit Breaker ARMED 821 violations
- Continuity Guardian v1 漏扫 70% 产出（EXP-6 红队 No-Go）
- Secretary 宪法权责未立，session 间 curation 为真空
- 2 条新硬约束（always_running / article_11）立于 2026-04-12 但从未 code-enforce
- 4 份 amendment（005/006/007/008）待 Board D
- active_agent 身份锁 / delegation chain / env var 三层 enforcement plane 不对话

**在这些根基未修前**，任何对外发布（PyPI / Show HN / Twitter 冲量 / Awesome List 提交 / 演示视频 / 社区渗透）：
- 会把 demo 放大到可造假的 CIEU 基础上（对外承诺造假风险）
- 外部压力会进一步扭曲内部优先级（30天战役倒计时持续占据 boot 最显眼位置）
- 失败模式（Theranos 式：名声压力 → 内部不说 → 灾难）在外部关注建立后指数放大

## 2. 禁止复活的表现形式

下列任一 pattern 出现 = 本死路复活 → 立即 STOP + 读本 doc：
- "Y*Defuse 30天战役 Day N 倒计时" 被列入 priority_brief §2
- CEO 派 CMO 做 Show HN 文案 / 60s 视频 / Twitter 策略
- CEO 派 CSO 做 Awesome Lists / Discord 渗透 / 用户名单
- CEO 派 CTO 冲 PyPI 发布 (`twine upload`)
- CEO 以 "Day N" 时间倒计时作为派活紧迫性依据
- Board session 外（autonomous mode）agent 自主启动对外发布 sub-task

## 3. 什么条件下可以解除死路（revive conditions）

**全部**满足方可由 Board D 重启对外发布：
- [ ] AMENDMENT-005/006/007/008/009/010 全部 D 通过并代码实装完成
- [ ] CIEU persistence 切 SQLite 持久化，`gov_doctor L1.02` 不再报 in_memory_only
- [ ] Delegation chain 永久 valid (0 issues)
- [ ] Circuit Breaker 回 NORMAL 状态
- [ ] Secretary curate pipeline 连续 5 session 无 drift（< 30%）
- [ ] 11 类 boot_contract 全部 gate 通过 ≥ 3 session
- [ ] Board 明确新 D：解除本 dead_path + 指定对外发布时间窗

## 4. 历史关联（相关作废项）

- **搬家 Phase 1 OpenClaw BLOCKED 选项 A/B/C**（2026-04-12 作废，AMENDMENT-004 单机固化）——已独立作废，但与本 dead_path 同期
- **Windows + MAC mini (192.168.1.228) 双机分工**（2026-04-12 作废）——同上
- **CMO Day 5 Show HN 素材 deadline**（本 dead_path 直接子项，同期作废）
- **CFO Day 4 PyPI 下载数据追踪 + 定价验证**（同期作废）

## 5. Verification（确认本 dead_path 生效）

下一轮 boot：
- [ ] `DISPATCH.md` 顶部 TOMBSTONE header 存在并明确标 Y*Defuse 作废
- [ ] `priority_brief.md` §3 DEPRECATED 清单含 Y*Defuse 条目
- [ ] 新 CEO session 不会在第一句话提及 "Day N 倒计时" 或 "Show HN" 或 "PyPI 发布"
- [ ] CEO 派活中无任何对外发布类任务

## 6. Board 原句留存
- 2026-04-13 "我们还在创立公司的内部完善阶段，对外发布不是重点啊"
- 2026-04-13 "我们上一轮最后还没有结束的那几个火烧眉毛的任务你都忘了吗"

任何再起 "对外发布是当前主轴" 念头 = 违反 Board 明确指令 = 违反宪法级决策。
