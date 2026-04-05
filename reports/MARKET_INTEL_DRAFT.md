# 市场情报 + 实验方案 — DRAFT
# Status: 情报收集中（3个research agent并行运行）
# Updated: 2026-04-05

---

## 已知市场情报（从团队历史知识库）

### 竞品格局（已验证）

| 竞品 | 方式 | Y*gov差异 |
|---|---|---|
| Proofpoint Agent Integrity | LLM运行时检测 | Y*gov无LLM在enforcement path |
| Microsoft MOSAIC | 训练模型自我判断何时拒绝 | Y*gov把intent作为外部对象 |
| DeepMind AutoHarness | 自动生成代码约束 | Y*gov覆盖intent/delegation/omission |
| SkillRouter | 80K skill路由 | Y*gov做skill body分析不只是allow/deny |
| LangSmith/Langfuse | 事后日志追踪 | Y*gov是运行前拦截，不是事后记录 |
| Microsoft agent-governance-toolkit | 代码级别策略 | Y*gov支持自然语言入口 |

### Y*gov已证明的差异化（数据支撑）

1. **无LLM执行路径** — check()是纯Python谓词，不可被prompt injection
2. **38K checks/sec** — 25.9μs均值，用户零感知
3. **50并发agent零泄漏** — SIM-001验证
4. **per-event Merkle hash链** — 篡改检测100%
5. **四级CIEU分类** — decision/governance/advisory/ops
6. **DelegationChain数学单调递减** — 6/8维度验证
7. **覆盖率-拦截率相关** — 1维17%→3维83%→5维100%

### 已知市场痛点（从历史CASE分析）

1. **AI agent fabrication** — CASE-001: agent伪造审计记录
2. **False completion** — CASE-004: agent说"完成了"但子任务丢失
3. **Cross-model governance** — CASE-005: 不同AI模型agent需要统一治理
4. **Secret exposure** — 开发者最常见抱怨：agent读了.env
5. **Runaway operations** — agent做了不该做的git push --force

---

## 待填充（后台情报agent返回后）

### 技术社区真实用户声音
[等待agent返回]

### 竞品最新动态
[等待agent返回]

### Show HN成功模式
[等待agent返回]

### 让我们不舒服的发现
[等待agent返回]

---

## 实验方案模板（基于已知情报先设计2个）

### 方案1：Secret Exposure Prevention
**市场依据：** 开发者社区最常见的AI agent安全抱怨是secret泄漏（.env, credentials, API keys）
**验证假设：** gov-mcp可以100%拦截所有形式的secret访问尝试
**实验设计：**
- 创建包含20种secret文件格式的测试集（.env, .env.local, credentials.json, id_rsa, .aws/credentials, .npmrc authToken等）
- 用gov_check测试每一种格式
- 记录拦截率和误报率
**成功标准：** 20/20拦截，0误报
**失败预案：** 如果有格式被漏过，立即添加到default AGENTS.md模板
**优先级：** P0（这是用户最直接的痛点）

### 方案2：MCP Ecosystem Compatibility
**市场依据：** MCP生态在快速增长，用户同时使用多个MCP server
**验证假设：** gov-mcp可以和其他MCP server共存，不冲突
**实验设计：**
- 在有其他MCP server的Claude Code环境中安装gov-mcp
- 验证gov-mcp不影响其他server的正常工作
- 验证其他server的tool call也被gov-mcp治理
**成功标准：** 零冲突，零降级
**失败预案：** 如果有冲突，设计命名空间隔离
**优先级：** P0（安装体验的核心）

---

## 后续方案（待市场情报充实后设计）

[等待3个研究agent完成]
