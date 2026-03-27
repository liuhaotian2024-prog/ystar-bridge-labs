# Case Study #001: Dependency-Based Obligation Gap

**Discovered:** 2026-03-26 | **Issue:** liuhaotian2024-prog/Y-star-gov#1

## What happened

Y* Bridge Labs has 5 AI agents governed by Y*gov. On 2026-03-26, the Board issued a P0 task (CTO install verification) and a lower-priority task (Directive #004 leadership briefs). The agents executed both in parallel because OmissionEngine only tracks time-based deadlines, not task dependencies. The P0 blocker was not enforced as a prerequisite.

## What Y*gov should have done

Blocked Directive #004 execution until the P0 was resolved. Emitted a `DEPENDENCY_BLOCKED` violation.

## Product improvement

GitHub Issue #1: Add `depends_on` parameter to `add_obligation()`. OmissionEngine will enforce task ordering, not just timing.

## Sales evidence

This proves Y*gov discovers its own gaps by running on itself. A governance framework that improves from its own audit trail is the product thesis.
