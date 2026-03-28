# Technical Debt Tracker — Y*gov

*Updated weekly by CTO. High-priority items submitted to Board for approval before fixing.*

## Priority: HIGH (Submit to Board)

| # | Debt | Impact | Est. Hours | File | Status |
|---|------|--------|-----------|------|--------|
| 1 | hooks.json uses `python3` — fails on Windows (MS Store stub) | Blocks Windows users | 2h | Y-star-gov/skill/hooks/hooks.json | Open |
| 2 | Silent exception swallowing in hook.py (lines 223, 454, 459) | Masks real errors from users | 4h | Y-star-gov/ystar/adapters/hook.py | Open |
| 3 | Two main() functions in _cli.py | Code smell, confusing entrypoint | 3h | Y-star-gov/ystar/_cli.py | Open |
| 4 | README still references some outdated commands | Confuses new users | 1h | Y-star-gov/README.md | Open |

## Priority: MEDIUM (CTO discretion)

| # | Debt | Impact | Est. Hours | File |
|---|------|--------|-----------|------|
| 5 | CIEU DB path hardcoded to current directory | Fragments audit history across projects | 3h | cieu_store.py:42 |
| 6 | No cleanup policy for sealed CIEU sessions | Unbounded DB growth | 4h | cieu_store.py |
| 7 | Thread-unsafe global state in engine.py and hook.py | Not safe for multi-threaded use | 3h | engine.py:103, hook.py:358 |
| 8 | Runtime monkey-patching in hook.py | Hard to debug, breaks static analysis | 2h | hook.py:439-454 |

## Priority: LOW (Track only)

| # | Debt | Impact | File |
|---|------|--------|------|
| 9 | No CLI tests (only core + integration tests) | CLI bugs go undetected | _cli.py |
| 10 | No caching in nl_to_contract.py | Same AGENTS.md re-translated every init | nl_to_contract.py |

## Last Updated: 2026-03-28
