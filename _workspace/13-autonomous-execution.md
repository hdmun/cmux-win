# 13. Autonomous Execution

> [!IMPORTANT]
> 이 문서는 `_workspace\` 문서, `plans\` JSON, `.rules\` 규칙이 완전 자율 구현에서 어떤 권한을 가지는지 고정한다.

## 1. authority model

| 경로 | 역할 | authoritative 범위 |
|------|------|--------------------|
| `_workspace\*.md` | 사람/에이전트 공용 계약 문서 | 아키텍처, milestone, gate, 도메인 규약 |
| `plans\index.json`, `plans\milestones\*.json` | 기계 판독 실행 상태 | task 상태, 의존성, 예상 산출물, 검증 명령 |
| `.rules\*.md` | 에이전트 운영 규칙 | 읽기 순서, 문서 동기화, 저장소 경계, workflow |
| `plans\session-state.md` | 세션 handoff snapshot | 현재 milestone, 마지막 완료 task, blocker, 다음 추천 task |

`plans\`는 `_workspace\`를 대체하지 않는다. Markdown은 의도를 설명하고, JSON은 실행 상태를 추적한다.

## 2. startup read order

새 AI 세션은 기본적으로 아래 순서로 읽는다.

1. `_workspace\00-overview.md`
2. `_workspace\12-tasks.md`
3. `plans\index.json`
4. 현재 milestone의 `plans\milestones\mN.json`
5. `plans\session-state.md`
6. 현재 task의 queue-number에 대응하는 `.rules\*.md` (`.rules\agent-workflow.md`의 queue mapping 기준)
7. 선택한 task의 `doc_refs`가 가리키는 문서

`plans\index.json`의 `startup_read_order`는 위 7단계를 그대로 표현해야 하며, 동적 단계는 `path_template`/selection metadata로 해석 가능해야 한다.

## 3. task selection 규칙

기본 선택 알고리즘은 아래와 같다.

1. `status = "ready"` 인 task만 후보로 삼는다.
2. `depends_on`에 있는 모든 task가 `done`이면 선택 가능하다.
3. 같은 조건이면 현재 milestone의 가장 낮은 번호 task를 우선한다.
4. `blocked` task는 `blocked_by`와 `notes`를 확인한 뒤 재시도 여부를 결정한다.

## 4. status semantics

| status | 의미 |
|--------|------|
| `pending` | milestone이나 의존성 때문에 아직 착수 대상이 아님 |
| `ready` | 즉시 착수 가능 |
| `in_progress` | 누군가 현재 진행 중 |
| `blocked` | 외부 결정 또는 선행 조건 때문에 진행 불가 |
| `done` | 산출물과 검증 기준이 충족됨 |

상태 변경 시에는 관련 `plans\milestones\*.json`과 `plans\session-state.md`를 함께 갱신한다.

## 5. required task fields

각 task는 최소 아래 필드를 가진다.

- `task_id`
- `title`
- `status`
- `summary`
- `depends_on`
- `doc_refs`
- `touches`
- `acceptance`
- `commands`
- `outputs`
- `blocked_by`
- `notes`

JSON 필드 이름은 모두 `snake_case`를 사용한다.

## 6. handoff rules

세션 종료 전 에이전트는 `plans\session-state.md`에 아래를 반영한다.

- 현재 milestone
- 마지막 완료 task
- 현재 `in_progress` 또는 `blocked` task
- blocker 요약
- 다음 추천 task

세션 상태를 남기지 않고 종료하지 않는다.

## 7. phase-1 exclusions

phase 1에서는 아래를 도입하지 않는다.

- `plans\leases\` 같은 ephemeral claim/heartbeat 파일
- task 상태를 외부 서비스에만 저장하는 경로
- Markdown과 JSON의 dual-authority 운용

필요하면 phase 2에서 운영 레이어로 추가한다.
