# Repository Delivery Bridge Status

- bridge_root: /tmp/ystar_delivery_bridge
- transport_mode: host_local_bridge
- bridge_installed: true
- launch_agent_plist_exists: true
- launch_agent_loaded: true
- pending_jobs: 0
- running_jobs: 0
- completed_artifacts: 0
- failed_artifacts: 3
- future_owner_delivery_commands_required: false
- per_milestone_bootstrap_allowed: false
- job_submission_contract: `scripts/repository_delivery_bridge_submit.py`
- credentials_printed: false

Future Codex tasks must submit bridge jobs.
Future Codex tasks must not ask owner to run per-milestone bootstrap.
Owner manual terminal command is only allowed for one-time bridge repair/reinstall.

## Activation Proof

- status: submitted_for_remote_confirmation
- validation_scope: bridge status, submitter, worker py_compile and bridge status/transport tests
- future_owner_delivery_commands_required: false
- per_milestone_bootstrap_allowed: false
