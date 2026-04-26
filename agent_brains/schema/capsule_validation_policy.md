# Capsule Validation Policy

This policy is static/reference-only. It does not implement runtime validation.

Minimum checks for future static validation:

- JSON syntax validation passes.
- Required files are present.
- DB contents are not opened.
- Source files are not edited by reference milestones.
- Runtime, daemon, scheduler, hook, boot, governance, and agent scripts are not run.
- Evidence paths exist or are clearly marked external/reference.
- `content_copied` is `false` for reference docs unless a future milestone
  intentionally summarizes content.
- Every capsule distinguishes persistent identity from execution tools.
- Every capsule defines open gaps.

No runtime validation, DB inspection, hook behavior, CIEU writes, or brain
writeback occurs under this policy.
