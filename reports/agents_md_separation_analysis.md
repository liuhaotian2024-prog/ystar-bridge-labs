# AGENTS.md 治理/组织 分离分析

**分析人：** Samantha Lin (Secretary)
**日期：** 2026-04-11
**状态：** 仅分析，不做修改。任何改动需Board批准。

---

## 分析结果

| Section | 行号范围 | 类型 | 说明 | 建议 |
|---------|---------|------|------|------|
| Header/Version | 1-7 | ORG | 文件元信息（版本号、owner、authority引用） | 留 |
| Iron Rule 1: Deterministic Enforcement | 10-16 | GOV | 禁止LLM进入check()路径，定义trust root | 迁移到Y*gov core contract（enforcement engine层） |
| Iron Rule 2: No Hardcoded Paths | 18-23 | GOV | 禁止硬编码路径，要求pathlib | 迁移到Y*gov engineering policy |
| Iron Rule 3: Ecosystem Neutrality | 26-51 | GOV | 禁止绑定特定生态，要求adapter层，commit验证格式 | 迁移到Y*gov engineering policy |
| CIEU Data Preservation Rule | 53-101 | GOV | 归档流程、cleanup前置条件、doctor检查 | 迁移到session config（CIEU相关obligation） |
| Directive Tracking Rule | 105-122 | GOV | Board指令10分钟分解、DIRECTIVE_TRACKER.md流程 | 迁移到session config（CEO obligation） |
| Social Media Engagement Rule | 125-191 | GOV | 外部发布审批流程、Content Approval Request模板 | 迁移到session config（publish gate） |
| Article Writing Rule | 193-218 | GOV | 内容source验证、fabrication=P0、domain claim禁令 | 迁移到CMO session config |
| Company Mission | 221-234 | ORG | 公司使命、产品定义、CIEU=销售证据 | 留 |
| Organizational Structure | 237-250 | ORG | 组织架构图、delegation chain层级 | 留 |
| Q1 2026 OKRs | 253-272 | ORG | 季度目标和关键结果 | 留（OKR是组织目标，不是治理规则） |
| Continuous Autonomous Work Mandate | 275-348 | MIXED | 规则1-6是GOV（idle=violation、report格式、enforcement timing）；规则7-8 Idle Learning Loop是GOV；第5条self-directed work examples是ORG（角色职责描述） | 拆分：examples留，enforcement rules迁移 |
| Operating Principles | 352-362 | MIXED | 原则1-5是ORG（文化价值观）；原则6 P0 blocker rule、原则7 CIEU liveness、原则8 Think-don't-just-execute是GOV（有enforcement后果） | 拆分：文化原则留，有enforcement后果的迁移 |
| CIEU Liveness Check | 365-398 | GOV | 每session运行doctor、异常=P0、具体enforcement细节 | 迁移到session config（boot obligation） |
| Absolute Prohibitions — Forbidden Paths | 401-407 | GOV | .env、.ssh、/etc等禁止访问路径 | 迁移到Y*gov policy（forbidden_paths列表） |
| Absolute Prohibitions — Immutable Files | 409-414 | GOV | AGENTS.md、agent definitions、cases、CIEU db只读 | 迁移到Y*gov policy（immutable_paths列表） |
| Absolute Prohibitions — Forbidden Commands | 416-421 | GOV | rm -rf、sudo、force push、DROP TABLE等 | 迁移到Y*gov policy（forbidden_commands列表） |
| Absolute Prohibitions — Forbidden Actions | 423-429 | GOV | 发邮件、publish、merge、花钱需Board | 迁移到Y*gov policy（board_gate列表） |
| CEO Agent | 432-455 | MIXED | Role/When CEO Activates是ORG；Write/Read Access是GOV；Obligations（SLA timing）是GOV | 拆分：role定义留，access/obligation迁移 |
| CTO Agent | 457-508 | MIXED | Role是ORG；Write/Read Access是GOV（boundary enforcement）；Obligations（P0=5min等SLA）是GOV；Engineering Standards是GOV；Release Obligations是GOV | 拆分：role留，access/obligations/standards迁移 |
| CMO Agent | 510-536 | MIXED | Role是ORG；Write/Read Access是GOV；Obligations是GOV；Default Output是ORG | 拆分 |
| CSO Agent | 539-563 | MIXED | 同CMO，role+default output是ORG，access+obligations是GOV | 拆分 |
| CFO Agent | 566-613 | MIXED | Role是ORG；Write/Read Access是GOV；Token Recording obligation是GOV；Data Integrity rules是GOV；Cost Categories是ORG | 拆分 |
| Escalation Matrix — Board Sign-Off | 616-628 | GOV | 需Board审批的动作清单 | 迁移到Y*gov policy（board_approval_required列表） |
| Escalation Matrix — CEO Can Approve | 630-641 | GOV | CEO委托权限清单 | 迁移到Y*gov policy（ceo_delegated_authority列表） |
| Escalation Matrix — Dept Head Autonomous | 643-648 | MIXED | 角色自治范围定义，介于ORG和GOV之间 | 拆分：角色描述留，权限边界迁移 |
| Cross-Review & CEO Approval | 650-708 | GOV | 交叉审核矩阵、SLA、P0 bypass规则、conflict resolution | 迁移到session config（review obligation） |
| Anti-Drift: Commit-Push Integrity | 710-718 | GOV | 30分钟内push、session end检查 | 迁移到session config（commit obligation） |
| Response Time SLAs | 720-731 | GOV | P0=5min、P1=15min等时间表 | 迁移到Y*gov obligation timing |
| Y*gov Governance Demonstration | 733-746 | ORG | 解释AGENTS.md与Y*gov的关系，外部展示用 | 留 |
| Case Accumulation Protocol | 749-768 | MIXED | case文档格式是GOV（流程规则）；三个purpose说明是ORG | 拆分 |
| Emergency Procedures | 770-774 | GOV | credential暴露、义务无法完成时流程 | 迁移到session config |
| Self-Bootstrap Protocol | 778-812 | MIXED | Power hierarchy说明是ORG；具体constraints和timing是GOV | 拆分 |
| Jinjin Delegation Protocol | 816-844 | MIXED | Jinjin是谁=ORG；delegation workflow rules=GOV；CEO inbox check obligation=GOV | 拆分 |
| Cross-Department Collaboration Protocol | 847-869 | ORG | 事件触发的协作流程描述，更像SOP | 留（但可考虑迁移到runbook） |
| Board Reporting Protocol | 872-889 | MIXED | 需Board审批清单=GOV（与Escalation Matrix重复）；CEO自决范围=GOV；决策框架=ORG | 拆分，去重 |
| Operational Files | 892-900 | ORG | CEO维护的文件列表 | 留 |
| Obligation Timing Registry | 903-927 | GOV | 所有义务timing配置，OmissionEngine直接读取 | 迁移到Y*gov session.json / contract |
| Fulfil机制说明 | 931-962 | GOV | 每个义务的fulfil标准和验证方式 | 迁移到Y*gov contract（与timing registry配套） |
| 合伙人宪法 | 964-1045 | MIXED | "我们是谁"段落=ORG（文化宣言）；七条标准中标准1-2-4-5-7偏ORG（文化价值观）；标准3质量+标准6诚实有enforcement后果=GOV；Fulfil机制段落=GOV | 拆分：文化宣言留，enforcement机制迁移 |
| CMO Content Governance | 1049-1069 | GOV | Deny rules、Allow rules、Content Footer要求 | 迁移到CMO session config / Y*gov policy |

---

## 统计汇总

- **纯GOV sections（应迁移）：** 20个
- **需要拆分的MIXED sections：** 14个
- **纯ORG sections（留在AGENTS.md）：** 7个

---

## 迁移建议

### 1. 迁移目标架构

```
AGENTS.md (瘦身后，约200-300行)
├── Company Mission
├── Organizational Structure
├── Q1 OKRs
├── 5个Agent的Role定义（仅who/what，不含access/obligations）
├── 合伙人文化宣言（去掉enforcement部分）
├── Y*gov Governance Demonstration说明
├── Operational Files列表
├── Cross-Department Collaboration Protocol
└── 每个constitutional rule保留一行引用（"详见Y*gov contract GOV-XXX"）

Y*gov Session Config / Contract (新增或扩展)
├── Iron Rules 1-3
├── Forbidden/Immutable paths
├── Forbidden commands/actions
├── Board approval gates
├── Agent access boundaries (read/write per agent)
├── All obligation timings
├── All fulfil standards
├── SLA table
├── Cross-review matrix
├── Content governance rules (CMO deny/allow)
├── Emergency procedures
├── CIEU preservation rules
└── Idle learning enforcement
```

### 2. 优先迁移项（风险最低、收益最高）

1. **Obligation Timing Registry（行903-927）** — 这段本来就是给OmissionEngine读的配置数据，以人类可读markdown存在AGENTS.md里是历史遗留。迁移到session.json零风险。
2. **Fulfil机制说明（行931-962）** — 与timing registry配套，一起迁移。
3. **Forbidden/Immutable paths（行401-414）** — 纯列表数据，适合机器读取。
4. **Response Time SLAs（行720-731）** — 纯数值表，迁移到contract。
5. **Agent access boundaries（散布在各Agent section）** — 每个agent的Write Access/Read Access段落，集中到一个policy文件。

### 3. 需谨慎处理的项

1. **Iron Rules 1-3** — 虽然是纯GOV，但它们是"宪法前言"性质。可以在AGENTS.md保留一行引用（"Iron Rules defined in Y*gov contract"），具体内容迁移。
2. **合伙人宪法** — 文化宣言和enforcement机制深度交织。拆分需要仔细措辞，避免削弱文化感染力。
3. **Idle Learning Loop** — 在AGENTS.md中重复出现5次（行76-98、166-188、325-347、374-396、685-707）。这是当前文件最严重的结构问题，迁移时应同时去重。

---

## 迁移风险

### 1. boundary_enforcer/hook 对AGENTS.md的依赖

当前Y*gov通过 `Policy.from_agents_md_multi()` 直接解析AGENTS.md来构建policy对象。具体调用链：

```
scripts/hook_wrapper_observe.py (行36):
    policy = Policy.from_agents_md_multi(agents_path)

scripts/governance_boot.sh (行117):
    测试immutable_paths enforcement时直接用AGENTS.md路径
```

**风险：** 如果将forbidden_paths、immutable_paths、agent access boundaries从AGENTS.md移除，`from_agents_md_multi()` parser将无法提取这些规则，导致enforcement静默失效。这是最危险的迁移风险。

**缓解方案：** 迁移必须分步执行：
1. 先在Y*gov中添加新的policy source读取能力（contract文件或session.json）
2. 修改 `from_agents_md_multi()` 使其同时读取AGENTS.md和contract文件（双source期）
3. 写集成测试验证新source产出的policy与旧source完全一致
4. 确认新source被正确加载后，才从AGENTS.md删除对应内容
5. 整个过程中hook enforcement不能有任何中断

### 2. Idle Learning Loop重复5次的问题

行76-98、166-188、325-347、374-396、685-707包含几乎完全相同的Idle Learning Loop内容。这看起来是多次AMENDMENT-003追加时的copy-paste错误。每个实例附带的"This rule exists because"段落内容不同（分别关于CIEU数据丢失、社交媒体、自主工作、CIEU liveness、cross-review），说明它们被追加到了不同constitutional rule的尾部。

**风险：** 如果不同实例之间有细微差异，迁移时需要确定哪个是canonical版本。

### 3. 文化内容与enforcement规则的耦合

合伙人宪法中"违反任何一条 = P0违规"这类enforcement语句嵌入在文化宣言中。如果只迁移enforcement部分，文化宣言可能失去"牙齿"。建议在AGENTS.md保留文化宣言全文，同时在Y*gov contract中镜像enforcement规则，形成双重保障。

### 4. Board Reporting Protocol与Escalation Matrix重复

行872-880的"Must submit to Board"清单与行616-628的"Always Requires Board Sign-Off"高度重复。迁移时应合并去重。

---

## 发现的额外问题

1. **Idle Learning Loop重复5次** — 同一段约30行的内容出现在5个不同位置，每次都作为某个constitutional rule的第7-8条。修复这个重复问题本身就能将AGENTS.md缩短约120行。这应该在任何迁移工作之前先修复。

2. **AGENTS.md当前约1069行** — 对于一个"宪法文件"来说过长。agent每次session boot都要加载全文，消耗大量context window。迁移后目标应在200-300行，聚焦组织架构和文化宣言。

3. **"This rule exists because"段落错位** — 多个section的历史原因说明被Idle Learning Loop的重复内容挤到了错误位置（例如行99的CIEU Preservation的because出现在Idle Learning Loop之后而非CIEU规则正文之后，行189的Social Media的because同理）。这降低了文件的可读性和可维护性。

4. **本次分析写入被hook拦截** — 原计划写入 `docs/` 目录，被CEO agent的write boundary拦截。这本身就是一个GOV规则（agent write access boundaries）生效的实例。改为写入 `reports/`（CEO允许的路径）。
