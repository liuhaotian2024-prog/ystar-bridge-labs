# E41 Whole Bridge Labs Runtime Archaeology

- Whole repository runtime inspected.
- Original runtime components and recent E31-E40 line were separated.
- Missing integration points documented.

## Components

- component: root company operating identity, function: Defines company identity, agent expectations, and operating frame., status: active
- component: Board/CEO/role governance, function: Defines CEO and functional role authority surfaces., status: active
- component: CZL closure loop, function: Tracks subgoals, completion, closure, and learning boundaries., status: active
- component: CIEU evidence chain references, function: Evidence chain references and event taxonomy; E41 evidence graph does not replace this., status: active
- component: gov-order NL pipeline, function: Natural-language governance order handling and undo support., status: active
- component: CROBA / pre-action boundary, function: Pre-action routing and build gates before operational movement., status: active
- component: daily operating memory, function: Session handoff, world state, daily briefs, and operational continuity., status: active
- component: directive tracking, function: Tracks Board/owner directives and pending queues., status: active
- component: repository delivery bridge, function: Host-local safe commit/push delivery boundary., status: active

## Missing integration points

- E31-E40 artifacts are mostly milestone-local JSON/reports with limited linkage into daily briefs.
- Recent line is connected to CEO KG deltas and CZL closures, but weakly connected to DIRECTIVE_TRACKER.md.
- Frontier capability import was scanned in E38 but lacked a permanent import loop before E41.
