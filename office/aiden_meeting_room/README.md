# Aiden CEO Meeting Room

Small repo-grounded meeting runtime for the original `ystar-bridge-labs` company repo.

Run:

```bash
python3.11 office/aiden_meeting_room/meeting_cli.py "Aiden, what should we build now to get the first dollar as quickly as possible?"
```

Owner-chat routing convention:

```text
Aiden: what should we build now to get the first dollar as quickly as possible?
```

`Aiden:` or `Aiden：` is the explicit CEO meeting-room prefix. Messages with
that prefix route to the governed Aiden behavior center. Messages without that
prefix remain normal Codex/executor conversation and must not be treated as
Aiden speaking.

Strategy routing:

If an `Aiden:` message asks about market strategy, first cash, product shape,
pricing, customer validation, competitors, or CPA/workflow rescue, the router
auto-upgrades the message to the governed E104 adaptive market-intelligence
strategy runtime instead of returning a plain meeting-room answer. The response
must include 6D brain provenance, current public-read market evidence,
competitor saturation, founder-market fit, customer-visible differentiation,
pricing-hypothesis boundary, strongest validation question, Y-star-gov decisions,
CIEUStore write status, and no-send owner-gated L4 packet status.

This reads safe local company context and answers as Aiden CEO. It does not send email, contact customers, publish, pay, submit forms, create accounts, read secrets/env/DB/WAL/SHM/log/active-agent marker contents, or write core memory/CIEU DB.
