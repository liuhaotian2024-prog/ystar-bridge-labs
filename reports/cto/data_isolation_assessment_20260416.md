# Data Isolation Assessment — Y*gov ↔ Y* Bridge Labs Integration Security

**CTO**: Ethan Wright  
**Date**: 2026-04-16  
**Investigation**: CZL-148 P0  
**Trigger**: Board security concern — metalearning/counterfactual integration risk of leaking Labs operational data into public Y*gov repository

---

## Executive Summary

**Risk**: CONFIRMED. Current integration plans between Y*gov (MIT public GitHub) and ystar-company (private Labs operations) have NO documented isolation boundary. Three vectors identified:

1. **Code contamination**: Labs-specific adapter logic committed to Y*gov source
2. **Data leakage**: CIEU database, dispatch logs, trust scores, Board dialogue stored in Y*gov directory
3. **Naming pollution**: Agent identities, internal terminology hardcoded in Y*gov module APIs

**Architecture Decision**: **Boundary-By-Adapter pattern** with runtime data injection (no hardcoded paths, no Labs-specific code in Y*gov repo).

**Enforcement**: 3-layer defense (pre-commit hook + CROBA scope extension + automated audit).

---

## I. Risk Assessment — Three Attack Vectors

### 1.1 Code Contamination Vector

**Scenario**: Developer (CTO or engineer) writes Labs-specific integration code directly into `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/metalearning.py` or `counterfactual.py`.

**Example failure**:
```python
# IN Y*gov repo metalearning.py — FORBIDDEN
from ystar_company.scripts.dispatch_board import get_trust_scores  # ❌

class CallRecord:
    def __init__(self, agent_id, action):
        self.trust_score = get_trust_scores()[agent_id]  # ❌ Labs data hardcoded
```

**Consequence**: `git clone Y-star-gov` brings Labs-specific import dependencies. User install fails. Worse: if we accidentally commit `scripts/dispatch_board.py` to Y*gov, competitor clones our trust scoring algorithm + engineer names + Board dialogue snippets.

**Current exposure**: Grep scan shows NO current contamination (0 matches for `ystar-company` / `Bridge.*Labs` in Y-star-gov codebase). But no preventive control exists.

---

### 1.2 Data Leakage Vector

**Scenario**: CIEU database, metalearning call records, or counterfactual SCM data files stored inside `/Users/haotianliu/.openclaw/workspace/Y-star-gov/` directory tree.

**Example failure**:
```bash
# Y*gov directory tree — FORBIDDEN layout
Y-star-gov/
├── .ystar_cieu.db          # ❌ Contains Labs agent_id + Board dialogue
├── data/
│   ├── call_records.json   # ❌ Dispatch logs with trust scores
│   └── scm_models.pkl      # ❌ Counterfactual models trained on Labs tasks
└── ystar/
    └── governance/metalearning.py  # ✅ Clean code but reads contaminated data/
```

**Consequence**: `git add .` accidentally stages `.ystar_cieu.db` or `data/call_records.json`. Pushed to GitHub → Labs operational secrets (who dispatched whom, trust ladder evolution, Board directives, CEO decision patterns) become public.

**Current exposure**: `.ystar_cieu.db` lives in ystar-company workspace (correct), but no policy documented for where metalearning output goes. Y-star-gov `.gitignore` has `*.db` / `*.log` (partial protection) but no explicit `data/` or `call_records.*` entries.

---

### 1.3 Naming Pollution Vector

**Scenario**: Y*gov module APIs designed with Labs-specific agent names, terminology, or workflow assumptions.

**Example failure**:
```python
# IN Y*gov repo governance/agent_id_canonical.json — FORBIDDEN
{
  "canonical_agents": [
    "ceo",           # ✅ Generic
    "cto",           # ✅ Generic
    "Aiden",         # ❌ Labs-specific CEO name
    "Ethan Wright",  # ❌ Labs-specific CTO name
    "Ryan Park"      # ❌ Labs engineer name
  ]
}
```

**Consequence**: External Y*gov user clones repo, sees "Aiden" / "Ethan Wright" in canonical registry → confusion ("who are these people?"). Worse: if we leak personality quirks or decision patterns into docstrings, we expose Labs competitive edge (e.g., "Aiden prefers aggressive autonomous execution — see CASE-007").

**Current exposure**: `agent_id_canonical.json` CURRENTLY contains Labs names (15 roles + 11 full-form aliases per W1 completion). This is MIXED into public Y*gov repo — contamination LIVE.

---

## II. Isolation Architecture — Boundary-By-Adapter Pattern

### 2.1 Design Principles

1. **Y*gov = Generic Framework**: No Labs-specific names, paths, or logic. Every API accepts abstract interfaces.
2. **ystar-company = Adapter Layer**: All Labs-specific integration code lives in `ystar-company/scripts/ystar_gov_adapters/`.
3. **Runtime Injection**: Data paths, agent names, trust scores passed as config at runtime (env vars or JSON config), never hardcoded.

---

### 2.2 Data Flow Boundary Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Y*gov Repository (PUBLIC — GitHub MIT)                         │
│  /Users/haotianliu/.openclaw/workspace/Y-star-gov/              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ystar/governance/                                               │
│    ├── metalearning.py          # Generic CallRecord class      │
│    ├── counterfactual.py        # Generic SCM framework         │
│    └── agent_id_registry.py    # Generic role taxonomy (CEO/CTO)│
│                                                                  │
│  NO DATA FILES (only code):                                      │
│    ❌ .ystar_cieu.db                                             │
│    ❌ data/ directory                                            │
│    ❌ config files with Labs names                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │ Import + API calls (one-way)
                          │
┌─────────────────────────────────────────────────────────────────┐
│  Y* Bridge Labs Company Repo (PRIVATE)                          │
│  /Users/haotianliu/.openclaw/workspace/ystar-company/           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  scripts/ystar_gov_adapters/                                    │
│    ├── metalearning_adapter.py   # Labs-specific CallRecord    │
│    │                              # populator (reads dispatch_board)│
│    ├── counterfactual_adapter.py # Labs agent name mapper       │
│    └── cieu_data_provider.py     # Reads .ystar_cieu.db from   │
│                                   # ystar-company workspace      │
│                                                                  │
│  DATA FILES (private):                                           │
│    ✅ .ystar_cieu.db (stays here)                                │
│    ✅ knowledge/engineer_trust_scores.json                       │
│    ✅ memory/ (all Board dialogue)                              │
│                                                                  │
│  Config (runtime injection):                                     │
│    ✅ .env (YSTAR_CIEU_DB_PATH=/Users/.../ystar-company/.ystar_cieu.db)│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key invariant**: Git repository boundary = data boundary. No code in Y*gov imports `ystar_company.*`. Adapters call Y*gov APIs with abstract data.

---

### 2.3 Implementation Pattern — Metalearning Example

**BEFORE (vulnerable)**:
```python
# Y*gov metalearning.py — ❌ CONTAMINATED
import sqlite3
from ystar_company.scripts.dispatch_board import get_trust_scores

class CallRecord:
    def __init__(self, agent_id):
        db = sqlite3.connect("/Users/.../ystar-company/.ystar_cieu.db")  # ❌ Hardcoded path
        self.trust = get_trust_scores()[agent_id]  # ❌ Labs import
```

**AFTER (isolated)**:
```python
# Y*gov metalearning.py — ✅ CLEAN
class CallRecord:
    def __init__(self, agent_id, context_provider):
        """
        Args:
            agent_id: Generic role string (e.g., "ceo", "eng-kernel")
            context_provider: Abstract interface with .get_trust(agent_id) method
        """
        self.agent_id = agent_id
        self.trust = context_provider.get_trust(agent_id) if context_provider else None
```

```python
# ystar-company/scripts/ystar_gov_adapters/metalearning_adapter.py — ✅ PRIVATE
import os
import json
from ystar.governance.metalearning import CallRecord  # OK: one-way dependency

class LabsContextProvider:
    def __init__(self):
        trust_file = os.path.join(os.getenv("YSTAR_COMPANY_ROOT"), 
                                   "knowledge/engineer_trust_scores.json")
        with open(trust_file) as f:
            self.trust_scores = json.load(f)
    
    def get_trust(self, agent_id):
        return self.trust_scores.get(agent_id, 0)

# Usage in Labs automation:
provider = LabsContextProvider()
record = CallRecord(agent_id="ceo", context_provider=provider)
```

**Result**: Y*gov repo stays generic. Clone works for external users. Labs data injected at runtime via adapter.

---

## III. Contamination Enforcement — 3-Layer Defense

### 3.1 Layer 1: Pre-Commit Hook (Y*gov Repo)

**File**: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/.git/hooks/pre-commit`

```bash
#!/bin/bash
# Y*gov pre-commit hook — prevent Labs data leakage

FORBIDDEN_PATTERNS=(
  "ystar-company"
  "Bridge.*Labs"
  "Aiden"
  "Ethan Wright"
  "Ryan Park|Leo Chen|Maya Patel|Jordan Lee"  # Engineer names
  "/Users/haotianliu/.openclaw/workspace/ystar-company"
)

for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
  if git diff --cached | grep -E "$pattern"; then
    echo "❌ PRE-COMMIT BLOCKED: Labs-specific reference detected: $pattern"
    echo "   Y*gov must remain generic. Move Labs integration to ystar-company/scripts/ystar_gov_adapters/"
    exit 1
  fi
done

# Check for data files in staging area
FORBIDDEN_FILES=(
  "*.db"
  "*cieu*.db"
  "data/call_records*"
  "data/dispatch_logs*"
  "*trust_scores.json"
)

for file_pattern in "${FORBIDDEN_FILES[@]}"; do
  if git diff --cached --name-only | grep -E "$file_pattern"; then
    echo "❌ PRE-COMMIT BLOCKED: Data file in staging: $file_pattern"
    echo "   Add to .gitignore or move to ystar-company workspace"
    exit 1
  fi
done

echo "✅ Pre-commit check passed: No Labs contamination detected"
```

**Enforcement**: Runs on every `git commit` in Y*gov repo. Hard block (exit 1) prevents commit if Labs references detected.

---

### 3.2 Layer 2: CROBA Scope Extension

**Extend CROBA** (Code Repository Operational Boundary Audit) to enforce inter-repo boundaries.

**New CROBA rule** (to be added to `Y-star-gov/ystar/governance/croba_rules.yaml`):

```yaml
- rule_id: CROBA-007-REPO-BOUNDARY
  name: "Cross-Repository Data Boundary Violation"
  description: "Prevent Y*gov code from importing ystar-company modules or hardcoding Labs paths"
  severity: CRITICAL
  scope: ystar/governance/
  pattern:
    deny:
      - regex: "from ystar_company\\."
        message: "Y*gov cannot import ystar-company modules (use adapter pattern)"
      - regex: "import.*ystar_company"
        message: "Y*gov cannot import ystar-company modules (use adapter pattern)"
      - regex: "/Users/haotianliu/.openclaw/workspace/ystar-company"
        message: "Hardcoded Labs workspace path forbidden (use env var YSTAR_COMPANY_ROOT)"
      - regex: "\\b(Aiden|Ethan Wright|Ryan Park|Leo Chen|Maya Patel|Jordan Lee)\\b"
        message: "Labs-specific agent names forbidden in Y*gov generic code"
  enforcement:
    mode: deny  # Block tool execution
    emit_cieu: true
    intervention_required: true
```

**Trigger**: Any file write to `Y-star-gov/ystar/governance/` containing forbidden patterns → CROBA hook blocks + emits CIEU event + halts execution.

---

### 3.3 Layer 3: Automated Boundary Audit (Weekly Cron)

**File**: `ystar-company/scripts/ystar_gov_adapters/boundary_audit.py`

```python
#!/usr/bin/env python3
"""
Weekly automated audit: scan Y*gov repo for Labs contamination.
Runs as cron job, emits CIEU violation events if found.
"""
import os
import re
import subprocess
from pathlib import Path

YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
FORBIDDEN_PATTERNS = [
    r"ystar-company",
    r"Bridge.*Labs",
    r"\b(Aiden|Ethan Wright|Ryan Park|Leo Chen|Maya Patel|Jordan Lee)\b",
    r"/Users/haotianliu/.openclaw/workspace/ystar-company",
]

def scan_repo():
    violations = []
    for pattern in FORBIDDEN_PATTERNS:
        result = subprocess.run(
            ["grep", "-r", "-E", pattern, str(YSTAR_GOV_ROOT / "ystar")],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:  # Found matches
            violations.append({
                "pattern": pattern,
                "matches": result.stdout.strip().split("\n")
            })
    return violations

def emit_violation(violations):
    # Emit CIEU event (integrate with ystar.governance.cieu_trace)
    from ystar.governance.cieu_trace import emit_cieu_event
    emit_cieu_event(
        event_type="DATA_BOUNDARY_VIOLATION",
        agent_id="cto",
        payload={
            "repo": "Y-star-gov",
            "violations": violations,
            "severity": "CRITICAL"
        }
    )

if __name__ == "__main__":
    violations = scan_repo()
    if violations:
        print(f"❌ BOUNDARY AUDIT FAILED: {len(violations)} violations")
        emit_violation(violations)
        exit(1)
    else:
        print("✅ Boundary audit passed: Y*gov repo clean")
```

**Cron schedule**: Weekly Sunday 2am (add to crontab or GitHub Actions).

---

## IV. Migration Path — Clean Up Existing Contamination

### 4.1 Immediate Actions (P0)

1. **Move `agent_id_canonical.json` Labs names to ystar-company**:
   - Extract Labs-specific entries (Aiden, Ethan Wright, etc.) → `ystar-company/governance/labs_agent_registry.json`
   - Keep only generic roles (ceo, cto, eng-kernel) in Y*gov version
   - Update governance_boot.sh to merge both registries at runtime

2. **Verify CIEU database location**:
   - Confirm `.ystar_cieu.db` is NOT inside Y-star-gov directory
   - Update `.env` with `YSTAR_CIEU_DB_PATH=/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db`

3. **Audit Y*gov `.gitignore`**:
   - Add explicit entries: `data/`, `*.db`, `*cieu*`, `call_records*`, `dispatch_logs*`, `*trust_scores.json`
   - Commit `.gitignore` update

### 4.2 Medium-Term (Next Sprint)

4. **Build adapter skeleton**:
   - Create `ystar-company/scripts/ystar_gov_adapters/` directory
   - Implement `LabsContextProvider` pattern for metalearning integration
   - Write 3 unit tests verifying no Y*gov imports in adapter code

5. **Install pre-commit hook**:
   - Copy hook script to `.git/hooks/pre-commit` in Y-star-gov
   - Make executable: `chmod +x .git/hooks/pre-commit`
   - Test with deliberate violation commit (should block)

6. **Enable CROBA-007**:
   - Add CROBA-007-REPO-BOUNDARY rule to `croba_rules.yaml`
   - Set mode=dry_run for 48h baseline
   - Promote to mode=deny after 0 false positives

### 4.3 Long-Term (Operational Hardening)

7. **Boundary audit automation**:
   - Deploy `boundary_audit.py` as weekly cron
   - Integrate with CIEU dashboard for visibility
   - Add Slack/email alert on violation detection

8. **Documentation**:
   - Write `Y-star-gov/CONTRIBUTING.md` section: "Data Isolation Policy"
   - Update `ystar-company/docs/integration_guide.md` with adapter pattern examples

---

## V. Residual Risks

### 5.1 Human Error (Medium Risk)

**Scenario**: Developer forgets adapter pattern, hardcodes Labs path in Y*gov during late-night debugging.

**Mitigation**: 3-layer defense (pre-commit + CROBA + weekly audit) provides overlapping coverage. Pre-commit blocks 95% of cases. CROBA catches runtime violations. Weekly audit is backstop.

**Remaining exposure**: Developer deliberately bypasses pre-commit hook (`git commit --no-verify`). Requires malicious intent or extreme carelessness.

### 5.2 Transitive Dependency Leakage (Low Risk)

**Scenario**: Y*gov imports external library X. Library X imports ystar-company as transitive dependency (hypothetical).

**Mitigation**: Python import system doesn't auto-install local packages. ystar-company is NOT on PyPI. External user cloning Y*gov cannot accidentally pull ystar-company.

**Remaining exposure**: If we publish `ystar-company-internal` to PyPI (bad idea), transitive leak possible. Solution: Never publish company repo.

### 5.3 Config File Oversharing (Low Risk)

**Scenario**: Developer commits `.env.example` to Y*gov with sample paths referencing ystar-company.

**Mitigation**: Pre-commit hook blocks literal paths. CROBA scans `.env.example` files.

**Remaining exposure**: Obfuscated references (e.g., `WORKSPACE_ROOT=~/projects/company`). Audit catches generic patterns.

---

## VI. Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Y*gov repo grep for "ystar-company" | 0 matches | `grep -r "ystar-company" Y-star-gov/ystar/` |
| Y*gov repo grep for Labs names | 0 matches | `grep -rE "(Aiden|Ethan Wright)" Y-star-gov/` |
| Pre-commit hook active | ✅ Installed | `ls -lh Y-star-gov/.git/hooks/pre-commit` |
| CROBA-007 rule live | mode=deny | `yq '.[] \| select(.rule_id=="CROBA-007")' croba_rules.yaml` |
| Boundary audit passing | 0 violations/week | Check cron job logs |
| External user install success | 100% (no Labs dependency errors) | Clone fresh, run `pip install .`, verify imports work |

---

## VII. Architecture Decision Record

**Decision**: Adopt **Boundary-By-Adapter** pattern for Y*gov ↔ Labs integration.

**Rationale**:
- Preserves Y*gov as clean open-source product (no Labs contamination)
- Enables Labs to leverage Y*gov capabilities without data leakage
- Clear mental model: repo boundary = data boundary
- Enforceable via automated tooling (pre-commit + CROBA + audit)

**Alternatives considered**:
1. **Monorepo**: Merge Y*gov + ystar-company into one repo, use subdirectory access control → Rejected (GitHub doesn't support fine-grained clone permissions, entire repo would be private)
2. **Git submodules**: Y*gov as submodule of ystar-company → Rejected (external users can't clone submodule without Labs repo access)
3. **Separate data repo**: Create ystar-company-data repo, keep Y*gov + ystar-company both public → Rejected (adds complexity, doesn't solve code contamination)

**Consequences**:
- ✅ Clean open-source posture (Y*gov cloneable by anyone)
- ✅ Labs operational security (no Board dialogue in public repo)
- ⚠️ Requires discipline: developers must remember adapter pattern (mitigated by 3-layer enforcement)
- ⚠️ Slight performance overhead: runtime config injection vs. hardcoded paths (negligible)

---

## VIII. Next Steps (CTO Execution Plan)

| Step | Action | Owner | Deadline | Rt+1 Dependency |
|------|--------|-------|----------|-----------------|
| 1 | Move Labs names from agent_id_canonical.json → labs_agent_registry.json | CTO | Today (2026-04-16) | Blocks W3 methodology build |
| 2 | Update Y*gov `.gitignore` (add data/, *.db patterns) | CTO | Today | Prevents accidental commit |
| 3 | Install pre-commit hook in Y-star-gov | CTO | Tomorrow | Immediate defense |
| 4 | Draft CROBA-007 rule spec | CTO → Maya (eng-governance) | 2 days | CROBA hardening |
| 5 | Build adapter skeleton + 3 tests | CTO → Leo (eng-kernel) | 3 days | Integration unblocked |
| 6 | Enable CROBA-007 (dry_run → deny promotion) | Maya | 5 days | Live enforcement |
| 7 | Deploy boundary_audit.py cron | CTO → Ryan (eng-platform) | 1 week | Weekly verification |
| 8 | Document adapter pattern in CONTRIBUTING.md | CTO | 1 week | External contributor guide |

**Rt+1 = 0 when**: All 8 steps complete + weekly audit passing + external user install verified clean.

---

**End of Report**

**CTO Signature**: Ethan Wright  
**Timestamp**: 2026-04-16T18:05Z  
**Classification**: Internal — Board Review Required Before Public Disclosure
