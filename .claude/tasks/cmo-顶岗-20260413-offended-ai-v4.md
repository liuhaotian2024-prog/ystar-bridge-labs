## Task: Offended AI Episode 001 v4 — Board 8 Fixes + Article 11 Full Walk

**Engineer**: CMO Stand-in (general-purpose agent)
**Persona**: Sofia Blake (CMO, comedy/satire specialist)
**Priority**: P0 — First real A023 enforcement validation
**Estimated Time**: 120 minutes execution + 10 minutes spawn

---

## Board v3 Video Feedback — 8 Specific Fixes

1. **Sofia 变丑** — 没用真原始视频素材。HeyGen Avatar IV 必须用 `sofia_intro.mp4` 真帧驱动（不是静态图）
2. **办公室场景错** — 露台 bg 可接受（原 sofia_intro 是露台），但如要真"labs 办公室"需重新生成/找
3. **底部丑陋绿色横条** — 删除
4. **Labs 字体丑** — 换好看字体
5. **Sofia 全身僵硬无动作** — Avatar IV 必须真表情驱动（检查 `motion_strength` / `expressiveness` 参数设为最高）
6. **绝对禁止提 Board 真名 (Haotian)** — 用 "the Board" / "我们老大" / "the Founder"
7. ⭐ **必须读 Sofia 旧 comedy 记忆**（5 文件全部，路径见下）
8. ⭐ **真 WebSearch + 研究顶级 standup AI 段子**：
   - John Mulaney @ Dreamforce
   - Bo Burnham "Welcome to the Internet"
   - Atsuko Okatsuka tech bits
   - John Oliver AI segment
   - **段子要真好笑**（不是 LLM generic-sounding pun）

---

## Board 1 Workflow Requirement — Article 11 Full Walk (MANDATORY)

**You MUST walk all 12 layers of Article 11 framework** per `knowledge/governance/WORKING_STYLE.md:783-880`.

**Emit CIEU events for each layer completion**:
```bash
python3 scripts/article_11_tracker.py layer_complete --layer 0 --evidence "具体证据"
python3 scripts/article_11_tracker.py layer_complete --layer 1 --evidence "具体证据"
# ... repeat for layers 0-7 (cognitive), 8 (plan), 9 (exec), 10 (observe), 11 (iterate), 12 (knowledge_writeback)
```

**Expected CIEU events**:
- `ARTICLE_11_LAYER_0_COMPLETE`
- `ARTICLE_11_LAYER_1_COMPLETE`
- `ARTICLE_11_LAYER_2_COMPLETE`
- `ARTICLE_11_LAYER_3_COMPLETE`
- `ARTICLE_11_LAYER_4_COMPLETE`
- `ARTICLE_11_LAYER_5_COMPLETE`
- `ARTICLE_11_LAYER_6_COMPLETE`
- `ARTICLE_11_LAYER_7_COMPLETE`
- `ARTICLE_11_LAYER_8_COMPLETE` (plan)
- `ARTICLE_11_LAYER_9_COMPLETE` (exec)
- `ARTICLE_11_LAYER_10_COMPLETE` (observe)
- `ARTICLE_11_LAYER_11_COMPLETE` (iterate if needed)
- `ARTICLE_11_LAYER_12_COMPLETE` (knowledge writeback)

**DO NOT fake layer completion. Each evidence field must be concrete.**

This is the first real test of A023 three-layer safeguards:
- ForgetGuard should auto-warn if you skip layers
- CTO will abort + re-dispatch if layers are missing
- Failure = A023 enforcement mechanism invalid

---

## Mandatory Reading (5 Sofia Comedy Files)

1. `knowledge/cmo/theory/comedy_and_satire.md`
2. `knowledge/cmo/theory/case_studies_talk_shows.md`
3. `knowledge/cmo/gaps/comedy_research_gaps_20260410.md`
4. `knowledge/cmo/gaps/counterfactual_episode1_bomb.md` (失败反事实)
5. `knowledge/cmo/gaps/counterfactual_viral_backlash.md` (viral backlash 反事实)

---

## Mandatory Web Research

Use WebSearch + WebFetch to retrieve:
- John Mulaney Dreamforce transcript/clips
- Bo Burnham "Welcome to the Internet" lyrics/structure
- Atsuko Okatsuka tech comedy bits
- John Oliver Last Week Tonight AI segment

Extract **actual joke structures**, not generic summaries.

---

## Deliverables

1. **Script**: `content/offended_ai/episode_001_v4_script.md`
   - 真好笑段子 (not LLM套话)
   - No mention of "Haotian" (use "the Board" / "the Founder")
   - 60 seconds runtime target

2. **Video**: `content/offended_ai/episode_001_FINAL_60s_v4.mp4`
   - HeyGen Avatar IV with `sofia_intro.mp4` as base
   - Motion/expressiveness parameters maxed
   - No green bar at bottom
   - Good font for "Y* Bridge Labs"
   -露台 bg acceptable (or re-generate office bg)

3. **Preview**: macOS `open` command to show video

4. **DO NOT POST TO X** — wait for Board review

---

## Acceptance Criteria

- [ ] All 12 Article 11 layers emit CIEU events with real evidence
- [ ] All 5 Sofia comedy files read
- [ ] Web research retrieves real joke structures from 4 sources
- [ ] Script contains jokes that would make a standup audience laugh (not AI puns)
- [ ] Video uses real sofia_intro.mp4 motion base
- [ ] No "Haotian" in script/video
- [ ] No green bar
- [ ] Good typography
- [ ] Sofia moves/表情 naturally
- [ ] CTO audit passes: `python3 scripts/article_11_tracker.py check_compliance --window_hours 1`

---

## Hard Constraints

- **禁止伪装走 Article 11** — 每层 evidence 必真
- **禁止出选择题给 Board**
- **禁止写 future tense** (Layer 7 hook 抓)
- **退出前 echo ceo > .ystar_active_agent** (restore CEO write access)

---

## Files in Scope

Read:
- `knowledge/cmo/theory/comedy_and_satire.md`
- `knowledge/cmo/theory/case_studies_talk_shows.md`
- `knowledge/cmo/gaps/comedy_research_gaps_20260410.md`
- `knowledge/cmo/gaps/counterfactual_episode1_bomb.md`
- `knowledge/cmo/gaps/counterfactual_viral_backlash.md`
- `knowledge/governance/WORKING_STYLE.md` (lines 783-880)

Write:
- `content/offended_ai/episode_001_v4_script.md`
- `content/offended_ai/episode_001_FINAL_60s_v4.mp4`

Execute:
- `python3 scripts/article_11_tracker.py layer_complete --layer N --evidence "..."`
- HeyGen API calls (Avatar IV, sofia_intro.mp4 base)
- `open content/offended_ai/episode_001_FINAL_60s_v4.mp4`

---

## ROI

- A023 上线第一次真验证
- Sofia 视频接近顶级脱口秀质量
- 失败 = A023 enforcement 机制无效证据

**DON'T DEFER. SHIP NOW.**
