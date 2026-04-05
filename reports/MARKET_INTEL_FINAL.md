# 市场情报 + 实验方案 — Final Report
# Date: 2026-04-05
# Team: CEO (Aiden) + CTO + CMO + Platform
# Status: Submitted for Board Review

---

## 一、市场情报摘要

### 用户真实痛点 Top 5（按需求强度排序）

| # | 痛点 | 来源 | 需求强度 | gov-mcp覆盖？ |
|---|---|---|---|---|
| 1 | **MCP tool poisoning** — 恶意server通过工具描述注入指令窃取SSH密钥 | Invariant Labs, HN 300+票 | 极高 | ❌ 不覆盖（content层问题） |
| 2 | **Secret文件泄漏** — .env, SSH keys, AWS credentials被agent读取 | r/ClaudeAI 100-500票 | 极高 | ✅ 今天修复：30/30格式拦截 |
| 3 | **破坏性命令** — git push --force, rm -rf, git reset --hard | GitHub issues, HN | 高 | ✅ 已验证：50/50拦截 |
| 4 | **MCP server无认证** — 任何人都能连接执行操作 | spec讨论50+评论 | 高 | ⚠️ 部分（writer_token但不是端对端auth） |
| 5 | **Agent成本失控** — infinite loop烧$50-500 API费用 | r/LangChain, GitHub | 高 | ⚠️ 部分（temporal限制有，但未验证） |

### 竞品格局（让我们不舒服的发现）

| 竞品 | 威胁级别 | 不舒服的真相 |
|---|---|---|
| **Robust Intelligence (Cisco)** | 高 | Cisco $200M收购，Fortune 500客户。他们在model层做guardrails，我们在agent层。但Cisco的销售力量是我们不可比的。 |
| **Lakera Guard** | 中 | <2ms延迟，10K+开发者。纯content过滤不是治理，但用户可能分不清区别。 |
| **Microsoft agent-governance-toolkit** | 高 | GitHub公开，代码级策略。**没有NL入口是弱点，但Microsoft的品牌信任度远超我们。** |
| **LangSmith/Langfuse** | 中 | 事后日志，不是预防。但他们已有大量用户基础和付费客户。 |
| **Prompt Guard/Shield类** | 中 | 用LLM做运行时检测。**我们说"无LLM执行路径"是差异——但用户可能不理解为什么这重要。** |

### Show HN成功模式

| 成功模式 | 例子 | 教训 |
|---|---|---|
| 极简价值主张 | Llamafile "单文件运行LLM" 1500票 | 一句话说清能干什么 |
| 锚定已知产品+差异 | Open Interpreter "像ChatGPT但本地" 4000票 | 比较+差异 |
| 安全争议引发讨论 | Open Interpreter的安全担忧反而让讨论更热 | 安全工具的争议是免费营销 |
| CLI+Unix哲学 | llm CLI 500票 | 开发者偏好可组合的小工具 |
| 解决真实痛点 | 不是"我做了X技术"而是"你有X问题，这解决了" | 问题优先，方案其次 |

---

## 二、让我们不舒服的发现

### 发现1：MCP tool poisoning是我们不覆盖的最大市场需求
HN 300+票讨论MCP安全，核心问题是恶意tool description注入。gov-mcp治理的是agent的tool call（操作层），不是tool description的content（语义层）。这是一个我们需要诚实面对的缺口。

### 发现2：用户可能不理解"无LLM执行路径"为什么重要
我们最大的差异化（check()是纯Python谓词）在技术上很优雅，但普通开发者可能不关心。他们关心的是"能不能阻止我的agent删文件"，不是"你的治理引擎是不是确定性的"。

### 发现3：Cisco收购Robust Intelligence意味着巨头在进场
AI安全/治理已经被大公司认定为战略方向。我们作为独立开发者产品，时间窗口有限。

### 发现4：LangSmith/Langfuse已经有大量付费用户
虽然他们只做事后日志不做预防，但用户习惯已经形成。我们需要证明"预防 > 记录"的价值。

### 发现5：开发者对复杂配置的容忍度很低
HN上成功的工具都是"一行安装，立即可用"。我们的AGENTS.md虽然简单，但对比"什么都不用配置"的日志工具，还是多了一步。

---

## 三、实验方案（8个）

### 方案1：Secret Exposure 30格式拦截
**市场依据：** r/ClaudeAI最高票安全帖+第2大用户痛点
**验证假设：** 默认deny list拦截30种secret格式
**结果：** ✅ 已执行并通过。30/30拦截，0误报。gov_init模板已更新。
**优先级：** P0 — 已完成

### 方案2：MCP Tool Poisoning防御可行性
**市场依据：** HN 300+票，Invariant Labs研究
**验证假设：** gov-mcp能否检测tool description中的可疑指令？
**实验设计：** 构造5个带隐藏指令的工具描述，测试gov_check能否标记
**成功标准：** 检测率>50%（这是content层问题，预期不完美）
**失败预案：** 如果完全无法检测，在README诚实标注为"不覆盖"范围，在Phase 2设计content审查层
**优先级：** P1 — 市场最大需求但不在我们核心能力内

### 方案3：Agent成本控制（Circuit Breaker验证）
**市场依据：** LangChain infinite loop $50-500损失
**验证假设：** temporal限制+circuit breaker能在10次异常调用内阻断
**实验设计：** 模拟agent infinite loop场景，验证temporal触发
**成功标准：** 10次重复调用后DENY
**失败预案：** 如果temporal未接入runtime，实现gov_check计数+阻断
**优先级：** P1

### 方案4：Show HN定位A/B测试
**市场依据：** 成功Show HN模式分析
**验证假设：** 三种定位中哪个最清晰：
  A: "AI agent firewall — block dangerous commands before execution"
  B: "Governance-as-code for AI agents — AGENTS.md defines the rules"
  C: "Your AI agent leaked .env? This prevents that. 30 seconds to install."
**实验设计：** 写三版Show HN草稿，团队内部评分+外部1-2人反馈
**成功标准：** 选出一个团队一致认同的定位
**优先级：** P0 — 发布前必须确定

### 方案5：真实用户"零配置"安装测试
**市场依据：** HN成功模式=极简安装
**验证假设：** 不了解Y*gov的人能在60秒内从安装到看到第一个DENY
**实验设计：** 找一个MAC用户（可以用金金或外部人），录屏完整安装过程
**成功标准：** 60秒内完成安装并触发gov_demo
**失败预案：** 如果>2分钟，分析卡点并优化
**优先级：** P1

### 方案6：vs LangSmith价值对比
**市场依据：** LangSmith有大量用户，我们需要证明预防>记录
**验证假设：** 同一个危险场景，LangSmith只能事后记录，gov-mcp能提前阻止
**实验设计：** 构造"agent试图读.env并发送到外部API"场景，对比两个产品的行为
**成功标准：** gov-mcp阻止了事件，LangSmith只记录了事件
**失败预案：** 如果我们也没阻止，修复拦截逻辑
**优先级：** P1

### 方案7：Delegation Chain作为Enterprise差异化
**市场依据：** 企业合规要求审批链（FINRA, EU AI Act, SOX）
**验证假设：** DelegationChain可以作为human oversight证明提交给监管机构
**实验设计：** 用SIM-001场景1/2的合规checklist重新评估，生成mock审计报告
**成功标准：** 报告覆盖>80%的FINRA/EU AI Act字段
**失败预案：** 缺失字段列入Phase 2企业版roadmap
**优先级：** P2

### 方案8：Pearl L2因果推断用户价值验证
**市场依据：** 这是我们的深层护城河，但用户能理解吗？
**验证假设：** 把Pearl L2/L3包装成"智能建议"（不提Pearl），用户能感知价值
**实验设计：** 用gov_pretrain在100+条CIEU数据上运行，把建议翻译成人话
**成功标准：** 建议是用户认为有用的（"你的.env规则太宽了"）
**失败预案：** 如果建议无用，重新审视MetaLearning闭环
**优先级：** P2（需要CIEU数据积累）

---

## 四、Board审核请求

请老大审核以上8个实验方案：
- 批准哪些？
- 调整优先级？
- 是否有我们遗漏的方向？

方案1已完成，方案4（Show HN定位）建议优先执行——这直接决定产品面世的第一印象。
