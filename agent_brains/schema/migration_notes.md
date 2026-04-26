# Migration Notes

Use these schemas as reference first.

- Do not rewrite existing capsules immediately unless validation finds concrete
  problems.
- First use the schemas as a review and creation guide.
- Create a static validator script only after the schemas stabilize.
- Do not migrate DBs.
- Do not auto-generate capsules from weak evidence.
- Do not treat Codex, Claude Code, terminal sessions, or GitHub as role
  identities.
- Do not resolve name conflicts silently.

Future migration should be incremental: validate existing capsules, document
deviations, then patch only the smallest surface needed.
