# gov-mcp 文档化提案分析(items 3 + 4)

**作者**: Ethan Wright (CTO)
**日期**: 2026-04-09
**优先级**: P2(产品文档,不阻塞内部治理)
**权限层级**: **Level 2**(影响 gov-mcp 仓库,跨 repo 但只是文档新增,无产品代码改动)
**状态**: 分析,待 Board 批准执行
**触发**: Board GOV-005 followup items #3 + #4 + "请你们分析这个解决方案是否合适"

---

## 调研结果(基于 gov-mcp 源码 + 现状)

### 事实 1: gov-mcp/docs/ 目录是空的

```
$ ls -la /Users/haotianliu/.openclaw/workspace/gov-mcp/docs/
total 0
drwxr-xr-x   2 haotianliu  staff   64 Apr  5 08:58 .
drwxr-xr-x  12 haotianliu  staff  384 Apr  5 16:57 ..
```

**0 文件**。Board 问题 #1 ("/messages/端点没有文档") **属实**。

### 事实 2: gov-mcp 用 MCP 官方 SDK 的 FastMCP

`gov-mcp/gov_mcp/server.py` line 17:

```python
from mcp.server.fastmcp import FastMCP
```

**`/messages/` 端点不是 gov-mcp 自己定义的**——它是 **MCP 官方 Python SDK 的 FastMCP 在 SSE 模式下自动暴露的标准端点**。意思是:

- gov-mcp 没有"自己的" `/messages/` 协议格式可以单独写文档
- 真正的 wire format 由 [MCP spec](https://spec.modelcontextprotocol.io/) 定义
- gov-mcp 自定义的部分是: **它注册的 38 个工具的名称 + 输入 schema + 返回 schema**

**Board 问题的精确含义应该重读为**: "想用 raw HTTP 调用 gov-mcp,但不知道 MCP SSE 协议长什么样,加上 gov-mcp 的具体工具签名也没文档"。这是一个文档真空,但不是"gov-mcp 写一个 /messages/ 文档" 那么窄——更应该是"gov-mcp 写一份 protocol-level 调用指南"。

### 事实 3: gov-mcp 没有任何 quick-start 不依赖现有 MCP client

`gov-mcp/cli.py` 的 `detect_ecosystems()` 只识别 4 种现成 MCP client: **Claude Code, Cursor, Windsurf, OpenClaw**。没有 CrewAI、LangChain、AutoGen、CrewMCP、AG2、自写 Python client 的任何示例。

**README.md 的 Quick Start 章节实际上是"假设你有一个 MCP client"**:

```bash
pip install gov-mcp
gov-mcp install   # ← 这一步只对 4 个 detected ecosystem 自动配置
```

如果用户没有 Claude Code/Cursor/Windsurf/OpenClaw,`gov-mcp install` 不会做任何 client 配置,用户会看到 server 跑起来但不知道怎么调它。Board 问题 #2 **属实且严重**——这是 gov-mcp 0-to-1 体验的最大死结。

### 事实 4: gov-mcp/tests/ 30 个 test 文件全是内部测试

```
test_concurrent_stress.py / test_e2e_flow.py / test_p0_security.py / ... ×30
```

这些是 gov-mcp 自己的回归测试,**不是用户可以拿来作 quick-start 的最小示例**。gov-mcp 的 product surface 没有 "5 分钟跑起来" 的入口。

### 事实 5: gov-mcp 在 PyPI 已经发布

README 写 `pip install gov-mcp` ——这是已发布的 product。任何外部用户(含潜在企业客户)拿到 PyPI 包后,如果他们用的不是 4 个 detected ecosystem 之一,**会立刻 stuck**。这是销售/采纳的硬障碍。

---

## 对 Board 提案的分析

### 问题 #1 ("/messages/端点没有文档") + Board 提的解决方案

**Board 的方案**: 写一份 `/messages/` 端点的请求格式文档。

**我的分析**: 方向正确,但**范围过窄**。原因:
- `/messages/` 端点的 wire format 由 MCP spec 定义,不是 gov-mcp 的自由发挥。如果只写"gov-mcp 的 /messages/ 端点接受 JSON-RPC 2.0 请求...",这等于复制 MCP spec,价值不高。
- 用户真正需要的是: **怎么用 raw HTTP 调用 gov-mcp 的某个具体工具**。例如 "POST 一个 tools/call 请求调用 gov_check 检查文件读权限",这是用户的实际场景。
- 此外: SSE handshake(必须先 GET /sse 建立 stream,再 POST /messages/?session_id=... 发请求),这个握手流程对没用过 MCP 的人来说**完全黑盒**。

**修正后的方案**(仍然是 Board 的"写文档",但更宽):

`gov-mcp/docs/PROTOCOL.md`(~250 行)涵盖:
1. **Why this doc exists** (1 段): MCP SSE 协议总览,gov-mcp 在它上面提供 38 个治理工具
2. **SSE handshake walk-through** (50 行): 如何先 GET /sse 拿到 session_id,如何然后 POST /messages/?session_id=... 发请求,带具体 curl 示例
3. **JSON-RPC 2.0 请求格式** (30 行): MCP 用的子集
4. **`tools/list` 完整请求/响应示例** (30 行): 列出 gov-mcp 的全 38 工具
5. **`tools/call` 完整请求/响应示例** (60 行): 调用 `gov_check` 的真实例子,展示 ALLOW + auto_executed + governance envelope 三个字段
6. **错误模式** (20 行): 常见 4xx/5xx + 解释
7. **upstream MCP spec 引用** (5 行): 链接到 modelcontextprotocol.io 的 spec

**为什么这个比"窄写 /messages/ 一个端点"更好**: 它是给真正想用 gov-mcp 但没有 Claude Code 的用户的**完整 0→1 路径**,不是孤立的 endpoint reference。

### 问题 #2 (没有 MCP client 体验不到 gov-mcp) + Board 提的解决方案

**Board 的方案**: 写一份不依赖 Claude Code 的 gov-mcp 快速入门,包含 CrewAI 集成示例。

**我的分析**: **方向 100% 正确,但 CrewAI 不应该是唯一目标**。原因:
- CrewAI 是 multi-agent 框架,有用户基础,但**它对 MCP 的官方支持是 2024 年中才加的**(`mcp-tool` 适配器),还不算 mainstream。
- 不依赖 Claude Code 的最 baseline 路径是 **用 raw `mcp` Python client SDK**——这是 5 行代码就能跑的最小示例,适用于任何 Python 用户,无框架依赖。
- CrewAI 集成示例是"框架级 quick-start" 中的 1 个,可以作为第二份文档。
- 还有 LangChain、AutoGen、AG2 等其它 mainstream framework,各自的 quick-start 是后续 P3 任务,不应该现在写齐。

**修正后的方案**(2 份独立文档,而不是 1 份):

**Doc A: `gov-mcp/docs/QUICKSTART_PYTHON.md`** (~150 行)
- 假设: 用户有 Python 3.10+,gov-mcp 已经 `pip install` 完
- 内容:
  1. 启动 gov-mcp server (`python -m gov_mcp --transport sse --port 7922`)
  2. 用 raw `mcp` 客户端 SDK 连接 server (~30 行 Python 示例)
  3. 调 `tools/list` 看到 38 个工具
  4. 调 `gov_check` 检查一个 hypothetical action,看到 ALLOW + governance envelope
  5. 调 `gov_check` 检查一个被禁止的 action,看到 DENY + violation reasons
  6. 调 `gov_report` 看 CIEU 库统计
- **目标用户**: 任何 Python 开发者,5 分钟跑起来

**Doc B: `gov-mcp/docs/QUICKSTART_CREWAI.md`** (~250 行)
- 假设: 用户有 CrewAI installed,想给 CrewAI agent 加治理
- 内容:
  1. 启动 gov-mcp server
  2. 用 CrewAI 的 `mcp-tool` 适配器连接 gov-mcp(~20 行 setup)
  3. 定义一个简单 Crew(1 个 agent + 1 个 task,例如 "read a file"),所有 tool call 经过 gov-mcp 治理
  4. 跑一次 Crew,看到 gov-mcp 拦截/允许的真实日志
  5. 故意让 agent 试图 `cat /etc/passwd`,看到 DENY 阻断
  6. 查 CIEU 库看完整审计链
- **目标用户**: CrewAI 开发者,15 分钟跑起来,看到"什么是治理化 agent"

**为什么不是 Board 提的"1 份 CrewAI"**: 
- Doc A(raw Python)适用面 100x 大于 Doc B(CrewAI)
- Doc A 是 Doc B 的前置(理解 raw 协议后才好用框架适配器)
- CrewAI 用户群是 Python 用户群的子集(估计 <10%),写 raw Python 示例覆盖更多潜在用户
- 但 CrewAI 示例展示了"端到端治理化 agent"的真实场景,有营销价值,值得单独写

---

## 反事实分析

### 方案 X: 严格按 Board 字面执行

**做法**: 写 1 份 `/messages/` 端点窄文档 + 1 份 CrewAI 示例。

**Yt**: 2 文档,大概 300+200 行,1 天工作。
**Rt**: 
- ✅ Board 字面意图满足
- ❌ 范围过窄,没解决"raw HTTP 怎么调 gov-mcp"的根本问题(因为 /messages/ 文档脱离了 SSE handshake 上下文)
- ❌ 没有 raw Python 示例,把所有不用 CrewAI 的 Python 用户排除在外

### 方案 Y: 修正后的 3 文档方案(我推荐)

**做法**: 写 3 份独立 doc:
- `gov-mcp/docs/PROTOCOL.md`(SSE handshake + raw HTTP + 38 工具签名)
- `gov-mcp/docs/QUICKSTART_PYTHON.md`(raw mcp Python client + 5 行可运行代码)
- `gov-mcp/docs/QUICKSTART_CREWAI.md`(CrewAI 集成端到端示例)

**Yt**: 3 文档,~250+150+250 = 650 行,1.5-2 天工作。
**Rt**:
- ✅ 真正消除文档真空(任何 Python 用户能 5 分钟跑起来)
- ✅ raw Python 示例覆盖最广用户群
- ✅ CrewAI 示例覆盖框架用户 + 营销
- ✅ PROTOCOL.md 是 reference,后续其它 framework 文档(LangChain/AutoGen)都可以引用它
- ⚠️ 工作量比方案 X 多 50%
- ⚠️ 跨 repo:gov-mcp 是单独 repo,需要在 gov-mcp/ 提 commit + push,影响 gov-mcp PyPI 下次发布

### 方案 Z: 最小可行(只写 PROTOCOL.md)

**做法**: 只写 1 份 `gov-mcp/docs/PROTOCOL.md`,详尽的 raw HTTP + 38 工具 reference,**跳过** quick-start 示例(用户自己看 reference 写代码)。

**Yt**: 1 文档,~250 行,半天工作。
**Rt**:
- ✅ 解决 Board 问题 #1
- ⚠️ 没解决问题 #2(用户还是要自己摸索如何用 raw mcp client)
- ✅ 工作量最小
- ✅ 单 commit 单 push,gov-mcp 下次发布 minimum 改动

---

## 最优解 = **方案 Y(3 文档)**

**理由(一句话)**: 文档真空是 gov-mcp 销售/采纳的硬障碍,既然要花时间填空,一次填到位比只解决一半的问题划算。3 份文档是分层结构(reference + raw quickstart + framework quickstart),互相独立,任何用户都能在 5-15 分钟内跑通他需要的那一份。

## 次优解 = **方案 Z(只写 PROTOCOL.md)**

**为什么不是最优**: 适合"只想验证 Board 是否真的想填这个空"的最小投入版本。如果 Board 觉得方案 Y 工作量过大,可以先做 Z,然后看用户反应再补 quickstart。

## 最不推荐 = **方案 X(严格按字面)**

**为什么**: Board 的字面方案有"窄文档 + 单框架示例"的两个独立缺陷,合起来不能解决根本问题。Board 的提案值得感谢(方向正确),但需要修正范围。

---

## 跨 repo 注意事项

3 份文档全部位于 `/Users/haotianliu/.openclaw/workspace/gov-mcp/docs/`,**不在 ystar-company repo**。

| 项 | ystar-company | gov-mcp |
|---|---|---|
| repo 路径 | `/Users/haotianliu/.openclaw/workspace/ystar-company` | `/Users/haotianliu/.openclaw/workspace/gov-mcp` |
| Ethan 写权限 | ✅ (CTO) | ✅ (CTO,见 agents/CTO.md "Y\*gov全部代码 + gov-mcp全部代码") |
| 本提案位置 | `reports/cto/gov_mcp_docs_analysis.md` | (暂不放) |
| 实施位置 | (无) | `gov-mcp/docs/PROTOCOL.md` 等 |
| commit + push | (本分析) | (实施时,在 gov-mcp repo 单独 commit) |

**实施会跨两个 repo**: 本分析在 ystar-company,实施在 gov-mcp。Board 批准后,Ethan 进入 gov-mcp 目录单独 commit + push,gov-mcp 下个 PyPI 发布时把 docs/ 包进去。

---

## 验证 Board 假设的关键事实

| Board 假设 | 现实 | 是否需要纠正 Board 理解 |
|---|---|---|
| `/messages/` 端点没有文档 | ✅ 真,gov-mcp/docs/ 是空的 | 不需要 |
| 写 `/messages/` 文档能解决问题 | ⚠️ 部分,真问题是缺乏完整 raw HTTP 调用指南 | **是**,需要扩展范围(PROTOCOL.md 而不是 endpoint reference) |
| 没有 MCP client 体验不到 gov-mcp | ✅ 真,4 个 detected ecosystem 之外都 stuck | 不需要 |
| CrewAI 是合适的 quick-start 框架 | ⚠️ 是,但不应该是唯一,raw Python 应在前面 | **是**,需要补 raw Python quickstart |
| 3 + 4 是 2 个独立任务 | 应是 3 个文档 | **是**,需要拆成 3 文档 |

---

## Board 决策需要回答

**只需要一句话**: 选 X、Y、Z?

- **Y(推荐)**: Ethan 1.5-2 天写 3 份 gov-mcp/docs/ 文档。完整 protocol reference + raw Python quickstart + CrewAI quickstart。3 commits in gov-mcp repo。
- **Z**: Ethan 半天写 1 份 PROTOCOL.md,跳过 quickstart。1 commit in gov-mcp repo。
- **X**: Ethan 1 天严格按 Board 字面写 endpoint doc + CrewAI 示例。2 commits in gov-mcp repo。

如果 Board 批准方案 Y 或 Z,Ethan 在下次 session(不在本 session,因为 GOV-005 已饱和)进入 gov-mcp 仓库单独提案 + 实施。

---

**End of analysis.** 等 Board 一句话决定方案,然后下次 session 启动实施。
