# Session State

> [!IMPORTANT]
> 이 문서는 세션 간 handoff를 위한 snapshot이다. 장문의 작업 일지를 쓰지 말고, 다음 에이전트가 바로 이어받을 수 있는 최소 상태만 유지한다.

## Current milestone

- milestone: `M0`
- active_task_ids: `[]`

## Last completed task

- task_id: `m0-7`
- summary: `Milestone metadata cleaned up (m0-4/m0-6/m0-7 marked done). Functional spec written and reviewed. All milestone JSONs fixed for autonomous execution readiness.`

## Blocked tasks

| task_id | blocker | next action |
|---------|---------|-------------|
| - | - | - |

## Next recommended task

- task_id: `m0-1`
- reason: `M0 has 4 ready tasks (m0-1, m0-2, m0-3, m0-5). m0-1 builds the CMake/vcpkg skeleton; everything else depends on it.`

## Notes for next session

- Startup read order: `_workspace/00-overview.md` → `_workspace/12-tasks.md` → `plans/index.json` → `plans/milestones/m0.json` → `plans/session-state.md` → queue rules from `.rules/agent-workflow.md` → task `doc_refs`.
- **Plan metadata cleanup completed (this session)**:
  - Every milestone task now has a `queue_number` (see `.rules/agent-workflow.md` queue table).
  - All build targets use canonical names: `cmux_app` / `cmux_cli` (not `cmux-win`).
  - `m5.json` was fully rewritten to restore the missing `m5-2` task (was lost to duplicate-key bug).
  - `m0-4` (ADR freeze), `m0-6` (settings schema), `m0-7` (release prework) marked `done` — outputs already existed.
- **Functional spec created (this session)**:
  - `_workspace/17-functional-spec.md` — comprehensive Windows v1 feature spec covering all 15 domains.
  - Reviewed and corrected by sub-agents: IPC catalog expanded, error codes completed, pipe discovery flow added, env-var rename map documented, cross-window move contradiction resolved, titlebar/backdrop matrix inlined, shortcut JSON schema added, appendix 18 (intentional divergences) added.
  - `.rules/docs-sync.md` updated to reference this file.
- **Remaining plan quality issues** (not yet fixed — future session work):
  - Most tasks still have `manual:`-only acceptance; executable `ctest` checks should be added per `_workspace/16-test-strategy.md`.
  - `m3-1`–`m3-4` have directory-only `outputs`; should be expanded to file-level.
  - `m2-4` and `m2-5` `depends_on` chains are weaker than their stated acceptance scope.
