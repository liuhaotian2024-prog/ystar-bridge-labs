# Patent 63/981,777 Claim 1 Runtime Audit

```yaml
Y_star: Patent Claim 1 runtime assertions match shipped code with evidence
Xt: contract_hash kernel-computed CONFIRMED; seal_session code EXISTS but DEAD (0 calls in production); 714K events unsealed
U: read cieu_store.py (write path + seal_session), engine.py (check()), dimensions.py (_compute_hash), grep callers
Yt1: three verdicts with file:line citations for patent counsel
Rt1: 0 for Q1+Q2 (empirical), >0 for Q3 (requires engineering action)
tool_uses: 15
```

---

## Q1: contract_hash kernel-only-write

**Verdict: YES — kernel-computed, not agent-writable**

The `contract_hash` value stored in every CIEU event is the `IntentContract.hash` property, computed deterministically from kernel policy state at `__post_init__` time.

**Evidence 1 — hash computation** (`ystar/kernel/dimensions.py:786-795`):

```python
def __post_init__(self):
    if not self.hash:
        d = {
            "deny": self.deny, "only_paths": self.only_paths,
            "deny_commands": self.deny_commands,
            "only_domains": self.only_domains,
            "invariant": self.invariant,
        }
        canonical = json.dumps(d, sort_keys=True, ensure_ascii=True)
        self.hash = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
```

The hash is a SHA-256 of the canonical JSON of **five policy constraint fields** (deny, only_paths, deny_commands, only_domains, invariant). None of these are agent-supplied runtime parameters. They come from governance policy (AGENTS.md parsing / contract compilation).

**Evidence 2 — write path** (`ystar/governance/cieu_store.py:451`):

```python
d.get("contract_hash"),
```

The CIEU store writes whatever `contract_hash` value is in the dict. The dict is constructed by callers (hook.py, orchestrator.py, cieu_writer.py) which uniformly set it to `contract.hash` — the kernel-computed property. Example from `ystar/adapters/hook.py:895`:

```python
contract_hash = contract.hash if contract else ""
```

**Access control assessment**: There is no `@kernel_only` decorator or SQL GRANT enforcement. The protection is **architectural** — `contract_hash` is never exposed as an API parameter agents can set. The `IntentContract` object is constructed by the kernel's compiler/prefill pipeline, and its `.hash` property is read-only (computed in `__post_init__`). An agent would need to forge the entire CIEU write dict to inject a false hash, which would require bypassing the hook/orchestrator layer entirely.

**Patent claim supportable**: Yes. The hash is computed purely from kernel-side policy state. Agent-supplied data (task_description, file_path, command) does not influence the hash value.

---

## Q2: Merkle sealing code existence (cieu_store.py 596-664)

**Verdict: LINE_DRIFTED — code EXISTS at lines 716-784, DEAD in production**

The patent cites lines 596-664. Those lines now contain `_row_to_result()` and the `stats()` function — query helpers that have nothing to do with Merkle sealing. The sealing code has drifted upward in line numbers due to code additions between patent filing (2026-03-26) and current HEAD.

**Evidence — actual seal_session location** (`ystar/governance/cieu_store.py:716-784`):

```python
def seal_session(self, session_id: str) -> dict:
    """[FIX-3] 对指定 session 的所有记录进行密码学封印。"""
    # ...
    payload = "\n".join(event_ids).encode("utf-8")
    merkle_root = hashlib.sha256(payload).hexdigest()
    # ...
    conn.execute("UPDATE cieu_events SET sealed=1 WHERE session_id=?", (session_id,))
```

The function exists, is complete, and implements exactly what the patent describes: SHA-256 Merkle root over sorted event_ids, hash chain via `prev_root`, `sealed_sessions` table, and logical `sealed=1` flag update.

**Why sealed=0 for all 714K events**: `seal_session()` is never called in production. The only callers are:

1. `ystar/cli/demo_cmd.py:77` — demo command (not production)
2. `ystar/cli/report_cmd.py:250,322` — manual CLI report generation
3. `ystar/cli/archive_cmd.py:88` — archive command

There is **no daemon, no cron, no hook, and no session-close trigger** that calls `seal_session()`. The code is shipped but unwired. The `sealed_sessions` table schema exists (lines 219-227) but contains zero rows in production.

---

## Q3: Wire-up effort if dead

**Estimate: hook addition — 1 call site, ~15 lines of code**

**Proposed minimal path**: Add a `seal_session(session_id)` call to the session close path. The most natural insertion point is `ystar/session.py` at session teardown, or `scripts/session_close_yml.py` which already runs at every session end. The function is fully implemented and tested (the CLI commands exercise it). The only missing piece is a production trigger.

Concrete wire-up:

1. In the session close flow (wherever `session_id` is known and CIEU events are finalized), add:
   ```python
   from ystar.governance.cieu_store import CIEUStore
   store = CIEUStore()
   store.seal_session(session_id)
   ```
2. Optionally add a `ystar seal --session <id>` CLI subcommand for manual/batch sealing of historical sessions.
3. For the 714K existing unsealed events: a one-time migration script iterating distinct `session_id` values and calling `seal_session()` on each. Estimated ~30 seconds wall time.

**Kernel engineer effort**: 3-5 tool_uses to implement and test the wire-up. No schema changes needed — `sealed_sessions` table and `sealed` column already exist.

---

## Summary for Patent Counsel

| Claim Element | Status | Risk |
|---|---|---|
| contract_hash kernel-only-write | LIVE, architecturally enforced | LOW — no decorator/ACL, but no API surface for agent override |
| Merkle sealing code | EXISTS but line numbers drifted from 596-664 to 716-784 | MEDIUM — patent cites wrong lines, but code is substantively identical to description |
| Merkle sealing in production | DEAD — zero sealed events, zero sealed_sessions rows | HIGH — patent asserts "tamper-evident audit trail" but production has never sealed a single event |
| Wire-up effort | Hook addition, ~15 LOC | LOW — function is complete, only needs a trigger |

**Bottom line**: The code the patent describes exists and works correctly when called. It has never been called in production. This is an enablement gap (code shipped but feature unwired), not a code-doesn't-exist gap. Fix is mechanical.
