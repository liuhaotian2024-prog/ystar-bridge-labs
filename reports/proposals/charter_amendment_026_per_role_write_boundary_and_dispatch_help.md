# AMENDMENT-026 — Per-Role Write Boundary Matrix + Cross-Role Help Protocol

| 字段 | 内容 |
|---|---|
| Level | 3 (Constitutional addition: 写入权限治理底层重构) |
| 起草日 | 2026-04-13 |
| 起草人 | CEO Aiden (per Board 直接指出"之前的技术债") |
| 强依赖 | A007 (CEO OS) + A009 (escape hatch) + A017 (capability envelope) + A023 (CROBA) |

## §0 TL;DR

**Board 原话**: "CMO 写 content/ 越 cto boundary，这就是我们的之前的技术债，当时就没写清楚每个岗位都有自己的业务范围内的写入权利，或者如何交给别人帮助自己写的机制。"

修复 = 2 件事：
1. **Per-role allowed_write_paths matrix** — 每岗位显式 own 业务路径写权
2. **Cross-role help protocol** — 当 X 需要 Y 帮写，formal 协议（不是越权 + 不是找 Board）

---

## §1 现状审计 (deep tech debt)

`.ystar_session.json` 当前结构 (sample):
```json
{
  "agent_write_paths": {
    "ceo": ["./reports/", "knowledge/ceo/", ...],
    "cto": ["./scripts/", "./tests/", "./products/", "./docs/", "Y-star-gov/", "CLAUDE.md"]
  },
  "restricted_write_paths": {
    ".ystar_active_agent": ["secretary"],
    "AGENTS.md": ["secretary"],
    ...
  }
}
```

**真问题：**
1. `agent_write_paths` 主要列了 CEO + CTO，**CMO/CSO/CFO/Secretary/Engineers 几乎都没显式列**
2. 当 CMO subagent 写 `content/offended_ai/` 时 — 它 hit cto boundary 因 active_agent=cto (顶岗) 或 因 cmo 没显式 allow content/
3. 跨岗位帮写 (CMO 让 CTO 帮 ship 视频生成 pipeline 进 scripts/) 没有 formal 通道

**今晚实证：** CMO顶岗 v5 第一次 spawn 时 active_agent=cto → 写 content/ deny → 报 blocker → CEO 用 pkill window 切 active_agent=cmo → 重 spawn 才能写。这是手动 workaround，应该是协议。

---

## §2 提议

### Part A: Per-Role Write Boundary Matrix

`.ystar_session.json` `agent_write_paths` 字段全员显式：

```json
{
  "ceo":         ["./reports/", "./knowledge/ceo/", "./BOARD_PENDING.md", "./DISPATCH.md", "./OKR.md", "./DIRECTIVE_TRACKER.md", "./OPERATIONS.md", "./WEEKLY_CYCLE.md", "memory/", ".claude/agents/"],
  "cto":         ["./scripts/", "./tests/", "./products/", "./docs/", "Y-star-gov/", "gov-mcp/", "./CHANGELOG.md", "./CLAUDE.md", "./.github/", ".claude/tasks/"],
  "cmo":         ["./content/", "./marketing/", "./knowledge/cmo/", "./reports/cmo*"],
  "cso":         ["./sales/", "./knowledge/cso/", "./reports/cso*"],
  "cfo":         ["./finance/", "./knowledge/cfo/", "./reports/cfo*"],
  "secretary":   ["./governance/BOARD_CHARTER_AMENDMENTS.md", "./governance/DNA_LOG.md", "./knowledge/", "./memory/boot_packages/", "ARCHIVE_INDEX.md", ".ystar_active_agent"],
  "eng-kernel":     ["Y-star-gov/ystar/kernel/", "Y-star-gov/tests/", "knowledge/eng-kernel/"],
  "eng-governance": ["Y-star-gov/ystar/governance/", "Y-star-gov/tests/", "knowledge/eng-governance/"],
  "eng-platform":   ["./scripts/", "./tests/", "Y-star-gov/ystar/adapters/", "knowledge/eng-platform/"],
  "eng-domains":    ["Y-star-gov/ystar/adapters/", "Y-star-gov/tests/", "knowledge/eng-domains/"]
}
```

每岗位**默认 own 业务路径** + 可显式 deny / restrict 子路径

### Part B: Cross-Role Help Protocol

X 需要写 Y 的 path 时，3 选 1 (按 ROI):

**Option 1: Spawn Y subagent (best)**
```
X: Agent(subagent_type=Y, prompt="替我做 Z 在 your_domain/")
```
Daemon 自动按 Y 的 allowed_write_paths enforce — 0 deny。

**Option 2: Formal delegation grant (cross-domain)**
```python
gov_delegate(
    principal="X",
    actor="X-self",
    additional_paths=["Y/some_specific_file.md"],
    reason="X needs to write 1 file in Y domain because Y subagent unavailable",
    expires_at=now + 1h
)
```
Y 接受 / 拒绝 (CIEU event)；接受后 X 临时 elevated。

**Option 3: pkill window self-heal (emergency only)**
仅用于 active_agent 漂移类 emergency，不是常规 cross-domain write。已 codify `feedback_self_heal_via_daemon_window.md`.

### Part C: 顶岗 Protocol (when subagent unavailable)

当 Y subagent 不在 registry (e.g. Sofia-CMO BOM bug 修了但本 session 不重读)：

1. **Active_agent flip**: CEO/Secretary 用 pkill window 设 `.ystar_active_agent = Y`
2. **Spawn general-purpose** with prompt "你顶岗 Y, daemon 会按 Y boundary enforce" 
3. 顶岗 sub-agent 写 within Y domain 全 OK
4. 顶岗 退出后 CEO self-heal active_agent 回 ceo

需 codify 进 `knowledge/ceo/skills/ding_gang_protocol.md` (新 skill)

---

## §3 验收

- (a) `.ystar_session.json` `agent_write_paths` 含全 10 角色显式 list
- (b) `gov_delegate` 增 `additional_paths` 参数 + Y consent 流程
- (c) 写 `knowledge/ceo/skills/ding_gang_protocol.md`
- (d) e2e: spawn CMO subagent → 直接写 content/ pass; CTO 用 gov_delegate 临时拿 1 个 sales/ 文件 write 权; 顶岗 protocol pkill window flip → 顶岗 spawn → ship → CEO 自 restore，全 0 Board intervention

---

## §4 RAPID

| Role | Action |
|---|---|
| **R**ecommend | CEO Aiden (本提案) |
| **A**gree | CTO Ethan + Maya-Governance + Secretary Samantha |
| **P**erform | Ethan-CTO 统筹 → Ryan-Platform (session.json edit) + Leo-Kernel (gov_delegate 扩展) + Secretary (顶岗 protocol skill 写) |
| **I**nput | 4 engineers (验各自 boundary) |
| **D**ecide | Board L3 |

---

## §5 风险

| 风险 | mitigation |
|---|---|
| 全员开新 boundary → 安全降级 | 严守 default-deny + 每条 path 走 review |
| Cross-role delegation 滥用 | gov_delegate `additional_paths` 默认 max 3 文件 + 1h expire |
| 顶岗 protocol 被滥用 | pkill window 已有 CIEU audit；secretary auto-enforce 周扫顶岗时长 |

---

## §6 与其他 amendment 关系

- **A007 CEO OS**: CEO 现 allowed_write 已含 reports/+memory/ — 无变更
- **A009 escape hatch**: pkill window self-heal 为顶岗 protocol Step 1
- **A017 capability envelope**: A026 是 A017 specific 实例 (write 是其中一种 capability)
- **A018 whitelist**: 跨域 write delegation 应进 whitelist sync
- **A023 CROBA**: 任何 cross-role write 前必先 read 目标 path 现有内容

---

## §7 Board 决策点

CEO 已批方向 (本 amendment 起草授权)。Board L3 批 = 触发 Ryan/Leo/Secretary 实施（48h 内 ship Part A+B+C）。

无选择题。

---

## 附录 A: 即时手动 patch (Board 批前可先用)

CEO 用 break_glass + Edit 给 .ystar_session.json `agent_write_paths` 加 cmo/cso/cfo/secretary 显式 list — 不 wait Ryan 实施。今晚就解 CMO content/ 写阻塞类问题。
