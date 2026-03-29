# Directive Tracker — 指令义务追踪表

**规则：每条Board指令收到后，CEO必须在10分钟内将所有子任务拆解到本表。**
**未拆解的子任务 = 不存在的义务 = 必然被遗漏。**

---

## 活跃指令（Active — 有未完成子任务）

### Directive #018-020 建司指令（2026-03-28）
| # | 子任务 | 负责人 | 状态 | 交付物 |
|---|--------|--------|------|--------|
| 0 | Y*gov治理一切行为 | 全员 | ✅ 持续 | Y*gov运行中 |
| 1 | OKR.md建立 | CTO | ✅ 完成 | OKR.md |
| 2a | DISPATCH.md维护 | CEO | ✅ 持续 | DISPATCH.md |
| 2b | BOARD_PENDING.md维护 | CEO | ✅ 持续 | BOARD_PENDING.md |
| 2c | WEEKLY_CYCLE.md建立 | CTO | ✅ 完成，待Board批 | WEEKLY_CYCLE.md |
| 2d | reports/daily/维护 | CEO | ✅ 持续 | reports/daily/ |
| 2e | CEO Session Start/End Protocol | CEO | ✅ 写入agent定义 | .claude/agents/ceo.md |
| 2f | 各部门自定每周节律 | 全员 | ❌ 未开始 | WEEKLY_CYCLE.md补充 |
| 3a | HN文章系列推进 | CMO | ⏳ 5篇draft，0发布 | content/articles/ |
| 3b | LinkedIn策略研究+提案 | CMO | ❌ 未开始 | 待提交Board |
| 4 | 公司行为投射方案 | CMO牵头 | ❌ 未开始 | 待提交Board |
| 5 | 产品拆分方案 | CTO | ❌ 未开始 | reports/proposals/ |
| 6a | tech_debt.md周更 | CTO | ✅ 文件存在 | reports/tech_debt.md |
| 6b | 技术升级提案流程 | CTO | ❌ 无提案 | reports/proposals/ |
| 6c | 测试覆盖率基线 | CTO | ❌ 未追踪 | 需建立基线 |
| 6d | CTO每周阅读+知识自举 | CTO | ❌ 未开始 | knowledge/cto/ |
| 7 | 跨部门协作协议写入AGENTS.md | CEO | ✅ 完成 | AGENTS.md |
| 8 | Board汇报协议写入AGENTS.md | CEO | ✅ 完成 | AGENTS.md |
| 9 | 对标学习写入知识库 | CEO | ✅ 原则写入 | AGENTS.md |

### Directive #016 文章写作（2026-03-28）
| # | 子任务 | 负责人 | 状态 | 交付物 |
|---|--------|--------|------|--------|
| 1 | 写作指南存档 | CMO | ✅ 完成 | knowledge/cmo/hn_writing_guide.md |
| 2 | Series 3初稿 | CMO | ✅ 完成 | 004_contract_validity_HN_draft.md |
| 3 | CTO技术审核 | CTO | ❌ 未做 | 需code_review文件 |

### Directive #017 文章系列规划（2026-03-28）
| # | 子任务 | 负责人 | 状态 | 交付物 |
|---|--------|--------|------|--------|
| 1 | CTO代码扫描 | CTO | ✅ 完成 | content/cto_concept_scan.md |
| 2 | 20篇规划v2 | CMO | ✅ Board已批 | content/article_series_plan_v2.md |
| 3 | Series 16替代方案 | CMO | ❌ 未提交 | 待CMO提案 |

### Directive #014 Y*文章（2026-03-27）
| # | 子任务 | 负责人 | 状态 | 交付物 |
|---|--------|--------|------|--------|
| 1 | 研究+写作 | CMO | ✅ 完成 | 001_what_is_ystar.md |
| 2 | CTO审核 | CTO | ✅ 完成 | 001_what_is_ystar_code_review.md |
| 3 | Board精修版 | Board | ✅ 完成 | 003_what_is_ystar_HN_ready.md |

### Directive #011 知识体系+NotebookLM（2026-03-27）
| # | 子任务 | 负责人 | 状态 | 交付物 |
|---|--------|--------|------|--------|
| 1 | Knowledge Retrieval Protocol | CTO | ✅ 完成 | 5个agent定义文件 |
| 2a | CEO NotebookLM计划 | CEO | ✅ 完成 | reports/notebooklm_plan_ceo.md |
| 2b | CTO NotebookLM计划 | CTO | ✅ 完成 | reports/notebooklm_plan_cto.md |
| 2c | CMO NotebookLM计划 | CMO | ✅ 完成 | reports/notebooklm_plan_cmo.md |
| 2d | CSO NotebookLM计划 | CSO | ✅ 完成 | reports/notebooklm_plan_cso.md |
| 2e | CFO NotebookLM计划 | CFO | ✅ 完成 | reports/notebooklm_plan_cfo.md |
| 3 | Board购买书籍+建NotebookLM | Board | ❌ 待Board决定 | ~$890预算 |

### 专利（2026-03-28）
| # | 子任务 | 负责人 | 状态 | 交付物 |
|---|--------|--------|------|--------|
| 1 | CSO知识自举 | CSO | ✅ 完成 | knowledge/cso/patent_law_knowhow.md |
| 2 | 专利草稿 | CSO | ✅ 完成 | reports/patent_ystar_t_provisional_draft.md |
| 3 | Board修改4处 | CSO | ✅ 完成 | 13 claims |
| 4 | Board终审 | Board | ❌ 待决定 | 律师审核→USPTO |

### K9 Scout验证（2026-03-28）
| # | 子任务 | 负责人 | 状态 | 交付物 |
|---|--------|--------|------|--------|
| 1 | Phase 1 check() | CTO | ✅ 10/10 | reports/k9_verification_results.md |
| 2 | Phase 2 OmissionEngine | CTO | ✅ 7/7 | 同上 |
| 3 | Phase 3 CIEU | CTO | ✅ 6/6 | 同上 |
| 4 | Phase 4 高级功能 | CTO | ❌ 未开始 | 待执行 |
| 5 | Phase 5 长期数据收集 | K9 | ⏳ 持续 | .ystar_cieu.db |
| 6 | 基线修复 | CTO | ✅ CASE-003修复 | 7/7 doctor |

---

## 已关闭指令（Closed — 所有子任务完成）

| 指令 | 关闭日期 | 子任务数 |
|------|---------|---------|
| #002 Org Design | 2026-03-26 | 7/7 |
| #003 Operational Autonomy | 2026-03-26 | 5/5 |
| #004 Leadership Heroes | 2026-03-27 | 6/6 |
| #006 CFO Disclaimer | 2026-03-27 | 3/3 |
| #007 CASE-002 + Pain Points | 2026-03-27 | 4/4 |
| #009 CFO OmissionEngine | 2026-03-27 | 3/3 |
| #010 Knowledge Foundation | 2026-03-27 | 5/5 |
| #012 Knowledge Base + Context | 2026-03-28 | 4/4 |
| #013 Self-Bootstrap Protocol | 2026-03-28 | 3/3 |
| #015 ObligationTrigger Design | 2026-03-28 | 4/4 (代码完成,部署待定) |

---

## 统计

- 活跃指令：7个
- 未完成子任务：12个（标记❌的）
- 已关闭指令：10个
