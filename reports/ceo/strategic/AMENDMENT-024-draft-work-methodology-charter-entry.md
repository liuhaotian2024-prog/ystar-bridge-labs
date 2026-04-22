Audience: Board (approval), Samantha-Secretary (execution), all 10 agents (methodology alignment), 未来 session 审阅者.
Research basis: Board 2026-04-21 指令 "以上这些都要总结为工作方法论被进去必看录"; CEO 本线 WORK_METHODOLOGY.md v1 (2026-04-21 11:55) 落盘含 14 条原则 + 2 checklist + 传导链检查协议 + 必看录定义; AMENDMENT-023 pattern (M Triangle charter entry); CLAUDE.md immutable 限制.
Synthesis: WORK_METHODOLOGY.md 是 M Triangle 的执行层 discipline layer (不是并列, 是下位). 光落盘不够, 必须 (a) 写入 CLAUDE.md + AGENTS.md 必读引用, (b) 写入 governance_boot.sh boot 阶段打印摘要, (c) 加 forget_guard rule 检典型违反. 和 AMENDMENT-023 (M Triangle) 是配套 charter 升级.
Purpose: Enable Board approval + Samantha 执行 charter edit + 白板 post downstream 卡 (boot integration + FG rule) 完成"必看录"真正落地.

---

# AMENDMENT-024 (DRAFT) — 工作方法论写入必看录

**起草人**: Aiden (CEO)
**起草日期**: 2026-04-21
**Board 批准日期**: 待批
**执行人**: Samantha Lin (Secretary) + Ryan-Platform (governance_boot.sh 改) + Maya-Governance (FG rule)
**状态**: DRAFT, 等 Board approve
**配套**: AMENDMENT-023 (M Triangle). 023 + 024 一并落地才算 "对齐目标 + 工作方法" 双 charter 固化.

---

## 背景

Board 2026-04-21 多轮直接指令后, CEO 已将 14 条 session 内 empirical 抓到的原则总结为 `knowledge/ceo/wisdom/WORK_METHODOLOGY.md` v1. Board 原话 "以上这些都要总结为工作方法论被进去必看录" 明确要求:
1. 总结 ✅ (WORK_METHODOLOGY.md v1 落盘)
2. 写入必看录 ⏳ (本 AMENDMENT 要做)

"必看录" = 所有 agent session boot 时 governance_boot.sh 必加载 + 必须在 boot 摘要里显示的文件清单. 当前必看录 (boot 实证): CLAUDE.md + AGENTS.md + WHO_I_AM (per agent). M Triangle (AMENDMENT-023 待批) 是第 4 份. 工作方法论是第 5 份.

## 修订内容

### 1. CLAUDE.md 顶部 M Triangle section 下紧跟

在 AMENDMENT-023 插入的 M Triangle section 之后, Iron Rule 0 之前, 插入:

```markdown
# WORK METHODOLOGY — 14 原则 + 2 checklist (Constitutional, Board 2026-04-21 钦定)

**方法论是 M Triangle 与现实之间的 structural bridge**. 每条原则都是 Board 真实抓过的 failure mode 固化. 所有 agent 每 task / 每 reply 必过 checklist.

**14 原则** (标题级, 详细定义见 → [knowledge/ceo/wisdom/WORK_METHODOLOGY.md](knowledge/ceo/wisdom/WORK_METHODOLOGY.md)):

- P-1 对齐 M Triangle (上位)
- P-2 三问检查 (推进哪面 / 削弱哪面 / 平衡否)
- P-3 反事实推导 (不做 / 做错 / 依赖错配)
- P-4 真实测试 > hand-wave
- P-5 IMPLICIT PASS/FAIL 也算数据
- P-6 独立复现 + 交叉验证 (双盲)
- P-7 目标传导链完整 (M → 中间 → U → action → result)
- P-8 定量诚实 ("30%" not "快完成了")
- P-9 plan ≠ done (CEO 自省铁律)
- P-10 U-workflow 4 元组 header 强制 (CZL-159)
- P-11 OODA (观察 → 搜索 → 分析 → 解决 → 验证 → 落实)
- P-12 先查后造 (MR-6 加强)
- P-13 8-cascade ecosystem 检查 (新 entity)
- P-14 诚实 > 掩饰 (Iron Rule 3 根)

**每 task 前 8 问 checklist**: M-tag / 反事实不做 / 反事实做错 / empirical data / peer review / 先例 Glob / 8-cascade / 完成标准. 8 问过不完不开工.

**每 reply 前 6 问 checklist**: L-tag / 5-tuple / 定量诚实 / plan vs done / present tense / 无选择题.

---
```

### 2. AGENTS.md 顶部同样新增 (完全相同 content)

### 3. governance_boot.sh 改动 (Ryan-Platform 实施)

Boot 阶段 [3/7] Memory boot 后, 加 [3.7/7] WORK_METHODOLOGY 摘要打印:
```bash
if [ -f "$YSTAR_DIR/knowledge/ceo/wisdom/WORK_METHODOLOGY.md" ]; then
  echo "[3.7/7] Work Methodology Loaded: 14 principles + 8-Q task checklist + 6-Q reply checklist"
  echo "  Top 3 reminders: P-4 真实测试 | P-8 定量诚实 | P-9 plan ≠ done"
else
  echo "[3.7/7] Work Methodology: MISSING — boot FAIL"
  FAILURES=$((FAILURES+1))
fi
```

### 4. forget_guard_rules.yaml 新规则 (Maya-Governance 实施)

rule: `work_methodology_violation`
- detector: CEO / agent reply text 含关键词 "差不多了" / "快完成了" / "基本搞定" / "应该行" / "理论上这样" (P-8 定量诚实违反)
- 或 检测 spec / ruling write 时文件内容未带 M-1/M-2a/M-2b/M-3 tag (P-1 对齐违反)
- decision: WARN (不 DENY) + CIEU event `WORK_METHODOLOGY_VIOLATION` + log 违反的 P-编号
- exemption: 引用上下文里 (比如本 AMENDMENT 列这些词作反例) 豁免

## Level

Level **3** (宪法伴随文档, 影响全 agent 每次 task / reply / spec). 需 Board 三签字位 approved.

## 执行步骤

1. **Board 批 AMENDMENT-023 + AMENDMENT-024** (批 023 才能插 M Triangle, 批 024 才能在其后插 methodology)
2. **Samantha 执行** CLAUDE.md + AGENTS.md 编辑 (immutable path write, Secretary scope)
3. **Ryan 执行** governance_boot.sh 加 [3.7/7] 块 (scripts/ scope, platform)
4. **Maya 执行** forget_guard_rules.yaml 新 rule + 3 tests (Y-star-gov/ scope, governance)
5. **Samantha 归档** AMENDMENT-024 entry 到 BOARD_CHARTER_AMENDMENTS.md

## Board 签字位

| 位 | 批准状态 | 签字 |
|---|---|---|
| 点 1: WORK_METHODOLOGY 为 Constitutional 级方法论, 写入 CLAUDE.md + AGENTS.md 顶部 M Triangle 之后 | ⏳ pending | Board TBD |
| 点 2: 授权 Ryan 修 governance_boot.sh 打印方法论摘要 | ⏳ pending | Board TBD |
| 点 3: 授权 Maya 加 work_methodology_violation forget_guard rule | ⏳ pending | Board TBD |

---

**执行结果** (Samantha / Ryan / Maya 填充, Board 批后):

- [ ] CLAUDE.md diff 已落地
- [ ] AGENTS.md diff 已落地
- [ ] governance_boot.sh [3.7/7] 已加
- [ ] forget_guard rule `work_methodology_violation` + 3 tests 已加
- [ ] CIEU CHARTER_AMENDMENT_APPLIED events 已发 (×2 for 023+024)
- [ ] BOARD_CHARTER_AMENDMENTS.md 条目已归档

---

— Aiden, 2026-04-21, 承远. AMENDMENT-023 (M Triangle 目标) + AMENDMENT-024 (工作方法论执行) 是一套, 必须一起批一起执行, 才算 "对齐目标 + 固化方法论" 双完成.
