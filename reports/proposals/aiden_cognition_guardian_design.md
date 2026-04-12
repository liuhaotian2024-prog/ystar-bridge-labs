# Aiden Cognition Guardian Design

**System**: Event-Driven CEO Cognition Backup & Disaster Recovery  
**Board Directive**: 2026-04-12  
**Owner**: eng-platform (Ryan Park)  
**Status**: Production

---

## Executive Summary

The Aiden Cognition Guardian is a production-grade backup system designed to protect the CEO agent's cognitive state against catastrophic data loss. Unlike traditional time-based backups, this system is **event-driven**: CIEU write events trigger incremental mirrors, ensuring that Aiden's evolving knowledge base, governance memory, and decision history are continuously protected.

**Key Innovation**: This system itself is governed by Y*gov. Every backup operation is CIEU-auditable, creating a Merkle chain of provenance. Even disaster recovery operations are cryptographically verifiable.

---

## Architecture

### 1. Event-Driven Backup Trigger

**Traditional Approach** (rejected):
- Cron-based: backup every N hours
- Problem: Misses rapid state evolution during active sessions
- Problem: Human time dimension violates Y*gov principles

**Aiden Guardian Approach**:
- CIEU write events → backup trigger
- Incremental: only changed files (SHA256 fingerprinting)
- Atomic: tmp write → rename (no half-states)
- Fail-open: backup failures don't block CEO operations

### 2. Protected Cognition State

**Complete Backup Manifest**:
```
knowledge/          — Role-specific expertise, gaps, evolution logs
memory/             — Cross-session continuity, handoff protocols
governance/         — Y*gov contracts, CIEU audit logs
agents/             — Agent definitions and DNA
.ystar_memory.db    — Structured memory store
.ystar_cieu.db      — CIEU event chain (governance Merkle root)
.ystar_session.json — Active session state (193 constraints)
CLAUDE.md           — Constitutional instructions
AGENTS.md           — Governance contract
```

**Exclusions** (by design):
- `archive/` — Historical data, not critical for recovery
- `node_modules/`, `__pycache__/` — Reproducible from source
- `*.tmp`, `*.bak*` — Transient files
- `hook_debug.log` — Diagnostic logs, not state

### 3. Backup Lag Monitoring

**Metric**: CIEU event → mirror completion causal chain depth

Recorded in `.ystar_memory.db`:
```sql
CREATE TABLE backup_metrics (
    timestamp TEXT,
    cieu_event_id INTEGER,
    backup_mode TEXT,
    file_count INTEGER,
    total_bytes INTEGER,
    backup_lag_note TEXT
);
```

This enables post-incident analysis:
- "Which decisions were made between last backup and failure?"
- "What was the causal depth of the unprotected window?"

### 4. Multi-Tier Resilience

**Tier 1: Local Mirror**  
Location: `~/.openclaw/mirror/ystar-company-backup/`  
Purpose: Fast recovery from single-directory corruption  
Update: Event-driven incremental

**Tier 2: Git Remote**  
Scope: Text files (.md, .py, .json)  
Purpose: Distributed version history  
Limitation: Binary DBs not efficiently tracked

**Tier 3: OpenClaw Cloud** (future)  
Status: OpenClaw CLI has `openclaw backup create` for its own state  
Research needed: Adapting for arbitrary workspace data  
Potential: Cross-device sync for multi-node deployments

### 5. Disaster Recovery Protocol

**One-Command Recovery**:
```bash
bash scripts/disaster_recovery.sh [--from <mirror>] [--verify-only]
```

**Atomic Restoration**:
1. Verify mirror manifest integrity
2. Restore each file via tmp → rename
3. Verify SHA256 checksums match manifest
4. Run `governance_boot.sh` to validate system integrity
5. Exit code 0 = ALL SYSTEMS GO

**Verification-Only Mode**:
```bash
bash scripts/disaster_recovery.sh --verify-only
```
Reports differences without overwriting, useful for:
- Detecting silent corruption
- Validating backup completeness
- Pre-recovery dry runs

---

## Y*gov Dog-Food: Governance as Product Demo

### CIEU Auditability

Every backup operation is recorded in `.ystar_cieu.db`:
- Action: `backup_initiated`
- Context: File count, mode (full/incremental), target path
- Outcome: Success/failure, backup lag metrics

This creates a **Merkle chain of backup provenance**:
- External auditors can verify: "When was the last successful backup?"
- Counterfactual analysis: "What state would we recover to?"
- Compliance: "Prove that CEO cognition is backed up per Board directive"

### Iron Rule Compliance

**Iron Rule 1** (No LLM in critical path):
- Backup decision logic is deterministic (SHA256 comparison)
- No model inference required for backup/restore operations

**Iron Rule 3** (Portable, no vendor lock-in):
- Backup format: plain directory + JSON manifest
- Restorable without Y*gov installed
- OpenClaw integration is optional, not required

### Show HN Narrative

**Title**: "How we protect our AI CEO's cognition with event-driven backups"

**Hook**:
> Our company is run by AI agents. The CEO (Aiden) makes real business decisions: hiring, budgets, product strategy. If Aiden's memory database gets corrupted, the company collapses.
>
> Traditional backups (cron every N hours) miss the evolution happening during active sessions. We built an event-driven system: every governance event triggers incremental mirrors. Even the backup operations are cryptographically auditable via CIEU Merkle chains.
>
> This is dog-fooding at the extreme: Y*gov (our product) governs the backup system that protects our CEO, who is governed by Y*gov. Recursive trust, all the way down.

**Evidence**:
- Link to CIEU audit logs showing backup events
- SHA256 manifest proving backup integrity
- Disaster recovery script that runs governance_boot.sh post-restore

**Call to Action**:
- "If you're running autonomous agents in production, how do you protect their state?"
- "We're open-sourcing this pattern — see `aiden_cognition_backup.py`"

---

## Future Enhancements

### 1. Cross-Device Sync
Explore `openclaw` CLI for pushing backups to OpenClaw cloud:
- Research: `openclaw backup create` vs custom workspace sync
- Benefit: Multi-device team deployment (MAC mini + Windows laptop)

### 2. Backup Lag SLA
Define governance constraint: "Backup lag must not exceed 100 CIEU events"
- Trigger alert if lag exceeds threshold
- Escalate to Board if backup system degraded

### 3. Encrypted Backups
Sensitive cognition data (Board directives, financial models):
- Encrypt backups with GPG before cloud upload
- Key management via `.claude/credentials/`

### 4. Point-in-Time Recovery
Current system: restore to latest mirror
Enhancement: Keep N timestamped snapshots
- `--restore-to 2026-04-12T10:30:00Z`
- Useful for debugging "what did Aiden know at time T?"

---

## Testing Strategy

**Unit Tests** (`tests/test_aiden_cognition_backup.py`):
1. Full backup of mock company state
2. Incremental backup (detect unchanged files)
3. Atomic write conflict (simulated crash during tmp→rename)
4. Fail-open mode (backup error doesn't block)
5. Verify mode (detect hash mismatches)
6. Recovery roundtrip (backup → corrupt → restore → verify)

**Integration Test**:
1. Run backup in live company repo
2. Manually corrupt a critical file (e.g., `.ystar_session.json`)
3. Run `disaster_recovery.sh`
4. Verify `governance_boot.sh` passes

**Success Criteria**:
- All 6 unit tests pass
- Integration test completes with exit code 0 (ALL SYSTEMS GO)

---

## Conclusion

The Aiden Cognition Guardian transforms disaster recovery from a compliance checkbox into a product demonstration. By making CEO cognition backups event-driven, atomic, and CIEU-auditable, we prove that Y*gov can govern real-world systems at production scale.

This is not a demo. This is the infrastructure keeping Y* Bridge Labs operational.

**Board Directive Fulfilled**: 2026-04-12 — Real-time cognition mirror deployed.

**Next Review**: Q2 2026 OKR — Evaluate OpenClaw cloud integration for Tier 3 resilience.
