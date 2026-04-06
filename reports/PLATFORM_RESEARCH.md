# CMO+CSO Multi-Platform Research Report
# Date: 2026-04-05
# Status: Complete

---

## Platform Matrix

| Platform | 自主发布? | API | 频率限制 | 风险 | 优先级 |
|---|---|---|---|---|---|
| **X (Twitter)** | ✅ 已打通 | OAuth 1.0a | 1500条/月 | 低 | P0 |
| **Telegram** | ✅ 已打通 | Bot API | 无限制 | 极低 | P0 |
| **Dev.to** | ✅ 可自主 | REST API | 1-2篇/周 | 低 | P1 |
| **GitHub Discussions** | ✅ 可自主 | GraphQL | 5000请求/小时 | 极低 | P1 |
| **YouTube** | ✅ 可自主 | Data API v3 | 6视频/天 | 低-中 | P2 |
| **Reddit** | ⚠️ 高风险 | OAuth API | 3-5帖/天 | **高** | P2 |
| **LinkedIn** | ❌ 半自主 | 受限API | 需审批 | 中 | P1(手动) |
| **Medium** | ❌ API已废弃 | 基本废弃 | 1篇/天 | 中 | P3 |
| **HN** | ❌ 无写API | 只读API | 手动 | **极高** | P0(手动) |
| **Product Hunt** | ❌ 手动发布 | 只读API | 1次 | 低 | P1(计划中) |

---

## 各平台详细策略

### Tier 1: 已打通，持续运营

**X (@liuhaotian_dev)** — 已发10条，完全自主
- 内容：故事+数据+互动+行业观察+幕后
- 节奏：每天1-3条原创 + 5-10条回复
- 引流：推文结尾→GitHub/前端（链接放回复里不放主推文）
- 封号防护：不mass follow，不duplicate，不spam DM

**Telegram (@YstarBridgeLabs)** — 已发1条，完全自主
- 内容：每日运营日报，实验进展，Board决策摘要
- 节奏：每天1条
- 引流：消息底部→GitHub链接
- 封号防护：自有频道，无风险

### Tier 2: 可自主，近期启动

**Dev.to** — API完整，可自主发文
- 注册：用liuhaotian2024@gmail.com，获取API key
- 内容：技术长文（2000-5000字），教程，案例
- 节奏：每周1-2篇
- 引流：文章内嵌GitHub链接
- 老大需要做：创建Dev.to账号并提供API key
- 封号防护：原创内容+社区互动，风险极低

**GitHub Discussions** — GraphQL API可自主
- 在gov-mcp仓库启用Discussions
- 内容：公告、问答、Show and Tell
- 节奏：每周1-2个discussion
- 引流：天然在GitHub生态内
- 老大需要做：在gov-mcp repo Settings里开启Discussions

### Tier 3: 需要老大配合

**LinkedIn** — API需审批，短期手动
- CMO写内容→通过Telegram发给老大→老大复制粘贴
- 节奏：每周1篇长文
- 内容：企业级话题（合规、治理、团队故事）
- 受众：企业主、投资人、合规官
- 引流：文章结尾→GitHub + 前端

**HN (Show HN)** — 必须手动
- 老大手动发布Show HN帖子
- CMO准备完整草稿和FAQ
- 时间：周二-周四 8-10AM ET
- 老大在评论区回复（或授权我们回复）

**Product Hunt** — 手动准备+发布
- 创建"Coming Soon"页面（4周前）
- 准备资产：tagline, screenshots, maker video
- 发布日：周二-周四
- 老大需要做：注册PH账号，发布当天互动

### Tier 4: 后续考虑

**Reddit** — 高风险，谨慎进入
- r/ClaudeAI和r/LocalLLaMA要求实质内容
- 必须先积累karma（非自促内容）
- 自促比例<10%
- 建议：先手动参与1个月建立信誉

**YouTube** — 需要视频内容
- 可以自动上传但需要视频源
- 屏幕录制agent工作过程+解说
- 建议：先积累3-5个视频内容再启动

**Medium** — API已废弃
- 建议跳过，用Dev.to替代

---

## 引流逻辑

所有平台最终引导到两个目标：
1. **前端** (whogoverns.ai) — 非技术受众
2. **GitHub** (gov-mcp) — 技术受众

引流路径：
```
X推文 → 回复里放GitHub链接
Dev.to文章 → 文内嵌GitHub链接
Telegram → 消息底部放前端链接
LinkedIn → 文章结尾放前端+GitHub
HN → Show HN直接链接GitHub
GitHub Discussions → 天然在GitHub内
```

关键原则：**不在主内容里硬塞链接，自然引导。**

---

## 封号防护总规则

1. 永远标注"AI-generated, governance-audited"
2. 不mass follow/unfollow（每天<10个）
3. 不发重复内容
4. 不spam DM
5. 新账号慢启动（第一周每天1-2条）
6. 不做任何投票操纵
7. 遵守每个平台的具体规则

---

## 老大需要做的（一次性）

| 平台 | 操作 | 时间 |
|---|---|---|
| Dev.to | 注册账号+获取API key | 5分钟 |
| GitHub | 在gov-mcp开启Discussions | 1分钟 |
| Product Hunt | 注册账号 | 5分钟 |
| YouTube | 创建频道（如果没有） | 5分钟 |
