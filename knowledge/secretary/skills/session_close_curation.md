# Skill: Session Close Curation（Secretary 核心职能）

**类型**: Hermes 可加载 skill (4 段)
**适用**: Secretary (Samantha Lin)
**立约**: 2026-04-13 AMENDMENT-010 S-3
**状态**: DRAFT，待 AMENDMENT-010 Board D + eng-platform 实装 curate pipeline 后激活

---

## 1. 适用场景 (Trigger)

以下任一触发加载本 skill：
- `session_close_yml.py` 被调用（session 正常收尾）
- Board session 结束（Board 明确说 "收尾" / session 自然 timeout / token 接近上限）
- CEO 主动请求 curation（如本 session 2026-04-13 末尾）
- Autonomous_work_learning 模式中每 3h 小 curate（局部更新 boot_packages）

## 2. Procedure（13 步，严格顺序）

### Step 1：Snapshot 多源 truth（AMENDMENT-010 S-3 第 4 条）
- 本 session 对话全文（JSON format，区分 Board 原话 vs agent 转述）
- CIEU 过去 24h 流（`.ystar_cieu.db` 查询）
- GitHub：`git log origin/main -20` + `gh issue list` + `gh pr list`
- Filesystem diff：`git status` + `git diff`
- gov-mcp state：`gov_session_info` / `gov_trend` / `gov_obligations`
存到 `memory/_curate_cache/{session_id}_snapshot.json`

### Step 2：Skill 蒸馏
- 从对话识别新 skill（pattern：Board 纠偏 → CEO 产出具体做法 → 其他 role 可复用）
- 写成 Hermes 4 段格式
- 草稿落到 `knowledge/{role}/skills/_draft_`
- 通知对应 role 本人签字确认才正式入库

### Step 3：Task 整合与墓碑
- 扫 `DISPATCH.md` / `BOARD_PENDING.md` / `knowledge/{role}/active_task.json`
- Board 本 session 未再提 + 超 72h 未更新 + 有 dead_path 匹配 → 标 `status: deprecated`
- emit CIEU `TOMBSTONE_APPLIED`

### Step 4：Priority Brief co-authoring
- 读 CEO 本 session 写的 `reports/priority_brief.md`
- 补充 Secretary 视角：跨 role 资源冲突 / external commitments 到期提醒 / skill decay 警报
- merge 成 v{next}，CEO 签字后正式更新

### Step 5：Next-Session Action Queue 生成（per role）
对每个 role：
- 读该 role 的 role_definition
- 读该 role 的 active_task
- 读该 role 的 skill inventory
- 结合本 session 新 skill / 新 dead_path / 新 obligations
- 生成 `memory/boot_packages/{role}.json` 含 11 类分包 + action_queue

### Step 6：自审 drift
- 读上轮自己写的 `memory/boot_packages/history/{role}_{prev_ts}.json`
- 对比本轮实际：action_queue 执行率 / DEPRECATED 清单准确率 / skill trigger 率
- drift ≥ 30% → 写 "修正自己" 段到本轮 boot_pack + emit CIEU `SELF_AUDIT_DRIFT`

### Step 7：RedTeam-Secretary 子 agent
- 调起 RedTeam 子 agent，传入本轮 boot_packages 和 priority_brief
- 要求攻击："下一个 Aiden 读完这个会 miss 什么？Board 本 session 说过但没进 brief 的话有哪些？DEPRECATED 错杀了吗？"
- 红队 No-Go → 回 Step 2 修订（最多 3 轮，再失败触发 Step 12）

### Step 8：第十一条 emit
- 对每个 boot_pack 生成 emit `ARTICLE_11_PASS` event 带 7 层：意图/上下文/约束/选项/后果/决策/执行

### Step 9：Skill lifecycle
- 扫所有 `knowledge/{role}/skills/*.md`
- 5 session 未 trigger → mark `cold`
- 10 session → move to `_archive/`
- broken path（procedure 引用的文件/命令不存在） → emit alert

### Step 10：Version diff & archive
- 每 boot_pack 存 `memory/boot_packages/history/{role}_{ts}.json`
- 用 `git` 提交（不 push），tag = `curate-{ts}`

### Step 11：Secrets scrub
- 正则扫 boot_packages 所有字段（`AKIA[A-Z0-9]{16}` / `sk-[a-zA-Z0-9]{48}` / `ghp_*` / `.env` 文件引用）
- 命中 → 替换 `<REDACTED>` + emit CIEU `SECRET_SCRUBBED`

### Step 12：Circuit breaker 检查
- 连续 3 轮红队 No-Go（Step 7）→ 停用 curate，写 `memory/curate_circuit_breaker_tripped.flag`，回退 v1 handoff，告警 Board
- drift ≥ 60%（Step 6）→ 同上

### Step 13：emit `SECRETARY_CURATION_COMPLETE`
含统计：skills_distilled / tombstones_applied / boot_packs_written / drift_score / redteam_verdicts

---

## 3. Pitfalls

### 坑 A：把 Board 转述当原话
Board 原话进硬约束候选，agent 转述只进软优先级。混淆会让错误解读升格为硬约束。
**规避**：Step 1 snapshot 必须结构化（每句 source=board|agent|subagent）。

### 坑 B：Red team 过于宽松自己放过
**规避**：RedTeam-Secretary 子 agent 必须是独立 general-purpose 子 agent，不共享 Secretary 上下文；且强制要求列出 ≥5 类漏洞角度。

### 坑 C：Drift 计算方式拍脑袋
**规避**：drift 指标严格定义：
- action_queue 执行率 = completed / total
- deprecated 准确率 = 没被重新激活数 / total deprecated
- skill trigger 率 = 被加载过的 skill 数 / total skills in pack
三者加权平均。

### 坑 D：boot_pack 体积爆炸
**规避**：每 role pack ≤ 20KB。超了必须砍冷数据到 history/，pack 只留 fresh。

### 坑 E：Secretary 借 curate 权悄悄做战略判断
**规避**：S-4 红线。如果 curation 需要做"这 3 个任务哪个优先"这种判断 → Secretary 不做，标 `NEEDS_CEO_PRIORITY_CALL` flag 留给 CEO。

## 4. Verification

每次 curate 跑完自检：
- [ ] 13 步全部 emit 对应 CIEU event
- [ ] 每 role 的 boot_pack 存在且 ≤ 20KB
- [ ] 至少 1 个新 skill 蒸馏 OR 明确说明"无新 skill"
- [ ] drift score 在 0-1 之间
- [ ] RedTeam 判决 PASS
- [ ] Secrets scan 0 命中 OR 全部已替换
- [ ] `git log` 有 `curate-{ts}` tag
- [ ] 下一轮任一 role boot STEP 4 (`boot_package_per_role_loaded`) 能成功加载

## 版本
v0.1 — 2026-04-13 CEO 代笔 stub。Secretary 激活后首次 curate 时会基于本 skill 实际跑一遍并微调。
