# Governed Read-Only Observation Tool

This pack defines the first callable governed tool wrapper for the labs/company runtime.

The tool reads only curated generated/read-model JSON summaries from an explicit allowed source registry. It validates the invocation contract, rejects unknown or unsafe requested sources, returns a normalized company observation result, and emits a dry-run CIEU-compatible event envelope.

This is not live execution. It does not call network services, execute external actions, create GitHub issues or PRs, push git commits, control daemons, persist CIEU records, write brain/memory, approve candidates, or read raw runtime artifacts.

## Generated Outputs

- `generated/tool_contract.json`
- `generated/allowed_source_registry.json`
- `generated/sample_tool_invocation.json`
- `generated/sample_tool_result.json`
- `generated/rejected_unsafe_invocation.json`
- `generated/tool_invocation_trace.json`
- `generated/tool_cieu_event.json`
- `generated/tool_readiness_summary.json`
- `generated/tool_wrapper_report.md`

## CLI

Run the sample wrapper locally:

```bash
python3 governed_readonly_observation_tool/tools/run_readonly_observation_tool.py \
  --input governed_readonly_observation_tool/generated/sample_tool_invocation.json \
  --output governed_readonly_observation_tool/generated/sample_tool_result.json
```

Build all wrapper artifacts:

```bash
python3 governed_readonly_observation_tool/tools/build_readonly_observation_tool_artifacts.py
```

