# Action Surface Policy

Action surfaces are inventoried but not enabled.

Every action candidate in L4.1 must keep `live_enabled: false`.

High-risk surfaces such as push, external communication, daemon control, brain
writeback, memory ingestion, and CIEU persistence remain blocked or
candidate-disabled until explicit governance, operator approval, rollback, and
CIEU event boundaries exist.
