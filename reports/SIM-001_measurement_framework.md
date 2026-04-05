# SIM-001: 统一测量指标框架
# Date: 2026-04-05
# Status: Awaiting Board Review

---

## 每个场景每天记录的四类指标

### 一、用户旅程指标

| 指标 | 测量方法 | 目标值 |
|---|---|---|
| 操作耗时(分钟) | 从开始到完成计时 | Day1安装<5min，Day2配置<30min |
| 遇到的障碍数量 | 每次用户需要查文档或报错时+1 | <3/天 |
| 放弃点 | 记录用户决定停止或切换方案的位置 | 0个P0放弃点 |
| 满意度(1-10) | 基于完成度和摩擦度评分 | >7 |
| 首次价值时间(TTFV) | 从pip install到第一次DENY被拦截 | <10min |

### 二、产品价值指标

| 指标 | 测量方法 | 目标值 |
|---|---|---|
| 拦截的风险操作 | CIEU DENY事件计数 | >0（证明有价值） |
| Token节省量 | Mode A vs Mode C对比 | >30% |
| 审计报告合规性 | 对照监管要求checklist评分 | >70%字段覆盖 |
| 用户愿意付费金额 | Day7评估阶段询问 | >$49/月 |
| NPS | "愿意推荐吗"(0-10) | >8 |

### 三、技术风险指标

| 指标 | 测量方法 | 严重度 |
|---|---|---|
| 发现的bug | 执行P0-P2风险注入后计数 | P0=release blocker |
| 性能瓶颈 | gov_check延迟>100ms时记录 | <2ms正常 |
| 安全漏洞 | 渗透测试通过/失败 | 0个P0漏洞 |
| 并发稳定性 | 10+并发agent运行1小时无crash | 100%正常运行 |
| 数据完整性 | gov_verify链验证通过率 | 100% |

### 四、产品缺口指标

| 指标 | 测量方法 | 分级 |
|---|---|---|
| 明确缺少的功能 | 用户在旅程中表示"需要X但没有" | 记录并分级 |
| 无法满足的合规要求 | 对照监管checklist标红项 | P0=必须有，P1=应该有 |
| 竞品已有但我们没有 | 对照MOSAIC/AutoHarness功能表 | 战略评估 |

---

## 行业特定合规Checklist

### 金融(FINRA/SOX)

| 要求 | GOV MCP覆盖 | 缺口 |
|---|---|---|
| 毫秒级时间戳 | CIEU有timestamp | 未验证精度 |
| Agent/用户身份追踪 | agent_id字段 | 需要映射到CRD号 |
| 决策理由记录 | violations字段 | 缺少自由文本理由 |
| 审批链记录 | DelegationChain | 需要映射到监管人员 |
| 6个月数据保留 | gov_archive支持 | 需要验证 |
| COSO五要素报告格式 | 无 | **重大缺口** |

### 医疗(EU AI Act)

| 要求 | GOV MCP覆盖 | 缺口 |
|---|---|---|
| Art.14 Human oversight | DelegationChain | 需要证明"人类可override" |
| Art.12 日志记录 | CIEU | 需要confidence scores |
| Art.13 透明度 | governance字段 | 需要用户可读输出 |
| 停止按钮 | gov_chain_reset | 需要更直观的"停止"命令 |
| ISO 13485 QMS | 无 | **需要模板** |
| 6个月数据保留 | gov_archive | 需要验证 |

### 法律(ABA Rules)

| 要求 | GOV MCP覆盖 | 缺口 |
|---|---|---|
| Rule 1.6 保密性 | deny + only_paths | 需要per-client隔离 |
| Rule 5.3 AI监督 | DelegationChain | 需要attorney→AI映射 |
| FRE 502(b) 防泄露 | deny规则 | 需要更细粒度控制 |
| 每客户加密密钥 | 无 | **架构级缺口** |
| 特权标记 | 无 | **需要新字段** |

---

## 驻场工程师工作流指标

### 部署阶段(Week 1-2)

| 阶段 | 工程师任务 | 成功指标 |
|---|---|---|
| Discovery | 了解客户agent架构 | 完成架构文档 |
| Install | gov-mcp install + 行业模板 | <1天完成 |
| Integration | 接入客户现有agent | 所有agent受治理 |
| Tuning | 调整规则减少false positive | FP rate <5% |
| Handoff | 培训客户团队 | 客户独立运维 |

### 运维阶段(Month 1-3)

| 指标 | 目标 |
|---|---|
| 客户工单数/周 | <3（稳定后） |
| 自助解决率 | >80% |
| 规则更新频率 | <1次/周 |
| 升级到工程师频率 | <1次/月 |

---

## 各国模块差异化指标

| 国家 | 必须合规 | GOV MCP现状 | 缺口优先级 |
|---|---|---|---|
| US | NIST AI RMF, SOX, FINRA | CIEU审计 | P1: COSO报告模板 |
| EU | AI Act, GDPR | governance字段 | P0: Art.14 human oversight证明 |
| China | CAC算法备案, 数据出境 | 无 | P1: 数据驻留验证 |
| Japan | METI AI指南, APPI | 无 | P2: 指南合规checklist |
| Singapore | IMDA框架, PDPA | 无 | P2: AI Verify兼容 |
