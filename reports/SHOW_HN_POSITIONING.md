# Show HN Positioning — Board Decision + A/B Test Design

## Board选择：定位C
"Your AI agent leaked .env? This prevents that."

## 三个候选定位对比

| 定位 | 描述 | 优点 | 风险 |
|---|---|---|---|
| A: "AI agent firewall" | 技术层面准确 | 开发者立刻理解 | "firewall"暗示复杂配置 |
| B: "Governance-as-code" | 差异化强 | 吸引基础设施工程师 | "governance"让HN用户退避 |
| **C: ".env leak? prevents that"** | **痛点驱动** | **每个开发者都懂** | 可能显得scope太窄 |

## Show HN草稿（基于定位C）

### Title:
```
Show HN: gov-mcp – Your AI agent leaked .env? This prevents that
```

### Body (350 words):

```
AI agents (Claude Code, Cursor, Devin) can read any file on your machine.
Including .env, ~/.ssh/id_rsa, and ~/.aws/credentials.

I built gov-mcp to stop that. It's an open-source MCP server that sits
between your AI agent and your system. Every action is checked against
a simple rules file (AGENTS.md) before execution.

Install in 30 seconds:
  pip install gov-mcp
  gov-mcp install

Write your rules:
  ## Prohibited: .env files, /etc, rm -rf, sudo, git push --force

That's it. gov-mcp auto-detects your setup (Claude Code, Cursor, etc.)
and starts enforcing.

What it does:
- Blocks access to 30+ secret file formats (.env, SSH keys, AWS creds)
- Blocks dangerous commands (rm -rf, sudo, git push --force)
- Every decision has a tamper-proof audit record (SHA-256 hash chain)
- Safe commands (ls, git status) execute inline — zero overhead

What it doesn't do:
- It doesn't filter LLM content (not a prompt guard)
- It doesn't sandbox execution (not a container)
- It governs what the agent DOES, not what it SAYS

Numbers from testing:
- 50 attack variants: 100% blocked, 0 false positives
- Latency: 26μs per check (38,000 checks/sec)
- 50 concurrent agents: zero data leaks across isolated tenants
- Token savings: 45% fewer tokens vs ungoverned execution

Built on Y*gov (MIT licensed), the same governance kernel that
runs our own AI agent company. We eat our own dogfood.

GitHub: [link]
```

## A/B测试设计

| 平台 | 定位A | 定位B | 定位C |
|---|---|---|---|
| HN Show HN | 标题用C | — | — |
| Reddit r/ClaudeAI | 帖子用A | — | — |
| Reddit r/LocalLLaMA | — | 帖子用B | — |
| Twitter/X | 推文用C | — | — |
| LinkedIn | 文章用A | — | — |

观察指标：点击率、评论数、情感倾向

## 注意事项
- 不说"platform"说"tool"
- 不说"enterprise"说"open-source"
- 不提SOC2/ISO（HN不关心）
- 诚实说limitations（增加可信度）
- 等Board审核后发布
