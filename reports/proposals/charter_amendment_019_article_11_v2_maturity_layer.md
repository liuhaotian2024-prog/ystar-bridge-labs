# CHARTER AMENDMENT-019: Article 11 v2 with Maturity Gate Integration

**Status**: L1 SPEC — Proposal submitted  
**Submission Date**: 2026-04-13  
**Proposer**: Ethan Wright (CTO), authorized by Board directive  
**Board Approval Required**: Yes  
**Estimated Implementation Time**: 4 hours (L1→L4)

---

## §0 TL;DR (Board Mandate Context)

**Board directive (2026-04-13):**  
"不只是进入 memory，而是要固化到你的岗位宪法里面，并且全部同步，让你每次都会必须这么想问题，处理问题。还有融入你的第十一条里面，形成一个更强大的第十一条。必须让你每次思考和行为都必须遵守这个机制。"

**Problem**: Article 11 v1 (Autonomous Mission methodology) tracks cognitive construction (Layers 0-7) and execution (Layers 8-9), but lacks explicit **maturity state tracking** and **completion validation**. Agents can emit "done" / "落盘" / "shipped" without standardized evidence gates, causing Board confusion about actual completion state.

**Solution**: Embed the 5-level maturity taxonomy (L0 IDEA → L5 ADOPTED) directly into Article 11 Layer 9 execution as mandatory state gates, and enforce L-tag presence in all status communication via CIEU hooks.

**Impact**: Every work product, from proposal to production, carries explicit maturity level. Board gets immediate clarity on what's idea vs what's running with real users.

---

## §1 Current State Audit: Article 11 v1 Gap Analysis

**Article 11 v1 Structure** (`governance/WORKING_STYLE.md` lines 783-880):

```
Phase 1: Cognition Construction (Layers 0-7)
  → Layer 0: Meaning
  → Layer 1: Goal Clarification
  → Layer 2: Assumption Explicitness
  → Layer 3: Theory Calibration
  → Layer 4: Benchmark
  → Layer 5: Relevance Filter
  → Layer 6: Case Extraction
  → Layer 7: Capability Boundary

Phase 2: Execution
  → Layer 8: Solution Design
  → Layer 9: Execute + CIEU logging
  → Ethics check before each release

Phase 3: Observation & Data Collection
  → Quantitative + Qualitative metrics
  → Assumption validation

Phase 4: Iteration & Recalibration
  → Trigger: 2 consecutive cycles miss target OR major assumption falsified
```

**Gap Identified**: Layer 9 says "execute" but does NOT decompose into maturity stages. An agent can write code (L2 IMPL), run tests (L3 TESTED), deploy to production (L4 SHIPPED), but Article 11 v1 treats all of these as undifferentiated "execution." When an agent reports "Task completed," Board has no standardized way to know if "completed" means "code written" or "users adopting."

**Evidence from Recent Work**:
- AMENDMENT-017 "completed" = L1 SPEC (6-pager written, not implemented)
- `scripts/session_boot_yml.py` "completed" = L3 TESTED (tests pass, not deployed as hook)
- `ystar doctor` L0 fixes "completed" = L4 SHIPPED (production running, adoption unknown)

All three used the same word "completed," creating ambiguity.

---

## §2 Proposal: Article 11 v2 with Embedded Maturity Gates

### 2.1 Core Change: Layer 9 Decomposition

**Replace Layer 9 single-stage execution** with **5 maturity gates**:

```
Layer 9: Execution with Maturity Progression

9.0 Initiation
    → Work begins, item registered in active_task.py
    → Default state: L0 IDEA

9.1 Specification (L0 → L1)
    → Output: written proposal / design doc / task card with acceptance criteria
    → Evidence: file exists + git commit hash OR task card ID
    → CIEU event: MATURITY_TRANSITION(item_id, L0, L1, evidence)

9.2 Implementation (L1 → L2)
    → Output: code written / content drafted / infrastructure deployed (pre-test)
    → Evidence: implementation file exists + git commit hash OR content file path
    → CIEU event: MATURITY_TRANSITION(item_id, L1, L2, evidence)

9.3 Testing (L2 → L3)
    → Output: tests pass / peer review approved / validation complete
    → Evidence: test output / review approval / validation report
    → CIEU event: MATURITY_TRANSITION(item_id, L2, L3, evidence)

9.4 Deployment (L3 → L4)
    → Output: production running / content published / feature live
    → Evidence: live behavior observable + monitoring active
    → CIEU event: MATURITY_TRANSITION(item_id, L3, L4, evidence)

9.5 Adoption (L4 → L5)
    → Output: ≥1 real user/consumer actively using the work product
    → Evidence: usage metric / user feedback / consumption log
    → CIEU event: MATURITY_TRANSITION(item_id, L4, L5, evidence)
```

**Key principle**: Each transition requires **explicit evidence**, not just agent assertion. CIEU records the transition + evidence payload.

### 2.2 Communication Protocol Change: Mandatory L-Tag

**All status communication must include maturity L-tag**:

- CEO → Board report: "AMENDMENT-019 [L1] submitted for approval"
- Agent → Agent handoff: "Session boot script [L3] tested, ready for hook integration [L2→L4 pending]"
- Commit message: "feat(governance): Article 11 v2 maturity gate [L2 IMPL]"
- Daily report: "Today shipped: session continuity guardian [L4], Blog post draft [L2], Pricing model [L1]"

**Violator Detection (automatic CIEU hook)**:

Hook scans all:
- Git commit messages
- File writes to `reports/` containing keywords: "done" / "completed" / "finished" / "shipped" / "落盘"
- `active_task.py update` calls

If keyword present but NO L-tag detected → emit CIEU event:
```
MATURITY_TAG_MISSING(
  source: commit_hash OR file_path OR task_id,
  keyword: detected_completion_word,
  timestamp: ISO8601
)
```

Secretary reviews all `MATURITY_TAG_MISSING` events weekly and flags repeat offenders.

### 2.3 Article 11 Phase 2 Updated Structure

**New Phase 2 structure**:

```
Phase 2: Execution with Maturity Tracking

Layer 8: Solution Design
  → Design this cycle's action plan
  → Map plan to Layer 1 stage targets
  → Declare intent via active_task.py start
  → Initial state: L0 IDEA

Layer 9: Maturity-Gated Execution
  → 9.1 Spec (L0→L1): written proposal/design/task + commit hash
  → 9.2 Impl (L1→L2): code/content/infra exists + commit hash
  → 9.3 Test (L2→L3): tests pass/review approved + evidence
  → 9.4 Deploy (L3→L4): production live + monitoring active
  → 9.5 Adopt (L4→L5): ≥1 real user + usage metric
  → Each transition emits MATURITY_TRANSITION CIEU event
  → Missing L-tag in status → MATURITY_TAG_MISSING event

Ethics Check (before each L3→L4 transition)
  → Check against governance/ETHICS.md
  → Any doubt → stop, escalate to Board
  → Default: do not ship if uncertain
```

---

## §3 Acceptance Criteria

This AMENDMENT reaches L4 SHIPPED when:

1. **[L2 IMPL]** `governance/WORKING_STYLE.md` Article 11 updated with §2.3 text (Board manual paste from Appendix B)
2. **[L2 IMPL]** `AGENTS.md` adds one hard constraint line (Board manual paste from Appendix A)
3. **[L3 TESTED]** CIEU hook `maturity_tag_check.py` written, tested, emits `MATURITY_TAG_MISSING` events correctly
4. **[L4 SHIPPED]** Hook integrated into `governance_boot.sh` + active in production for ≥7 days
5. **[L5 ADOPTED]** Board + all C-suite + 4 engineers use L-tags in ≥90% of status reports for 1 week, verified by Secretary audit of CIEU `MATURITY_TAG_MISSING` event count = 0 for that week

---

## §4 RAPID Analysis

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Reversible** | 3/10 | Maturity taxonomy becomes load-bearing in all communication. Reversal = retraining entire team. Low reversibility. |
| **Asymmetric** | 9/10 | Upside: Board gets instant clarity on delivery state. Downside: agents spend 5 sec/report tagging L-level. Highly asymmetric. |
| **Probabilistic** | 2/10 | Deterministic taxonomy. No LLM involved. Very low failure probability. |
| **Irreversible** | 7/10 | Once adopted, removing L-tags = loss of maturity tracking capability. Hard to reverse. |
| **Delegable** | 1/10 | Board cannot delegate maturity gate design. This is constitutional-level decision. Non-delegable. |

**RAPID Conclusion**: **Board Approve** required. High asymmetry, low reversibility, constitutional impact.

---

## §5 Risk & Mitigation

### Risk 1: Cognitive Load on Agents
**Description**: Every status report requires L-level calculation. Adds cognitive overhead.

**Mitigation**: Provide **verb→L mapping table** in Appendix C. Agents use table lookup instead of reasoning from first principles.

Example mapping:
- "proposed" → L1
- "wrote code" → L2
- "tests pass" → L3
- "deployed" / "live" → L4
- "user reported" / "usage metric" → L5

### Risk 2: CIEU Event Noise
**Description**: Every L-transition emits CIEU event. Could flood CIEU database.

**Mitigation**: `MATURITY_TRANSITION` events are high-value audit trail, not noise. They answer "when did this item become production-ready?" — core governance question. Accept the volume.

### Risk 3: L-Tag Enforcement Friction
**Description**: Agents forget L-tags, get `MATURITY_TAG_MISSING` warnings, feel micromanaged.

**Mitigation**: Frame as **service to Board clarity**, not policing. Secretary weekly review is educational, not punitive. First 2 weeks = warning only, no penalty.

---

## §6 Relationship to Other Amendments

- **AMENDMENT-007 (CEO Operating System)**: CEO's "今日发货" section now requires L-tags for all items.
- **AMENDMENT-010 (Secretary Curation Charter)**: Secretary's weekly curation must include CIEU `MATURITY_TAG_MISSING` audit report.
- **AMENDMENT-012 (Deny as Teaching)**: When GOV MCP denies an action, denial reason should include "current maturity: LX, required: LY" where applicable.
- **AMENDMENT-015v2 (LRS Unified)**: Session handoff `memory/session_handoff.md` must include maturity state of all in-flight work.
- **AMENDMENT-017 (Capability Envelope)**: Self-mirror's "我现在能做到什么" section must state maturity level for each capability claim.

---

## §7 Board Action Required

**Approve or Reject this AMENDMENT**:
- [ ] **APPROVED** — proceed to L2 implementation (paste Appendix A + B into immutable files)
- [ ] **REJECTED** — rationale: ___________
- [ ] **DEFER** — request revision on: ___________

**Upon approval, Board must manually**:
1. Copy Appendix A text → paste into `AGENTS.md` after line 7 (Iron Rules section)
2. Copy Appendix B text → replace `governance/WORKING_STYLE.md` lines 829-843 (Phase 2 section)
3. Notify Ethan (CTO) to proceed with L3 hook implementation

---

## Appendix A: Ready-to-Paste Diff for AGENTS.md

**Insert after line 7 (after Iron Rule 1, before Iron Rule 2):**

```markdown
---

## Iron Rule 1.5: Maturity State Transparency (Constitutional, non-violable)

All work products must carry explicit maturity level (L0 IDEA → L5 ADOPTED) in status communication. All git commits, reports, and task updates containing completion-indicating keywords ("done", "completed", "shipped", "finished", "落盘") must include L-tag in format `[LX]` or `LX STATE_NAME`.

Maturity taxonomy:
- L0 IDEA: verbal/written concept, zero artifact, no validation
- L1 SPEC: proposal submitted, commit hash or task card exists
- L2 IMPL: code/content written, pre-test, file exists
- L3 TESTED: tests pass / review approved / validation complete
- L4 SHIPPED: production running / content live / feature deployed
- L5 ADOPTED: ≥1 real user/consumer actively using, usage metric exists

Missing L-tag in completion communication triggers `MATURITY_TAG_MISSING` CIEU event. Secretary audits weekly. This rule enforces Board's ability to distinguish "code written" from "users adopting" without asking clarifying questions.

Violation = communication ambiguity, degrades Board trust. Fulfill via Appendix C verb→L mapping table (see Article 11 v2).

---
```

---

## Appendix B: Ready-to-Paste Text for governance/WORKING_STYLE.md Article 11 Phase 2

**Replace lines 829-843 with:**

```markdown
### 阶段二：执行落地与成熟度跟踪

每个执行周期的结构：

**方案设计（第 8 层）**：基于认知框架设计本周期具体行动，必须回对第 1 层的阶段性指标，用 `active_task.py start` 声明意图。初始状态：L0 IDEA。

**执行（第 9 层）：成熟度门控执行**

所有执行必须经过 5 级成熟度门控，每个门控转换需显式证据 + CIEU 记录：

- **9.1 规格化 (L0 → L1 SPEC)**：输出书面提案/设计文档/任务卡，证据 = 文件存在 + git commit hash 或任务卡 ID，触发 `MATURITY_TRANSITION(item_id, L0, L1, evidence)` CIEU 事件
- **9.2 实现 (L1 → L2 IMPL)**：代码/内容/基础设施完成（测试前），证据 = 实现文件存在 + commit hash 或内容路径，触发 `MATURITY_TRANSITION(item_id, L1, L2, evidence)`
- **9.3 验证 (L2 → L3 TESTED)**：测试通过/同行评审批准/验证完成，证据 = 测试输出/评审记录/验证报告，触发 `MATURITY_TRANSITION(item_id, L2, L3, evidence)`
- **9.4 部署 (L3 → L4 SHIPPED)**：生产环境运行/内容发布/功能上线，证据 = 可观察的线上行为 + 监控激活，触发 `MATURITY_TRANSITION(item_id, L3, L4, evidence)`
- **9.5 采用 (L4 → L5 ADOPTED)**：≥1 真实用户/消费者主动使用，证据 = 使用指标/用户反馈/消费日志，触发 `MATURITY_TRANSITION(item_id, L4, L5, evidence)`

**状态通信硬约束**：所有状态报告必须包含成熟度 L 标签。格式：`[LX]` 或 `LX STATE_NAME`。所有包含完成性关键词（"done" / "completed" / "finished" / "shipped" / "落盘"）的 git commit、报告、任务更新，如缺失 L 标签，触发 `MATURITY_TAG_MISSING` CIEU 事件，Secretary 每周审计。

**违反者检测**：CIEU hook 自动扫描所有 commit 消息、`reports/` 写入、`active_task.py update` 调用，检测完成性关键词 + L 标签缺失组合。

**伦理检查（每次 L3→L4 转换前强制）**：对照 `governance/ETHICS.md` 逐条检查。任何一条有疑问，停止执行，上报 Board。**不确定的情况下，默认不发布**。
```

---

## Appendix C: Verb → Maturity Level Mapping Table (Agent Quick Reference)

| Verb / Phrase | Maturity Level | Evidence Required |
|---------------|----------------|-------------------|
| "proposed", "drafted proposal", "designed" | L1 SPEC | Proposal file + commit hash |
| "wrote code", "implemented", "built", "drafted content" | L2 IMPL | Code/content file + commit hash |
| "tests pass", "review approved", "validated" | L3 TESTED | Test output / review record |
| "deployed", "shipped", "live", "published", "上线" | L4 SHIPPED | Production URL / live behavior |
| "user reported", "adopted by X", "usage metric", "真实用户" | L5 ADOPTED | Usage log / user feedback |
| "idea", "concept", "口头讨论" | L0 IDEA | None (pre-artifact state) |

**Usage**: When writing status report, scan your action verb against this table. Insert `[LX]` tag immediately after the item name.

**Example**:
- ❌ "Session boot script completed" (ambiguous)
- ✅ "Session boot script [L3] tests pass, pending hook integration"
- ✅ "AMENDMENT-019 [L1] submitted for Board approval"

**Edge case**: If an item spans multiple maturity levels in one report, use the **highest achieved level**:
- "Wrote hook code [L2] and ran tests [L3]" → tag as `[L3]`

---

**END OF AMENDMENT-019 6-PAGER**  
**Current Maturity**: L1 SPEC — proposal submitted, awaiting Board approval to advance to L2 implementation.
