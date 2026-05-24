# Session State

> [!IMPORTANT]
> 이 문서는 세션 간 handoff를 위한 snapshot이다. 장문의 작업 일지를 쓰지 말고, 다음 에이전트가 바로 이어받을 수 있는 최소 상태만 유지한다.

## Current milestone

- milestone: `M0`
- active_task_ids: `[]`

## Last completed task

- task_id: `none`
- summary: `not started`

## Blocked tasks

| task_id | blocker | next action |
|---------|---------|-------------|
| - | - | - |

## Next recommended task

- task_id: `m0-1`
- reason: `bootstrap files do not exist yet and M0 has no completed outputs`

## Notes for next session

- Startup read order: `_workspace/00-overview.md` → `_workspace/12-tasks.md` → `plans/index.json` → `plans/milestones/m0.json` → `plans/session-state.md` → the current task queue's `.rules/*.md` from `.rules/agent-workflow.md` → the selected task's `doc_refs`.
