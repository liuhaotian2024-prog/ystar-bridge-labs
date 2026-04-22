# 原则固化: Agent Self-Modification in Bounded Scope

Audience: 未来 CEO session / Ethan CTO / Maya Governance / Leo Kernel / Board continuity reference / 顾问 review
Research basis: Board 2026-04-21 night 原话 "其实这一条也可以变通一下, 自己要改代码的时候可以提请 Board 申请, 批准后可以. 不过这些都是只限于 Labs 运营团队, 不能涉及到其他仓库"; Gödel Agent (arxiv 2410.04444) + Darwin-Gödel Machine (Sakana) + Huxley-Gödel (arxiv 2510.21614) 已有 recursive self-improvement 架构; 我们 AMENDMENT 系统 (governance/BOARD_CHARTER_AMENDMENTS.md) 已累积 23+ 条历史修订记录
Synthesis: AI agent self-modification 不是绝对禁止, 而是**双约束下开放**. 约束 1 scope 限定 Labs 运营 repo (ystar-company); 约束 2 程序经由 AMENDMENT 机制 Board 批准. 这把 Gödel-pattern 合法化, 同时保持 Board 对产品 + 外部 repo 的硬边界. 关键洞察: 我们现有 AMENDMENT 系统本来就是 Darwin-Gödel archive 的"人工审批版", 升级只需让 agent 自动生成 AMENDMENT proposal, infra 都有.
Purpose: 替代之前"Gödel 不采纳"的判断; 指导未来 self-modification milestone 的 scope 边界 + 机制设计

---

## Scope 白名单 (可改)

- `ystar-company/scripts/**` (Labs 运营脚本 — hooks, daemons, brain, governance glue)
- `ystar-company/.claude/agents/**.md` (agent prompts/skills — self-tuning scope)
- `ystar-company/knowledge/{role}/**` (agent 自我知识库, sensitive: knowledge/ceo/wisdom/ 需 Board 签)
- `ystar-company/reports/**` (自己写自己的报告)
- `ystar-company/governance/{非宪法性}` (dispatch_board, enforce_status_dashboard 等运营态, BOARD_CHARTER_AMENDMENTS.md 仍 Board-only)

## Scope 黑名单 (agent 绝对不碰, 即使申请也 deny)

- `Y-star-gov/**` (产品 source, MIT license, 外部用户, 改动 = 产品变更, Board + CTO 双签)
- `gov-mcp/**` (产品 MCP server)
- `K9Audit/**` (上游 read-only per CLAUDE.md)
- `ystar-company/governance/BOARD_CHARTER_AMENDMENTS.md` (宪法档, Board-only)
- `ystar-company/CLAUDE.md` + `AGENTS.md` 根目录宪法级 (Samantha scope, 需 AMENDMENT header)
- 任何 external repo / GitHub org

## 机制: agent-driven AMENDMENT 流程

现有 AMENDMENT 流程是 Board/CEO 手动发起. 升级为 agent 可自主发起 proposal:

1. Agent 发现 gap (e.g., "scripts/X.py 有 pattern 我应该改") → 在 CIEU 发 `SELF_MOD_PROPOSAL` 事件
2. 同时生成 `reports/cto/amendment_draft_<ts>.md`, CZL-159 header + before/after diff + rationale
3. OmissionEngine tracked_entity 催 Board review, deadline 可配 (默认 72h)
4. Board review: accept / reject / request-change. Accept → Samantha 归档 + 执行 edit
5. 执行后 pytest 回归必 PASS, 否则 auto-rollback

## 风险分层 (3 tier)

| Tier | 例子 | 审批流 |
|---|---|---|
| Low | 改自己 prompt / 自己的 knowledge node / 自己 report 格式 | 轻量 AMENDMENT (Board 默认 24h 无异议 = 批) |
| Medium | 改 hooks / daemons / brain pipeline 逻辑 | 标准 AMENDMENT + pytest 回归 + CIEU smoke |
| High | 改 governance core (forget_guard / boundary_enforcer / CIEU schema) | AMENDMENT + Board 必审 + peer agent review + 48h cooldown |

## 与 M Triangle 对齐

- **M-1 Survivability**: agent 可自进化 = 生存能力升级 (跨 session / 跨硬件 / 跨 API 之外, 再加跨版本自持)
- **M-2a 防做错**: AMENDMENT 流程本身是 commission 过滤
- **M-2b 防漏做**: Tracked entity + deadline 催 Board review, 不让 proposal 烂在队列
- **M-3 Value Production**: 这是 Y\*gov 的**产品 demo** — "governed AI agent can safely self-modify in bounded scope"

## 与外部前沿对齐

- Gödel Agent (arxiv 2410.04444): agent 自决 utility 函数 → 我们 utility = M Triangle, Board 钦定, agent 不自决顶层
- Darwin-Gödel (Sakana): archive 所有 self-modified variants → 我们 archive = BOARD_CHARTER_AMENDMENTS.md
- Huxley-Gödel (arxiv 2510.21614): 搜索 self-mod 树 → 我们先不搜索, 由 agent 按需 propose 一条 path

## 不做 (保留未来)

- 全自动 merge (无 Board 审批) — 除非 low tier 且 48h Board 无异议才 auto-accept
- Cross-repo self-mod (Y-star-gov 等) — 产品变更永远 Board + CTO 双签
- self-rewrite utility function (不自改 M Triangle / WORK_METHODOLOGY 顶层)
