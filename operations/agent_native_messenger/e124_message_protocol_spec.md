# E124 Message Protocol Spec

Protocol: `aiden_agent_native_company_messenger_protocol_v1`

## Required Message Shape
- `human_readable_text`
- `cieu_five_tuple.Y_star_t`
- `cieu_five_tuple.X_t`
- `cieu_five_tuple.U_t`
- `cieu_five_tuple.Y_t_plus_1`
- `cieu_five_tuple.R_t_plus_1`

## Supported Paths
- human_to_agent
- agent_to_human
- agent_to_agent
- group_meeting
- file_attachment_metadata
- image_attachment_metadata
- wallet_proposal_no_payment
- external_agent_proposal_no_send

## Boundaries
- local_messenger_only: true
- external_agent_delivery: owner_approved_future_boundary_required
- wallet: proposal_only_until_payment_boundary_exists
- CIEUStore: mandatory for every formal message
- model_orchestration: mandatory when any agent participates
