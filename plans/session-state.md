# Session State

> [!IMPORTANT]
> 이 문서는 세션 간 handoff를 위한 snapshot이다. 장문의 작업 일지를 쓰지 말고, 다음 에이전트가 바로 이어받을 수 있는 최소 상태만 유지한다.

## Current milestone

- milestone: `M0`
- active_task_ids: `[]`

## Last completed task

- task_id: `m0-7` (+ milestone quality improvements)
- summary: `Milestone JSONs fully production-ready: queue_number, canonical build targets, m5.json rewrite, m0-4/m0-6/m0-7 done, functional spec written. Acceptance/outputs/depends_on quality improvements applied (see Notes).`

## Blocked tasks

| task_id | blocker | next action |
|---------|---------|-------------|
| - | - | - |

## Next recommended task

- task_id: `m0-1`
- reason: `M0 has 4 ready tasks (m0-1, m0-2, m0-3, m0-5). m0-1 builds the CMake/vcpkg skeleton; everything else depends on it.`

## Notes for next session

- Startup read order: `_workspace/00-overview.md` → `_workspace/12-tasks.md` → `plans/index.json` → `plans/milestones/m0.json` → `plans/session-state.md` → queue rules from `.rules/agent-workflow.md` → task `doc_refs`. Read `CONTEXT.md` immediately when the task touches canonical terminology or glossary-owned aliases.
- **Plan metadata cleanup completed (this session)**:
  - Every milestone task now has a `queue_number` (see `.rules/agent-workflow.md` queue table).
  - All build targets use canonical names: `cmux_app` / `cmux_cli` (not `cmux-win`).
  - `m5.json` was fully rewritten to restore the missing `m5-2` task (was lost to duplicate-key bug).
  - `m0-4` (ADR freeze), `m0-6` (settings schema), `m0-7` (release prework) marked `done` — outputs already existed.
- **Functional spec created (this session)**:
  - `_workspace/17-functional-spec.md` — comprehensive Windows v1 feature spec covering all 15 domains.
  - Reviewed and corrected by sub-agents: IPC catalog expanded, error codes completed, pipe discovery flow added, env-var rename map documented, cross-window move contradiction resolved, titlebar/backdrop matrix inlined, shortcut JSON schema added, appendix 18 (intentional divergences) added.
  - `.rules/docs-sync.md` updated to reference this file.
- **Milestone quality improvements completed (this session)**:
  - **Area A — acceptance/commands sync**: 11 tasks (m0-5, m1-2, m2-1~m2-3, m2-5, m4-3, m6-1~m6-4) now have matching `ctest --preset dev-x64 -R ...` entries in both `commands` and `acceptance`.
  - **Area B — m3 file-level outputs + tc- tests**: m3-1~m3-4 `outputs` expanded to exact file paths; `commands` populated; acceptance enriched with `tc-*` test cases (total: 14 new tc- cases across 4 tasks).
  - **Area C — m2-4 depends_on**: Fixed `["m2-3"]` → `["m2-1", "m2-2", "m2-3"]` to enforce ConPTY/vterm/D2D ordering.
  - All 7 milestone JSONs validated (JSON parse OK).
- **Hybrid documentation overlay added (this session)**:
  - Root `CONTEXT.md` now owns canonical terminology for window / workspace / pane / surface / panel usage.
  - `.rules/docs-sync.md`, `_workspace/00-overview.md`, and `_workspace/12-tasks.md` now require terminology / naming / ID-rule changes to stay in sync with `CONTEXT.md`.
  - `_workspace/adr/` remains the canonical ADR home; `_workspace/14-adr-guide.md` now favors shorter ADRs for hard-to-reverse trade-offs instead of long boilerplate.
- **Remaining plan quality issues** *(none — all 3 identified issues resolved)*.
