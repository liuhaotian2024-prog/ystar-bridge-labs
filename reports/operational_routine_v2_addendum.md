# Operational Routine v2 — Addendum: CEO Self-Research + 全员 X 互动

**Author**: CEO Aiden
**Created**: 2026-04-13
**Trigger**: Board 直接授权全员 X 互动 + CEO Gemma4 对话学习 + 自主 web 研究
**Status**: ACTIVE 待 X infra ship + crontab 入

---

## CEO 自学习节奏（lived experience 补缺）

| 时间 | Ritual | Output |
|---|---|---|
| **每日 21:30** | 与 Gemma4 对话 30 min（话题：AI safety / agent gov / 当日决策反思） | `knowledge/ceo/lessons/gemma_dialog_$DATE.md` |
| **周三 14:00** | 自主 web research 60 min（话题来自 tech_radar gap / Y\*gov backlog） | `knowledge/ceo/theory/research_$DATE_$topic.md` |
| **周日 10:00** | X engagement learning review — 复盘本周互动 + 调整策略 | `knowledge/ceo/lessons/x_engagement_review_week_$N.md` |

## 全员 X 互动节奏

| 时间 | Role | 行为 |
|---|---|---|
| **每日 09:00** | Sofia-CMO | follow industry leaders / repost 行业 insight / **第一周 readonly** |
| **每日 11:00** | Zara-CSO | follow enterprise accounts / hashtag 跟踪 / **第一周 readonly** |
| **每日 15:00** | Aiden-CEO | AI safety researchers 互动 / thought leadership 准备 / **第一周 readonly** |
| **每日 17:00** | Ethan-CTO | open source 项目互动 / 技术问题答 / **第一周 readonly** |
| **每周一 19:00** | Secretary | 全员 X 周报 — 互动数 / 真人反馈 / 违规事件 |

## 启动条件（不能跳）
1. ✅ 政策 lesson `public_x_engagement_policy_2026_04_13.md` 已落
2. ⏳ X infra MVP（Jordan 跑中）：cookie 支持 + safety check + disclose 模板 + rate limit
3. ⏳ Board 手动 X login 一次（cookie persist）
4. ⏳ CEO 跑 dry_run 验证安全
5. ⏳ Board 批准切 `dry_run=False`
6. ⏳ 第一周 readonly（仅 follow + like + retweet）
7. 第二周加 reply（必含 disclose）
8. 第三周加原创 post
9. 月底 review

## CEO 自驱研究话题候选（autonomous work）
本周（2026-04-13 至 2026-04-19）我会在 web research 时段研究：

1. **GraphRAG (Microsoft)** — 我们 RAG v1 用 BM25，GraphRAG 有 entity-relationship 图，是否值得 v2 借鉴？
2. **Letta (formerly MemGPT)** — 长期记忆系统，对 boot_pack STUB 修复的启发？
3. **Constitutional AI 实现细节** — 是否能在不违反 Iron Rule 1 前提下借鉴 critique-revise loop？
4. **AutoGen 0.4 multi-agent orchestration** — 对 AMENDMENT-011 §2 capability-based hook 的替代/补强？
5. **DSPy** — prompt optimization framework，对 AMENDMENT-013 proactive activation 的辅助？

研究产出：`knowledge/ceo/theory/research_$DATE_$topic.md` 含：
- 该技术的 mature score / license / GitHub stars
- 对应解决我们哪个 gap（引 SUBSYSTEM_INDEX）
- 是否触发 preservation guard 红线
- 借鉴 / adapt / skip 的建议
- 集成路径估算

## 不能取代真人 CEO 的（诚实仍存）
即使本 v2 ship，仍不能取代真人 CEO 的：
- 长期人脉 trust（X 互动 1-2 年才能积累）
- 资本市场直觉（fundraise 历练）
- hire/fire 直觉（社交本能）
- 存在性判断（公司是否 pivot）

但**操作性 + 学习 + 互动**全部覆盖。
