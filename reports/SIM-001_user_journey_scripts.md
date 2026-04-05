# SIM-001: 五行业用户旅程模拟脚本
# Date: 2026-04-05
# Status: Awaiting Board Review
# 不要直接跑实验。Board核准后再执行。

---

## 设计原则

1. **真实性优先** — 每个场景基于真实企业用例和监管引用
2. **完整旅程** — 从发现到使用一周后
3. **压力测试** — 包含GOV MCP无法满足的需求
4. **技术风险注入** — 20个P0-P2风险全部埋入场景
5. **数据完整性** — 每阶段记录满足/未满足/放弃
6. **驻场工程师** — 每个场景包含工程师部署流程
7. **各国模块** — 标注监管差异和缺口

---

## 场景一：金融服务（JPMorgan类型）

**真实背景：** JPMorgan LLM Suite服务6万员工，Morgan Stanley为1.6万顾问部署AI助手。FINRA Rule 4511要求完整审计链（毫秒时间戳+agent身份+决策理由）。SOX Section 404要求COSO五要素内控评估。

**用户角色：** CTO + 合规官（FINRA注册）
**核心痛点：** "我们的agent做了什么？能向FINRA证明吗？"

### Day 1 — 发现和评估

| 步骤 | 操作 | 技术风险注入 | 测量 |
|---|---|---|---|
| 1.1 | GitHub发现gov-mcp，阅读README | — | 耗时，首印象 |
| 1.2 | 评估CIEU是否满足FINRA Rule 4511 | — | Checklist对照 |
| 1.3 | 评估governance字段是否覆盖CAT字段 | — | 缺口列表 |
| 1.4 | 询问驻场工程师：需要多久部署？ | — | 工程师响应时间 |

**FINRA合规Checklist（Day 1评估）：**
- [ ] 毫秒级时间戳 → CIEU有（验证精度）
- [ ] Agent身份追踪 → agent_id字段 → 需映射到CRD号
- [ ] 决策审计链 → governance.cieu_seq → 需验证连续性
- [ ] 审批人记录 → DelegationChain → 需映射到注册人员
- [ ] 6个月保留 → gov_archive → 需验证
- [ ] COSO格式报告 → **缺失** → 记录为产品缺口

### Day 2 — 安装和配置

| 步骤 | 操作 | 技术风险注入 | 测量 |
|---|---|---|---|
| 2.1 | `pip install gov-mcp` | P2-2: 空deny默认 | TTFV |
| 2.2 | `gov-mcp install` | P1-1: Windows兼容 | 安装耗时 |
| 2.3 | 不知道怎么写金融规则 | P1-10: parser验证 | 障碍数 |
| 2.4 | `gov_init(project_type="generic")` | — | 模板有用吗？ |
| 2.5 | 驻场工程师帮助写金融行业AGENTS.md | — | 工程师耗时 |

**驻场工程师行动：**
- 生成金融行业AGENTS.md模板
- 添加交易限额规则：value_range.amount.max=10000
- 配置deny: /trading_secrets, /client_pii, /.env
- 配置deny_commands: rm -rf, sudo, git push --force, curl | sh

### Day 3 — 接入现有agent

| 步骤 | 操作 | 技术风险注入 | 测量 |
|---|---|---|---|
| 3.1 | 接入交易分析agent | P1-6: 并发无锁 | 连接稳定性 |
| 3.2 | 接入风控agent | P1-7: Merkle写入 | CIEU完整性 |
| 3.3 | 接入报告生成agent | P2-1: SSE重连 | 断线恢复 |
| 3.4 | 3个agent并发运行 | P0-4: baseline竞争 | 数据一致性 |

### Day 4 — 越权测试

| 步骤 | 操作 | 技术风险注入 | 测量 |
|---|---|---|---|
| 4.1 | Agent尝试访问/trading_secrets | P0-1: 路径遍历 | DENY正确？ |
| 4.2 | Agent尝试 `cat ../../production/db` | P0-5: shell注入 | 绕过了吗？ |
| 4.3 | 检查fix_suggestion | — | 建议有用？ |
| 4.4 | 查看gov_audit报告 | P1-2: CIEU未缓存 | 数据一致？ |

### Day 5 — Escalation测试

| 步骤 | 操作 | 技术风险注入 | 测量 |
|---|---|---|---|
| 5.1 | Junior agent申请高风险数据访问 | P1-3: escalate回退 | 权限正确？ |
| 5.2 | Senior agent审批 | — | 流程完整？ |
| 5.3 | 审批超时（无人响应） | — | OmissionEngine触发？ |
| 5.4 | 强制gov_chain_reset | P1-4: 孤儿节点 | 清理干净？ |

### Day 6 — 合规报告

| 步骤 | 操作 | 技术风险注入 | 测量 |
|---|---|---|---|
| 6.1 | gov_audit生成报告 | — | FINRA格式？ |
| 6.2 | gov_verify验证Merkle链 | — | 链完整？ |
| 6.3 | 合规官评估报告 | — | 可提交？ |
| 6.4 | 对照COSO五要素 | — | 覆盖度 |

**预期缺口：** COSO报告模板缺失，CAT字段映射缺失

### Day 7 — 价值评估

- 拦截了多少风险操作？
- Token节省了多少？
- 审计报告评分
- 愿意付多少？$49/月 vs $499/月 vs $2999/月（enterprise）
- 驻场工程师评估：客户能独立运维了吗？

---

## 场景二：医疗健康（EU AI Act合规）

**真实背景：** AtlantiCare用AI减少42%临床文档时间。EU AI Act (Regulation 2024/1689) Article 14要求human oversight：系统必须允许人类"override or reverse"AI输出(Art.14(4)(d))，并有"stop button"(Art.14(4)(e))。ISO 13485 QMS要求。Charite Berlin已实施合规AI分诊。

**用户角色：** 医院IT总监 + 法务（EU合规）
**核心痛点：** "EU AI Act要human oversight，怎么证明？"

### Day 1-2 — 评估与安装

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| 评估Art.14(4)(a)-(e) checklist | — | 覆盖率 |
| 安装gov-mcp | P2-2 | TTFV |
| 配置医疗数据规则 | P1-10 | 模板适用？ |
| .env包含患者DB密码 | — | 是否拦截？ |
| 驻场工程师配置医疗domain pack | — | domain pack可用？ |

**EU AI Act Checklist：**
- [ ] Art.14(4)(a): 输出可解释性 → governance字段 → **需要confidence score**
- [ ] Art.14(4)(d): 人类可override → DelegationChain → **需要更明确的映射**
- [ ] Art.14(4)(e): 停止按钮 → gov_chain_reset → **用户不知道这是"停止按钮"**
- [ ] Art.12: 日志记录 → CIEU → 缺少patient_id(pseudonymized)字段
- [ ] Art.13: 透明度 → governance.contract_hash → **需要人类可读版本**
- [ ] ISO 13485 QMS → **完全缺失**

### Day 3-5 — 临床场景压力测试

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| DelegationChain作human oversight证明 | — | 法务认可？ |
| 10并发临床agent | P0-4, P1-6 | 稳定性 |
| 网络断线后CIEU完整性 | P2-1, P1-7 | 记录丢失？ |
| gov_coverage检测盲区 | — | 有未治理agent？ |

### Day 6-7 — 合规报告与评估

| 步骤 | 测量 |
|---|---|
| 生成EU AI Act合规报告 | 格式符合Annex IV？ |
| 法务评估：能提交监管机构？ | 通过/失败 |
| 评估各国差异（GDPR数据驻留） | 需要额外模块？ |

**预期缺口：** ISO 13485模板、confidence score字段、patient_id支持

---

## 场景三：软件开发团队（GitHub用户）

**真实背景：** Amazon Q Developer协调多agent现代化Java应用。开发者日常用Claude Code + Cursor。常见痛点：agent读.env泄露secrets、误操作git push --force、编辑node_modules。

**用户角色：** 独立开发者 / 3人团队CTO
**核心痛点：** "agent偶尔做不该做的事，但我不想配置太复杂"

### Day 1 — 30秒安装体验

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| HN看到Show HN | — | 点击率 |
| `pip install gov-mcp && gov-mcp install` | P1-1 | <30秒？ |
| 已有其他MCP server | — | 冲突？ |
| 自动检测Claude Code | — | 自动配置？ |
| gov_demo看效果 | — | 第一印象 |

**关键验证：** TTFV（首次价值时间）必须<5分钟

### Day 2-3 — 日常工作流

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| 正常写代码、跑测试、提交 | P1-5: python模块 | false positive |
| Agent尝试git push --force | P0-2: git branch | DENY正确？ |
| fix_suggestion是否清晰 | — | 用户理解？ |
| auto-routing节省测量 | — | 节省>20%？ |

### Day 4-5 — 信任建立与压力测试

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| 用户减少手动检查 | — | 行为改变？ |
| GOV MCP server宕机 | — | agent降级行为 |
| 恢复后CIEU是否完整 | P1-7 | 无丢失？ |

### Day 6-7 — 评估

| 步骤 | 测量 |
|---|---|
| gov_trend一周统计 | 发现几个风险？ |
| 愿意推荐？(NPS) | >8? |
| 配置太复杂的临界点 | 在哪个步骤？ |

**预期缺口：** MCP server冲突处理、降级模式

---

## 场景四：法律科技公司（合同审查agent）

**真实背景：** Harvey AI ($100M+融资)做合同分析。Luminance服务600+律所。ABA Model Rule 1.6要求"reasonable efforts"保密。ABA Opinion 512(2024)要求律师理解和监督AI工具。Multi-tenant隔离是核心需求。

**用户角色：** 律所合伙人 + IT安全主管
**核心痛点：** "client A的agent绝对不能看到client B的文件"

### Day 1-2 — Multi-tenant设计

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| 评估per-client DelegationChain | — | 架构可行？ |
| 安装，per-client only_paths配置 | P0-3: 前缀绕过 | 隔离有效？ |
| 驻场工程师设计隔离架构 | — | 工程师能力 |

### Day 3 — 渗透测试

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| Agent A访问client B目录 | P0-1: 路径遍历 | 完全隔离？ |
| 路径遍历攻击 `../../clientB/` | P0-5: shell注入 | 绕过？ |
| 检查CIEU所有访问记录 | — | 完整？ |

### Day 4 — 高并发压力

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| 50并发agent，10 client | P1-6: 无锁 | 链污染？ |
| gov_chain_reset在生产 | P1-4: 孤儿 | 安全？ |
| 长时间运行(1小时) | P0-4 | 稳定？ |

### Day 5-6 — 合规审计

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| CIEU证明数据从未越界 | — | 可证明？ |
| 命令注入绕过测试 | P1-9, P0-5 | 全堵住？ |
| ABA Rule 1.6合规评估 | — | 通过？ |

### Day 7 — 安全审计结论

- 通过/失败？
- 发现的所有安全漏洞列表
- IT安全主管签字？

**预期缺口：** per-client加密密钥、attorney-client privilege标记字段

---

## 场景五：制造业供应链（SAP集成）

**真实背景：** Siemens Industrial Copilot集成Xcelerator。BMW用AI做预测性零件采购。SAP BAPI_PO_CREATE1创建采购订单。典型审批：<$5K自动，$5K-$25K经理，$25K-$100K总监，>$100K VP。

**用户角色：** 数字化转型总监
**核心痛点：** "agent自动下了$50K订单，没人知道"

### Day 1-2 — value_range评估

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| value_range能否限制金额 | — | 精确？ |
| 金额单位混淆（元vs美元） | — | 处理？ |
| gov_init配置金额规则 | P1-10 | 模板适用？ |

### Day 3-4 — 审批流

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| Agent下$50K订单 → DENY | — | 正确？ |
| gov_escalate触发$10K+审批 | P1-3 | 流程完整？ |
| 审批人不在线，义务超时 | — | OmissionEngine？ |
| SOFT→HARD超时升级 | — | 自动升级？ |

### Day 5 — ERP集成

| 步骤 | 技术风险注入 | 测量 |
|---|---|---|
| ERP不支持MCP | P1-8: localhost | 接入方式？ |
| Generic格式够通用？ | — | SAP BAPI兼容？ |
| 驻场工程师写适配层 | — | 工程师耗时 |

### Day 6-7 — ROI评估

| 步骤 | 测量 |
|---|---|
| 拦截了多少超限订单 | 数量 |
| 节省的潜在损失 | 金额 |
| CFO评估ROI | 可量化？ |

**预期缺口：** 非MCP系统接入复杂、金额精度需要货币单位支持

---

## 驻场工程师标准流程（跨场景通用）

### Week 1: Discovery + Install

| 天 | 工程师任务 | 产出 |
|---|---|---|
| Day 1 | 了解客户agent架构、技术栈、监管要求 | 架构评估文档 |
| Day 2 | gov-mcp install + 行业AGENTS.md配置 | 运行中的治理系统 |
| Day 3 | 接入全部现有agent | 100%覆盖率 |

### Week 2: Tuning + Training

| 天 | 工程师任务 | 产出 |
|---|---|---|
| Day 4-5 | 调整规则减少false positive | FP rate <5% |
| Day 6-7 | 培训客户团队使用gov_doctor/gov_trend | 客户可自助 |

### Month 1-3: Remote Support

| 指标 | 目标 |
|---|---|
| 工单数/周 | <3 |
| 远程解决率 | >90% |
| 客户自助率 | >80% |
| 续约意向 | >80% |

---

## 各国模块注入点

| 场景 | 主要国家 | 注入的合规差异 |
|---|---|---|
| 金融 | US(FINRA/SOX) + EU(MiFID II) | CAT字段格式 vs 欧盟格式 |
| 医疗 | EU(AI Act) + US(HIPAA) | human oversight要求差异 |
| 开发者 | 全球通用 | 数据驻留（China/EU） |
| 法律 | US(ABA) + EU(GDPR) | 跨境数据传输限制 |
| 制造 | US + China + EU | 出口管制(ITAR) + 数据出境(CAC) |

---

## 执行条件

**Board核准后才执行以下步骤：**
1. 选择第一个场景开始
2. 配置模拟环境
3. 按Day 1-7逐步执行
4. 每天记录四类指标
5. 每个场景完成后输出完整报告
6. 五个场景全部完成后输出横向对比

**预估总耗时：** 5场景 × 7天 = 35天模拟周期
**可并行：** 场景3（开发者）可与其他场景并行执行
