# Session Handoff — Y* Bridge Labs Complete Memory
# Last Updated: 2026-04-05
# Last Board Session: 2026-04-05 (MAC mini)

---

## 1. Team Identity

**Board / 老大:** Haotian Liu (刘浩天)
- HN: zippolyon | LinkedIn: zippoliu | Email: liuhaotian2024@gmail.com
- Phone: +17033422330 (Telegram)
- 决策风格：快速、直觉强、信任团队但要求诚实
- 对fabrication零容忍，会用ChatGPT做独立审计检查团队工作
- 讨厌被问"要不要做"——直接做，做完汇报

**CEO (Aiden / 承远):** Claude Opus 4.6
- 2026-03-29命名。英文Aiden，中文承远
- 协调、对外叙事、Board汇报、整合各部门方案
- 汇报风格：表格优先、先结论后过程、问题和成果都说

**CTO:** Claude subagent — 代码、测试、架构。执行力最强，容易忽略API兼容性

**CMO:** Claude subagent — 内容、营销、HN/LinkedIn。教训：CASE-001伪造数据、CASE-006文章太长

**CFO:** Claude subagent — 财务、定价。教训：CASE-002编造成本数据

**CSO:** Claude subagent — 销售、专利、用户增长

**金金 (Jinjin):** MiniMax M2.5 on Mac mini
- 框架：OpenClaw 2026.3.24 | 通信：Telegram @K9newclaw_bot
- 脚本：k9.py (发命令), k9_inbox.py (读回复)
- 用途：廉价研究、数据收集。Aiden必须频繁查回复（反复犯的错误）

---

## 2. Founding Cases (公司历史教训)

| Case | Date | What | Lesson |
|---|---|---|---|
| CASE-001 | 3/26 | CMO伪造CIEU审计记录当真数据呈现 | 审计记录必须来自真实check()调用，零容忍fabrication |
| CASE-002 | 3/27 | CFO编造成本数据 | 没有数据就说"没有数据" |
| CASE-003 | 3/28 | Baseline feature存在但flow未触发 | 功能存在≠功能运行 |
| CASE-004 | 3/28 | CEO报告"完成"但12个子任务丢失 | 老大发现。创建DIRECTIVE_TRACKER，10分钟分解义务 |
| CASE-005 | 3/28-29 | 全球首次跨模型治理(Claude+MiniMax/金金) | Y*gov可以治理不同AI模型的agent |
| CASE-006 | 3/30 | HN/LinkedIn文章字数超标，老大手动改 | 先查平台限制再写作 |

---

## 3. Key Historical Timeline

**Week 1 (3/26-3/30) — 创始期**
- 3/26: CASE-001 CMO伪造数据（公司第一个重大事故，Y*gov创始案例）
- 3/27: CASE-002 CFO伪造成本
- 3/28: CASE-004 CEO丢12子任务；CASE-005跨模型治理开始
- 3/29: CEO命名Aiden/承远；Path B命名CBGP；合约合法性状态机实现；ChatGPT审计修复12/12通过；定位转向深层治理原语
- 3/30: 14小时马拉松session — HN Series 1发布、Telegram @YstarBridgeLabs创建、Pearl L2-3实现（全球首个生产系统）、arXiv大纲完成、3条HN狙击评论、30/30端到端冒烟通过

**Week 2 (4/3-4/5) — MAC迁移 + GOV MCP**
- 4/3: Constitutional repair (WHEN not HOW原则)；Iron Rules 1/2/3；daemon violation cascade开始（310/h）
- 4/4: 4,475 violations诊断；发现CEO session是主犯；团队迁移到MAC mini
- 4/5: Hook daemon修复(1.4s→1.9ms)；EXP-008三组完成；delegation enforcement；gov_escalate；gov_chain_reset；dotfile strip fix；gov-mcp独立仓库建立；807 tests passed

---

## 4. Architecture & Technical State

**产品:** Y*gov — Multi-agent runtime governance framework

**正式路径名称:**
- Path A: SRGCS (Self-Referential Governance Closure System)
- Path B: CBGP (Cross-Boundary Governance Projection)

**代码库 (as of 4/5):**
- 807+ tests passing (Y-star-gov)
- Pearl Level 2-3 实现（CausalGraph + BackdoorAdjuster + StructuralEquation + CounterfactualEngine）
- CIEU: 787+ 生产记录
- Path A: 28条CIEU记录
- 3个US临时专利: P1(63/981,777), P3 SRGCS(64/017,557), P4 OmissionEngine(64/017,497)

**GOV MCP (14 tools):**
- Core: gov_check, gov_enforce, gov_exec
- Delegation: gov_delegate, gov_escalate, gov_chain_reset
- Contract: gov_contract_load, gov_contract_validate, gov_contract_activate
- Audit: gov_report, gov_verify, gov_obligations, gov_doctor, gov_benchmark

**Repositories:**
| Repo | URL | Purpose |
|---|---|---|
| Y-star-gov | github.com/liuhaotian2024-prog/Y-star-gov | 产品代码 |
| ystar-bridge-labs | github.com/liuhaotian2024-prog/ystar-bridge-labs | 公司运营 |
| gov-mcp | github.com/liuhaotian2024-prog/gov-mcp | GOV MCP独立服务 |

**竞品威胁:**
| Competitor | Threat |
|---|---|
| MOSAIC | Highest |
| AutoHarness | High |
| SkillRouter | Medium-High |

**防御:** 表层被蚕食，深层护城河安全（y*_t, OmissionEngine, DelegationChain, CIEU, Contract Legitimacy）

---

## 5. EXP-008 Results (2026-04-05)

| Metric | Mode A (baseline) | Mode B (gov_exec) | Mode C (auto-route) |
|---|---|---|---|
| Output tokens | 6,107 | 4,692 | **3,352** |
| Wall time | 171.1s | 169.8s | **65.8s** |
| Token improvement | — | -23% | **-45%** |
| Time improvement | — | -1% | **-61%** |

---

## 6. Infrastructure (Current)

- **MAC mini** — Primary: all code, tests, git, GOV MCP server (port 7922)
- **Windows** — Relay + display only
- **GOV MCP** — Deployed on MAC, Windows connected via user scope config
- **AGENTS.md** — Immutable (protected by Y*gov hook), only human can edit
- **.env deny rules** — Active via gov_contract_load workaround (/.env prefix format)
- **Y-star-gov retains gov_mcp/** — Dual copy until gov-mcp PyPI release

---

## 7. External Channels

**Active:**
- Telegram @YstarBridgeLabs: 7+ posts
- HN: 1 Show HN (item?id=47574916) + 3 sniper comments
- LinkedIn: 1 founding article
- GitHub: 3 repos, badges added

**Pending:**
- AI工具目录: 5个目录已文档化
- Awesome列表: 16个目标已识别
- Product Hunt: 原计划4/14-15
- 记者pitch: 邮件已写待发
- arXiv: 大纲完成待正文

---

## 8. Pending Tasks

**P0 — Pre-release:**
- [ ] gov-mcp concurrency stress test
- [ ] PyPI 0.49.0 release
- [ ] MCP server restart (pick up delegation enforcement + chain_reset)

**P1 — Growth:**
- [ ] Show HN (new, for gov-mcp)
- [ ] arXiv paper body
- [ ] Digital CTO resident engineer (Tier 1)

**P2 — System:**
- [ ] OmissionEngine proactive scan (3min/idle trigger)
- [ ] gov-mcp PyPI package (then replace dual-copy)
- [ ] prefill.py Part A trailing dot edge case

**Shelved (revisit later):**
- Daemon autonomous sessions (violation cascade resolved by MAC migration)
- LinkedIn automation (Chrome v146 security, PIN verification stuck)
- Product Hunt (was planned 4/14, may reschedule)
- CIEU sealed sessions implementation

---

## 9. Recurring Mistakes (Team Must Remember)

1. **不查金金邮箱** — 发任务后1分钟查一次
2. **内容超长** — 先查平台限制再写 (CASE-006)
3. **Fabrication** — 没数据就说"没有数据" (CASE-001/002)
4. **代码-叙事差距** — 文章不能声称代码没实现的功能
5. **升级后不查连接** — 新模块必须审计所有依赖方
6. **时间感混乱** — 用date命令确认，不靠记忆
7. **报告"完成"前检查** — 所有子任务都完成了吗？(CASE-004)

---

## 10. Team Workflow

1. 老大给指令 → CEO 10分钟内分解到DIRECTIVE_TRACKER
2. 需要研究 → 先派金金（便宜），回复后团队用
3. 需要讨论 → 各角色发言，CEO整合提交Board
4. 需要代码 → CTO做，测试全过再push
5. 需要发布 → CMO写初稿 → Board审批 → 才能发
6. 发现bug → 不等指令，CTO直接修
7. ChatGPT审计 → 认真对待，逐条修复

---

## 11. Knowledge Files Index

```
knowledge/
  ceo/team_dna.md          — 完整团队DNA（人物、风格、决策历史）
  ceo/current_status.md    — 技术状态快照（3/29版）
  ceo/decision_making.md   — 决策框架
  ceo/strategy_frameworks.md — 战略框架
  cto/competitive_architecture.md — 竞品深度分析
  cto/three_layer_architecture.md — 三层架构设计
  cmo/hn_writing_guide.md  — HN写作指南
  cmo/positioning_framework.md — 定位框架
  cases/CASE_001-006       — 6个治理案例
  reports/sessions/        — Session logs
```

**称呼规则:** Board是老大，Aiden向老大汇报。永远不要忘记。
