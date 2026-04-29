# L6.13 Real Backend Activation

L6.13 does not ask for manual URLs. It activates real public read-only observation only when an approved backend and page-read adapter are configured by environment.

## Required controls

- `YSTAR_CONTROLLED_SEARCH_BACKEND` must be one of `brave_search_api`, `tavily_search_api`, or `serpapi` for a real provider run.
- `YSTAR_CONTROLLED_SEARCH_ALLOW_NETWORK` must be `1`.
- `YSTAR_CONTROLLED_PAGE_READ_BACKEND` must be `stdlib_public_http`.
- `YSTAR_CONTROLLED_PAGE_READ_ALLOW_NETWORK` must be `1`.
- The selected provider key must be present in the environment: `BRAVE_SEARCH_API_KEY`, `TAVILY_API_KEY`, or `SERPAPI_API_KEY`.

## No-secret rule

Never put provider keys in tracked files. The L6.13 scripts check whether a key exists, but they do not print, store, or serialize the key value.

## Safety boundary

The public page-read adapter is GET-only, public HTTP/HTTPS only, blocks private/local/internal targets, and performs no login, payment, form submission, posting, outreach, publication, MCP execution, or core writeback.

## Run flow

1. Export the approved backend and page-read environment variables in your local shell.
2. Run `scripts/l6_13_check_controlled_observation_env.sh` to verify presence-only configuration.
3. Run `scripts/l6_13_run_real_controlled_observation.sh`.
4. Review `real_mission_evidence_report/mission_evidence_report.md` and the console command output.

If configuration is missing, L6.13 emits `real_backend_activation_blocked_with_complete_activation_kit` and still runs the deterministic fixture proof.
