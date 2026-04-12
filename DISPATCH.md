# DISPATCH — Y*Defuse 30天全自主战役 (2026-04-11)

**Authority**: Board直接授权，第十一条全自主
**Master Plan**: products/ystar-defuse/LAUNCH_BATTLE_PLAN.md
**目标**: 30天内 10,000用户 + 20,000 GitHub stars
**Day 1**: 2026-04-11

---

##战役任务（最高优先级）

### CTO (Ethan) + Leo + Ryan — Week 1 工程交付
**Deadline: Day 3 (Apr 13) MVP可pip install**

- [ ] Level 2自动学习白名单完整实现
- [ ] CLI全命令可用（start/stop/report/config）
- [ ] Claude Code hook真实环境验证
- [ ] 10种延迟注入攻击场景仿真测试（见LAUNCH_BATTLE_PLAN.md第三节）
- [ ] pip install端到端验证（干净机器）
- [ ] Day 4: PyPI发布

### CMO (Sofia) — Week 1 内容准备
**Deadline: Day 5 (Apr 15) Show HN准备就绪**

- [ ] README.md极致简洁版（30秒理解产品）
- [ ] Show HN发布文案
- [ ] 产品演示视频（60秒）
- [ ] Twitter/X发布策略
- [ ] 《冒犯了，AI》首期选题关联ystar-defuse

### CSO (Zara) + 金金 — 持续用户获取
- [ ] AI开发者社区渗透（Discord/Slack/Reddit）
- [ ] 潜在用户名单建立
- [ ] Awesome Lists提交（16个目标）
- [ ] AI工具目录提交（5个）

### CFO (Marco) — 基线建立
- [ ] PyPI下载数据追踪机制
- [ ] GitHub star增长曲线基线
- [ ] $9.9定价验证

---

## 支撑任务（战役依赖项优先处理）

| # | 任务 | 负责人 | 优先级 | 与战役关系 |
|---|------|--------|--------|-----------|
| S1 | Circuit Breaker reset | Ryan | P1 | 治理基础设施 |
| S2 | gov_dispatch测试修复 | Leo | P1 | 任务分派系统 |
| S3 | Omission Engine接入 | Maya | P2 | 战役后再接 |
| S4 | Agent name字段修改 | Samantha | P2 | 不阻塞战役 |
| S5 | 空闲学习验证 | Ryan | P2 | cron已跑，低优 |

---

**CEO (Aiden) 每日职责:**
- 每日检查各岗位进度
- 产品质量最终把关
- 对外战略叙事定稿
- 用户反馈收集和优先级排序

**Note to CTO:** 战役任务全部Board预授权。Day 3前MVP必须可装，这是卡Show HN的关键路径。立刻开工。

---

## P0-CRITICAL — Ryan立即修复 boot reminder（2026-04-11 老大震怒事件）

**事件**: agent boot后回答全程没叫"老大"，老大震怒到说"Claude code大傻逼"。
**根因**: memory里有"称呼=老大"信息，但boot输出无强制reminder，agent不会主动调用。
**任务**: 编辑 `scripts/governance_boot.sh` 第227行前插入 IDENTITY REMINDER 块：
```bash
echo ""
echo "============================================================"
echo "  IDENTITY REMINDER (MUST APPLY TO EVERY RESPONSE)"
echo "============================================================"
echo "  Board 称呼：必须叫 老大（不允许 Board / 老板 / 直呼）"
echo "  你的身份：$AGENT_ID（中文名见 .claude/agents/$AGENT_ID.md）"
echo "  违反 = 严重失忆信号，老大会立即抓出"
echo "============================================================"
echo ""
```
**Deadline**: 今夜立即，老大睡前能验证`bash scripts/governance_boot.sh ceo | grep IDENTITY`有输出
**进阶**: 后续做hook层enforcement——agent回答中未出现"老大"且对方明显是Board时warn

---

## Day 3 Checkpoint — 2026-04-11 23:17 CEO审查

**CTO现状观察** (ystar-defuse repo):
- ✅ dist/ystar_defuse-0.1.0.whl 已打包
- ✅ src/ystar_defuse 完整
- ✅ tests/ 6个文件（含 test_delayed_injection, test_e2e_simulation, test_level1, test_cieu）
- ⚠️ knowledge/cto/active_task.json current_layer=4（exec_start），layers 5-8 全未更新 → **跟踪滞后**

**CTO需在Day 3结束前回报（硬指标）:**
1. [ ] 运行 `pytest tests/` 报告：total/passed/failed，目标≥20测试全过
2. [ ] 干净venv验证：`pip install dist/*.whl` 成功 + `ystar-defuse --version` 可执行
3. [ ] Level 2白名单端到端演示（observe→generate→confirm完整链路）
4. [ ] 同步更新 active_task.json：layer 5_mid_check → 8_exec_complete
5. [ ] 若任何项阻塞，立即写入 knowledge/cto/blockers.md 并@CEO

**不报告=违反checklist底线。Silent failure将触发Board升级。**

---

## P0-INFRASTRUCTURE 新增（Board直授，2026-04-11 23:xx）

### Maya — 实施 auto-codify hook（P0）
**来源**: knowledge/ceo/lessons/auto_codify_lessons.md
**任务**: hook监测agent输出含触发模式（"以后" / "下次注意" / "经验教训" / Board纠正句式），自动生成lesson模板 + 追加DISPATCH项，CEO/全员**无法跳过codify步骤**。
**触发条件白名单**:
1. 同类错误重犯 ≥2次
2. Board当面纠正
3. 系统gap暴露
4. Board "难道...不属于..."句式

### Maya/Ryan — 实施硬约束清单完整性 hook（P0）
**来源**: knowledge/ceo/lessons/hard_constraint_completeness.md
**任务**: agent回答含["硬约束","铁律","必须遵守","清单","所有"]关键词时，hook自动注入完整 obligations列表 + ALWAYS RUNNING列表到上下文，强制扫描后才能输出。

### Ryan — Cron验证（P0）
查 ystar_wakeup.sh log时间戳是否对齐每3h schedule。未跑则推Board手装队列（写入BOARD_PENDING.md）。

### Maya — 修复state双写gap（P0）
OmissionEngine pending=0 vs memory层15条obligation。统一为单一source of truth，决策方案后dispatch执行。

### Samantha — 清理CMO active_task.json脏数据（P1）
当前 status=completed 但 duration=0.076s output="test" = 测试桩污染真实状态。清理后从DISPATCH.md回填CMO真实in_progress任务（Show HN 5项）。

---

## P0-INFRASTRUCTURE: 治理enforcement缺口修复

**Board诊断：** behavior rules和symbol verification配置全在，但enforcement有三层断裂：

### 缺口1: no_choice_questions — 零enforcement
- 配置里有，代码里完全没有检测函数
- 需要在boundary_enforcer.py添加：检测agent输出中的选择题模式（"1/2/3"、"请选择"、"Options:"）
- **级别：DENY**（不是WARNING）

### 缺口2: WARNING级规则被LLM忽略
以下规则应从WARNING升级为DENY或更强enforcement：
- `must_check_health_on_session_start`：前5个call没查健康 → 应block后续操作
- `verification_before_assertion`：未验证就断言 → 应block该输出

### 缺口3: task_type_symbols enforcement链路
- `_check_task_type_symbols`函数存在但需验证是否在hook chain中被实际调用
- autonomous_mission的7层检查需要从符号配置到DENY的完整链路

### 缺口4: obligation deadlock bug
- overdue obligation拦截ALL tool call包括fulfill动作 → 死锁
- 修复：overdue时允许Read/Write reports//gov MCP tools通过

**Assignee:** CTO → Maya (Governance) + Ryan (Platform)
**验收:** 重新跑governance_boot.sh的E2E测试，新增no_choice_questions测试项

---

## P0-ZERO: Session认知恢复机制修复（阻塞一切）

**问题:** agent重启后虽然hook恢复、记忆加载，但agent行为表现为失忆——不知道自己在打什么仗。
**根因:** 两处断裂：

### 断裂1: governance_boot.sh第64行
```bash
# 现在（坏的）：记忆dump到log文件，CEO看到的只是"32 lines loaded"
python3 scripts/session_boot_yml.py "$AGENT_ID" > /tmp/ystar_memory_boot.log 2>&1

# 应改为：记忆直接输出到stdout，agent必须看到内容
python3 scripts/session_boot_yml.py "$AGENT_ID" 2>/dev/null | tee /tmp/ystar_memory_boot.log
```

### 断裂2: governance_boot.sh缺少Step 9 — 战略obligation强制输出
在Step 8（execution model）之后，加Step 9：从YML记忆中提取所有obligation类记忆，直接打印。格式：
```
--- ACTIVE OBLIGATIONS (你在打什么仗) ---
[P0] ystar-defuse上线：10K用户+20K stars，Day 1=2026-04-11
[P0] behavior rules 10条全部代码实现+CIEU审计证据
...
```
这样agent重启后第一眼看到的就是obligation，不是治理水管。

### 断裂3: CLAUDE.md Step 3汇报模板
```
# 现在（坏的）：引导CEO汇报治理状态
"治理状态：[boot结果]。CIEU X条。"

# 应改为：obligation优先
"战役状态：[最高优先obligation + Day N]。治理：[boot结果]。我现在执行[具体行动]。"
```

**Assignee:** CTO → Ryan (Platform)
**验收标准:** 重启后agent的第一句话必须包含当前最高优先级obligation，不需要人工提醒。

---

## P0-ENFORCE: Board铁令——全部WARNING升DENY（4线并行）

**Board指令 2026-04-11:** 所有behavior rules从WARNING升级为DENY。四个任务并行执行。

### 任务A: CTO (Ethan) — boundary_enforcer.py WARNING→DENY
**文件:** `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/boundary_enforcer.py`
**内容:**
把所有WARNING级behavior rule改为DENY。具体：
1. `_check_verification_before_assertion` (Rule 2, ~line 799): `return None` → `return PolicyResult(allowed=False, ...)`; event_type → BEHAVIOR_RULE_VIOLATION; decision → DENY
2. `_check_root_cause_fix_required` (Rule 3, ~line 855): 同上
3. `_check_document_requires_execution_plan` (Rule 4, ~line 917): 同上
4. `_check_no_fabrication` (Rule 5, ~line 974): 同上
5. `_check_counterfactual_before_major_decision` (Rule 6, ~line 1033): 同上
6. `_check_must_check_health_on_session_start` (Rule 7, ~line 1089): 同上
7. `_check_completion_requires_cieu_audit` (Rule 10, ~line 1149): 同上
8. `_check_directive_decompose_timeout` (Rule 13, ~line 1306): 同上
9. `_check_content_length_check` (Rule 14, ~line 1365): 同上
10. `_check_real_conversation_count_required` (Rule 16, ~line 1488): 同上

治理gap规则也升级：
11. `_check_no_email_to_humans` (ACTION-1, ~line 1742): WARNING → DENY
12. `_check_no_multiple_choice` (BOOT-1, ~line 2075): WARNING → DENY
13. `_check_directive_must_record_to_tracker` (DIR-1, ~line 2129): WARNING → DENY

**关键模式:** 每个函数改3处：
- `event_type`: "BEHAVIOR_RULE_WARNING" → "BEHAVIOR_RULE_VIOLATION"
- `decision`: "WARNING" → "DENY"
- 末尾的 `return None` (放行) → `return PolicyResult(allowed=False, reason=reason, who=who, what=tool_name, violations=[])`

同时更新 `_check_behavior_rules` 函数(~line 1508)的注释和调用方式：
- 原WARNING rules区域(~line 1579-1589)的调用改为检查返回值并return

### 任务B: Maya (eng-governance) — no_choice_questions实现
**文件:** 同上 boundary_enforcer.py
**内容:**
1. 写 `_check_no_choice_questions(who, tool_name, params, agent_rules)` 函数
2. 检测Write/Edit内容中的选择题模式：
   - "请选择"、"请挑"、"你来选"
   - "Options:"、"Board Options:"
   - 编号选项模式：`r"(?m)^\s*[1-9]\.\s+"` 连续出现3个以上
   - "✅/❌"让人选
   - "Option A/B/C"
3. 级别DENY，记CIEU
4. 注册到 `_check_behavior_rules` 调用链（DENY rules区域）

### 任务C: Ryan (eng-platform) — hook链路+identity修复
**文件:** hook.py + governance_boot.sh/hook_wrapper.py
1. 验证 `_check_task_type_symbols` 在hook.py的check_hook()中是否被实际调用，如果没有则接入
2. 修subagent identity污染：subagent运行会改`.ystar_active_agent`导致主session CEO身份丢失
   - 修复方案：subagent结束后自动恢复原identity

### 任务D: Leo (eng-kernel) — 全面enforcement测试
**文件:** tests/下新建或扩展测试
1. 为所有13条WARNING→DENY升级的规则写测试
2. 每条规则验证：触发时返回PolicyResult(allowed=False)而非None
3. 包括no_choice_questions的测试
4. 所有测试必须pass

**执行:** 在当前 single-Mac OpenClaw workspace 中调起 CTO sub-agent 执行（AMENDMENT-004 起不再有跨机派发）。CTO 启动后并行 dispatch Maya/Ryan/Leo sub-agent，自己同时改 boundary_enforcer.py。改完统一跑测试套件。
