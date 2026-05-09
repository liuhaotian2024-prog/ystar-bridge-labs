# Aiden Agent-Native Company Messenger

Local-first company messenger for humans and agents.

## Start

```bash
python3 office/agent_native_messenger/server.py
```

Open `http://127.0.0.1:8784`.

## Rules

- Every formal message must contain human-readable text.
- Every formal message must contain the CIEU/CZL five tuple: `Y_star_t`, `X_t`, `U_t`, `Y_t_plus_1`, `R_t_plus_1`.
- Any agent-involved message must include governed model-orchestration metadata.
- External-agent contact is proposal-only in E124.
- Wallet and USDC support is proposal-only in E124; no payment or transfer is executed.
- Every formal message is validated by Y-star-gov and recorded in CIEUStore.
