# Goal 4 Demonstrator — Y*gov Module Liveness (CEO_ENGINEERING_OVERRIDE 2026-04-18)
Generated: 2026-04-18T20:40:28

**Summary**: scanned=150 LIVE=91 (60.7%) DORMANT=46 DEAD=13

## Top DEAD candidates (archive for Strangler Fig)

| module | callers | fires_30d |
|---|---|---|
| `ystar.dev_cli` | 0 | 0 |
| `ystar.cli.archive_cmd` | 0 | 0 |
| `ystar.cli.quality_cmd` | 0 | 0 |
| `ystar.path_b.external_governance_loop` | 0 | 0 |
| `ystar.pretrain.synthesize_obligations` | 0 | 0 |
| `ystar.governance.ml_registry` | 0 | 0 |
| `ystar.governance.ml_discovery` | 0 | 0 |
| `ystar.governance.ml_core` | 0 | 0 |
| `ystar.governance.ml_semantic` | 0 | 0 |
| `ystar.governance.ml_loop` | 0 | 0 |
| `ystar.governance.omission_scheduler` | 0 | 1 |
| `ystar.governance.claim_mismatch` | 0 | 0 |
| `ystar.governance.ml_adaptive` | 0 | 0 |

## LIVE modules (sample)

| module | callers | fires_7d |
|---|---|---|
| `ystar._hook_server` | 0 | 2 |
| `ystar._whitelist_emit` | 0 | 12 |
| `ystar._cli` | 12 | 353 |
| `ystar.session` | 83 | 19503 |
| `ystar.capabilities` | 4 | 5 |
| `ystar.template` | 18 | 329 |
| `ystar._hook_entry` | 0 | 3 |
| `ystar._hook_daemon` | 1 | 110 |
| `ystar.__main__` | 19 | 388 |
| `ystar.domains.openclaw.adapter` | 54 | 217 |
| `ystar.domains.finance.config` | 54 | 15492 |
| `ystar.domains.finance.adapters` | 35 | 205 |
| `ystar.memory.store` | 70 | 13292 |
| `ystar.memory.ingest` | 17 | 14 |
| `ystar.memory.models` | 30 | 24 |
| `ystar.memory.decay` | 6 | 4 |
| `ystar.cli.safemode_cmd` | 1 | 3 |
| `ystar.integrations.simulation` | 12 | 5 |
| `ystar.integrations.runner` | 4 | 9 |
| `ystar.integrations.base` | 82 | 227 |
