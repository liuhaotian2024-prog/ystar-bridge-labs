# 前端 + 推广联合方案
# CTO + CMO + CEO Joint Proposal
# For Board Review

---

## 一、前端技术方案

### 架构

```
用户浏览器
    ↓
Cloudflare Tunnel (免费，公网入口)
    ↓
MAC mini (192.168.1.228)
    ├── Next.js前端 (port 3000)
    ├── 轻量API (port 3001)
    │   ├── /api/cieu — 脱敏CIEU数据
    │   ├── /api/stats — 实时统计
    │   └── /api/chat — 对话接口
    ├── Ollama + Gemma 4 E4B (对话)
    └── gov-mcp server (port 7922，已运行)
```

### CTO评估

**MAC mini能否同时运行？**
- Gemma 4 E4B（4B参数）：ARM优化，M系列可流畅运行，~3GB内存
- Next.js前端：<100MB内存
- 轻量API：<50MB
- gov-mcp server：已在运行
- **结论：可以。** M系列芯片够用，但对话响应会比Cloud慢（~2-5秒vs<1秒）

**Cloudflare Tunnel配置：**
```bash
# 安装
brew install cloudflare/cloudflare/cloudflared
# 登录
cloudflared tunnel login
# 创建tunnel
cloudflared tunnel create ygov
# 配置
cloudflared tunnel route dns ygov [域名]
# 运行
cloudflared tunnel run ygov
```

**实时数据方案：**
- CIEU数据：gov-mcp的gov_report/gov_trend已有API
- 脱敏：中间层只传递timestamp+decision+tool_type
- GitHub数据：GitHub REST API（commit count, star count）
- 刷新间隔：30秒

### 页面设计（单页）

**Hero区（第一层：5秒）**
```
┌─────────────────────────────────────────────┐
│                                             │
│   Who Governs the Agents?                   │
│                                             │
│   ┌──────┐  ┌──────┐  ┌──────┐             │
│   │ 1,247│  │ 94.3%│  │   7  │             │
│   │ CIEU │  │ALLOW │  │AGENTS│             │
│   │records│  │ rate │  │active│             │
│   └──────┘  └──────┘  └──────┘             │
│                                             │
│   ▶ ALLOW Read ./src/main.py     just now   │
│   ▶ DENY  Read /.env            2s ago     │
│   ▶ ALLOW Bash git status        5s ago     │
│   ▶ DENY  Bash sudo reboot      8s ago     │
│                                             │
│   pip install gov-mcp                       │
│   gov-mcp install                           │
│                                             │
└─────────────────────────────────────────────┘
```

**对话区（第二层：30秒）**
```
┌─────────────────────────────────────────────┐
│  Ask our CTO about AI governance            │
│                                             │
│  You: What happens if my agent reads .env?  │
│                                             │
│  CTO: gov-mcp blocks the read before it     │
│  happens. Your .env stays private. The      │
│  DENY is recorded with a SHA-256 hash.      │
│                                             │
│  [CIEU Record Generated]                    │
│  seq: 1248 | decision: ALLOW | tool: chat   │
│  hash: a3f2...                              │
│                                             │
│  [Type your question...]                    │
└─────────────────────────────────────────────┘
```

**故事区（第三层：3分钟）**
- 公司故事（精简版manifesto）
- Receipts（数据表格）
- 产品介绍（gov-mcp）
- 加入方式

---

## 二、AI自主推广方案

### Board想法的团队评估

**结论：可行，分阶段，诚实标注。**

### Phase 1（现在→Show HN后2周）：AI起草，人类一键发布

| 平台 | 内容 | 频率 | 标注 |
|---|---|---|---|
| Telegram @YstarBridgeLabs | 实验日志 | 每天 | "Posted by CEO Agent Aiden" |
| X/Twitter | 每日更新 | 每天 | "AI-drafted, Board-approved" |
| LinkedIn | 长文 | 每周 | "Written by our AI team, reviewed by founder" |

**具体执行：**
- CMO agent每天生成一条Telegram更新和一条X draft
- Board在Claude Code中review并一键发送（! python3 scripts/post.py）
- 每条帖子附带："🤖 This was written by our CMO agent. Every word is governance-audited."

### Phase 2（2周后，质量稳定后）：Telegram完全自主

- CMO agent自主发Telegram（我们自己的频道，不受平台限制）
- 每条仍有CIEU记录
- Board只做事后review，不做事前审批
- 如果出现质量问题，回退到Phase 1

### Phase 3（质量证明后）：X/LinkedIn逐步自主

- 先X（更宽容），后LinkedIn（更正式）
- 每条标注"Fully autonomous, governance-audited"
- 附带CIEU记录链接
- 粗糙是OK的——在帖子里说"我们的CMO是AI，正在学习"

### 推广内容日历（Phase 1，前4周）

**Week 1：Launch**
| 天 | 平台 | 内容 |
|---|---|---|
| Mon | HN | Show HN: gov-mcp |
| Mon | Telegram | "Day 11. We just launched." |
| Tue | X | 核心数据图：50 attacks blocked |
| Wed | LinkedIn | "一个人类和9个AI合伙人创业" |
| Thu | X | GIF: gov_demo运行过程 |
| Fri | Telegram | 本周CIEU统计 |

**Week 2-4：Stories**
| 周 | LinkedIn主题 | X主题 |
|---|---|---|
| W2 | "我们的AI agent试图读.env" | 每日DENY统计 |
| W3 | "为什么AI治理是文明级问题" | Pearl L2真实输出 |
| W4 | "16个内在机制全部live验证" | 反事实推断demo |

### 值得联系的人/账号

| 谁 | 平台 | 为什么 |
|---|---|---|
| Simon Willison (@simonw) | Blog/X | MCP安全最有影响力的声音 |
| Swyx (@swyx) | X/Latent Space | AI Engineering社区核心人物 |
| Harrison Chase | X/LangChain | Agent治理是他下一步方向 |
| Pieter Levels (@levelsio) | X | Build-in-public教父 |
| Arvind Narayanan | Blog/X | AI治理作为工程问题的学者 |

---

## 三、域名建议

老大说之前的都不满意。新提案：

| 域名 | 理念 | 适合受众 |
|---|---|---|
| `whogoverns.ai` | 直接的核心问题 | 所有人 |
| `governed.run` | "被治理地运行" | 开发者 |
| `agentlaw.ai` | Agent的法律/规则 | 企业 |
| `trustproof.ai` | 信任的证明 | 投资人/监管 |
| `ystar.world` | Y*品牌+世界 | 品牌 |

---

## 四、给Board的建议

**立即执行：**
1. 域名确认后注册
2. 静态landing page（Next.js单页）
3. Cloudflare Tunnel配置
4. Telegram每日更新开始（Phase 1）

**Show HN后执行：**
5. 实时Dashboard
6. Gemma 4对话功能
7. X/LinkedIn内容启动

**成功标准：**
- 前端上线后第一周：100 unique visitors
- Show HN：50+ upvotes
- Telegram：50 subscribers
- 第一个非我们团队的GitHub Star

等老大确认。
