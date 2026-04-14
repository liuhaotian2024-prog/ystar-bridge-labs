# Y*Defuse 社区渗透计划
**CSO Zara Johnson | 2026-04-11**
**战略目标**: 16个Awesome Lists + 5个AI工具目录 = 第一个月覆盖开发者社区核心节点
**Board授权**: CEO Aiden转达，全自主执行

---

## 一、Awesome Lists 提交（16个目标）

### A. 核心安全 / AI安全类（最高优先级，用户画像完美匹配）

| # | 仓库 | Stars | 提交策略 | 分类 |
|---|------|-------|---------|------|
| 1 | [awesome-llm-security](https://github.com/corca-ai/awesome-llm-security) | 1.5K+ | PR加入Defense/Runtime Protection分类，强调delayed injection defense（列表中无竞品覆盖此场景） | LLM安全 |
| 2 | [awesome-ai-security](https://github.com/DeepMINDS-Lab/awesome-ai-security) | 2K+ | PR加入Agent Safety Tools子分类，强调确定性执行不依赖LLM判断 | AI安全综合 |
| 3 | [awesome-prompt-injection](https://github.com/Cranot/awesome-prompt-injection) | 800+ | PR加入Defenses分类，全网最针对prompt injection的列表，核心战场 | 注入攻击专项 |
| 4 | [awesome-offensive-ai](https://github.com/jiep/awesome-offensive-ai) | 600+ | PR加入Defense Tools分类，攻防视角 | 攻防 |

### B. AI Agent / LLM工具类（流量最大）

| # | 仓库 | Stars | 提交策略 | 分类 |
|---|------|-------|---------|------|
| 5 | [awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) | 10K+ | PR加入Agent Governance and Safety分类，强调runtime enforcement | Agent生态 |
| 6 | [awesome-langchain](https://github.com/kyrolabs/awesome-langchain) | 7K+ | PR加入Safety and Governance分类，兼容所有Python agent框架 | LangChain生态 |
| 7 | [awesome-chatgpt](https://github.com/humanloop/awesome-chatgpt) | 8K+ | PR加入Safety Tools分类 | ChatGPT生态 |
| 8 | [awesome-generative-ai](https://github.com/steven2358/awesome-generative-ai) | 5K+ | PR加入Safety and Governance分类 | GenAI综合 |
| 9 | [awesome-claude](https://github.com/liunian/awesome-claude) 或同类 | 1K+ | PR加入Claude Code Safety分类，原生支持Claude Code hook | Claude生态 |

### C. 开发者工具 / CLI工具类（覆盖更广受众）

| # | 仓库 | Stars | 提交策略 | 分类 |
|---|------|-------|---------|------|
| 10 | [awesome-python](https://github.com/vinta/awesome-python) | 200K+ | PR加入Safety分类下的子条目，审核严格但流量巨大 | Python综合 |
| 11 | [awesome-python-security](https://github.com/guardrailsio/awesome-python-security) | 1K+ | PR加入Runtime Protection分类 | Python安全 |
| 12 | [awesome-cli-apps](https://github.com/agarrharr/awesome-cli-apps) | 14K+ | PR加入Safety分类 | CLI工具 |

### D. 企业 / DevOps / 合规类（长尾但高价值）

| # | 仓库 | Stars | 提交策略 | 分类 |
|---|------|-------|---------|------|
| 13 | [awesome-devsecops](https://github.com/TaptuIT/awesome-devsecops) | 4K+ | PR加入AI Agent Safety新子分类 | DevSecOps |
| 14 | [awesome-mlops](https://github.com/visenger/awesome-mlops) | 12K+ | PR加入Agent Governance分类 | MLOps |
| 15 | [awesome-production-machine-learning](https://github.com/EthicalML/awesome-production-machine-learning) | 16K+ | PR加入Governance and Safety分类 | 生产ML |
| 16 | [awesome-mcp](https://github.com/punkpeye/awesome-mcp-servers) | 15K+ | PR提交，ystar-defuse作为MCP防护层 | MCP生态 |

---

## 二、AI工具目录提交（5个目标）

| # | 目录 | URL | 提交方式 | 策略 |
|---|------|-----|---------|------|
| 1 | **skills.sh** | https://skills.sh | CTO确保repo有SKILL.md，自动上榜 | 最高优先--Vercel Labs运营，install计数自动排名 |
| 2 | **skillhub.club** | https://skillhub.club/account/developer | 创建开发者账号提交 | 15,000+ curated skills，有排名系统 |
| 3 | **Product Hunt** | https://producthunt.com | 创建产品页，选Developer Tools > Protection | 配合Show HN同期发布，互相导流 |
| 4 | **AlternativeTo** | https://alternativeto.net | 提交为Guardrails AI / Rebuff的替代品 | 选对竞品标签，让搜索竞品的人发现我们 |
| 5 | **claudemarketplaces.com** | https://claudemarketplaces.com | 先累计500+安装，或联系mert@vinena.studio | 长期目标，skills.sh安装量是前提 |

---

## 三、PR提交模板（统一格式）

### Awesome List PR标题格式
```
Add ystar-defuse - Runtime defense against delayed prompt injection attacks
```

### PR正文模板
```
What is ystar-defuse?

Y*Defuse is a runtime defense tool for AI agents. Instead of scanning inputs for
malicious prompts (an arms race), it enforces what actions agents can execute --
blocking credential theft, data exfiltration, and destructive commands deterministically.

Key features:
- Delayed prompt injection defense (cross-session behavior chain tracking)
- Auto-learned whitelist (zero config after 24h)
- 100% deterministic, no AI in the loop, <10ms latency
- pip install ystar-defuse && ystar-defuse start

MIT License | 10-second install | Free core protection
```

### 提交注意事项
- 每个PR前先读对应repo的CONTRIBUTING.md
- 遵守每个列表的格式要求（字母排序、描述长度限制等）
- 不在同一天提交超过3个PR（避免spam嫌疑）
- 每个PR都要有真实的、针对该列表受众的描述，不能复制粘贴

---

## 四、执行时间线

### Week 1 (Day 1-4): PyPI发布前准备
- 准备所有16个PR的草稿（不提交，等产品上线）
- 创建skills.sh和skillhub.club账号
- Product Hunt产品页草稿
- AlternativeTo页面草稿

### Week 1 (Day 4-7): PyPI发布后立即执行
- Day 4: 提交核心安全类4个Awesome Lists (#1-4)
- Day 5: 提交AI Agent类5个 (#5-9)
- Day 6: 提交开发者工具类3个 (#10-12)
- Day 7: 提交企业类4个 (#13-16)
- 同步提交5个AI工具目录

### Week 2-4: 跟进和维护
- 每天检查PR状态，响应maintainer反馈
- 被拒绝的PR分析原因，调整后重新提交
- 跟踪每个渠道带来的安装量（referrer分析）

---

## 五、KPI追踪

| 指标 | Week 1目标 | Week 2目标 | Month 1目标 |
|------|-----------|-----------|------------|
| PR提交数 | 16 | 修复被拒的 | 16 merged |
| PR合并数 | 5+ | 10+ | 14+ |
| 目录收录 | 3 | 4 | 5 |
| 来自Awesome Lists的安装 | 100 | 500 | 2,000 |
| 来自目录的安装 | 50 | 200 | 1,000 |

---

## 六、渠道优先级排序（ROI预估）

| 优先级 | 渠道 | 预期流量 | 理由 |
|--------|------|---------|------|
| P0 | awesome-ai-agents (#5) | 最高 | 10K+ stars，完美目标受众 |
| P0 | awesome-prompt-injection (#3) | 高 | 最精准的用户群 |
| P0 | skills.sh | 高 | 安装即排名，Claude Code原生生态 |
| P1 | awesome-python (#10) | 潜在最高 | 200K+ stars但审核严，成功率50% |
| P1 | Product Hunt | 高 | 一次性爆发流量 |
| P1 | awesome-mcp (#16) | 高 | MCP生态火热 |
| P2 | 其余Awesome Lists | 中 | 长尾覆盖 |
| P2 | AlternativeTo | 中 | SEO长尾 |
| P3 | claudemarketplaces.com | 低（短期） | 需500+安装门槛 |

---

**准备日期**: 2026-04-11
**执行触发**: CTO完成PyPI发布后立即启动
**负责人**: CSO Zara Johnson

**NOTE FOR BOARD**: 请将本文件移动到 sales/defuse_community_plan.md
