# Resident Engineer Proposal

**Product:** Y*gov Resident Engineer Service  
**Target:** Enterprise customers who want embedded governance for their AI agent development  
**Author:** CTO (Ethan Wright)  
**Date:** 2026-04-10  

---

## Executive Summary

A "Resident Engineer" is an embedded Y*gov governance agent that lives inside a customer's repository, continuously monitoring and improving their AI agent systems. Unlike one-time audits, the Resident Engineer runs 24/7, providing:

1. **Continuous governance health monitoring** (ystar doctor, automated scans)
2. **Proactive violation detection** (obligation tracking, contract drift)
3. **Automated remediation suggestions** (fix templates, safety patches)
4. **Integration with customer CI/CD** (pre-commit hooks, PR checks)
5. **Causal audit trails** (CIEU logs, K9Audit integration)

Target customer: Enterprise teams building multi-agent systems who need ongoing governance assurance, not just a one-time compliance check.

---

## 1. Technical Implementation

### 1.1 Deployment Architecture

Three deployment options:

**Option A: Claude Code Agent (Recommended)**
- Customer runs Claude Code agent in their repo
- Agent definition: `.claude/agents/ystar-resident.yml`
- Triggered by: cron schedule, git hooks, manual `/resident` command
- Pros: Full autonomy, rich interaction model, integrated with customer workflow
- Cons: Requires Claude Code harness

**Option B: MCP Server + Scheduled Runner**
- Deploy gov-mcp server as systemd service / launchd daemon
- Cron job calls `gov_doctor`, `gov_obligations`, `gov_audit` periodically
- Pros: No Claude dependency, lightweight
- Cons: Less interactive, requires manual configuration

**Option C: GitHub Actions Workflow**
- `.github/workflows/ystar-resident.yml`
- Runs on schedule (hourly/daily), on PR, on push to main
- Uses `ystar doctor`, reports to PR comments / Slack
- Pros: Zero local infra, easy to demo
- Cons: Cloud-only, limited runtime context

**Recommendation:** Start with **Option C** (GitHub Actions) for demo/onboarding, offer **Option A** (Claude Code agent) for mature customers.

---

### 1.2 Customer Onboarding

What customer needs to provide:

1. **AGENTS.md or .ystar_session.json**  
   - Governance contract defining agent roles, delegation chains, scope constraints
   - Can be bootstrapped via `ystar init --interactive`

2. **Repository access**  
   - Read: scan codebase for violations
   - Write (optional): auto-fix via PR, commit hook enforcement

3. **Integration preferences**  
   - Slack webhook for alerts?
   - PagerDuty for critical violations?
   - Email digest (daily/weekly)?

4. **Custom rules (optional)**  
   - Domain-specific invariants (e.g., "no agent can call stripe API without CFO approval")
   - Custom obligation types (e.g., "all LLM calls must log prompts")

**Onboarding flow:**
```bash
# Step 1: Install Y*gov
pip install ystar

# Step 2: Initialize governance contract
ystar init --interactive
# (Guides customer through role definition, delegation setup)

# Step 3: Run initial health check
ystar doctor
# (Produces baseline report: 0 violations = clean state)

# Step 4: Deploy Resident Engineer
# For GitHub Actions:
ystar resident install --platform github
# (Generates .github/workflows/ystar-resident.yml)

# For Claude Code:
ystar resident install --platform claude-code
# (Generates .claude/agents/ystar-resident.yml)
```

---

## 2. Current `ystar doctor` Capabilities

### Layer 1: Zero-Dependency Health Checks
- CIEU database presence and integrity
- Omission database presence and schema validation
- Session config (.ystar_session.json) schema version check
- AGENTS.md parsing confidence score
- Database file permissions

### Layer 2: Dependency Health Checks
- Python environment (version, packages)
- Git repository status
- Pre-commit hooks installed
- Test suite passing (pytest)
- Memory store (YML) connectivity

### What's Missing for Resident Engineer Service

1. **Obligation Aging Analysis**  
   - "You have 3 obligations overdue by >24h"
   - "Agent 'cto' has never acknowledged a task"
   - Currently: obligations are stored, but not analyzed in `doctor`

2. **Contract Drift Detection**  
   - "AGENTS.md changed but .ystar_session.json not regenerated"
   - "New agent roles added without delegation chain update"
   - Currently: no diff tracking between contract sources

3. **Scope Violation History**  
   - "Agent 'eng-kernel' attempted to write outside ystar/kernel/ 12 times in past week"
   - "Most violated rule: 'no direct DB access' (45 violations)"
   - Currently: violations are CIEU-logged, but not aggregated

4. **Performance Regression Detection**  
   - "Average check latency increased 300% since last week"
   - "Omission store queries now taking >500ms (was 50ms)"
   - Currently: no baseline tracking or trend analysis

5. **Remediation Templates**  
   - When a violation is detected, suggest fix
   - Example: "Agent X violated scope Y → Add 'only_paths: [Y]' to contract"
   - Currently: violations reported, but no auto-fix suggestions

6. **Integration Health**  
   - "Git pre-commit hook not called in last 100 commits"
   - "CIEU events stopped writing 6 hours ago (last event: ...)"
   - Currently: checks if hook is installed, but not if it's actually running

---

## 3. K9Audit Integration

K9Audit provides causal chain analysis and residue detection. Integration plan:

### 3.1 License Compatibility
- **Y*gov:** MIT (permissive, commercial-friendly)
- **K9Audit:** AGPL-3.0 (copyleft, requires derivative works to be open-sourced)

**Integration approach:**  
- Do NOT copy K9Audit code into Y*gov (would infect Y*gov with AGPL)
- Instead: **optional dependency** + plugin architecture

```python
# ystar/integrations/k9audit_plugin.py
try:
    from k9log.causal_analyzer import CausalChainAnalyzer
    K9_AVAILABLE = True
except ImportError:
    K9_AVAILABLE = False

def analyze_causal_chain(cieu_log_path):
    if not K9_AVAILABLE:
        return {"error": "K9Audit not installed. Run: pip install k9audit"}
    
    analyzer = CausalChainAnalyzer(cieu_log_path)
    return analyzer.trace_chains()
```

**Customer decision:**  
- If customer wants causal analysis → they install k9audit separately
- If they don't install it → Y*gov still works, just without causal tracing

### 3.2 What K9Audit Brings

1. **Causal Chain Tracing**  
   - "Violation X was caused by agent decision Y, triggered by event Z"
   - Y*gov records CIEU events, K9Audit stitches them into causal DAG

2. **Residue Detection**  
   - "Agent wrote .env file, deleted it, but residue still in git history"
   - K9Audit scans filesystem + git for governance-relevant artifacts

3. **Secret Leakage Analysis**  
   - "API key detected in commit abc123, used in 5 CIEU events"
   - K9Audit Auditor class provides secret scanning

4. **Scope Forensics**  
   - "Agent was delegated only src/, but read .env via Python import"
   - K9Audit tracks indirect access paths Y*gov might miss

**Integration in Resident Engineer:**
```bash
# Enhanced doctor command with K9 integration
ystar doctor --with-k9-analysis

# Output:
[✓] CIEU database integrity
[✓] Obligation tracking
[!] K9Audit causal analysis: 3 indirect violations detected
    → Agent 'eng-platform' read ystar/kernel/dimensions.py via import
    → Outside delegated scope ystar/adapters/
    → Suggest: Add read-only exception for cross-module imports
```

---

## 4. Health Check Report Template

```markdown
# Y*gov Resident Engineer Report
**Repository:** acme-corp/agent-platform  
**Scan Time:** 2026-04-10 14:30:00 UTC  
**Report ID:** resident-20260410-143000  

---

## Summary
- **Status:** ⚠️ WARNING (3 issues found)
- **Obligations:** 2 overdue, 5 pending, 12 fulfilled
- **Violations:** 1 scope violation, 2 soft violations
- **Contract Health:** 95% (AGENTS.md confidence: 0.92)

---

## Issues Detected

### 1. Scope Violation (Severity: HIGH)
- **Actor:** eng-platform (Ethan Wright)
- **Violation:** Wrote to `ystar/kernel/intent.py` (outside delegated scope)
- **Timestamp:** 2026-04-10 12:15:33
- **CIEU Event:** `evt_abc123`
- **Suggested Fix:**
  ```yaml
  # Update delegation contract in .ystar_session.json
  - actor: eng-platform
    scope: "ystar/adapters/, ystar/kernel/"  # Add kernel to scope
  ```

### 2. Overdue Obligation (Severity: MEDIUM)
- **Actor:** cto
- **Task:** Review Q1 governance metrics (task-001)
- **Due:** 2026-04-09 09:00:00 (overdue by 29h)
- **Type:** REQUIRED_ACKNOWLEDGEMENT
- **Suggested Action:**
  ```bash
  # Acknowledge or reject the task
  ystar acknowledge --task task-001 --actor cto --accept
  ```

### 3. Contract Drift (Severity: LOW)
- **Issue:** AGENTS.md modified 3 days ago, .ystar_session.json not regenerated
- **Risk:** Runtime contract may be out of sync with documented intent
- **Suggested Fix:**
  ```bash
  ystar contract update --from AGENTS.md
  ```

---

## Metrics
- **Check Latency:** 0.15s (baseline: 0.12s, +25%)
- **CIEU Events (24h):** 342 events
- **Top Event Type:** file_write (123 events, 36%)
- **Most Active Actor:** eng-kernel (89 events)

---

## Recommendations
1. **Immediate:** Fix scope violation for eng-platform (high priority)
2. **This Week:** Resolve 2 overdue obligations
3. **This Month:** Improve AGENTS.md → .ystar_session.json sync (automate?)

---

## Next Scan
Scheduled: 2026-04-10 15:30:00 UTC (in 1 hour)  
To change frequency: `ystar resident config --schedule hourly|daily|weekly`
```

---

## 5. Pricing Model Implications

(For CSO/CFO consideration)

**Resident Engineer tiers:**

| Tier | Scope | Price (monthly) | Features |
|------|-------|----------------|----------|
| **Community** | Open-source repos | Free | Basic doctor checks, manual scans |
| **Startup** | <10 agents, 1 repo | $499 | Hourly scans, Slack alerts, 7-day CIEU history |
| **Business** | <50 agents, 5 repos | $1,999 | Real-time monitoring, K9Audit integration, 90-day history |
| **Enterprise** | Unlimited | Custom | On-prem deployment, custom rules, SLA, dedicated support |

**Value prop:**  
- Community tier: Try before you buy, builds ecosystem
- Startup tier: Cheaper than hiring a governance engineer ($6k/mo salary)
- Business tier: Replaces compliance consultant ($10k-20k per audit)
- Enterprise tier: Competes with Satori, Privacera ($50k-200k/year)

---

## 6. Next Steps

### For CTO (Ethan)
1. ✅ Write this proposal
2. Implement missing `doctor` features:
   - Obligation aging analysis
   - Contract drift detection
   - Scope violation history aggregation
3. Build `ystar resident install` command
4. Create GitHub Actions workflow template
5. Test with ystar-company repo as pilot

### For CMO (Sofia)
1. Write launch blog post positioning Resident Engineer
2. Create landing page: ystar.dev/resident-engineer
3. Demo video: "5 minutes to embedded governance"

### For CSO (Zara)
1. Identify 3 pilot customers (existing contacts, warm leads)
2. Pricing validation: would they pay $499-1999/mo?
3. Competitive analysis: what do Satori/Privacera offer that we don't?

### For CFO (Marco)
1. Revenue model: SaaS monthly vs. annual contract vs. one-time license
2. Cost structure: hosting (if cloud), support headcount
3. Break-even analysis: how many customers needed to sustain 6-agent team?

---

## Appendix: Related Work

- **K9Audit:** AGPL-3.0, causal analysis, residue detection  
  - Integration: Optional plugin, customer installs separately
  - Repo: https://github.com/liuhaotian2024-prog/K9Audit

- **Satori:** Commercial data governance platform  
  - Focus: Database access control, PII masking
  - Gap: No AI agent-specific governance

- **Privacera:** Enterprise data governance  
  - Focus: Policy enforcement, audit trails
  - Gap: No multi-agent delegation, no obligation tracking

- **OpenAI's Governance Dashboard (rumored):**  
  - Focus: LLM usage monitoring, cost tracking
  - Gap: No scope enforcement, no causal analysis

**Differentiation:**  
Y*gov Resident Engineer is the only solution purpose-built for multi-agent systems with:
- Delegation chain enforcement
- Obligation tracking (not just logging)
- Causal audit trails
- Open-source core + commercial managed service

---

**Status:** Proposal complete, awaiting Board review.  
**Next:** CEO (Aiden) prioritizes with other Q2 initiatives.
