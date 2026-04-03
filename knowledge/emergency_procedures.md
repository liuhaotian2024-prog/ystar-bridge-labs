# Emergency Procedures — Crisis Response Protocol

**Source:** AGENTS.md Emergency Procedures章节  
**Moved to knowledge:** 2026-04-03（Constitutional cleanup）  
**Authority:** Constitutional layer

---

## ⚠️ CRITICAL: Read Constitutional Rule First

**From AGENTS.md:**

> 发现credential暴露：立即停止所有操作，上报Board，不得自行修复  
> 无法完成义务：写入reports/blockers/，上报CEO

**This guide provides HOW to execute those requirements.**

---

## Emergency Type 1: Credential Exposure Detected

### Immediate Response (< 1 minute)

**STOP ALL OPERATIONS IMMEDIATELY**

1. Do NOT make any commits
2. Do NOT push anything to GitHub
3. Do NOT attempt to fix the exposure yourself
4. Do NOT delete files or modify git history

### Documentation (< 5 minutes)

Create incident report:

```bash
# File: reports/security/incident-YYYY-MM-DD-HHMMSS.md
```

**Required contents:**
```markdown
# Security Incident — Credential Exposure

**Detected by:** [Agent role]  
**Timestamp:** [YYYY-MM-DD HH:MM:SS UTC]  
**Severity:** CRITICAL

## What was exposed

- **Credential type:** [API key / token / password / certificate]
- **Service:** [GitHub / AWS / OpenAI / etc.]
- **File path:** [exact path where found]
- **Commit hash:** [git hash if committed]
- **Pushed to remote:** [YES / NO / UNKNOWN]

## Detection method

[How was this discovered? Automated scan? Manual review? External report?]

## Scope assessment

**Files containing credential:**
- [List all files]

**Commits containing credential:**
```bash
git log --all --full-history -- path/to/file
```

**Branches affected:**
```bash
git branch --contains <commit_hash>
```

**Pushed to GitHub:**
```bash
git log origin/main..main  # If empty, it's pushed
```

## Immediate actions taken

1. ⏸️ Stopped all operations
2. 📝 Created this incident report
3. 🚨 Notified Board (see below)

## Awaiting Board authorization

- [ ] Revoke exposed credential at source (GitHub/AWS/etc.)
- [ ] Assess blast radius (what could attacker access?)
- [ ] Git history rewrite (if Board authorizes)
- [ ] Force push (if Board authorizes)
- [ ] Rotate all related secrets
- [ ] Post-incident review

**DO NOT PROCEED BEYOND THIS POINT WITHOUT BOARD EXPLICIT AUTHORIZATION**
```

### Board Notification (< 2 minutes)

**Escalation path:**

1. Write to `BOARD_URGENT.md` (top of file):
```markdown
# 🚨 CRITICAL SECURITY INCIDENT — Credential Exposure

**Agent:** [Your role]  
**Time:** [timestamp]  
**Report:** reports/security/incident-[timestamp].md

**Action required:** Board must authorize remediation steps immediately

**Exposed credential:** [brief description]  
**Pushed to GitHub:** [YES/NO]

See full incident report for details.
```

2. Do NOT start any remediation work
3. Wait for Board response (typically < 1 hour for CRITICAL)

---

## Emergency Type 2: Cannot Complete Obligation

### When This Applies

- Obligation deadline approaching, cannot fulfill
- Technical blocker prevents completion
- Lack of authority/permissions
- Dependency on another agent/external system

### Response Protocol (< 10 minutes)

#### Step 1: Create Blocker Report

```bash
# File: reports/blockers/YYYY-MM-DD-HHMMSS-[brief-description].md
```

**Template:**
```markdown
# Blocker Report — [Brief Description]

**Reported by:** [Agent role]  
**Timestamp:** [YYYY-MM-DD HH:MM:SS]  
**Severity:** P0 | P1 | P2

## Obligation affected

**Obligation ID:** [if known]  
**Obligation type:** [e.g., knowledge_gap_bootstrap, token_recording]  
**Deadline:** [timestamp when obligation expires]  
**Time remaining:** [hours/minutes]

## What is blocked

[Describe what you're trying to accomplish]

## Why it's blocked

**Root cause:**
[Technical issue / Missing permission / Dependency / Knowledge gap]

**Details:**
[Specific error messages, logs, or context]

## What I've tried

1. [Attempted solution 1] — Result: [failed because...]
2. [Attempted solution 2] — Result: [failed because...]

## What I need to unblock

**Option A (preferred):**
[What Board/CEO could do to unblock immediately]

**Option B (workaround):**
[Alternative approach if Option A not feasible]

**Option C (escalation):**
[Who else could help? External expert? Another agent?]

## Impact if not unblocked

- **Obligation:** Will expire at [timestamp], triggering [SOFT_OVERDUE / HARD_OVERDUE]
- **Downstream:** [What work depends on this?]
- **Business:** [Any external impact? Customer? Release?]

## Requested action

- [ ] Board: Authorize workaround
- [ ] Board: Provide missing permission/access
- [ ] Board: Reassign obligation to another agent
- [ ] Board: Cancel obligation (if no longer applicable)
- [ ] CEO: Escalate to [another agent]

**Awaiting response**
```

#### Step 2: Escalate to CEO

**Notification:**
```markdown
# CEO Blocker Report

**From:** [Your agent role]  
**File:** reports/blockers/[filename].md  
**Deadline:** [obligation deadline]  
**Urgency:** [hours until deadline]

CEO: Need decision on how to proceed. See blocker report for options.
```

#### Step 3: CEO → Board Escalation (if unresolved in 2 hours)

**CEO adds to daily report:**
```markdown
## 🚨 Unresolved Blocker — [Brief Description]

**Agent:** [Blocked agent]  
**Obligation:** [What's blocked]  
**Deadline:** [When it expires]  
**Attempted resolutions:** [What we tried]  
**Board decision needed:** [Specific ask]

See: reports/blockers/[filename].md
```

---

## Emergency Type 3: System Failure (Y*gov Down)

### Symptoms

- CIEU database not recording
- Hook not executing
- Governance decisions not enforced
- `ystar doctor --layer1` fails

### Immediate Response

**Priority:** STOP all governed work

1. **Verify failure:**
```bash
ystar doctor --layer1
```

2. **If CIEU is dead:**
   - See `knowledge/ceo/cieu_liveness_guide.md`
   - Follow P0 Response Protocol
   - Report to Board immediately

3. **If governance is offline:**
   - Treat as ungoverned environment
   - Do NOT make any decisions requiring governance
   - Wait for Board authorization to proceed ungoverned

---

## Emergency Type 4: Agent Conflict

### When This Applies

- Two agents have contradictory obligations
- Agent cannot determine which instruction takes precedence
- Constitutional rules conflict (rare, but possible)

### Response Protocol

**DO NOT:**
- Guess which obligation is higher priority
- Proceed with either conflicting option
- Ask another agent to decide (they lack authority)

**DO:**

1. **Document conflict:**
```markdown
# Agent Conflict Report

**Conflict between:**
- Obligation A: [description] from [source]
- Obligation B: [description] from [source]

**Why they conflict:**
[Explain mutual exclusivity]

**Constitutional question:**
[Which rule takes precedence?]
```

2. **Escalate to CEO within 10 minutes**
   - CEO has authority to resolve agent conflicts
   - CEO may escalate to Board if constitutional

3. **Wait for resolution**
   - Do NOT proceed with either option
   - Do NOT attempt to find "middle ground"
   - Wait for explicit CEO decision

---

## Emergency Type 5: External Security Report

### If Someone Reports a Vulnerability

**Immediate response:**

1. **Thank the reporter**
```markdown
Thank you for the responsible disclosure. We take security seriously.

Our security response process:
1. Verify the report (< 24 hours)
2. Assess severity and impact
3. Develop and test fix
4. Coordinate disclosure timeline with you

Point of contact: [Board email]
```

2. **Create incident report** (same as Emergency Type 1)

3. **Do NOT:**
   - Argue with reporter
   - Downplay severity
   - Promise specific fix timeline without Board approval
   - Disclose to public before fix is ready

4. **Escalate to Board immediately**
   - Board decides disclosure timeline
   - Board coordinates with reporter
   - Board authorizes fix deployment

---

## Common Mistakes to Avoid

❌ **Attempting "quick fixes" for credential exposure**  
✅ **Stop, document, escalate**

❌ **Hiding blockers until deadline**  
✅ **Report blockers as soon as identified**

❌ **Making up priorities during conflicts**  
✅ **Escalate to CEO for authoritative decision**

❌ **Deleting evidence during security incidents**  
✅ **Preserve all logs and evidence**

❌ **Proceeding ungoverned when governance fails**  
✅ **Stop work, wait for Board authorization**

---

## Escalation Timeframes

| Emergency Type | Initial Report | CEO Escalation | Board Escalation |
|----------------|----------------|----------------|------------------|
| Credential Exposure | < 1 min | Immediate | Immediate |
| Cannot Complete Obligation | < 10 min | < 10 min | < 2 hours |
| System Failure | < 5 min | < 5 min | < 1 hour |
| Agent Conflict | < 10 min | < 10 min | If constitutional |
| External Security Report | < 1 hour | < 1 hour | Immediate |

---

## Post-Emergency Review

After emergency is resolved:

1. **CEO writes post-mortem:**
   - reports/postmortem/YYYY-MM-DD-[incident].md
   - What happened, why, how we responded, what we learned

2. **Update relevant guides:**
   - If new type of emergency, update this guide
   - If constitutional rule was unclear, propose amendment

3. **CIEU audit:**
   - Review full event chain from emergency
   - Verify all decisions were properly governed
   - Check for any ungoverned decisions made during crisis

---

**Last updated:** 2026-04-03  
**Authority:** Constitutional layer (AGENTS.md)  
**Next review:** After next emergency incident
