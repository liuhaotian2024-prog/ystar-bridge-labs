# Lesson: 提新 ARCH 前必扫行业对标

**Date**: 2026-04-18
**Trigger**: Board 原话 "行业早就有改写的先例了，我却不知道，真是太耽误事儿啦" — 下午讨论 CZL-ARCH-14 REWRITE decision 后
**Audience**: future CEO sessions; Ethan-CTO (architecture integration); Secretary (archive lessons)
**Purpose**: codify the habit of proactively searching industry precedents BEFORE proposing a new ARCH concept, so Board is not forced to pattern-match on the spot.

**Research basis**: CEO 2026-04-18 proposed CZL-ARCH-14 (REWRITE decision — hook auto-corrects non-compliant payloads + proceeds). Ethan's architecture doc later added 6 industry analogs (black / prettier / Istio mTLS / SQL sanitize / clippy --fix / goimports). Board commented that these precedents are 10-20 years old and the delay was unnecessary. The pattern is "cross-domain pattern transfer" (auto-formatter at dev-time → governance at agent-runtime), which is legitimate CEO work, but requires explicit citation.

**Synthesis**: Most "new" governance problems are established patterns from adjacent domains (OS syscall → tool hook; type system → identity enforce; auto-formatter → REWRITE; service mesh → route-registry). CEO must surface these mappings upfront, not be caught by Board asking "is this really new?". The internal-repo scan rule `feedback_god_view_before_build` only covers "is this code already in our repo"; this lesson adds "is this pattern already in another domain".

## Hard constraint for future CEO

Before proposing any new ARCH task / new EnforceDecision value / new governance mechanism, CEO MUST:

1. Scan at least 3 industry precedents (OSS README, Wikipedia, arxiv, CNCF spec, OS history, classic papers).
2. For each precedent write 3 lines: (a) original-domain pattern name, (b) core mechanism, (c) cross-domain adaptation needed for our agent-runtime context.
3. Add an "Industry precedent" section at the top of the ARCH task description.
4. If scan turns up nothing across ≥3 domains → mark "no known precedent, propose net-new" (rare; needs strong justification).

## Negative example (today)

CZL-ARCH-14 task description lacked precedent citation. Ethan's supplement doc (`reports/cto/arch_14_15_rewrite_and_autospawn_20260418.md`) backfilled 6 analogs. Board reviewed and said the delay was unnecessary — if CEO had surfaced precedents at spec time, Board could have approved faster.

## Affected memory / norms

- `knowledge/shared/rules_first_team_norm_20260418.md` — "查规则先再动手" complementary norm (internal-repo rules)
- `MEMORY.md` entry `feedback_god_view_before_build` — existing internal scan habit
- This lesson upgrades those with external industry scan

## Review cadence

Apply on every new ARCH proposal. Board catches at any session are escalation triggers.
