# E27 Live Readiness Validator V2

- dry_run_ready: True
- sandbox_ready: True
- live_test_gate_ready: True
- production_live_ready: False
- production_blockers: production_live_enabled_false, production_credentials_absent_by_design, production_persistent_idempotency_not_configured, production_kill_switch_default_block, production_live_tests_not_configured
