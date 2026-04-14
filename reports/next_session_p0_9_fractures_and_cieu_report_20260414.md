# NEXT SESSION P0 — 9 断裂修 + CIEU 工作法 codify + 首战 report

**Priority**: P0 — next session 第一 item
**Dispatch via**: Ethan-CTO → Leo/Maya/Ryan per 断裂域 (Path B-lite)
**Triggered by**: 顾问 2026-04-14 全系统审计 catch 9 断裂 + Board 创 CIEU 工作法后 codify enforcement gap

---

## Y\* (11 criteria, all ✓ = Rt+1=0)

### A. 9 断裂修 (Y*-1 to Y*-9)

1. **P0-A** `gov_mcp/health.py` 存在, `from gov_mcp.health import compute_health_score` OK
2. **P0-B** `scripts/hook_session_start.py` 调 `session_boot_yml.py` + session-close hook 调 `session_close_yml.py`
3. **P1-C** `hook.py` / `server.py` 调 `ystar.memory.ingest.enqueue()` on CIEU event (桥通)
4. **P1-D** `.claude/agents/ceo.md` 加 "dispatch 前必先 gov_dispatch" + ForgetGuard `ceo_skip_gov_dispatch`
5. **P1-E** `memory/session_handoff*.md` + `continuation*.md` + `wisdom_package*.md` 迁 YML + archive
6. **P1-F** `labs_router.py` 硬编码 `ystar-company` → `os.environ.get('YSTAR_LABS_DIR')`
7. **P2-G** `wire_integrity_check.py` cron hourly + emit `WIRE_BROKEN` CIEU
8. **P2-H** Verify `twin_evolution.py` YML write 真生效 via `gov_memory_summary` lesson count
9. **P2-I** `AGENTS.md` 加 "Memory & Continuity Systems" 章节列 LRS / twin / wisdom / working_memory_snapshot / YML

### B. CIEU 工作法 codify + report (Y*-10 to Y*-11)

10. **P0-J** `WORKING_STYLE.md` 加第十二条 "CIEU 任务工作法" (Y\*/Xt/U/Rt+1 格式强制) + ForgetGuard `task_dispatch_without_y_star`
11. **CIEU 首战 report** `reports/experiments/exp_cieu_5tuple_first_battle_20260414.md` (classical 7-section: Abstract / Background / Method / Evidence / Reproducible code / Discussion / Conclusion)

---

## Xt (baseline at next session boot)

(列 断裂当前状态, 见 Y\* 各项的 "未修" 条件)

---

## U dispatch sequence (Ethan-CTO orchestrate Path B-lite, 总 ~4h)

- U1 Leo-Kernel: 修 P0-A health.py (≤30min)
- U2 Ryan-Platform: 修 P0-B YML boot/close hook (≤30min)
- U3 Maya-Governance: 修 P1-C CIEU→YML bridge + P1-E 迁 handoff (≤60min)
- U4 Maya: 修 P1-D ceo.md + P0-J ForgetGuard (≤30min)
- U5 Leo: 修 P1-F env-var (≤30min)
- U6 Ryan: 修 P2-G wire_integrity cron (≤15min)
- U7 Maya: 修 P2-H twin_evolution verify (≤20min)
- U8 CEO break_glass: 修 P2-I AGENTS.md + 第十二条 (≤10min)
- U9 Ethan-CTO: 写 Y*-11 CIEU 首战 report (≤60min)
- U10 CEO final Rt+1 verification + commit + push + priority_brief v0.9

## CIEU 循环硬约束

每 U 后强制 print `[Rt+1 CHECK] Y*-N: [✓/✗]` × 11 + `Rt+1 = N/11` . 禁止 "done" 未 Rt+1=0.

## Evidence for Y*-11 (CIEU 首战 report 内容 outline)

- Y\* (YML last-mile 7): scripts 2 + STEP 8.7 + cron + E2E + commit/push + priority_brief
- Xt: YML lib ✓ gov-mcp 6 tool ✓ _State ✓ 但 entry/exit 0
- U1-U7 Ryan-Platform dispatch + truncate
- U8-U12 CEO takeover finish (cron install / E2E run / commit / priority_brief)
- Final Rt+1=0 verified (commits 80e723f + 6508275)
- Lessons: sub-agent truncate 后 CEO 可接手不丢 context (因 Y\* 明确); Rt+1 pattern 替代 self-claim
- Product positioning: CIEU 工作法 **itself is Y\*gov USP** — structured task accountability 无 prior art in classical MAS / LangChain / AutoGen

---

## Triple-redundancy

此文件位于 `reports/` (git tracked, CEO allowed write). Auto-mirror via 5min + 10min crons. Push GitHub 次次重试自恢复.
