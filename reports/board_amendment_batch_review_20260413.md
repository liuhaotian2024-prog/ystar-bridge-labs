# Board Amendment Batch Review — 12 Pending Amendments
**Date**: 2026-04-13
**Sealed so far**: 001 / 002(占位) / 003 / 004
**Pending**: 005 → 016 (12 个)
**Goal**: Board 一次看完，按行打 ✅ / ❌ / 🟡(改) / ⏸(deferred)，CEO 据此安排 Secretary 批量归档

---

## 优先级排序（按因果，不按编号）

| # | 名 | 1-句话本质 | 关键风险 | Recommend |
|---|---|---|---|---|
| **016** | Rule Mirror Sync | 6 处规则源合并为 SSoT + watcher 传播 | 实验今晚已派 Maya，2 天内出 verdict | ⏸ 等 exp7 verdict 再批 |
| **015 v2** | LRS Unified | 全生命周期复活架构（C5 snapshot + C7 replay + 11-cat boot pack） | 单体最大 amendment，影响范围最广 | ✅ 已部分 ship (C5/C7 commit b9376ee/d251946)，建议批 |
| **011** | Truth Source Consolidation | 多 agent DNA 切片 + AGENTS.md 单 source | 与 016 部分重叠（rules 也是 truth source 之一） | 🟡 等 016 verdict 后合并范围再批 |
| **012** | Deny-as-Teaching | hook 拒绝时返回 compliance recipe，不只 deny | **今天 6-lock incident 直接证据** | ✅ 强烈建议批，代码改动小 |
| **013** | Proactive Skill Activation | hook 三态 `{allow, deny, activate}` 主动注入 skill | Jordan 已 in-progress (commit 304b869) | ✅ 已实施，正式批确认 |
| **014** | Closed-Loop CIEU + RLE | CIEU 事件触发 reactive loop 闭环 | Maya 今晚已 ship (commit f03ddd2) | ✅ 已实施，正式批确认 |
| **009** | Priority Brief + Tombstone + Escape Hatch | 治理元规则三件套 | priority_brief.md 已实操使用 | ✅ 已实操，正式批确认 |
| **010** | Secretary Curation + 11-Category Boot | boot pack 11 类分包注入 | 今晚发现 cat11 populator bug（Ryan 修中） | 🟡 等 cat11 fix 后批 |
| **006** | 6-pager 派活格式 | 任务卡 schema 升级为 Amazon 6-pager | 低风险，纯 process | ✅ 建议批 |
| **005** | RAPID 替 L0-L3 | 决策分级框架替换 | 影响所有 dispatch 流程，需配套培训 | 🟡 与 006 一起批，2 周磨合期 |
| **007** | CEO Operating System | 6 层 CEO 操作系统 | EXP-5A 仅 4.8/10，需 hook 强制层修订后再交 | ⏸ 修订后 resubmit |
| **008** | BHAG + Tenets + META 护栏 | 战略级使命陈述 + 12 tenets | 文化层文档，不阻塞工程 | ✅ 建议批 |

---

## 一行话推荐

**今晚可批 (6 个，全是低风险或已实施事后追认)**：009 / 012 / 013 / 014 / 015v2 / 006 / 008  → 共 7 个
**等子条件 (3 个)**：010 (cat11 修完) / 011 (016 verdict) / 016 (exp7 verdict)
**修订重提 (1 个)**：007
**配套批 (1 个)**：005 与 006 同批

---

## Board 反馈格式（推荐）

复制下面这段在对话里改一下 emoji 即可：

```
009 ✅  010 🟡  011 🟡  012 ✅  013 ✅  014 ✅  015v2 ✅  006 ✅  005 🟡  007 ⏸  008 ✅  016 ⏸
```

CEO 拿到后立刻让 Secretary 把 ✅ 项归档进 `governance/BOARD_CHARTER_AMENDMENTS.md`，🟡/⏸ 项保留在 proposals/ 等条件满足。
