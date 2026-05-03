# E15A Feedback Capture Form

## 人话摘要

Owner 收到回复后，只需要选 action_id，写一句 raw_feedback_summary，再勾选反馈类型。没有真实发送 ledger 时，不要记录 no_response。

## Valid Actions
- Alice Labs AI Operations Consulting: action_id `c2_action_primary_001_cand_alicelabs_alicelabs`, ledger_id `ledger_c2_action_primary_001_cand_alicelabs_alicelabs`, feedback_event_id `feedback_c2_action_primary_001_cand_alicelabs_alicelabs`
- BotSquash AI Automation Agency: action_id `c2_action_primary_002_cand_botsquash_botsquash`, ledger_id `ledger_c2_action_primary_002_cand_botsquash_botsquash`, feedback_event_id `feedback_c2_action_primary_002_cand_botsquash_botsquash`
- WotAI AI Automation: action_id `c2_action_primary_003_cand_wotai_wotai`, ledger_id `ledger_c2_action_primary_003_cand_wotai_wotai`, feedback_event_id `feedback_c2_action_primary_003_cand_wotai_wotai`

## Feedback Types

no_response, positive_interest, request_for_details, price_question, referral, negative_not_relevant, negative_timing, unsubscribe_or_do_not_contact, safety_or_trust_concern, unclear_response

## Boundary

- Public evidence is not validation feedback.
- no_response requires a valid sent ledger and wait window.
- Do not invent customer response.
