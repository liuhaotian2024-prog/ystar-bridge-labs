# Governed Tool Invocation Bridge

This pack routes the first governed read-only tool call through a Pre-U bridge.

The bridge proves this chain:

agent tool request -> Pre-U tool packet -> governance decision envelope -> bridge authorization -> governed read-only observation tool -> normalized result -> dry-run CIEU event -> residual delta -> next work recommendation

The bridge is local-only and dry-run only. It does not execute live actions, call network services, create GitHub issues or PRs, push git commits, control daemons, persist CIEU records, write brain/memory, approve candidates, or read raw runtime artifacts.

## Commands

Build all generated bridge artifacts:

```bash
python3 governed_tool_invocation_bridge/tools/build_tool_invocation_bridge.py
```

Run the bridge over the sample request:

```bash
python3 governed_tool_invocation_bridge/tools/run_governed_tool_bridge.py \
  --request governed_tool_invocation_bridge/generated/agent_tool_request.json \
  --output-dir governed_tool_invocation_bridge/generated
```

