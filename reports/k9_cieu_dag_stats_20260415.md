# K9 CausalChainAnalyzer on CIEU (2026-04-15 2h 窗口)

## DAG
- Nodes: 645
- Edges: 644

## 事件类型分布 (top 15)
-  436 × `MIRROR_SYNC`
-   30 × `HOOK_BOOT`
-   17 × `BEHAVIOR_RULE_VIOLATION`
-   15 × `Bash`
-   13 × `omission_setup_complete`
-   13 × `cmd_exec`
-   13 × `intervention_gate:deny`
-   13 × `governance_coverage_scan`
-   13 × `circuit_breaker_armed`
-   13 × `orchestration:governance_loop_cycle`
-   13 × `handoff`
-   13 × `orchestration:path_a_cycle`
-   13 × ``
-   13 × `orchestration:path_b_cycle`
-   13 × `external_observation`

## Agent 分布 (top 10)
-  436 × `ryan-platform`
-   86 × `agent`
-   39 × `orchestrator`
-   26 × ``
-   13 × `intervention_engine`
-   13 × `path_a_agent`
-   11 × `a36e4eab715fd6f73`
-    8 × `-Users-haotianliu--openclaw-workspace-ystar-company`
-    6 × `ac48ccf2bd50e73ac`
-    5 × `a97e31c1bb2bb8e7f`

## DRIFT events: 0

## K9 find_root_causes schema mismatch (P1 bug)
K9 causal_analyzer.py:243 expects violations[i].get('severity', 0) where violations is list of dicts.
我们 CIEU 导出 violations 是 JSON string (per cieu_events.violations column). 需要先 parse.
**Bug for K9 maintainer**: `_identify_root_causes` 未处理 str-typed violations column.
