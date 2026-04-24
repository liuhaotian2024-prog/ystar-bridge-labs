---
Audience: Board (Haotian) — architectural approval for universal role retrofit; Ethan (CTO) — Wave-2 primary lead for runtime impl + peer review; Samantha (Secretary) — canonical archival per constitutional scope; Maya (Auditor) — self-runtime first retrofit; all 8 role agents (CEO/CTO/CSO/CFO/CMO/Secretary/Auditor/Engineer) — target receivers of role-specific instantiations
Research basis: Board 2026-04-24 Role Runtime Methodology expansion (8 roles × mode taxonomy × Y* × residual × evidence); Board 2026-04-24 CEO Runtime 8-step Management Cycle (parent spec reports/ceo/ceo_runtime_v0.1_spec_20260424.md now superseded as specific instantiation); U_v2 schema experiment in-flight (action-scale dual); tonight's CZL termination drift lesson; memory project_enforce_as_router_thesis (Board 2026-04-18)
Synthesis: Role Runtime Framework is universal cognitive-enforcement template at ROLE scale. Parent CEO Runtime spec is demoted to `role_runtimes/ceo.yaml` specific instantiation. Together with U_v2 action-scale schema, this forms 4-layer enforce stack (action / role / session / cross-session). Positions Y*gov v0.7 as "dynamic role orchestration system" — generation beyond Microsoft AGT policy engine, beyond any multi-agent framework (autogen/CrewAI just define roles, we define role *runtimes* with mode+Y*+residual).
Purpose: (1) Universal Role Runtime template spec; (2) 8 role instantiation table (Mode × Y* × Rt+1 × Evidence × Handoff × Memory); (3) Retrofit wave sequencing (P0 control-plane 4 roles first, P1 revenue-plane 3, then Engineer); (4) Integration with existing mechanisms; (5) Permanence enforce via 4-layer schema
---

# Role Runtime Framework v0.1 — Universal Dynamic Position System

## 0. North-Star reframe (constitutional candidate)

> A company is NOT a group of agents chatting.
> A company IS a set of ROLE RUNTIMES coupled via shared state + residual propagation.

Each agent = one typed role runtime instantiation. Role = not name + tools + memory; role = mode-awareness + Y* + residual + minimal intervention + verification + writeback cycle.

**Generation-ahead positioning claim**: Microsoft AGT (policy engine), AutoGen / CrewAI (role definitions + tool calls) all operate at action/role-definition layer. Y*gov v0.7 operates at role-RUNTIME layer — each role has its own dynamic mode detector + goal binder + residual engine. Proof of novelty: zero known framework treats role as stateful runtime with mode transitions.

---

## 1. Universal Role Runtime template (applies to ALL 8 roles)

```yaml
role_runtime_cycle_v0.1:
  required_steps:  # each role completes these 7 per cycle; missing → hook DENY + REDIRECT
    
    1_role_mode:
      field: current_mode
      type: enum (role-specific vocabulary)
      example_vocabularies:
        CEO: [Survival, Product, Engineering, Growth, Governance, Crisis, Research]
        CTO: [Architecture, Delivery, Recovery, Refactor, Verification]
        CSO: [MarketDiscovery, Positioning, Keyword, Competitive, GTM]
        CFO: [Pricing, Payment, UnitEconomics, RevenueExperiment, Tax]
        CMO: [BuildInPublic, SEO, Launch, Story, SocialProof]
        Secretary: [Handoff, Memory, TaskLedger, Recovery, AuditIndex]
        Auditor: [EmpiricalVerify, Forensic, Evidence, Regression, Risk]
        Engineer: [Diagnosis, Patch, Test, Integration, Regression]
      rationale: str (min_length: 50, why this mode now)
    
    2_role_y_star:
      field: current_y_star
      type: structured
      structure:
        completion_standard: str (NOT "do many tasks" — specific state)
        phase_scope: enum [north_star, phase, cycle]
        bound_to: goal_tree_node_id
      role_specific_y_star_examples:
        CEO: "让公司整体 Rt+1 最大幅下降"
        CTO: "让技术系统更可运行/可验证/可扩展"
        CSO: "找到最短变现路径和最清晰的市场切口"
        CFO: "让生产结果能自动定价/交付/收款"
        CMO: "让真实产品进展变成可传播/可搜索/可转化的内容资产"
        Secretary: "让下一轮团队能无损接手当前状态"
        Auditor: "证明完成是否真实, 把失败转化成系统改进"
        Engineer: "把明确问题转成可运行/可测试/可审计的变更"
    
    3_role_residual_diag:
      field: role_rt_plus_1
      type: list of {dimension: str, gap: str, metric: str|null}
      role_specific_dimensions:
        CEO: [product, revenue, distribution, execution, trust, architecture]
        CTO: [code_written_not_tested, module_exists_not_wired, docs_diverge_runtime, import_fails, ux_install_degrades]
        CSO: [no_keyword_data, no_user_pain_mapped, competitor_unscanned, pricing_unvalidated, no_first_success_defined]
        CFO: [no_stripe_link, no_price, free_vs_paid_unclear, no_rev_dashboard, monetize_depends_manual]
        CMO: [no_daily_public_content, no_keyword_page, no_demo_video, no_share_card, no_user_result_mechanism]
        Secretary: [MEMORY_unwritten, taskboard_drift, claim_no_evidence, artifact_unindexed, handoff_missing]
        Auditor: [no_tests_run, no_smoke_import, diff_unread, no_evidence_path, self_reported_rt_unverified]
        Engineer: [surface_fix_only, root_cause_uncovered, missing_tests, not_main_line, not_user_visible]
    
    4_role_constraint:
      field: active_constraints
      type: list
      examples: [permission_missing, info_missing, time_window, tool_unavailable, dependency_blocked, market_uncertain, code_blocker, evidence_missing]
      hardest_constraint: str + justification
    
    5_minimal_intervention:
      field: chosen_action
      type: structured
      structure:
        candidates: list (≥2 alternatives, forcing comparison)
        chosen: str
        expected_rt_delta: str (which dimension, how much)
        tu_cost: int
        score: float (rt_delta / tu_cost)
    
    6_delegation_or_self:
      field: execution_route
      type: enum [self_execute, delegate_to_role_X, escalate_to_CEO, request_Board]
      if_delegate:
        owner_role: str
        permission_grant: path_allowlist
        completion_criteria: str
        live_fire_gate: str
    
    7_verification:
      field: empirical_evidence
      type: list  # SAME schema as U_v2 empirical_basis
      each: {source: enum, ref: str}
      role_specific_evidence_types:
        CEO: [dashboard_delta, p0_count_trend, revenue_landed]
        CTO: [tests_passing, smoke_import, cli_demo, real_repo_run, commit_diff, ci_result]
        CSO: [keyword_volume, landing_conversion, waitlist_count, ph_hn_feedback, competitor_matrix]
        CFO: [buy_button_live, test_payment_passed, first_paid_user, cac_api_margin, payout_record]
        CMO: [impressions, clicks, signups, installs, shares, backlinks, conversion]
        Secretary: [handoff_prompt_usable, next_session_reproducible, memory_import_verified, taskboard_consistent, evidence_path_exists]
        Auditor: [pytest_pass, smoke_import, git_diff, report_file, cieu_chain, reproduction_steps]
        Engineer: [unit_tests, integration_tests, manual_smoke, diff_review, line_level_evidence, issue_closure]
    
    8_state_writeback:
      field: state_delta
      type: structured
      structure:
        memory_write: [paths updated]
        baseline_updated: bool
        report_landed: [path]
        taskboard_delta: str
        cieu_event_emitted: event_type
      trigger_location: enum [role_internal, shared_company_state, brain_writeback]
```

---

## 2. 8-role instantiation table (concise reference)

| Role | Mode vocab (count) | Y* (1-line) | Top 3 Rt+1 dims | Primary evidence | Handoff to |
|---|---|---|---|---|---|
| **CEO** (Aiden) | 7 (Survival/Product/Eng/Growth/Gov/Crisis/Research) | 让公司整体 Rt+1 最大幅下降 | product, revenue, architecture | dashboard delta, P0 trend, revenue | CTO/CSO/CFO |
| **CTO** (Ethan) | 5 (Arch/Delivery/Recovery/Refactor/Verif) | 让技术系统更 runnable/verifiable/scalable | tests_not_passing, module_not_wired, import_fails | pytest, smoke import, commit diff | Engineers (Leo/Maya/Ryan/Jordan) |
| **CSO** (Zara) | 5 (MarketDiscovery/Position/Keyword/Competitive/GTM) | 找最短变现 + 最清晰切口 | no_keyword_data, competitor_unscanned, pricing_unvalidated | keyword volume, landing conversion, competitor matrix | CEO / CMO |
| **CFO** (Marco) | 5 (Pricing/Payment/UnitEcon/RevExp/Tax) | 生产结果自动定价/交付/收款 | no_stripe_link, no_price, monetize_manual | buy button live, test payment, first paid user | CEO / CSO |
| **CMO** (Sofia) | 5 (BIP/SEO/Launch/Story/SocialProof) | 真实进展→可传播/可搜索/可转化 | no_daily_content, no_keyword_page, no_demo_video | impressions, signups, conversion | CSO / Engineer (demo) |
| **Secretary** (Samantha) | 5 (Handoff/Memory/TaskLedger/Recovery/AuditIndex) | 下一轮团队无损接手当前状态 | MEMORY_unwritten, taskboard_drift, claim_no_evidence | handoff usable, memory import verified, evidence path | CEO (state report) |
| **Auditor** (Maya as governance-auditor function) | 5 (EmpiricalVerify/Forensic/Evidence/Regression/Risk) | 证完成真实 + 把失败转系统改进 | no_tests_run, no_smoke, self_report_unverified | pytest, CIEU chain, reproduction | CEO (findings) / Engineer (fix) |
| **Engineer** (Leo/Maya-gov/Ryan/Jordan) | 5 (Diagnosis/Patch/Test/Integration/Regression) | 明确问题→可 run/test/audit 变更 | surface_fix, no_tests, not_main_line | unit/integration tests, diff, line-level | CTO (review) / Auditor (verify) |

---

## 3. Retrofit sequencing (P0 → P1, 不 propose — 实 ship plan)

### P0 Control-plane (4 roles, retrofit first — these are the governance primitives)

| Role | Retrofit owner | Schema file | Phase 1 live-fire |
|---|---|---|---|
| CEO | Ethan peer review + Leo schema build | `Y-star-gov/governance/role_runtimes/ceo.yaml` | mock cycle reply → hook catches missing 7-step |
| CTO | Ethan self-retrofit (dogfood) | `Y-star-gov/governance/role_runtimes/cto.yaml` | mock CTO receipt → schema validates |
| Secretary | Samantha self-retrofit | `Y-star-gov/governance/role_runtimes/secretary.yaml` | handoff doc passes schema |
| Auditor | Maya (governance 身份双兼) | `Y-star-gov/governance/role_runtimes/auditor.yaml` | audit doc passes schema |

### P1 Revenue-plane (3 roles)

| Role | Retrofit owner | Schema file |
|---|---|---|
| Engineer | Jordan (domains 承) | `Y-star-gov/governance/role_runtimes/engineer.yaml` (shared across Leo/Maya/Ryan/Jordan) |
| CSO | Zara self-retrofit | `Y-star-gov/governance/role_runtimes/cso.yaml` |
| CFO | Marco self-retrofit | `Y-star-gov/governance/role_runtimes/cfo.yaml` |
| CMO | Sofia self-retrofit | `Y-star-gov/governance/role_runtimes/cmo.yaml` |

### P2 Integration layer

- `scripts/role_runtime_dispatcher.py` — Stop hook + role-specific schema route + CIEU emit
- `scripts/role_runtime_dashboard.py` — per-role mode + Y* + Rt+1 snapshot
- `scripts/session_close_yml.py` extend — record exit mode per role for cross-session continuity

---

## 4. Integration with existing mechanisms (critical — NOT re-architecture)

| Existing mechanism | Role Runtime integration point |
|---|---|
| **U_v2 schema** (action-scale, in-flight Leo+Ryan) | Role Runtime step 7 verification REUSES U_v2 `empirical_basis` schema. No new work. |
| **CZL 5-tuple receipt** | Extended: Role Runtime cycle receipt is 7-step YAML frontmatter superset of CZL 5-tuple (Y* + Xt + U + Yt+1 + Rt+1 all subsume into cycle steps) |
| **场泛函 goal_tree** (Phase 3) | `role_y_star.bound_to: goal_tree_node_id` — each role cycle MUST bind to specific goal node |
| **M Triangle M(t)** | North-Star Y* for all roles (constitutional invariant) |
| **forget_guard / router_registry** | New rule class `role_runtime_cycle_incomplete` + `role_mode_undeclared` etc. Fits existing Axis-A/B/C/D framework. |
| **break_glass / K9 Rescue** | Role Runtime mode="Crisis" triggers K9 physical escape. Tonight's K9 Daemon fits. |
| **ceo_mode_manager.py** (existing) | Generalize to `role_mode_manager.py` — each role has own mode state. Current CEO-only is specific case. |
| **Agent tool dispatch** | Role Runtime step 6 delegation — dispatch prompt template MUST declare receiver role's expected mode + Y* binding + completion criteria matching schema |
| **hooks (Pre/Post/Stop)** | Role Runtime step enforcement via hooks (same pattern as U_v2 stop_hook + czl_termination_drift stop_hook) |

---

## 5. Permanence enforce — 4-layer stack (same pattern as U_v2)

### Layer A — Schema (structure)
8 files in `Y-star-gov/governance/role_runtimes/*.yaml` — per-role instantiation of universal template.

### Layer B — Hook runtime enforce
`scripts/hook_stop_role_runtime_check.py` — detects agent identity from marker, loads appropriate role schema, validates receipt, DENY+REDIRECT missing steps.

### Layer C — Role-aware dashboards
`scripts/role_runtime_dashboard.py --role=ceo|cto|...` — shows per-role mode + Y* + Rt+1 top-3.

### Layer D — Cross-session persistence
`session_close_yml.py` records per-role exit_mode + phase_y_star_binding. `governance_boot.sh` restores + detects transitions.

---

## 6. Tonight's in-flight work natural fit

| In-flight task | Role Runtime mapping |
|---|---|
| Ethan 92 regression triage | CTO in Recovery Mode, Y* = restore test suite green, Rt+1 = 92 failures, evidence = pytest re-run |
| Maya Item #4 OmissionEngine | Auditor/Engineer in Patch Mode, Y* = live-fire OmissionEngine rule fires, Rt+1 = rule_silent, evidence = pytest + CIEU delta |
| Maya czl_termination_drift rule | Auditor in Regression Mode, Y* = stop hook catches CEO drift, Rt+1 = lesson prose only not enforced, evidence = live-fire pattern detect |
| Leo Item #9 break-glass + U_v2 validator | Engineer in Integration Mode (break-glass) + Test Mode (U_v2 validator) |
| Ryan U_v2 instrument | Engineer in Integration Mode, Y* = hook injects schema + emits CIEU events, evidence = env var toggle + SQL verify |

Each in-flight can be **自验证** against new framework when they return — CEO (me) validates each receipt against role's expected Role Runtime cycle schema. That itself is empirical dogfood.

---

## 7. 诚实 reservations (P-14)

1. **Scope creep risk**: 8 roles × 4 enforce layers = large surface. P0 ships first (4 control-plane roles), P1 iterative. Don't try all 8 at once.
2. **Mode taxonomy uncertainty**: Board's 5-7 modes per role are starting point, may need iteration after empirical use.
3. **Schema overhead per role interaction**: similar to U_v2 concern, tiered (routine vs major decision).
4. **Retrofit requires self-modification by each agent**: dogfood risk — Samantha self-retrofit requires Samantha's agent file edit scope verify.
5. **Integration with current Wave-2**: must NOT block Wave-1.5 regression triage + U_v2 experiment. Role Runtime is P2 of Wave-2, not P0.

---

## 8. NOW 执行 (not propose)

- 本 spec 落盘 (已 done)
- 下 session Wave-2 kickoff 按以下顺序:
  - a. Ethan peer review 本 spec + 校正 taxonomy 错误
  - b. Leo 从 `ceo.yaml` schema 起 (最急 + 今晚有 regression 案例 dogfood)
  - c. Samantha + Maya 自 retrofit (control-plane 核心)
  - d. P1 roles 按依赖顺序

- **当前所有 in-flight sub-agent 返回时, CEO validate 他们 receipt 已 自然符合 Role Runtime cycle 多少步** — 这就是 retrofit 的 dogfood baseline measurement (当前 prose compliance rate, 后续 schema 启用后对比)

- 此 spec 与 U_v2 experiment 4-phase 协调: Role Runtime 是 U_v2 的 role-scope 上层, 共享 empirical verify 方法学 (同 hypothesis testing + A/B + persistence + theater)

---

**统一一句话**: 从今夜起, Y*gov 不再是 rule engine, 是 **role-runtime orchestration system**. 每个 agent = typed role runtime = mode + Y* + residual + minimal intervention + verification + state. 这就是 Board 2026-04-24 立的 v0.7 北星.
