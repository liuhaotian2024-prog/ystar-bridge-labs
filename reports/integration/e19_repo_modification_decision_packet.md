# E19 Repo Modification Decision Packet

- cross_repo_mutation_performed: false
- bridge_labs_only_delivery: true
- external_action_executed: false

| repo | decision | reason |
| --- | --- | --- |
| ystar-bridge-labs | bridge_labs_update_only | E19 control room is company runtime and should be delivered in bridge-labs. |
| gov-mcp | future_gov_mcp_update_required | No immediate mutation; future real provider adapter implementation belongs here. |
| Y-star-gov | no_change_needed | Governance kernel remains canonical; E19 does not require contract mutation. |
| ystar-company | future_ystar_company_migration_required | Historical assets can be reviewed later, but should not be active authority now. |
