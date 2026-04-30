# L7.4R Real Labs Office Web UI Runtime

The prior `labs_office_home.html` was audited and found owner-usable: **False**.

This sprint creates a real local office runtime at:

`http://127.0.0.1:8765`

Run:

`bash scripts/run_l7_labs_office_web.sh --mode serve`

The page shows the recovered Y*Bridge Labs team, agent rooms, work queue, pending approvals, blocked actions, and local-only message/team task forms that create JSON packets without external side effects.
