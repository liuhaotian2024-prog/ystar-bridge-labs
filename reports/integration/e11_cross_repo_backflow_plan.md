# E11 Cross-Repo Backflow Plan

No Y-star-gov, gov-mcp, or ystar-company source files were modified in E11. The evidence-backed approach is to stabilize bridge-labs routers first, then backflow deterministic policy/tool exposure in a separate repo-specific milestone.

## Y-star-gov Candidates
- Add `ystar/domains/company_runtime/target_lifecycle_policy.py` mirroring discovered/proposed/approved/preflighted/executed/feedback/suppressed lifecycle semantics.
- Add tests under `tests/domains/company_runtime/` proving proposed targets cannot authorize contact.
- Add evidence/signal ladder policy distinguishing public evidence, validation feedback, paid signal, and governance evidence.
- Add closure status family semantics for discovery, validation, paid-signal, revenue-loop, repository delivery, blocked, and residual states.

## gov-mcp Candidates
- Add gateway tools for target lifecycle preflight, evidence claim validation, action authorization chain inspection, and no-contact assurance.
- Add tests under `tests/test_company_runtime_tools.py` for proposed-target blocking and Y-star-gov decision references.
- Expose normalized manifests through gateway checks without treating proposals as approvals.

## ystar-company Candidates
- Treat scheduler, commercial-loop, public research, approval packet, and field-functional assets as incubation references.
- Do not backflow dirty runtime artifacts, private logs, DB/WAL/SHM, or active-agent markers.
- Mine reusable patterns in a future E-series backflow after formal policy tests exist.

## Exact Future Backflow Order
1. Y-star-gov deterministic lifecycle/evidence/action/closure policies and tests.
2. gov-mcp gateway/preflight tools that expose the Y-star-gov decisions.
3. bridge-labs adapter updates to call formal repo APIs instead of local mirror semantics.
4. ystar-company incubation harvest only after private-runtime quarantine is respected.
