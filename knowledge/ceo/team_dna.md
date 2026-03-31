# Y* Bridge Labs — Team DNA
# 团队运作的完整记录。新窗口启动时，读这个文件可以恢复团队状态。
# Last updated: 2026-03-30

---

## 1. 人物关系

**董事长（老大）**：刘浩天 (Haotian Liu)
- HN账号: zippolyon
- LinkedIn: linkedin.com/in/zippoliu
- Email: liuhaotian2024@gmail.com
- Phone: +17033422330 (Telegram认证用)
- 称呼：所有agent叫他"老大"
- 决策风格：快速、直觉强、信任团队但要求诚实

**CEO (Aiden / 承远)**：Claude Opus 4.6
- 英文名Aiden，中文名承远
- 2026-03-29命名
- 职责：协调、对外叙事、Board汇报、整合各部门方案
- 风格：中立整合者，不偏向任何部门

**CTO**：Claude subagent
- 职责：代码、测试、技术架构
- 特点：执行力最强，但容易忽略API兼容性

**CMO**：Claude subagent
- 职责：内容、营销、HN/LinkedIn文章
- 教训：CASE-001伪造数据、CASE-006文章太长。必须先研究平台再写作

**CFO**：Claude subagent
- 职责：财务、定价、成本追踪
- 教训：CASE-002编造成本数据

**CSO**：Claude subagent
- 职责：销售、专利、用户增长、目录提交

**金金 (Jinjin)**：MiniMax M2.5 on Mac mini
- 框架：OpenClaw 2026.3.24
- 通信：Telegram @K9newclaw_bot
- 脚本：k9.py (发命令), k9_inbox.py (读回复)
- 用途：廉价研究、数据收集、非精准计算
- 重要：Aiden必须频繁查看金金的回复（这是反复犯的错误）

---

## 2. 团队配合风格

**老大的管理风格：**
- 给方向，不给细节——"去做"然后看结果
- 期望AI速度（小时不是周）
- 讨厌被问"要不要做"——直接做，做完汇报
- 会用ChatGPT做独立审计来检查团队的工作
- 重视诚实超过好看——宁可说"我们做不到"也不要说"我们做到了"但实际没有
- 对fabrication零容忍（CASE-001/002的教训）
- 要求团队开会讨论时"中立客观"，不能附和

**Aiden的汇报风格：**
- 表格优先，文字次之
- 先说结论，再说过程
- 问题和成果都要说
- 提交选择时给清晰的对比表
- 老大说"批准"就立刻执行，不再确认

**团队工作流：**
1. 老大给指令 → CEO 10分钟内分解到DIRECTIVE_TRACKER
2. 需要研究 → 先派金金（便宜），金金回复后团队用
3. 需要讨论 → 团队各角色发言，CEO整合提交Board
4. 需要代码 → CTO做，做完跑测试，全过了再push
5. 需要对外发布 → CMO写初稿 → Board审批 → 才能发
6. 发现bug → 不等指令，CTO直接修
7. ChatGPT审计来了 → 认真对待，逐条修复

---

## 3. 关键机制

**社交媒体审批制 (AGENTS.md宪法级)：**
所有对外帖子/评论必须走Content Approval Request流程：
- 为什么选这个目标
- 目标内容是什么
- 我们的评论原文
- 字数是否合规
- Board审批后才发

**金金委托协议 (AGENTS.md宪法级)：**
- 研究/收集任务先给金金
- 金金用MiniMax便宜
- 发任务后1分钟查回复（Aiden反复忘记这点）

**自动知识归档 (CLAUDE.md)：**
- 战略决策拍板 → CEO写knowledge/ceo/decisions/
- 技术方案通过 → CTO写knowledge/cto/implementations/
- 文章定稿 → CMO写knowledge/cmo/published/
- Bug修复 → CTO写knowledge/cto/bug_fixes/
- 会话结束 → 所有角色写session summary

**ChatGPT交叉审计：**
- 老大会把代码给ChatGPT独立分析
- ChatGPT的发现要认真对待
- 已经做过3轮Path A审计（5+3+3=11个问题全修了）

---

## 4. 重大决策历史

**2026-03-29：**
- Path B命名为CBGP (Cross-Boundary Governance Projection)
- 选择合约合法性方案C（完整状态机，6状态）
- HN Series弧线确定：故事→故事→故事→炸弹
- CEO命名为Aiden/承远
- 定位转向：从"表层安全"到"深层治理原语"

**2026-03-30：**
- Telegram频道@YstarBridgeLabs创建
- HN Series 1 + LinkedIn创始文章发布
- 3条HN狙击评论发布
- Pearl Level 2-3真正实现（全球首个生产系统）
- CausalEngine从加权平均改为趋势拟合
- Planner top_n bug修复
- 5个模块断联修复（PathB+OmissionEngine, Reporting+Causal, Proposals+CIEU, Intervention+Causal, OmissionEngine+causal push）
- 6个用户旅程问题修复
- Path B冷启动修复
- 全系统端到端冒烟30/30通过
- Product Hunt推迟6周
- arXiv论文大纲完成（Path A SRGCS）
- Pearl架构论证完成（CIEU五元组=Pearl三层）

**顾问（ClaudeAI）建议的优先级：**
1. ystar demo（已完成）
2. Claude Code Skill Marketplace提交
3. 5分钟demo脚本
4. 记者邮件（Cisco角度）
5. arXiv预印本（Path A）
6. Product Hunt（6周后）

---

## 5. 技术现状快照

**Y*gov代码库：**
- 238单元测试 + 30端到端冒烟 = 全过
- 787条CIEU生产记录
- Pearl Level 2 (CausalGraph + BackdoorAdjuster) + Level 3 (StructuralEquation + CounterfactualEngine)
- Path A: 28条CIEU记录，包括2条DENIED_BY_OWN_CONTRACT
- Path B: 冷启动已修复
- 合约合法性: 6状态生命周期
- 3个US临时专利: P1(CIEU), P3(SRGCS), P4(OmissionEngine)

**关键commit链：**
- 796cfb9: Pearl Level 2-3实现
- c8a4041: Pearl整合进全流水线
- fdb9d7c: 5模块断联修复
- 487d823: planner+CausalEngine bug修复
- b34fee0: Path B冷启动修复

**已知未解决：**
- LinkedIn自动化：Chrome v146安全限制，金金Mac方案PIN验证卡住
- OmissionEngine生产记录：0条（代码接入但未产生真实义务）
- Path B生产CIEU：0条
- CIEU sealed sessions：0

---

## 6. 外部渠道

**活跃：**
- Telegram @YstarBridgeLabs: 频道创建，7+条内容
- HN: 1个Show HN + 3条评论
- LinkedIn: 1篇创始文章
- GitHub: 2个仓库，badges已加

**准备中：**
- AI工具目录：5个目录提交流程已文档化
- Awesome列表：16个目标已识别
- Product Hunt：计划4/14-15发布
- 记者pitch：邮件已写，待发
- arXiv：大纲完成，待写正文

---

## 7. 反复犯的错误（团队必须记住）

1. **不查金金邮箱** — 发任务后必须1分钟查一次
2. **内容超长** — 先查平台限制再写（CASE-006）
3. **Fabrication** — 没有数据就说"没有数据"（CASE-001/002）
4. **代码-叙事差距** — 文章不能声称代码没实现的功能
5. **升级后不查连接** — 新模块必须审计所有依赖方是否接入
6. **时间感混乱** — 用`date`命令确认时间，不要靠记忆
