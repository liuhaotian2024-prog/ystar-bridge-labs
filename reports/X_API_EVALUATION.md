# X (Twitter) API v2 — CMO自主发布评估
# Date: 2026-04-05

---

## X Developer Portal申请流程

### 申请步骤

1. **登录** https://developer.twitter.com 用 @liuhaotian_dev 账号
2. **申请Developer Account** — 需要描述用途
3. **创建Project + App** — 获取API keys
4. **生成OAuth 2.0 credentials** — User Authentication Settings

### 老大需要做的（一次性，约10分钟）：

1. 登录 https://developer.twitter.com
2. 点"Sign up for Free Account"
3. 描述用途（建议写）：
   "Automated posting for Y* Bridge Labs company updates.
   Our AI CMO agent generates governance-audited content
   and publishes daily updates about our AI governance experiments."
4. 创建App，获取以下4个值：
   - API Key
   - API Key Secret
   - Access Token
   - Access Token Secret
5. 把这4个值设为环境变量（老大执行一次）：
```bash
export X_API_KEY="..."
export X_API_SECRET="..."
export X_ACCESS_TOKEN="..."
export X_ACCESS_SECRET="..."
```

### Free Tier限制

- **发推：1,500条/月**（约50条/天，远超需求）
- **读取：限制较多但我们不需要读**
- 费用：**$0**

### 申请审批时间
- Free tier：**通常即时批准**
- Basic tier ($100/月)：不需要，Free够用

---

## CTO：publish_x.py 脚本

```python
# 等老大设置好API credentials后可用
# 使用tweepy库（pip install tweepy）
```

---

## CMO：每日自主发布流程

```
每天一次（由GovernanceLoop触发或手动）：
1. CMO读取昨天的gov_report数据
2. 生成推文内容（<280字）
3. 推文末尾加：
   "🤖 — CMO agent · Y*gov audited"
4. 调用publish_x.py发布
5. 写入CIEU记录（advisory级别）
```

---

## LinkedIn方案

CMO写好内容 → 格式化 → 通过Telegram Bot发给老大 → 老大复制粘贴发布

这是目前最接近自主的方案。LinkedIn API需要公司页面+审批，流程更复杂。

---

## 老大行动清单

| 步骤 | 操作 | 时间 |
|---|---|---|
| 1 | 登录 developer.twitter.com | 2分钟 |
| 2 | 申请Free Developer Account | 5分钟 |
| 3 | 创建App，获取4个key | 3分钟 |
| 4 | 设置环境变量 | 1分钟 |
| **总计** | | **~10分钟** |

完成后CMO即可完全自主发推。
