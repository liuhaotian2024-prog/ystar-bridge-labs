# CZL 核心 Rule 落地审计 — 2026-04-15 PM

**Auditor**: Samantha (Secretary) | **Trigger**: Board 午后质询 U4 交付 prose-claim 嫌疑
**Scope**: `ceo_skip_gov_dispatch` / `task_dispatch_without_y_star` / `ceo_direct_engineer_dispatch`

## CIEU 5-tuple [L3]

- **Y\***: 三 rule 在正确 yaml 落地 + mode=deny + commit 铁证
- **Xt**: Board PM grep 的是 `ystar-company/governance/forget_guard_rules.yaml`（AMENDMENT-020 schema），非 Y\*gov 产品侧
- **U**: grep × 3 repo + git log + 定位 runtime 读取路径
- **Yt+1**: 状态判定 + IMMUTABLE-DRIFT-20260415-002 立档（若需）+ AGENTS.md 过时声明修正
- **Rt+1**: 0 (审计类) 当报告落盘 + 修复建议明确

## 判定结论 [L3]

**三条 rule 全部 EXIST, mode=deny, 未 drift** — U4 报告属实,Board 前提错（grep 错文件）。

### 证据

| rule | 位置 | 行 | mode | created_at | ship commit |
|---|---|---|---|---|---|
| `ceo_direct_engineer_dispatch` | `Y-star-gov/ystar/governance/forget_guard_rules.yaml` | 5 | deny | 2026-04-13T16:30Z | `41e66c8` (04-13 22:25 EDT) |
| `ceo_skip_gov_dispatch` | 同上 | 13 | deny | 2026-04-15T14:00Z | `a153132` (04-15 15:32 EDT) |
| `task_dispatch_without_y_star` | 同上 | 21 | deny (dry_run until 2026-04-22) | 2026-04-15T14:00Z | `a153132` |

### Runtime 路径验证

`Y-star-gov/ystar/governance/forget_guard.py:44`:
```python
rules_path = Path(__file__).parent / "forget_guard_rules.yaml"
```
→ engine 只读产品侧 yaml，三条 rule 在其中 → **Layer 3 enforcing 实际生效**。

### Board grep 错位解释

Board PM grep 的 `ystar-company/governance/forget_guard_rules.yaml` 是 **AMENDMENT-020 institutional memory** 实例（`schema_version: 1.0, default_action: warn`），不是 CZL dispatch gate 的运行时 yaml。两套 ForgetGuard 系统并存、不同 schema、不同 engine、不同目的。

## AGENTS.md 过时声明 [L2]

`AGENTS.md:443` 声明"ceo_skip_gov_dispatch / task_dispatch_without_y_star / ceo_direct_engineer_dispatch — **Layer 1 缺失**（U4 声称加了但 grep 查不到）" — 此声明写时未区分两 yaml，**已过时**，建议 CEO 下令修正为:

> 三条 rule 均在 `Y-star-gov/ystar/governance/forget_guard_rules.yaml` 落地 mode=deny（见 `reports/secretary/czl_core_rules_drift_audit_20260415.md`）。Layer 1 缺失项应改列：CIEU 5-tuple 未在 AGENTS.md 文档化 + Iron Rule 1.6 索引缺失。

`knowledge/shared/czl_persistence_covenant.md:52` 同样列"forget_guard_rules.yaml 不含 `ceo_skip_gov_dispatch` rule" — 过时，需同步订正。

## IMMUTABLE-DRIFT Ticket [L3]

**无需开 ticket**。U4 交付非 prose-claim，rule 确已 ship (`a153132`)。但需订正两处文档误导（AGENTS.md:443, czl_persistence_covenant.md:52）— 属 doc sync，不属 drift。

## 修复建议 [L3]

1. **CEO**: 更新 `AGENTS.md:443` 与 `knowledge/shared/czl_persistence_covenant.md:52`（Samantha 可执行 — 有 knowledge/ 写权，AGENTS.md 需 Board 明示）
2. **Maya**: 无 action（rule 已落地）
3. **Platform eng**: 考虑在 `wire_integrity_check.py` 加双 yaml 区分断言,防止未来 grep 错位重演
4. **Board 认知校准**: 以后 grep CZL rule 走 `Y-star-gov/ystar/governance/forget_guard_rules.yaml`，不是 company 侧

## Rt+1 Judgment [L3]

Rt+1 = 0 ✅ — 报告落盘、三 rule 状态铁证判定（均 EXIST+DENY）、过时文档定位、修复建议明确、无需 IMMUTABLE-DRIFT ticket。
