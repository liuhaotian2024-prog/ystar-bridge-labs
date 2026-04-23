---
goal_id: Y_001 + Y_004 (deferred)
reason: Board 2026-04-23 directive — gov-mcp 真实维度成熟度不足, 卖线排后, 先办公室
status: ARCHIVED (pending un-defer when办公室 complete + due-diligence 调研完成)
---

# gov-mcp 卖线 — 存档清单 (2026-04-23 Board decision)

Board directive: "卖 gov-mcp 这项工作应该排在后面，实现的部分先存档，等眼前的其他工作完成后再上". 

当前现实: gov-mcp 本身真维度实现深度不足 (场泛函 L2-L3 / 99 failing tests / 无真使用时长 data / ICP 没做 / 治理路径可能 duplicate).

**本 manifest 锁定当前所有 gov-mcp 相关 artifacts**. 办公室完成 + Leo/Ethan due-diligence 回后, 开箱.

## 已落 artifacts (都 deferred 不丢失)

### 价格策略
- `reports/ceo/pricing_proposal_v1_20260423.md` — CEO v1.1 (3-tier Dev/Team $129/Enterprise $2500+$500). 未 Board ratify.
- `reports/cfo/pricing_v1_review_20260423.md` — Marco CFO review (SHIP WITH ADJUSTMENTS), 数据 gap 标 CASE-002
- 下一步 (解冻后): (1) CTO dogfood compute COGS measurement (2) Zara CAC model (3) Board ratify (4) move → `finance/pricing_v1.md` (5) Stripe SKU setup

### 产品文档
- `products/ystar-gov/docs/install.md` — Ethan 257 行 install guide (6 sections, 875 words). 命令 cross-ref Y*gov 源码 verified. 
- TODO 解冻后: endpoint ref / examples

### 测试基线 + triage
- `reports/platform/test_coverage_baseline_20260423.md` — Ryan baseline 53% coverage / 100 failing tests / top 3 gaps (metalearning 27% / prefill 31% / dimensions 58%)
- `reports/platform/test_failure_triage_20260423.md` — Ryan triage: **82 regressions 源自 c1f38c9 (2026-04-21 WIP commit)** 机械可修; 6 real-bugs; 5 obsolete; 4 flaky; 3 dep. Attack order: regressions → real-bugs → skip obsolete → flaky → dep
- TODO 解冻后: 批量修 82 regression 一次性 → 补 27pt coverage to 80%

### P0 非 gov-mcp 独立 hot-fix 发现 (本存档外, 需独立跟进)
- **`ystar/governance/intervention_engine.py:515`** 使用 `os.environ.get(...)` 但文件头**缺 `import os`**, 触发 NameError. Path: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/intervention_engine.py`
- 当前热度: 0 CIEU hit in 24h (不常跑), risk 低但非零; 如果 actor 有 hard_overdue 提示触发就 crash
- Fix: 单行 `import os` 加在 line 27 之后
- **不 park 到 gov-mcp manifest** — 这是 live 治理代码 bug, 下次 Leo/kernel dispatch 窗口插队修

### 市场/战略 (部分)
- `sales/cso_patent_report_001.md` — 专利 US 63/981,777 filed 2026-03-26 (Merkle sealing wire-up 已 retroactive fix)
- `content/arxiv/pearl_architecture_argument.md` — arxiv CIEU ≅ P(E|do(I=Y*_t)) 数学 isomorphism claim
- `content/whitepaper/enterprise_compliance_audit_trails.md` — whitepaper
- `reports/ceo/strategic/field_functional_claims_audit_20260423.md` — general-purpose external claims audit (patent LIABILITY 已降等)
- TODO 解冻后: Sofia+Zara 完整市场企划 v1 (ICP / GTM / 定位 / 渠道 / compete matrix)

### 专利维护
- `reports/kernel/patent_claim1_runtime_audit_20260423.md` — Leo Q1-Q3 audit (contract_hash kernel-only LIVE / Merkle sealing LINE_DRIFTED + DEAD → Leo wire-up 已 fix)
- `reports/kernel/patent_claim1_wireup_receipt_20260423.md` — 659K sealed events + 29K sealed_sessions
- 专利行号漂移 Samantha 归档 `ARCH-2026-04-23-PATENT-DRIFT` 截止 2027-03-26

### 场泛函 3-Phase infra (保留 live — 不存档)
- Phase 1 m_functor 分类: `scripts/_cieu_helpers.py` inference layer + `scripts/field_coverage_dashboard.py` + 每 15min cron backfill
- Phase 2 role_scope + goal_tree: `scripts/phase2_*.py` + `scripts/y_star_field_validator_run.py`
- Phase 3 NL → tree: `scripts/phase3_goal_decomposer.py` (Gemma + role_scope keyword inference)
- 这些基础设施**继续跑**不存档, 办公室不需要推进但他们是 infra, 跑着就行
- **未来 gov-mcp 解冻时, 场泛函深度可以绑 Y_002 办公室任务驱动 iterate, 再补 L4 signal 深度**

### Goal tree 状态 (db 已更)
- `Y_001` + `Y_001_1..4`: status=`deferred`
- `Y_004` + `Y_004_1..5`: status=`deferred` (Phase 3 auto-generated gov-mcp tree, same deferral scope)
- `Y_002` + `Y_002_1..4`: status=`active` — **办公室, 焦点**
- `Y_003` + `Y_003_1..4`: status=`active` + 已完成 (场泛函 Phase 2 infra)

## Due-diligence 调研 (派出去的先完成, 之后合并)

- 调研 #1 (LIVE bg): Leo gov-mcp vs Y*gov 两路径 audit — 让他跑完, 结果存档
- 调研 #2 (queued, NOT dispatched): Ethan gov-mcp 12 维度盘点 — **保持 queued 不 spawn** per Board
- 调研 #3 (queued, NOT dispatched): Sofia+Zara 市场企划 v1 — **保持 queued 不 spawn** per Board
- Ryan Y_001_2 triage (LIVE bg): 让他跑完, 结果存档到本 manifest 下

## 未来解冻 condition (Rt+1=0 path to un-archive gov-mcp 卖)

1. Y_002 办公室 MVP 全 4 sub-goals LIVE + Board 验收 (工程能力 + 思考+动手能力 demo)
2. Due-diligence 调研 #1 回 (两路径清楚: 单一或合并路径)
3. Board 给 directive 说可开 gov-mcp

## 简报 (一句话)

"**办公室做实 + 场泛函 infra 继续爬**, gov-mcp 卖锁冰箱等解冻, 不再扑."

## CEO 自我记录 (feedback 也写进了 memory)

Board 2026-04-23 这轮严 catch 值得记:
- CEO 扑太快散 (一天 10+ dispatches 涉 4 track) 没做"先查后造" 前期 due diligence
- 把 infra ship 误当 "能力 ship", 差点把 pricing tier 当真在市场
- 这次 Board 直接停 + 收束 + 要求全维度企划 — **CEO 学: 任何"产品线要出去"类 goal 必先要求 due-diligence 成熟度证明, 不能凭感觉扑**
- 学到: `plan ≠ done`, `ship ≠ ready-to-sell`, 3 个不同 maturity level 不能 conflate
