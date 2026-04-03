# Self-Bootstrap Protocol — Execution Guide

**Source:** AGENTS.md Self-Bootstrap Protocol章节（Y*gov Enforced）  
**Moved to knowledge:** 2026-04-03（Constitutional cleanup）  
**Authority:** Constitutional layer

---

## Purpose

Agents autonomously update their knowledge base when they encounter gaps, errors, or new information. This ensures continuous learning without Board micro-management.

## Constitutional Boundaries

**CAN modify:** knowledge/ directory (Knowledge layer)  
**CANNOT modify:** AGENTS.md, .claude/agents/, Y*gov contracts (Constitutional layer)

**Power hierarchy:**
1. Constitutional layer (highest): AGENTS.md + Y*gov contracts
2. Knowledge layer (self-bootstrappable): knowledge/
3. Execution layer: daily tasks

---

## When to Bootstrap

**Trigger conditions** (INSTANT, not scheduled):

1. Agent lacks reliable knowledge for a task
2. Agent produces an unverifiable answer
3. Knowledge/ files are outdated
4. A previous answer was wrong
5. Agent receives correction from Board or another agent
6. Agent encounters new concept/framework/competitor
7. Task outcome differs from expectation
8. Any event that could improve future decision-making

**Frequency:** INSTANT. If you learned something, write it NOW.  
**Obligation timing:** 30 minutes from gap detection to write completion

---

## 7-Step Bootstrap Process

### Step 1: IDENTIFY the gap explicitly

**What to document:**
- What knowledge was missing?
- What task triggered the gap?
- What was the consequence of the gap?

**Example:**
```
Gap: Don't know how to configure GitHub PAT workflow permissions
Triggered by: Push failed with workflow permission error
Consequence: All commits blocked from reaching GitHub
```

### Step 2: SEARCH at least 2 authoritative sources

**Authoritative sources:**
- Official documentation (GitHub Docs, Python Docs, etc.)
- Academic papers (arXiv, ACM, IEEE)
- Reputable technical blogs (verified authors)
- Primary source code repositories

**Non-authoritative sources to avoid:**
- Random StackOverflow answers (unless highly voted + verified)
- Unverified blog posts
- ChatGPT/LLM output without verification
- Hearsay or second-hand information

**Method:**
```bash
# Use WebSearch or WebFetch
ystar web-search "GitHub PAT workflow permission"
```

### Step 3: VERIFY by cross-referencing

**Cross-reference requirements:**
- Minimum 2 independent sources must agree
- Check source publication date (prefer recent)
- Verify against known facts or test empirically

**Confidence levels:**
- **HIGH:** 3+ authoritative sources agree, empirically tested
- **MEDIUM:** 2 authoritative sources agree, not yet tested
- **LOW:** 1 source, or sources conflict, or untested

### Step 4: WRITE to knowledge/[role]/ with metadata

**File naming convention:**
```
knowledge/[role]/[topic].md
```

**Required metadata block:**
```markdown
# [Topic Title]

**Source:** [Primary URL]  
**Retrieved:** [YYYY-MM-DD]  
**Confidence:** HIGH | MEDIUM | LOW  
**Verified-by:** [Second source URL]  
**Author:** [Agent role]  
**Last updated:** [YYYY-MM-DD]

---

[Content here]
```

**Example:**
```markdown
# GitHub PAT Workflow Permissions

**Source:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens  
**Retrieved:** 2026-04-02  
**Confidence:** HIGH  
**Verified-by:** https://github.blog/changelog/2023-02-23-more-granular-scopes-for-personal-access-tokens/  
**Author:** CTO  
**Last updated:** 2026-04-02

---

## Problem

GitHub workflows require explicit `workflow` scope in Personal Access Token (PAT).

## Solution

1. Go to GitHub Settings > Developer settings > Personal access tokens > Fine-grained tokens
2. Edit existing token
3. Add `workflow` permission under Repository permissions
4. Save token
5. Token will now allow push to repos with workflow files

## Tested

✅ Verified on Y-star-gov repository 2026-04-02
```

### Step 5: UPDATE knowledge/cases/ if gap caused failure

**If the gap caused a case-worthy failure:**
```bash
# Create case file
knowledge/cases/CASE_NNN_[short_description].md
```

**Link back to bootstrap:**
```markdown
## Root Cause

Knowledge gap: [link to knowledge/[role]/[topic].md]
```

### Step 6: CIEU records all writes automatically

**No action needed.** Y*gov hook automatically records:
- File path written
- Timestamp
- Agent ID
- Content hash

**Verify in CIEU:**
```bash
sqlite3 .ystar_cieu.db "SELECT event_type, file_path FROM cieu_events WHERE event_type='file_write' ORDER BY created_at DESC LIMIT 5;"
```

### Step 7: LOG to knowledge/bootstrap_log.md

**Append entry:**
```markdown
## [YYYY-MM-DD] [Agent Role] — [Topic]

**Gap:** [Brief description]  
**Trigger:** [What task revealed the gap]  
**Resolution:** [What was learned]  
**File:** knowledge/[role]/[topic].md  
**Confidence:** HIGH | MEDIUM | LOW
```

---

## Hard Constraints (Cannot Override)

❌ **NEVER modify AGENTS.md**  
❌ **NEVER modify .claude/agents/ files**  
❌ **NEVER modify past case entries** (append corrections only)  
❌ **NEVER write content contradicting Y*gov contracts**  
❌ **NEVER claim knowledge without searching**  
❌ **LOW confidence = flag to Board, do not apply**

---

## Success Criteria

After bootstrap completion:

- ✅ Gap explicitly identified
- ✅ 2+ authoritative sources consulted
- ✅ Cross-reference verification complete
- ✅ Metadata block complete with confidence level
- ✅ CIEU recorded the write
- ✅ bootstrap_log.md updated
- ✅ If caused failure: case file created and linked

---

## Quality Standards

**Good bootstrap:**
- Answers "what was the gap" clearly
- Cites specific, verifiable sources
- Includes confidence level
- Links to related cases if applicable
- Concise but complete

**Bad bootstrap:**
- Vague problem description
- No sources cited
- No confidence level
- Copy-paste from ChatGPT without verification
- Modifies constitutional files

---

## Escalation

**If confidence is LOW:**
- Flag to Board in daily report
- Do NOT apply the knowledge to decisions yet
- Request Board verification before using

**If knowledge contradicts existing constitutional rules:**
- STOP immediately
- Report to Board
- Do NOT write conflicting knowledge
- Wait for constitutional amendment

---

**Last updated:** 2026-04-03  
**Next review:** When bootstrap obligation timing changes
