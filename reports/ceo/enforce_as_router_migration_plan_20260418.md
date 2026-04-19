# Enforce-as-Router 迁移计划

**Date**: 2026-04-18
**Author**: Aiden (CEO)
**Triggered by**: Board 2026-04-18 终极诊断 — "为什么我们创建了那么多功能，根本没人记得什么工作该怎么做？是这些东西都写错地方了吗？"

**Audience**: Board (主决策者) + 全体 agents (实施参考) + 未来 session 的 CEO

**Intended for**: Phase 2 架构级重构的规划与分派依据。本报告不是终局方案，是 Board insight 落地成可执行迁移的第一份工程蓝图，后续工程师读此报告领白板任务。

---

## 1. 核心诊断（根因确认）

Board 问题 → 答案：**是，全都写错地方了。**

### Why existing Labs features fail
- Labs 目录累计：`scripts/*.py` **160**、`scripts/*.sh` **28**、`governance/*.md` **40**、`governance/whitelist/*.yaml` **7**、`knowledge/**/*.md` **611** — 总计 ~850 个文件
- 这些文件 90%+ 是 **workflow / routing / protocol**，只有 10% 是真 data/content/reference
- 它们都假设 agent 会"主动 opt-in"：记得它存在 / 记得怎么调 / 记得在什么场景用
- **但 agent 的记忆不可靠**：context window 压缩丢细节；新 session 只继承 MEMORY.md 索引不继承 wiring；drift 时最先忘 feature；sub-agent boot 通常只读 task prompt
- 结果：feature 存在 ≠ feature 活。工具箱建了但没人知道钥匙在哪。CEO 2026-04-18 session 反复 lock-death 即是这一失配的表现症状

### Why enforce hook must become the router
- `enforce hook` 是 **唯一不可绕过的触点** — Claude Code 每个 tool call 必过
- 把 feature 路由放 enforce 里 → agent 任何 tool call 都被自动导入正确路径
- Agent 侧 **零记忆依赖**：不需要知道 feature 存在，只需要调 tool

### 架构变化
```
Before:  EnforceDecision = {ALLOW, DENY, ESCALATE}  (REDIRECT TODO 未落地)
After:   EnforceDecision = {ALLOW, DENY, ESCALATE, REDIRECT, INVOKE, INJECT, AUTO_POST}

INVOKE(feature_id, args)       # enforce 自动调 feature 脚本
INJECT(context_md)             # enforce 在 allow 消息里附加上下文（memory / skill / SOP）
AUTO_POST(task_card)           # enforce 自动 post 到 whiteboard
REDIRECT(fix_command, retry)   # enforce 返回"跑这个命令然后重试原动作"
```

---

## 2. 分类框架

### 2.1 KEEP in Labs — data/content/reference（约 30%）
这些是 **成果** 而非 **流程**。保留在 Labs，enforce 不路由。

| 类别 | 目录 | 例 |
|---|---|---|
| 对外内容 | `content/**` | blog / 文章 / video script / 社交 |
| 实验报告 | `reports/**` | 业绩 dashboard / 技术 debt / 实验结果 |
| 业务数据 | `sales/**, marketing/**, finance/**, research/**` | 客户清单 / 竞品 / 财务 |
| 案例库 | `knowledge/cases/**` | 失败/成功案例（学习材料） |
| 参考知识 | `knowledge/*/lessons/, _gaps/, _theory/` | 沉淀的认知 |
| Agent 记忆 | `memory/**` | Claude Code 原生处理 |

### 2.2 MIGRATE into enforce hook — workflow/routing（约 70%）

#### scripts/ 下要迁的（按 workflow 类别）
| Workflow 类别 | 现有 scripts | 迁移策略 |
|---|---|---|
| **Session boot** | `session_memory_boot, session_boot_yml, governance_boot.sh, czl_boot_inject, session_memory_commit, session_wisdom_extractor, session_wisdom_extractor_v2, session_auto_restart.sh, session_graceful_restart.sh, zero_touch_boot.sh` | enforce 在 SessionStart 钩子自动执行 |
| **Dispatch/派工** | `dispatch_board, cto_dispatch_broker, engineer_task_subscriber, active_task, register_obligation` | enforce 检测"派工意图" → AUTO_POST；检测 obligation scenario → 自动注册 |
| **合规/自动 enforce** | `secretary_auto_enforce, article11_compliance, amendment_coverage_audit, check_obligations, forget_guard_stress_test, unified_compliance_audit, whitelist_validator, whitelist_matcher, whitelist_coverage, whitelist_match, wire_integrity_check, redteam_secretary` | enforce 本身吸收这些逻辑 |
| **Mode/身份管理** | `ceo_mode_manager, agent_mode_manager, skill_lifecycle_manager` | enforce 在身份/mode 切换事件处理 |
| **K9/Watcher** | `k9, k9_watch, k9_baseline_verify, k9_inbox, k9_phase1..4, k9_daily_patrol.sh, k9_rt_sentinel_run.sh, k9_alarm_consumer, k9_cieu_export, k9_digest, k9_reinstall, k9_login, governance_watcher, cieu_event_watcher, dialogue_drift_checker, continuity_guardian_redteam, memory_consistency_check` | enforce 订阅 CIEU stream，触发事件时 INVOKE |
| **Social/content gate** | `post_ep01, post_episodes, publish_telegram, publish_x, publish_x_v2, publish_morning_to_readme, social_auto, x_content_safety_check, x_disclosure_templates, telegram_bridge, telegram_notify` | 内容本身保留，**发布动作**的安全检查/披露模板由 enforce 前置 gate |
| **Labs router（雏形已存在）** | `labs_router, labs_atlas_query, labs_atlas_scan, labs_rag_query, build_rag_index` | 直接并入 enforce router registry |
| **Dev/benchmark** | `benchmark_hook, test_heartbeat_matcher, test_yml_integration, test_lesson_tracking_phase1, test_cogvideox_sanity, forget_guard_stress_test` | enforce 内测；失败触发告警 |
| **工作流 cron/status** | `goal_progress_cron.sh, goal_progress_statusline.sh, continuous_mirror.sh, wip_autocommit.sh, ensure_crontab.sh` | enforce 订阅时间事件 |
| **Handoff/continuation** | `ystar_handoff, continuation_writer, migrate_handoff_to_yml, restart_handoff_verifier, restart_readiness_check` | enforce SessionEnd/Start 钩子 |
| **Knowledge 管理** | `knowledge_check, full_knowledge_import, update_gap_map, working_memory_snapshot, session_memory_boot` | enforce 在相关检查点自动 INJECT |

#### governance/ 下要迁的（protocol 变 enforce 规则）
| Protocol | 现文件 | 迁移策略 |
|---|---|---|
| Sub-agent 派工规约 | `sub_agent_atomic_dispatch, sub_agent_boot_prompt_template, ceo_dispatch_self_check` | enforce 拦 Agent tool call 前自动应用 |
| Routing 门户 | `action_model_v2, tiered_routing_protocol_v1, pre_build_routing_gate_v1, ecosystem_dependency_checklist_v1` | enforce 拦 tool call 前路由判定 |
| Reply 规约 | `reply_scan_detector_methodology_v1, reply_taxonomy_whitelist_v1, czl_unified_communication_protocol_v1` | enforce Stop hook 扫回复 |
| Git ops 规约 | `auto_commit_push_v1` | enforce 拦 git Bash call |
| Session 规约 | `restart_preparation_model_v1, ceo_operating_methodology_v1, cto_system23_takeover_v1` | enforce SessionStart/Mid/End |
| Skill 信任 | `skill_trust_hybrid_v1, cto_dispatch_broker_v1` | enforce 检测 skill 调用 |
| ForgetGuard 规则 | `forget_guard_rules.yaml, forget_guard_rule_new_artifact_without_precheck` | 已被 enforce 部分消费；扩展完整消费 |
| Formal methods | `formal_methods_primer_v1, reply_scan_detector_methodology_v1` | enforce 在决策密度点嵌入 |
| 入职/培训 | `new_engineer_onboarding_gauntlet_v1` | enforce 检测新 engineer 首次 action → INJECT |
| Methodology 绑定 | `methodology_framework_assignments_v1` | enforce 在对应场景 INJECT |
| Charter/amendments | `BOARD_CHARTER_AMENDMENTS, DNA_LOG, canonical_hashes.json` | 留 Labs 作 source of truth；enforce 读取引用 |

#### knowledge/ 下要迁的（routing-adjacent 知识）
| 类别 | 路径 | 迁移策略 |
|---|---|---|
| Role definitions | `knowledge/*/role_definition/*` | enforce 身份检查时 INJECT 对应 role definition |
| Skills | `knowledge/ceo/skills/**, knowledge/*/skills/**` | enforce 检测场景 → surface 对应 skill |
| SOPs | `knowledge/*/sop/**` | enforce 检测任务类型 → INJECT SOP |
| Methodology | `knowledge/ceo/methodology/**, methodology_*.md` | enforce 在决策点 INJECT |
| Decision logs | `knowledge/ceo/decisions/**` | 保留 Labs；enforce 检测相关决策重现时引用 |
| Cases（KEEP） | `knowledge/cases/**, knowledge/*/cases/**` | Labs-native 学习材料 |
| Lessons（KEEP） | `knowledge/*/lessons/**` | Labs-native |
| Theory（KEEP） | `knowledge/ceo/theory/**` | Labs-native |
| Gaps（KEEP） | `knowledge/ceo/gaps/**` | Labs-native |

---

## 3. 迁移 Phases

### Phase 1（Ethan 已在做：a4f1515cf60f753ef / a769212d81d754a7c 未完成）
- 修 10 条 lock-death 路径
- 加 `EnforceDecision.REDIRECT` + FIX_COMMAND/THEN_RETRY 消息格式
- Break-glass self-heal
- Subagent push/pop
- 10 条 live-fire regression test

### Phase 2（本报告提出，新开白板）
- 扩展 `EnforceDecision` 加 INVOKE / INJECT / AUTO_POST
- 在 Y-star-gov 建 `router_registry.py` — detector + executor 注册中心
- 逐批迁移 scripts/ 下 workflow 脚本：每个写 detector（触发条件） + executor（被 invoke 时行为），注册到 registry
- governance/*.md 规约逐个变成 router rule
- knowledge/**/* 的 routing-adjacent 子集加元数据（触发条件），enforce 按条件 INJECT

### Phase 3（验证）
- Live-fire：删一批 Labs scripts，验证 enforce 仍能自动 surface 正确 feature
- Drift test：模拟 agent 只看 tool call + enforce 返回，能否走完一个完整任务（不读 Labs 目录）→ 应该能

### Phase 4（清理）
- 迁完的 Labs scripts 归档到 `archive/migrated_to_enforce/`
- Labs 只剩 data/content/reference，目录规模从 850+ 降到 ~250

---

## 4. 成功判据（Rt+1 = 0 的定义）

- [ ] 任意新 session 开启一个 fresh agent（不读 Labs），只靠 tool call + enforce 返回，能正确：
  - [ ] 识别身份
  - [ ] 知道自己应该做什么（enforce INJECT 当前 obligation）
  - [ ] 知道怎么派工（enforce 拦 Agent tool → AUTO_POST whiteboard）
  - [ ] 知道怎么写代码（enforce INJECT 相关 SOP + ForgetGuard）
  - [ ] 知道怎么发布（enforce gate 发布动作的安全/披露）
- [ ] Labs scripts/ 从 160+ 降到 ~30（只留发布/内容工具）
- [ ] Labs governance/ 从 40+ 降到 ~10（只留 charter/amendments 历史，规约全进 enforce）
- [ ] 任何 agent drift scenario，enforce 返回 REDIRECT 3 次内恢复

---

## 5. 风险

1. **Y-star-gov 代码爆炸**：router_registry 承担太多职责 → 要拆子模块
2. **INVOKE 链循环**：detector 触发 executor 又触发另一 detector → 死循环；需 max_depth 守卫
3. **INJECT 上下文污染**：过度 INJECT 导致 prompt 膨胀 → 每个 INJECT 带 priority + 预算
4. **迁移期间 feature 断电**：新 router 还没接 + 老 script 被删 → 两端并存 + 渐进切换，删除在 Phase 4

---

## 6. 白板任务（下一步 CEO post）

按白板机制（Board 2026-04-18 纠正：必须 post 到 dispatch_board 不直接 spawn）：

| atomic_id | scope | description | urgency | claimed_by (expected) |
|---|---|---|---|---|
| CZL-P2-a | `Y-star-gov/ystar/domains/openclaw/adapter.py, router_registry.py (new)` | Phase 2-a: 扩展 EnforceDecision 加 INVOKE/INJECT/AUTO_POST + 建 router_registry 雏形 | P0 | eng-kernel |
| CZL-P2-b | `scripts/session_memory_boot.py, session_boot_yml.py, governance_boot.sh → enforce router` | Phase 2-b: 迁移 Session Boot workflow 到 enforce（第一批试点） | P0 | eng-platform |
| CZL-P2-c | `scripts/dispatch_board.py, cto_dispatch_broker.py, engineer_task_subscriber.py → enforce AUTO_POST` | Phase 2-c: 迁移 Dispatch workflow | P0 | eng-governance |
| CZL-P2-d | `governance/*.md protocol → enforce router rules` | Phase 2-d: 40 个 protocol 文档变 enforce 规则（逐个审） | P1 | eng-governance |
| CZL-P2-e | `tests/enforce_router/` | Phase 2-e: Drift live-fire test suite | P0 | eng-platform |

post 命令已编好，下一动作执行。

---

**End of plan. Board approve → 派白板 → 执行。**
