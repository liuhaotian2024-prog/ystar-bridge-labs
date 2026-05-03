# E15D Outbound Authorization Envelope Request

## 人话摘要

这是未来 E16 pilot 的窄授权请求，不是 owner approval。默认状态是 `owner_review_required`，所以 send-gated 执行仍然 blocked。

- draft_only_allowed_now: true
- send_allowed_now: false
- max_actions_per_batch: 3
- max_actions_per_day: 1

## Not Authorized

- real email/message send before owner activation
- publication
- payment
- account creation
- form submission
- login
- external validation submission
- customer system access
- legal or financial commitment
- credential disclosure
- core brain/CIEU/memory writeback
