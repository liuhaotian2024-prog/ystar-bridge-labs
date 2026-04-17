---
name: CEO Product Management — PLG + PMF + Prioritization (学习笔记 Round 11)
type: ceo_learning
discovered: 2026-04-17
source: Product-Led Growth / Sean Ellis PMF / RICE-ICE prioritization
depth: deep
---

## 3 个产品管理核心概念 + Y* Labs 适用

### 1. Product-Led Growth (PLG)
- 核心: 产品本身是获客/转化/留存的引擎 (不靠销售团队)
- PLG 飞轮: 免费试用 → 用户体验价值 → 转化付费 → 口碑传播 → 更多免费用户
- 成功案例: Slack / Notion / Figma / GitHub / Atlassian

**Y* Labs PLG 路径**:
```
pip install ystar-gov  (免费开源)
    ↓
ystar hook-install && ystar doctor  (3 命令体验)
    ↓
用户看到 CIEU audit + K9 violations  (立即感知价值)
    ↓
需要 enterprise features → 付费  (domain packs / 高级分析)
    ↓
用户推荐 → 更多开发者试用  (flywheel)
```

**前提**: `pip install ystar-gov` 必须成功！这是 PLG 的第一道门。当前状态: 坏的 → **CTO P0**。

**PLG 对 AI 公司的独特优势**:
- 无销售成本 (产品自说话)
- 开发者用户 = 最理性买家 (不靠推销靠体验)
- 开源 = 信任基础 (代码可审计 → "我看过源码，确实好")

### 2. Product-Market Fit (PMF) — Sean Ellis Test
- **The 40% Rule**: 问用户 "如果明天不能用这个产品你怎么想?"
  - ≥40% 回答 "非常失望" → 有 PMF
  - <40% → 还没找到 PMF
- **关键**: PMF 不是猜的 → 靠用户数据验证

**Y* Labs PMF 适用**:
- 当前: 0 用户 → 无法做 Sean Ellis Test
- **替代**: dogfood 自测 — 我们自己如果不能用 Y*gov 会"非常失望"吗?
  - 治理系统 (K9/FG/CIEU): 是 → 没有 K9 我们 session 质量会崩
  - 产品安装: 否 → 我们用 symlink 绕过 pip install → 说明安装体验差
- **行动**: 先让产品 install 通 → 找 3-5 外部开发者试用 → 做 Sean Ellis Test

### 3. Feature Prioritization — RICE + ICE
**RICE** (Reach × Impact × Confidence / Effort):
- Reach: 多少用户受影响
- Impact: 每用户影响多大 (1-3 scale)
- Confidence: 多确定效果 (0-100%)
- Effort: 需要多少人-周

**ICE** (Impact × Confidence × Ease):
- 更轻量，适合快速实验
- 1-10 打分 × 3 维 → 排序

**Y* Labs 当前 feature RICE 排序**:
| Feature | Reach | Impact | Confidence | Effort | RICE Score |
|---|---|---|---|---|---|
| pip install fix | 100% users | 3 (blocker) | 90% | 2 weeks CTO | **135** |
| `ystar doctor` 诊断命令 | 80% | 2 | 70% | 1 week | 112 |
| Domain pack: DevOps | 30% | 3 | 50% | 3 weeks | 15 |
| Web dashboard | 20% | 2 | 40% | 4 weeks | 4 |

**结论**: pip install fix 是唯一 blocker → 再次验证 dependency_sequencing 正确

## CEO 产品方法论 v0.1

```python
def product_decision(feature_request):
    # 1. PLG gate: 会改善"免费体验→付费转化"路径吗?
    if not improves_plg_funnel(feature_request):
        return "低优先 — 不在 PLG 关键路径"
    
    # 2. RICE 打分
    score = (reach * impact * confidence) / effort
    
    # 3. PMF 检验: 做了这个 feature 后，40% test 会提升吗?
    if not increases_pmf_40pct_score():
        return "nice-to-have 不是 must-have"
    
    # 4. 依赖检查
    if has_unmet_dependency():
        return "先完成前置 (e.g., pip install 必须先通)"
    
    return f"优先级 {score}, PLG 路径关键, PMF 贡献预期: {pmf_delta}"
```

## 对 CEO Operating Manual v0.1 的补充

- Part 8 Strategy 加: PLG 是我们的 go-to-market 策略 (不是 sales-led)
- Part 5 Execution 加: feature 优先级用 RICE 打分 (不拍脑袋)
- Part 10 Cross-dimension: PLG funnel = Strategy ∩ Product ∩ Execution 交叉点
