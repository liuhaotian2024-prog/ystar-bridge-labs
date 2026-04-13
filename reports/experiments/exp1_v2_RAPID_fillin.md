# RAPID 填充 — 闭环4 优先级决策

## R — Secretary Recommend

### R.1 方案陈述
建议将闭环 4（Secretary auto-memory sync）**绑定为 DIRECTIVE-004 的技术前置**，与 004 同批启动；不作为独立优先级条目插队到 003 之前，也不等 005/006 全部收敛。

### R.2 证据
- `knowledge/{role}/` 实测条目数（feedback/decisions/lessons）：
  - ceo: 2 / 1 / 3（共 6 条）
  - cto / cmo / cso / cfo / secretary / eng-platform / eng-kernel: 全 0
  - 结论：知识蒸馏目前是 CEO 单点，其他岗位尚未产出——闭环 4 当前实际要同步的存量极小。
- Claude harness auto-memory 路径 `~/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/` 只有 session jsonl 转录文件，**不存在 `memory/` 子目录**，即原生 auto-memory 在本项目从未被种入过任何 `knowledge/` 条目。
- 今日 session CEO 新写入 `knowledge/ceo/feedback/permission_self_classify_before_escalation.md` 与 `knowledge/ceo/decisions/pricing_premature_no_external_disclosure.md` 两条，**均未进入** auto-memory；下次 session 启动时 harness 的 memory 段不会自动出现这两条，完全依赖 governance_boot.sh + session_handoff.md 补偿。补偿路径已被证明够用但每次 boot 成本非零。

### R.3 备选方案
- **方案 A（立即启动）**：与在线 P0（DIRECTIVE-006 active_agent 并发）抢同一个 Ryan，会放大并发 bug 暴露面，A 段明确拒绝。
- **方案 B（003 之后）**：003 是对外发布主线但不依赖 auto-memory，插在此处对 003 无增益，闭环 4 价值被推迟。
- **方案 C（004 之后）**：004 交付"团队整理"成果需要写入下次 session 的 prompt 才能落地复利，如果 004 完成而闭环 4 未完成，成果蒸发——顺序反了。
- **方案 D（006 之后）**：先修并发再做 sync，安全性最高，但会让 004 的知识蒸馏价值继续无法复利。

### R.4 Secretary 的 Recommend
**推荐 C 的变体：闭环 4 与 004 同批启动，作为 004 的技术前置一起交付。** 理由：存量极小（6 条 CEO 条目）→ backfill 风险低；004 的产出强依赖 auto-memory 通路；单独立项会再起一次 RAPID，不经济。

— by Secretary Samantha Lin

---

## A — Maya Agree

### A.1 治理审查
- **DIRECTIVE-005 冲突**：005 要求 write 动作先过 `require_self_classification`。Secretary 的 sync 脚本写入 auto-memory 路径属新 write_path，必须先在 L3 扩权里显式声明并携带 risk class，否则触发 hook 拒绝。这是必须条件，不是加分项。
- **Iron Rules**：sync 是"知识蒸馏 → 复制到 harness 可见路径"，不产生新事实、不绕过 CIEU、不对外发布，不破坏任何 Iron Rule。
- **DIRECTIVE-006 放大风险**：active_agent 并发 BUG 未修前，若 Secretary sync 与其他 agent 同时读写 `knowledge/{role}/`，会命中同一个并发窗口。缓解：sync 必须 read-only 对 `knowledge/`（只读源）+ atomic write 目标文件；源侧零写入即可避开 006 的热区。

### A.2 Maya 的判决
**CONDITIONAL AGREE** — 同意 R.4 推荐，但推进到 P 前必须满足两条前置：
1. L3 扩权声明 Secretary 的 auto-memory 新 write_path，并通过 `gov_contract_validate`。
2. sync 脚本合约：对 `knowledge/` 源目录**只读**，写入仅限 auto-memory 目标路径 + atomic rename。

满足则 AGREE；不满足退回 R。

— by Maya Patel

---

## P — Ryan Perform Plan

### P.1 技术方案
`scripts/secretary_auto_memory_sync.py` 草案：
- **入口**：`sync(role=None, mode="incremental")`，role=None 遍历全部角色。
- **源扫描**：`knowledge/{role}/{feedback,decisions,lessons}/*.md` 只读。
- **目标**：`~/.claude/projects/-Users-haotianliu--openclaw-workspace-ystar-company/memory/{role}__{category}__{slug}.md`（首次创建 `memory/` 目录）。
- **格式**：注入 Claude harness memory frontmatter（`---\ntype: knowledge\nrole: {role}\ncategory: {category}\n---`）后拼接原文。
- **原子性**：`write tmp + os.rename`；幂等键为源文件 sha256，存 `scripts/.secretary_sync_index.json`，hash 未变跳过。
- **触发方式选择**：采用 **event-driven（CIEU trigger）**，理由——cron 有时序漂移、fsnotify 在 macOS/远端混合场景易丢事件、CIEU 已经是 write 动作的必经锚点，在 CEO/CTO 等写入 `knowledge/` 时由 CIEU 回调触发 sync，最贴合治理主干；保留 `--full` 手动兜底。
- **失败处理**：fail-open——sync 失败不阻塞写入主流程，错误写 `reports/daily/secretary_sync.log`，下次触发重试。

### P.2 前置依赖
1. DIRECTIVE-005 L3 扩权：Secretary 的 `write_paths` 增加 `~/.claude/projects/**/memory/`。
2. `.ystar_session.json` 的 `agents.secretary.write_paths` 字段同步修改并跑 `gov_contract_validate`。
3. CIEU 提供 `on_knowledge_write` 回调钩子（若未有，Ryan 先加 hook 再接 sync）。
4. `memory/` 目标目录首次创建权限确认（harness 沙箱是否允许）。

### P.3 工作量（intent completion 闭环数）
**2 个 intent completion 闭环**：
- 闭环①：hook + sync 脚本 + 索引 + dry-run 打通（对 CEO 6 条做 backfill 验证）。
- 闭环②：接入 CIEU trigger + fail-open 日志 + atomic 竞态测试 + Maya 的只读/原子合约验证。

— by Ryan Park

---

## I — CTO Ethan Input

### 技术风险视角
- **并发安全**：006 active_agent 并发 BUG 的根因是共享 session 字段竞态；sync 只读 `knowledge/` + 原子写独立 `memory/` 目标，不与 006 共享临界区，可先行。但 sync 自身多进程互斥需要——建议用 `fcntl.flock` 锁 `.secretary_sync_index.json`，拿不到锁即跳过本次触发（幂等保证下次不丢）。
- **历史 vs 增量**：当前源侧仅 6 条（均 CEO），**首次上线直接全量 backfill**，成本可忽略；不必单独设计 backfill 模式，复用 `--full`。一旦其他角色开始蒸馏，增量 hash 索引已能承接，不会退化为 O(全量)。
- **格式对齐**：Claude harness memory 对 frontmatter 是硬约束——`type` 字段若不在白名单会被丢弃；Ryan 草案里 `type: knowledge` 需先用一条样本在 harness 实机验证能被 auto-memory 段加载，不要盲信 schema 文档。建议闭环①的 dry-run 输出一条、手动重启一次 session 验证 prompt 里可见，再进入闭环②。
- **风险红线**：sync 绝不能反向写 `knowledge/`，否则 CIEU 的知识蒸馏权威源与 harness 镜像会出现双写冲突，违反单向复制原则。

— by CTO Ethan Wright
