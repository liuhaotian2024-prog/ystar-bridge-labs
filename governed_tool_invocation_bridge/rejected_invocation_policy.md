# Rejected Invocation Policy

The bridge rejects requests before invoking the tool when:

- An agent attempts direct tool invocation without a Pre-U packet.
- The governance decision is missing or does not allow local read-only invocation.
- The request asks for live action, external action, CIEU persistence, brain writeback, or memory ingestion.
- Requested sources are not present in the governed read-only observation tool registry.
- The bridge authorization is missing, not local-read-only, or permits a forbidden behavior.

Rejected requests produce generated fixture JSON only. They do not invoke the tool and do not read unsafe sources.

