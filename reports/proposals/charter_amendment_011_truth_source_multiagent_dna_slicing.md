# AMENDMENT-011 — Truth Source Consolidation + Multi-Agent Sub-agent Model + Per-Role DNA Slicing

**Author**: CEO (Aiden / 承远)
**Status**: PROPOSED (awaits Board D/A/S/C)
**Created**: 2026-04-13 (session 2026-04-12 夜→2026-04-13 晨 产出)
**Authority**: 第十一条自主 + Board 口头授权立项
**Related**: AMENDMENT-009（priority_brief 机制）、AMENDMENT-010（11 类 boot contract + secretary curation charter）

---

## 0. TL;DR

本 session 实证 Y*gov 治理系统在"无缝衔接"上仍有三个结构性漏洞：
1. **Truth source 冲突**：session_handoff / DISPATCH / priority_brief 三份同权威文件讲不同故事，新 Aiden 按哪份都可能跑错方向
2. **C-suite 无法在同 session 协作**：CEO/CTO/CMO/CSO/CFO 只有顶层身份可启动，非 sub-agent，跨岗位派活物理不可行（除非 Board 多开终端）
3. **DNA 未切片**：11 类 boot_packages 其实是一份 AGENTS.md 全文加载，各岗位读的是同一份 DNA，"岗位定制"还没实现

本 amendment 提议三项修复，每项附实装路径和验收标准。

---

## §1 Truth Source Consolidation（治"三份文件打架"）

### 1.1 问题实证
本 session 2026-04-12 23:22 CEO boot，同时读到：
- `memory/session_handoff.md` action_queue[1] = "check CTO Y*Defuse active_task"
- `reports/priority_brief.md` §3 DEPRECATED 清单把 "Y*Defuse 30天战役当前为最高优先级" 标 DEPRECATED
- `DISPATCH.md` tombstone header 说 DEPRECATED，但正文 Day 3 倒计时仍在

CEO 按 handoff 读了第一件事才发现和 priority_brief 冲突，再读 DISPATCH 确认是 tombstone。**三次读 + 一次自我纠偏** = boot 协议把冲突成本推给 agent 自觉。

### 1.2 提议
- `priority_brief.md` 为**唯一真理源**（已在 AMENDMENT-009 立约，本 amendment 加 enforcement）
- `session_handoff.md` 和 `DISPATCH.md` boot 时**自动校验**与 priority_brief 一致性：
  - 任何 action_queue 条目引用的 obligation / campaign / deadline，必须在 priority_brief §2/§3 出现且状态一致
  - 出现 DEPRECATED 条目 → 自动从 handoff action_queue 删除
  - 冲突 → boot FAIL，require Board 手动 reconcile
- 具体实装：`scripts/truth_source_consistency_check.py`，在 `governance_boot.sh` [0/7] 阶段调用

### 1.3 验收
- 构造一个 handoff 和 priority_brief 冲突的假样本，boot 必须 FAIL
- 真实场景：Y*Defuse DEPRECATED 后，新 session boot 不再把 Y*Defuse 列入 action queue

### 1.4 派给
Ryan-Platform（一致性检查脚本 + boot 钩子）+ CEO 签字 priority_brief 为 canonical

---

## §2 Multi-Agent Sub-agent Model（治"CEO 喊不动 CTO"）

### 2.1 问题实证
`.claude/agents/` 里存在 `ceo.md / cto.md / cmo.md / cso.md / cfo.md` 五个顶层 agent 定义（name = Aiden-CEO / Ethan-CTO / ...），但 Claude Code 启动 session 时只**选一个为顶层身份**，其他人不是 sub-agent。sub-agent 池只有 4 个工程师（Ryan-Platform / Leo-Kernel / Maya-Governance / Jordan-Domains）。

结果：
- CEO session 里要派 CTO → 只能靠 Board 另开终端并启动 Claude Code as CTO
- CTO 作为顶层 agent 也无法在自己 session 里 spawn CEO
- hook `must_dispatch_via_cto` 要求 CEO 经 CTO 派工程师，但 CTO sub-agent 不存在，导致**物理上 CEO 永远无法派工程师**

本 session 已被此漏洞卡死 3 次 deny，最终靠 Board shell `board_ceo_override.sh grant` 绕过。

### 2.2 提议（两路径二选一，建议路径 B）

**路径 A — 把 C-suite 全做成 sub-agent**：
- `.claude/agents/{ceo,cto,cmo,cso,cfo}.md` 里改 frontmatter，让 Claude Code 识别为 sub-agent_type
- 后果：顶层身份丢失，boot 只能以某个 "主角 agent" 启动，C-suite 变成同级 sub-agent 池
- 风险：破坏现有 governance_boot.sh 的身份识别语义

**路径 B（推荐）— 把 hook 规则改为 gov_delegate chain 验证**：
- `must_dispatch_via_cto` 当前 enforce 逻辑是**名字匹配**：CEO 不能 spawn 名字以 `eng-` 或 Name-Role 形式的工程师 agent
- 改为：如果 `gov_delegate` 里有 valid chain (principal=ceo → actor=cto → subactor=engineer, monotone, not expired)，就放行
- 单机单 session 场景：CEO 先 `gov_delegate(ceo→cto)` 并 `allow_redelegate=True`，然后 CEO 直接 spawn engineer，hook 查 chain valid 即 allow
- 相当于用 capability-based security 替代 name-based blacklist

### 2.3 验收
- 单 session 内 CEO 经 valid gov_delegate chain 成功 spawn Leo-Kernel，hook 放行，CIEU 记录 `dispatch_via_valid_chain`
- chain invalid（expired / scope violated）时 hook deny，并在 deny 消息里提示具体违规项

### 2.4 派给
Ryan-Platform 改 `boundary_enforcer.py::_check_must_dispatch_via_cto` 函数；Leo-Kernel 审 grant chain 逻辑边界情况（expiration / redelegate）。

---

## §3 Per-Role DNA Slicing（治"全员共读同一份 DNA"）

### 3.1 问题实证
CLAUDE.md 声称 "team_dna 和 thinking_dna 已经在 AGENTS.md 里"。实际 boot 时 Claude Code 加载的是项目级 CLAUDE.md（全员共用）+ AGENTS.md（全员共用）。岗位独有的认知模式 / 决策偏好 / 行为反射，**没有切片注入到当前身份的上下文**。

当前 `memory/boot_packages/{role}.json` 的 `category_1_identity_dna` 字段只写了：
```json
{
  "active_agent_marker_path": ".ystar_active_agent",
  "note": "Identity DNA loaded from AGENTS.md + team_dna.md via session_boot_yml.py"
}
```
— 是指针，不是 sliced payload。

### 3.2 提议
- `AGENTS.md` 结构化为 YAML 或 TOML frontmatter + 分段：
  - `<common>` — 全员共用 constitutional / decision_making / 十二 Tenets
  - `<role:ceo>` — CEO 专属 cognitive_profile / 反思清单 / 决策模式
  - `<role:cto>` ...
- `session_wisdom_extractor.py` boot_pack 生成时，`category_1_identity_dna` 内嵌对应 role 段的 parsed content（不是 note 和 path 指针）
- `governance_boot.sh` 把 boot_pack 的 `category_1 ~ category_3`（identity / charter / role_mandate）作为 **session 首条 context 注入**，而不是靠 Claude Code 全文加载

### 3.3 验收
- 对比 ceo.json 和 cto.json 的 `category_1_identity_dna` 字段：内容**实质不同**（不止文件路径不同）
- 新 session boot 时在 wisdom package 里能看到 "你是 Aiden，你倾向 X 认知，你避免 Y 模式" 的 role-specific 一段

### 3.4 派给
Jordan-Domains（AGENTS.md 分段重构）+ eng-platform（wisdom_extractor 解析逻辑）。

---

## §4 附加 — Secretary 13 步 curation pipeline（AMENDMENT-010 S-3 跟进）

Board 本 session 另问：秘书的"随时监视 + 持续总结 + 下 session 代码级 prompt"有没有落地。

**实况**：
- `scripts/secretary_curate.py` 只是 98 行 stub，13 步全 no-op
- 当前 `memory/boot_packages/*.json` 由 `session_wisdom_extractor.py v2` 在 session close 时生成（不是 secretary_curate 实装），只做 close-time snapshot，不做**持续**蒸馏
- 13 步 pipeline（skill_extract / tombstone / truth_triangulation / drift_self_audit / redteam_secretary / skill_lifecycle / article_11_enforce / secrets_scrub / circuit_breaker / time_layering）**一步都没真实实装**

**本 amendment 不重复 AMENDMENT-010 §S-3 的立约**，而是要求**设 72h 硬 deadline**：
- 4 月 15 日 EDT 前，`secretary_curate.py` 至少落地 Step 1（skill_extract）+ Step 2（tombstone）+ Step 5（next-session action queue generation）
- 派给：eng-platform + secretary 自己（跨 session 协作）
- 验收：session close 时自动触发 curate，产出 `memory/_curate_cache/{session_id}_snapshot.json` + 10 个 `memory/boot_packages/{role}.json` 含实际 skill_extract 结果（不只是 wisdom_extractor 的机械蒸馏）

---

## §5 优先级 & 依赖

| 提议 | P | 依赖 | ETA |
|---|---|---|---|
| §1 Truth source consistency check | P0 | 无 | 48h |
| §2 gov_delegate chain-based hook | P0 | `board_ceo_override.sh` 已证概念 | 72h |
| §3 Per-role DNA slicing | P1 | AGENTS.md 结构化重构 | 5 天 |
| §4 Secretary curate 3 步最小实装 | P0 | AMENDMENT-010 已批 §S-3 | 72h |

---

## §6 风险 & 反例

- §1 过严可能导致 false-fail boot（如 priority_brief 过期但 handoff 是 truth）→ 缓解：consistency_check 输出 conflict 报告，Board 可一条命令 reconcile
- §2 capability-based security 如果实装有漏洞（chain check bypass），反而放宽越权 → 缓解：单元测试覆盖过期 / scope violation / redelegate disabled 三种边界
- §3 AGENTS.md 分段若没 migration 脚本，会断掉现有 session_boot 流程 → 缓解：先加段不删段，eng-platform 把新字段读起来后再删旧
- §4 72h deadline 对 eng-platform 任务量紧张 → 缓解：只做 3 步最小可用，其余 10 步继续 stub，下个 amendment 再补

---

## §7 Board 决策点

- **D (Decide)**：三项是否本轮一起立项，还是只立 §1 + §2（基础设施优先）
- **A (Authorize)**：是否授权 CEO 自主协调 Ryan/Leo/Jordan/eng-platform 实装，每项完成后 Board 签字 acceptance
- **S (Stakeholder)**：Samantha Lin（秘书）需 review §3 的 AGENTS.md 结构化格式 + §4 的 pipeline 实装任务
- **C (Checkpoint)**：72h 后（2026-04-16 EDT）Board review §1 和 §2 交付，5 天后 review §3，持续跟踪 §4 的 3 步里程碑
