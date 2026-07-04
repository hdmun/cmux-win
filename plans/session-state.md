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
- 18개 validate warning은 의도된 것(doc/policy-freeze·release·AT gate task의 빈 `acceptance_auto`, m0-3 glob touches).
- 2026-07-04 grill-me 7개 결정 반영 완료: (1) v1 100% = v1 스코프 46기능, 기준 정의는 18 §1; (2) partial 재감사 doc-freeze task `m0-8` 등록 (절차는 18 §7); (3) milestone별 AT gate task `m0-9`/`m1-6`/`m2-8`/`m3-10`/`m4-5`/`m5-7`/`m6-12` 등록 — **자율 루프는 AT gate task를 집지 말고 사람에게 핸드오프** (plans/README 'AT gate 규칙'); (4) 하이브리드 빌드: cmux_app 셸만 vcxproj+MSBuild, 진입점은 cmake preset 불변 (11 §1.1), m0-1은 빌드 스파이크로 취급; (5) cmux/ submodule pin `ee5902de`(v1.38.1) — 이미 커밋되어 있었음, 문서 명기만 추가; (6) 지원 floor Win11 22H2+ 상향 — Win10 삭제, ADR-0002 개정(passthrough 기본), 00 §4/17 §12/09/03/cmux-spec 갱신; (7) 포팅 완료 선언 = M6 AT gate(`m6-12`) 통과, M7은 별도 배포 게이트.
