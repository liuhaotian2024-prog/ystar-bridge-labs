# CMO (Sofia Blake) — theory/

The theory library for this role. One file per task type listed in
`role_definition/task_type_map.md`. Built via the **6-step theory
calibration protocol** documented in `governance/WORKING_STYLE.md` 第九条
(as the expansion of layer 3 of the 12-layer autonomous execution
framework).

## What goes here

One markdown file per task type. Filename: `<task_type>.md`
(snake_case, matching the task_type_map entries).

Each file contains theories relevant to that task type. Each theory
entry follows this format:

```markdown
## Theory name

- **Core proposition**: one or two sentences stating the theory's claim
- **Insight for this task type**: one sentence on how it applies here
- **Source**: paper / book / Wikipedia / author — with link where available
- **Date added**: YYYY-MM-DD
- **Added via**: [自主学习 | 任务触发 | gemma 提问 | 其他]
```

Theories are not added at random. The 6-step protocol is:

1. Decompose the task type into 2–4 core verbs
2. Map each verb to the nearest academic discipline
3. Search `<verb> theory` → most-cited classic → one-page summary
4. Deep-dive any theory that answers 2+ uncertainty-list items
5. Write the theory entry here
6. **Then** (and only then) look for concrete cases under this
   theory's frame

## How it is used

- When a directive in this task type arrives, the agent reads this
  file first — *before* looking at similar past cases
- Theory gives the conceptual frame; the frame decides what cases
  even count as relevant
- No theory for a task type = the agent is working blind on that type
  and should prioritize building it next idle cycle

## Owned by

The role itself. Theory quality is the role's own professional
responsibility, not a distillation task Secretary can do on its behalf.

## Source

Board capability system directive (2026-04-10); 6-step theory
calibration protocol in `governance/WORKING_STYLE.md` 第九条 layer 3.
