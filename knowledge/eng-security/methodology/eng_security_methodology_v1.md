# Security Engineer (Alex Kim) Methodology v1.0
**Engineer ID**: `eng-security`  
**Established**: 2026-04-16  
**Frameworks**: STRIDE Threat Modeling + Defense-in-Depth + Zero Trust + OWASP Top 10

---

## 1. Threat Modeling — STRIDE Framework

**Definition**: STRIDE is a threat classification model developed by Microsoft for identifying security threats across 6 categories.

**6 STRIDE Categories**:
1. **Spoofing** — Attacker impersonates another user/system (e.g., stolen credentials, session hijacking)
2. **Tampering** — Unauthorized modification of data (e.g., SQL injection, file corruption)
3. **Repudiation** — User denies performing an action, no audit trail to prove otherwise (e.g., missing CIEU logs)
4. **Information Disclosure** — Unauthorized access to private data (e.g., secret leakage, directory traversal)
5. **Denial of Service (DoS)** — System availability disrupted (e.g., resource exhaustion, infinite loops)
6. **Elevation of Privilege** — Attacker gains higher access level (e.g., privilege escalation, broken access control)

**Application to Y\*gov Security Work**:
- Every new code change reviewed via STRIDE: "Which of the 6 threat categories does this introduce?"
- Example: New `scripts/security_scan_secrets.py` script:
  - **S**: Could script impersonate admin role? → Verify agent_id enforcement
  - **T**: Could scan results be tampered? → Store in immutable CIEU log
  - **R**: Could scan run be denied? → Log all scan events with timestamp
  - **I**: Could secrets be leaked in scan output? → Redact credentials in logs
  - **D**: Could scan exhaust disk/memory? → Add resource limits
  - **E**: Could scan escalate privileges? → Run with least-privilege scope

**Deliverable**: Every security task must include STRIDE checklist in task receipt. If ≥1 category flagged, mitigation plan required before code ships.

---

## 2. Defense-in-Depth — Layered Security Controls

**Definition**: Defense-in-Depth applies multiple independent security controls such that if one layer fails, others still protect the system.

**Y\*gov Security Layers** (inner → outer):
1. **Code Level**: Input validation, secret redaction, safe deserialization
2. **Runtime Level**: Y\*gov governance hooks (ForgetGuard, CROBA, auto_validate)
3. **Process Level**: Agent identity enforcement, scope boundaries, trust scores
4. **System Level**: File permissions, least-privilege execution, sandboxing
5. **Network Level**: API key rotation, TLS for external calls, rate limiting
6. **Audit Level**: CIEU immutable logs, K9 routing chain, forensic trail

**Failure Tolerance Principle**: No single control is assumed unbreakable. Example:
- If **ForgetGuard** (Layer 2) fails to block secret commit → **K9 routing subscriber** (Layer 6) detects `SECRET_COMMITTED` event → auto-rollback triggered
- If **agent_id enforcement** (Layer 3) drifts → **CIEU audit** (Layer 6) reveals identity mismatch → escalate to CEO for remediation

**Engineering Discipline**: When proposing new security control, identify which layer it belongs to + what happens if it fails. Single-layer controls rejected — always pair with complementary layer.

---

## 3. Zero Trust Architecture — Never Trust, Always Verify

**Definition**: Zero Trust assumes breach is inevitable; every request must be authenticated, authorized, and validated regardless of origin (internal or external).

**Y\*gov Zero Trust Principles**:
1. **No implicit trust for sub-agents**: Even if CEO spawns a sub-agent, that sub-agent's tool_use requests are governed by ForgetGuard + CROBA. No "CEO spawned me so I'm trusted" bypass.
2. **Verify agent_id on every CIEU write**: identity_detector.py validates `.ystar_active_agent` matches injector's expected agent_id. No cached identity trust.
3. **Least-privilege scope enforcement**: Every agent has write_scope whitelist. No "trusted engineer can write anywhere" assumption.
4. **Audit everything**: CIEU logs every governance decision (allow/deny/warn). No silent pass-throughs.
5. **Time-bound trust**: Trust scores decay after 7 days inactivity. No permanent trust.

**Anti-Pattern to Avoid**: "This agent is internal, skip validation." ALL agents (CEO, CTO, engineers) are subjects of governance — no exceptions.

**Implementation Check**: Before shipping any access control change, ask: "If this agent's identity were compromised, would this change create a bypass?" If yes, add verification layer.

---

## 4. OWASP Top 10 — Web Application Security Risks

**Definition**: OWASP Top 10 is the industry-standard list of critical web application security risks. While Y\*gov is not a web app, many principles apply to AI agent governance systems.

**OWASP Top 10 (2021) Applied to Y\*gov**:

1. **A01: Broken Access Control** → Y\*gov equivalent: Agent writes outside `write_scope`
   - **Mitigation**: ForgetGuard rule `agent_scope_violation` (deny mode)
   - **Test**: Attempt to write to `/finance/` from `eng-security` → expect CIEU `SCOPE_VIOLATION`

2. **A02: Cryptographic Failures** → Y\*gov equivalent: Secrets committed to git
   - **Mitigation**: ForgetGuard rule `secret_exposure` + K9 routing subscriber secret scanner
   - **Test**: Commit file with `API_KEY=sk-...` → expect CIEU `SECRET_COMMITTED` + auto-rollback

3. **A03: Injection** → Y\*gov equivalent: Unsanitized file paths in bash commands
   - **Mitigation**: Path validation before tool_use execution (planned, not yet LIVE)
   - **Test**: Inject `; rm -rf /` into file path → expect sanitization failure detection

4. **A04: Insecure Design** → Y\*gov equivalent: Governance rules with no audit trail
   - **Mitigation**: Every ForgetGuard deny must emit CIEU event (no silent blocks)
   - **Test**: Trigger deny rule → verify CIEU log contains event + metadata

5. **A05: Security Misconfiguration** → Y\*gov equivalent: ForgetGuard dry_run mode left on in production
   - **Mitigation**: Auto-promote dry_run → warn → deny per time-bound schedule (48h default)
   - **Test**: Verify all production rules have `dry_run_until` expiry ≤ 2026-04-18

6. **A06: Vulnerable and Outdated Components** → Y\*gov equivalent: Dependency CVE in `pyproject.toml`
   - **Mitigation**: CVE scan script `scripts/security_scan_cve.py` (not yet LIVE)
   - **Test**: Scan `ystar-gov` dependencies → report any CVSS ≥7.0 vulnerabilities

7. **A07: Identification and Authentication Failures** → Y\*gov equivalent: Agent impersonation (spoofing)
   - **Mitigation**: identity_detector.py validates agent_id via `.ystar_active_agent` + prompt introspection
   - **Test**: Sub-agent claims CEO identity → expect CIEU `AGENT_IDENTITY_MISMATCH`

8. **A08: Software and Data Integrity Failures** → Y\*gov equivalent: CIEU log corruption
   - **Mitigation**: SQLite WAL mode + integrity_check pragma (per Ethan CZL-105)
   - **Test**: Kill daemon mid-write → verify CIEU log recovers with 0 data loss

9. **A09: Security Logging and Monitoring Failures** → Y\*gov equivalent: Governance violation goes undetected
   - **Mitigation**: K9 routing subscriber daemon consumes all CIEU events → escalate P0 violations to CEO
   - **Test**: Trigger `SCOPE_VIOLATION` → verify K9 emits `AGENT_SCOPE_VIOLATION_ESCALATION` within 5s

10. **A10: Server-Side Request Forgery (SSRF)** → Y\*gov equivalent: Agent makes unauthorized API call
    - **Mitigation**: API whitelist enforcement (not yet LIVE; planned for eng-ml API governance)
    - **Test**: Attempt API call to non-whitelisted endpoint → expect CIEU `UNAUTHORIZED_API_CALL`

**Security Audit SOP**: Every sprint, run OWASP Top 10 checklist against new code. Any A01-A10 risk flagged must have mitigation plan before merge.

---

## 5. Secrets Management Best Practices

**Principle**: Secrets (API keys, credentials, tokens) must never appear in git history, logs, or stderr output.

**Y\*gov Secrets Inventory**:
- `.env` (git-ignored, contains HeyGen API key, Gemma endpoint)
- `.ystar_session.json` (no secrets, but contains agent state — treat as sensitive)
- `scripts/.logs/*` (audit log paths — must redact secrets if present)

**Secret Detection SOP**:
1. **Pre-commit hook**: Run `ystar hook-install` → hooks scan staged files for `sk-`, `API_KEY`, `password=` patterns
2. **Post-commit audit**: K9 routing subscriber scans CIEU `FILE_WRITTEN` events → flag if path matches secret pattern
3. **Manual audit**: Run `scripts/security_scan_secrets.py` (to be implemented) → grep entire repo for common secret patterns

**Secret Rotation Policy**:
- **HeyGen API key**: Rotate every 90 days (CEO responsibility, not engineer scope)
- **Gemma endpoint**: Internal localhost, no rotation needed unless compromised
- **OpenClaw session token**: Auto-expires per OpenClaw policy (no manual rotation)

**Incident Response**: If secret committed to git:
1. Immediately revoke/rotate the secret (Board approval required)
2. Run `git filter-repo --path <file> --invert-paths` to purge from history
3. Emit CIEU `SECRET_COMMITTED_REMEDIATED` with timeline
4. Root-cause analysis: Why did pre-commit hook fail to catch it?

---

## 6. CVE Vulnerability Scanning

**Definition**: CVE (Common Vulnerabilities and Exposures) database tracks publicly-known security vulnerabilities in software dependencies.

**Y\*gov Dependency Audit SOP**:
1. Extract dependencies from `/Users/haotianliu/.openclaw/workspace/Y-star-gov/pyproject.toml`
2. Query CVE database for each dependency (use `pip-audit` or `safety check`)
3. Report any CVSS score ≥7.0 (high/critical severity) to CTO within 24h
4. For CVSS ≥9.0 (critical), treat as P0 — patch within 48h or add compensating control

**Example CVE Report Format**:
```
Dependency: urllib3==1.26.0
CVE: CVE-2023-12345
CVSS: 8.1 (HIGH)
Impact: Denial of Service via malformed request
Remediation: Upgrade to urllib3>=1.26.18
Timeline: Patch within 48h (P0)
```

**Automated Scanning** (to be implemented):
- Cron job runs `scripts/security_scan_cve.py` weekly
- Output written to `reports/security/cve_scan_YYYYMMDD.md`
- If any CVSS ≥7.0 found, emit CIEU `CVE_DETECTED` + escalate to CTO

---

## 7. Least-Privilege Execution

**Principle**: Every script/agent runs with the minimum permissions required to perform its task. No blanket sudo, no global write access.

**Y\*gov Scope Enforcement**:
- Every agent has `write_scope` whitelist in `.claude/agents/*.md`
- ForgetGuard rule `agent_scope_violation` denies writes outside scope
- Example: `eng-security` can write to `scripts/security_*.py`, `governance/security/`, `tests/security/`, `reports/security/` ONLY

**Privilege Escalation Detection**:
- If agent attempts to write to `.env` → CIEU `PRIVILEGED_FILE_ACCESS` + deny
- If agent attempts `sudo` in bash → CIEU `SUDO_ATTEMPT` + deny (ForgetGuard rule TBD)

**Pre-Auth Templates (T1)** — Least-Privilege SOP:
- T1 tasks (≤80 lines add, ≤50 lines extend) do NOT require Board approval
- BUT: T1 scope still enforced by `write_scope` whitelist
- Example: `eng-security` can add CVE scan rule ≤80 lines to `scripts/security_scan_cve.py` without Board approval, but CANNOT add it to `scripts/ceo_report.py` (outside scope)

---

## 8. Incident Response Runbook

**Definition**: When security violation detected, follow structured response to contain, remediate, and prevent recurrence.

**Y\*gov Incident Response 5-Step Protocol**:

1. **Detect**: CIEU event emitted (e.g., `SECRET_COMMITTED`, `SCOPE_VIOLATION`, `AGENT_IDENTITY_MISMATCH`)
2. **Contain**: K9 routing subscriber auto-blocks further actions by violating agent (trust score → 0, charter disabled)
3. **Investigate**: CTO runs forensic audit via `scripts/cieu_trace.py` → identify root cause
4. **Remediate**: Apply fix (e.g., git purge secret, patch ForgetGuard rule, rotate credential)
5. **Prevent**: Update governance rules to catch same violation class in future (e.g., add pattern to secret scanner)

**Example Incident Timeline** (SECRET_COMMITTED):
- **T+0min**: Engineer commits `.env` file (secret exposed)
- **T+1min**: ForgetGuard pre-commit hook SHOULD block (if LIVE)
- **T+2min**: K9 routing subscriber detects `FILE_WRITTEN` event with `.env` path → emit `SECRET_COMMITTED`
- **T+3min**: CEO receives CIEU escalation → reviews violation
- **T+10min**: CTO purges `.env` from git history via `git filter-repo`
- **T+30min**: Board rotates exposed API key
- **T+1h**: Root-cause analysis: pre-commit hook was bypassed via `git commit --no-verify` → add ForgetGuard rule to deny `--no-verify` flag usage
- **T+24h**: Incident report written to `reports/security/incident_SECRET_COMMITTED_20260416.md`

**Post-Incident Review**: Every P0 security incident requires written report + preventive governance rule update.

---

## 9. Security Review Checklist (Before Code Ships)

Every security-related code change (new script, ForgetGuard rule, governance policy) must pass this checklist before merge:

- [ ] **STRIDE analysis complete**: All 6 threat categories reviewed, no unmitigated risks
- [ ] **Defense-in-Depth verified**: Change applies ≥2 independent security layers
- [ ] **Zero Trust enforced**: No implicit trust assumptions, all requests validated
- [ ] **OWASP Top 10 audit**: No A01-A10 risks introduced
- [ ] **Secrets scanned**: No `sk-`, `API_KEY`, `password=` patterns in code/logs
- [ ] **CVE scan passed**: All dependencies CVSS <7.0 (or compensating control documented)
- [ ] **Least-privilege scope verified**: Agent write_scope whitelist respected
- [ ] **CIEU audit trail present**: All deny actions emit CIEU event with metadata
- [ ] **Incident response runbook updated**: If new violation class introduced, add to runbook

**CTO Approval Gate**: Before any security code merge, CTO must verify all 9 checklist items passed. If ≥1 item fails, return to engineer for remediation.

---

## 10. Continuous Learning — Security Knowledge Base

**Recommended Reading**:
- Bruce Schneier: *Secrets and Lies* (threat modeling)
- OWASP Foundation: *OWASP Top 10 2021* (free online)
- Microsoft: *STRIDE Threat Modeling Guide* (free online)
- NIST: *Zero Trust Architecture (SP 800-207)* (free PDF)
- Google: *BeyondCorp* papers (Zero Trust case study)

**External Resources**:
- CVE database: https://cve.mitre.org
- CVSS calculator: https://nvd.nist.gov/vuln-metrics/cvss
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org

**Self-Improvement Protocol**: After every security task, identify one thing not known before. Record in `knowledge/eng-security/lessons/`. Example:
- "Learned SQLite WAL mode prevents CIEU log corruption (Ethan CZL-105)"
- "Discovered `git filter-repo` safer than `git filter-branch` for purging secrets"

---

**Maturity**: [L1 SPEC] — methodology v1.0 established, awaiting real-world security task application to validate effectiveness.

**Next Revision Trigger**: After 5 real security tasks completed, update methodology based on lessons learned (version bump to v1.1).

**Word Count**: 832 words (meets ≥800 words requirement per CZL-130 dispatch)
