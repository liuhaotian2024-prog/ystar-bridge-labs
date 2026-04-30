# L7.0Q2 Full Repository Conservatism Scan

This scan used tracked files from `git ls-files` and skipped DB/WAL/SHM/log/active-agent/env/secret/binary surfaces.

## Core Principle

Maximize discovery and useful commercial planning. Minimize owner manual burden. Block unapproved external side effects. Block unreviewed permanent writeback.

## Summary

- Total tracked files scanned: 42041
- Total text files scanned: 41019
- Total findings: 127905
- Harmful overconservatism count: 69439
- Legitimate hard boundary count: 56209
- Files needing policy_ref migration: 38342
- Policy coverage: 1.78%

## Top Owner Burden Findings
- `ceo_command_brief/l6_16_ceo_command_brief.json:68` ask_user_url: "ask_user_url"
- `ceo_command_brief/l6_16_ceo_command_brief.json:84` manual URL: "A seed URL/manual URL request path.",
- `ceo_command_brief/l6_16_ceo_command_brief.md:47` manual URL: - A seed URL/manual URL request path.
- `controlled_no_action_receipts/no_action_receipt_index.json:29` ask_user_url: "controlled_no_action_receipts/no_ask_user_url_receipt.json",
- `controlled_no_action_receipts/no_ask_user_url_receipt.json:3` ask_user_url: "action": "ask_user_url",
- `controlled_no_action_receipts/no_ask_user_url_receipt.json:7` ask_user_url: "receipt": "no_ask_user_url"
- `controlled_no_action_receipts/no_side_effect_receipt.json:30` ask_user_url: "controlled_no_action_receipts/no_ask_user_url_receipt.json"
- `decision_boundary_packet/decision_boundary_packet.json:43` ask_user_url: "ask_user_url"
- `docs/l6_13_real_backend_activation.md:3` manual URL: L6.13 does not ask for manual URLs. It activates real public read-only observation only when an approved backend and page-read adapter are configured by environment.
- `internal_strategy_memo/l6_16_internal_strategy_memo.json:101` ask_user_url: "ask_user_url"
- `internal_strategy_memo/l6_16_internal_strategy_memo.md:61` ask_user_url: - ask_user_url
- `l6_10v_read_model/l6_10v_blockers.json:9` reviewed seed locator: "Add one reviewed seed locator entry to seed_locator_registry/reviewed_seed_locator_registry.json, or",
- `l6_10v_read_model/l6_10v_cieu_like_fixture.json:7` reviewed seed locator: "U_t": "Create reviewed seed locator and explicit controlled search enablement paths for one work order.",
- `l6_10v_read_model/l6_10v_cieu_like_fixture.json:18` reviewed seed locator: "reviewed seed locator still required",
- `l6_10v_read_model/l6_10v_next_milestone_recommendation.json:3` reviewed seed locator: "next_milestone": "L6.10W Reviewed Seed Locator Population or Controlled Search Backend Enablement v0",
- `l6_10v_read_model/l6_10v_read_model_summary.json:79` reviewed seed locator: "Add one reviewed seed locator entry to seed_locator_registry/reviewed_seed_locator_registry.json, or",
- `l6_10v_read_model/l6_10v_readiness_assessment.json:16` reviewed seed locator: "next_step": "reviewed seed locator required or explicit controlled search resolver enablement required",
- `l6_10v_read_model/l6_10v_readiness_assessment.json:17` reviewed seed locator: "next_recommended_milestone": "L6.10W Reviewed Seed Locator Population or Controlled Search Backend Enablement v0",
- `l6_10w_read_model/l6_10w_blockers.json:3` user_must_provide: "primary_blocker": "user_must_provide_one_reviewed_seed_locator_url",
- `l6_10w_read_model/l6_10w_blockers.json:5` user_must_provide: "user_must_provide_one_reviewed_seed_locator_url"
