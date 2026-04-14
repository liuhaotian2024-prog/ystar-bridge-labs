## Mission 6: A025 Active Read + Passive Injection (CROBA Meta-Fix)
Engineers: eng-governance (Maya Patel) + eng-platform (Ryan Park)
Priority: P1
L-label: L7 (Leadership Loop - eliminate CROBA root cause)

Gap: Sub-agents don't auto-read role definitions, causing CROBA drift. CEO/CTO manually remind.

Acceptance Criteria:
- [ ] Maya: Extend UserPromptSubmit hook in `ystar/adapters/hooks.py` — inject full ForgetGuard rule text when Edit/Write targets high-risk paths
- [ ] Ryan: Extend subagent spawn logic — force `cat .claude/agents/{role}.md` before any tool call
- [ ] Add CIEU event `ROLE_DEFINITION_INJECTED` on each injection
- [ ] Test: spawn eng-kernel sub-agent, verify role def read logged
- [ ] Commit both changes, report hash + L7 label

Files in scope: ystar/adapters/hooks.py, .claude/agents/*.md (read-only)
