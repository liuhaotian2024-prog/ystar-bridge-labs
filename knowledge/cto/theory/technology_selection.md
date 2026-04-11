# CTO Theory: 技术选型 (Technology Selection)
# Priority 2 理论库 · 2026-04-11 · CEO代CTO自主学习

---

## 核心框架：RICE-G（Risk-aware, Iron Rule Compliant, Cost-effective, Ecosystem-neutral, Governance-compatible）

### 1. Risk-aware（风险感知）
评估新技术时先问：如果这个技术失败/被废弃/不兼容，回退成本是多少？

**今天的实例**：Letta 0.16.7
- 引入成本：安装+配置+学习API
- 回退成本：极高（PostgreSQL+pgvector+Docker依赖链）
- 决策：放弃，自建YML（回退成本≈删一个SQLite文件）

### 2. Iron Rule Compliant（铁律合规）
任何技术选型必须过三条Iron Rule检查：
- IR1：是否引入LLM到enforcement路径？→ DENY
- IR2：是否引入硬编码路径？→ DENY
- IR3：是否绑定特定生态？→ DENY

### 3. Cost-effective（成本效率）
用最简单的技术解决问题。

| 需求 | 重型方案 | 轻型方案（选这个） |
|------|---------|------------------|
| 记忆持久化 | Letta(PostgreSQL+50kLOC) | YML(SQLite+400LOC) |
| 向量搜索 | pgvector | sqlite-vss（待需要时加） |
| 视频生成 | 云端API($$$) | 本地Wan2.1(免费) |
| Agent通信 | 复杂消息队列 | Telegram bot(已有) |

### 4. Ecosystem-neutral（生态中立）
技术选型不能让Y*gov绑定任何特定框架。
- 选SQLite不选PostgreSQL → SQLite无服务器依赖
- 选MCP协议不选私有API → MCP是开放标准
- 选适配器模式不选直接集成 → 新生态加适配器即可

### 5. Governance-compatible（治理兼容）
新技术引入后能否被Y*gov治理？
- 有hook点吗？（能插入gov_check吗？）
- 有审计能力吗？（能写CIEU吗？）
- 有权限控制吗？（能接delegation chain吗？）

## 决策模板

```
技术选型：[名称]
用途：[解决什么问题]
RICE-G评估：
  R(风险)：回退成本 [低/中/高]
  I(铁律)：IR1[✅/❌] IR2[✅/❌] IR3[✅/❌]
  C(成本)：[具体成本 vs 替代方案]
  E(中立)：[是否绑定特定生态]
  G(治理)：[能否被Y*gov治理]
结论：[采用/拒绝/待验证]
```

---

*今天的教训：Letta评估花了1小时才得出"不可行"的结论。如果先跑RICE-G模板，5分钟就能在R(回退成本高)和C(50kLOC解决400LOC的问题)上否决。*
