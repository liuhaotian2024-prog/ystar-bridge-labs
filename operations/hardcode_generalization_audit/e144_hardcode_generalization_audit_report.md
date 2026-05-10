# E144 Hardcode Generalization Audit

This audit treats hardcoded intelligence as a class-level system risk, not a one-off x402/meeting-room bug.

## Coverage
- scanned_files: 364513
- runtime_files: 11409
- skipped_large_files: 737
- finding_count: 13530
- critical_or_high_count: 2018

## Counts By Repo
- Y-star-gov: 104
- bridge-labs: 1216
- codex-local: 12207
- gov-mcp: 3

## Counts By Type
- fixture_or_snapshot_runtime_risk: 5858
- issue_specific_literal: 1072
- keyword_router_branch: 1020
- machine_receipt_rendered_to_owner: 377
- static_route_menu: 5203

## Direct Runtime Fixes
- Replaced aiden_meeting_room keyword intent chain with feature-scored intent profiles.
- Replaced answer_owner fixed handler map with dynamic repo-evidence/action-packet answer builder.
- Added owner-facing generalization gate for machine receipts, point-fix next-step loops, process-over-content, and issue-specific leakage.
- Moved strategy receipt proof behind content-first Chinese explanation in messenger policy.

## Top Runtime Findings
- bridge-labs:office/mission_command/e111_aiden_host_runtime_and_autonomy_control_plane.py:503 [machine_receipt_rendered_to_owner/high] f"- CIEU events: {report['CIEUStore_summary']['event_count']}\n\n"
- bridge-labs:office/mission_command/e61_live_public_read_core.py:227 [keyword_router_branch/high] if isinstance(reason, socket.gaierror) or "name or service" in text or "nodename" in text or "temporary failure in name resolution" in text:
- bridge-labs:office/mission_command/e7_evidence_quality.py:59 [keyword_router_branch/high] if any(token in lower for token in ['"@context"', '"featureflags"', '{"', '":']):
- bridge-labs:office/mission_command/e18_batch_target_selection.py:67 [keyword_router_branch/high] if role in {"primary", "fallback"} and any(term in text for term in fit_terms):
- bridge-labs:office/mission_command/e126_adaptive_retrieval_planner_runtime.py:510 [machine_receipt_rendered_to_owner/high] f"- CIEU events: {result['CIEUStore_summary']['event_count']}",
- bridge-labs:office/mission_command/e65_market_dynamics_model.py:182 [keyword_router_branch/high] if any(term in text for term in terms):
- bridge-labs:office/mission_command/c2_ygov_action_decision.py:87 [keyword_router_branch/high] if any(gate in text or gate.replace("_", " ") in text for gate in HARD_GATES):
- bridge-labs:office/mission_command/e112_cieu_backed_brain_learning_loop.py:715 [keyword_router_branch/high] if any(term in text for term in ("competitor", "competition", "alternative", "substitute", "incumbent")):
- bridge-labs:office/mission_command/e112_cieu_backed_brain_learning_loop.py:717 [keyword_router_branch/high] if any(term in text for term in ("fail", "risk", "crowded", "trust", "regulation", "friction")):
- bridge-labs:office/mission_command/e112_cieu_backed_brain_learning_loop.py:756 [keyword_router_branch/high] if any(term in text for term in ("competitor", "competition", "alternative", "substitute", "incumbent")):
- bridge-labs:office/mission_command/e112_cieu_backed_brain_learning_loop.py:758 [keyword_router_branch/high] if any(term in text for term in ("standard", "regulation", "law", "compliance")):
- bridge-labs:office/mission_command/e112_cieu_backed_brain_learning_loop.py:100 [keyword_router_branch/high] elif any(term in text for term in ("competitor", "competition", "alternative", "substitute", "incumbent")):
- bridge-labs:office/mission_command/e112_cieu_backed_brain_learning_loop.py:102 [keyword_router_branch/high] elif any(
- bridge-labs:office/mission_command/e91_open_world_doctrine_discovery.py:696 [keyword_router_branch/high] if any(term in doctrine_id for term in ("owner_decision", "revenue", "payment", "customer")):
- bridge-labs:office/mission_command/e108_live_global_open_world_strategy_runtime.py:836 [keyword_router_branch/high] if any(term in text for term in ["healthcare", "insurance", "legal", "tax"]):
- bridge-labs:office/mission_command/e108_live_global_open_world_strategy_runtime.py:227 [issue_specific_literal/high] _domain("ai_security_compliance", "AI security, compliance, and audit readiness", False, ["AI security compliance gap buying urgency 2026", "AI audit readiness evidence pack buyers"]),
- bridge-labs:office/mission_command/e108_live_global_open_world_strategy_runtime.py:683 [issue_specific_literal/high] "cpa_tax_accounting_first_cash_pack",
- bridge-labs:office/mission_command/e68_cieu_route_evaluation_model.py:188 [keyword_router_branch/high] if any(term.lower() in (rel + "\n" + text).lower() for term in terms):
- bridge-labs:office/mission_command/e110_labs_universal_operating_control_plane.py:123 [keyword_router_branch/high] if any(term in text for term in strategy_terms):
- bridge-labs:office/mission_command/e97_unanchored_global_strategy_rerun.py:515 [machine_receipt_rendered_to_owner/high] f"- CIEU events: `{receipt['CIEU_event_count']}`",
- bridge-labs:office/mission_command/e19_ecosystem_alignment_scanner.py:64 [keyword_router_branch/high] if any(keyword.lower() in text for keyword in keywords):
- bridge-labs:office/mission_command/e113_no_new_wheel_runtime_law.py:362 [keyword_router_branch/high] if any(str(keyword).lower() in text for keyword in domain["keywords"]):
- bridge-labs:office/mission_command/e123_aiden_model_orchestration_runtime.py:207 [keyword_router_branch/high] if any(term in text for term in ["governance", "validator", "contract", "治理", "验证"]):
- bridge-labs:office/mission_command/e123_aiden_model_orchestration_runtime.py:209 [keyword_router_branch/high] if any(term in text for term in ["implement", "code", "test", "repo", "commit", "实现", "代码", "测试"]):
- bridge-labs:office/mission_command/e123_aiden_model_orchestration_runtime.py:211 [keyword_router_branch/high] if any(term in text for term in ["strategy", "market", "revenue", "competitor", "赚钱", "战略", "市场", "竞品"]):
- bridge-labs:office/mission_command/e123_aiden_model_orchestration_runtime.py:213 [keyword_router_branch/high] if any(term in text for term in ["model", "gemma", "gpt", "claude", "orchestration", "模型", "调度"]):
- bridge-labs:office/mission_command/e96_ceo_controlled_capability_control_plane.py:747 [keyword_router_branch/high] if _contains_any(text, ("owner must", "owner decision", "manual", "approve")):
- bridge-labs:office/mission_command/resource_capability_matrix.py:281 [keyword_router_branch/high] if any(key in normalized for key in ["contact", "customer", "email", "message"]):
- bridge-labs:office/mission_command/e94_behavior_center_runtime_gateway.py:118 [keyword_router_branch/high] if any(term in text for term in HIGH_RISK_TERMS):
- bridge-labs:office/mission_command/e94_behavior_center_runtime_gateway.py:126 [keyword_router_branch/high] if any(term in text for term in PROVIDER_TERMS):

## Truth Boundary
- This does not claim every historical hardcoded string is removed.
- Tests, reports, generated snapshots, and historical artifacts are classified separately from runtime-active owner-facing code.
- The new gate prevents the most damaging class: machine receipt/template/point-fix answers being presented as CEO intelligence.
