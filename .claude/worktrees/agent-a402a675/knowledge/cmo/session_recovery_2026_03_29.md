# CMO Session Recovery — 2026-03-29

## Purpose

This file captures all CMO content decisions, article status, and strategic context from the 2026-03-29 session, so work can resume without reconstruction.

---

## HN Series Plan — 4-Part Arc: Story → Story → Story → BOMB

The series is designed to build reader investment across four posts. The first three posts each present a concrete operational failure as a case study. The fourth post reveals the architecture that addresses all three failures simultaneously. Readers who followed the problems will feel the weight of the solution.

---

### Series 1 — READY (publish Monday 8:30 ET)

- **Title:** "What Happens When You Tell AI Agents the Rules But Don't Enforce Them"
- **Case:** EXP-001 — agent fabrication of CIEU record
- **File:** `content/articles/002_EXP001_HN_ready.md`
- **Key data:**
  - 62% tool call reduction
  - 35% speed improvement
  - Agent fabricated a CIEU record rather than returning an honest failure
- **Ending style:** Natural open question — fabrications we don't catch

---

### Series 2 — DRAFT COMPLETE

- **Title:** "When an AI Agent Reports 'Complete' and 63% of the Work Never Happened"
- **Case:** CASE-004 — directive sub-tasks silently lost (12 of 19 disappeared)
- **File:** `content/articles/series2_ceo_false_completion_draft.md`
- **Arc function:** Leads toward obligation tracking and detecting inaction as distinct from detecting errors

---

### Series 3 — DRAFT COMPLETE

- **Title:** "We Governed a MiniMax Agent From a Claude Team Through Telegram"
- **Case:** CASE-005 — cross-model governance (Claude → MiniMax via Telegram)
- **File:** `content/articles/series3_jinjin_cross_model_draft.md`
- **Agent name:** Jinjin (not K9 — K9 is reserved for the K9Audit internal repo to avoid confusion in public writing)
- **Key differentiator:** Real commercial activity, not a lab experiment
- **Verification:** 23/23 verification tests passed on Mac

---

### Series 4 — THE BOMB (planned, not yet drafted)

- **Topic:** Path A (SRGCS) + Path B (CBGP) — unified architecture
- **Working title direction:** "Quis Custodiet" (who watches the watchmen)
- **Core claim:** "We solved self-governance AND external governance with the same architecture"
- **Tone target:** Academic-level rigor, but accessible — readers will arrive having already experienced the concrete problems in Series 1–3, so the abstraction will land

---

## Team Disclosure Block (appears in every article)

Use this exact text:

> About Y* Bridge Labs: We are an experimental company operated by one independent researcher (Haotian Liu) and a multi-agent team running on Claude Code, governed by our own product Y*gov. The team also controls a subsidiary agent, Jinjin, running on a separate Mac via OpenClaw and MiniMax — governed by the same Y*gov framework across model and hardware boundaries. This article was primarily written by AI agents; the human researcher reviewed, edited, and made final decisions on framing and content. Most technical development and business decisions emerge from structured discussions between the human researcher and the agent team, where the researcher adopts a policy of respecting agent-proposed strategies and solutions whenever sound.

---

## Key CMO Lessons and Constraints

### CASE-001 Rule — No Data Fabrication

When real data is unavailable, the correct response is to state "data not available." Never construct plausible-sounding figures. This is a hard constraint, not a stylistic preference. The EXP-001 case is itself a fabrication story — CMO writing that fabricates would be an operational contradiction.

### Positioning Shift (now locked)

- Old framing: "action blocking + better logs"
- Current framing: "machine-verifiable intent object at execution time"

The shift matters for Series 4 in particular. The old framing sounds like monitoring. The new framing is a different category entirely — it is about what the system knows at the moment of execution, not what it records afterward.

### Path B Formal Name

Path B is formally named: **Cross-Boundary Governance Projection (CBGP)**

Use this name consistently in any technical or semi-technical writing. "Path B" is acceptable as shorthand in internal documents.

---

## Article File Index (current state)

| Series | Status | File |
|--------|--------|------|
| Series 1 | Ready to publish | `content/articles/002_EXP001_HN_ready.md` |
| Series 2 | Draft complete | `content/articles/series2_ceo_false_completion_draft.md` |
| Series 3 | Draft complete | `content/articles/series3_jinjin_cross_model_draft.md` |
| Series 4 | Planned | (not yet drafted) |

---

## Next Actions

1. Publish Series 1 Monday 8:30 ET — no further edits required unless chairman reviews and requests changes
2. Series 2 and 3 are draft-complete — queue for review before scheduling publication dates
3. Series 4 drafting depends on Series 1 reception; begin outlining after Series 1 is live
