# L6.10W Reviewed Seed Locator Injection & Tiny Observation Retry v0

L6.10W narrows the locator blocker: it either uses one existing reviewed seed
locator from local registry artifacts or emits a precise `USER_ACTION_REQUIRED`
packet asking for exactly one public URL tied to the selected work order.
