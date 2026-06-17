# Session State

> 세션 간 handoff snapshot. 최소 상태만 유지한다. 변경 이력은 git에 남긴다.

## Current milestone

- milestone: `m0`
- active_task_ids: `[]`

## Last completed task

- task_id: `-` (이번 세션은 자율 실행 하네스 + 계획계층 정비; 앱 구현 task 미착수)

## Blocked tasks

| task_id | blocked_by | notes |
|---------|-----------|-------|
| - | - | - |

## Next recommended task

- task_id: `m0-1`
- reason: `status ready, deps done, milestone gate satisfied (cmux-plan next)`

## Notes for next session

- 자율 실행은 `cmux-plan` CLI로 구동한다: `next` → `status <id> in_progress` → `brief <id>` → 구현 → `verify <id>` → `validate` → `status <id> done`. 스킬: `.claude/skills/cmux-win-autonomous-execution/` (SKILL.md, `scripts/`, `tests/`).
- acceptance는 `acceptance_auto`(기계 gating) / `acceptance_manual`(사람·AT, 큐잉)로 분리됨. `plans/*` 또는 `_workspace/*` 수정 후 `cmux-plan validate`가 **0 error**여야 한다.
- parity 7갭이 `m3-7`~`m6-11` (10 task)로 등록됨; 계약 stub은 08 §13/§14·claude-hook payloads, 17 §3.8/§4.9, 06 §10에 있음 (18 §6.5).
- 11개 validate warning은 의도된 것(doc/policy-freeze·release task의 빈 `acceptance_auto`, m0-3 glob touches).
