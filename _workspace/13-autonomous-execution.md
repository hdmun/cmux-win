# 13. Autonomous Execution

> [!IMPORTANT]
> 이 문서는 `_workspace\` 문서, `plans\` JSON, `.rules\` 규칙이 완전 자율 구현에서 어떤 권한을 가지는지 고정한다.

## 1. authority model

| 경로 | 역할 | authoritative 범위 |
|------|------|--------------------|
| `CONTEXT.md` | canonical terminology glossary | user-facing 용어, 금지 alias, 용어 충돌 해소 |
| `_workspace\*.md` | 사람/에이전트 공용 계약 문서 | 아키텍처, milestone, gate, 도메인 규약 |
| `plans\index.json`, `plans\milestones\*.json`, `plans\schema\task-registry.schema.json` | 기계 판독 실행 상태와 schema | task 상태, 의존성, `doc_refs` 해석 규칙, 예상 산출물, 검증 명령 |
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
7. 현재 milestone의 `doc_refs`, 다음에 선택한 task의 `doc_refs`가 가리키는 문서

`plans\index.json`의 `startup_read_order`는 위 7단계를 그대로 표현해야 하며, 동적 단계는 `path_template`/selection metadata로 해석 가능해야 한다.

step 7의 `doc_refs` 해석은 아래를 따른다.

- merge order: `active_milestone.doc_refs` → `selected_task.doc_refs`
- dedupe: 앞에서부터 첫 항목만 유지
- `#` 뒤 fragment는 파일 경로가 아니라 같은 Markdown 파일 안의 heading slug를 뜻한다
- user-facing behavior, command catalog, settings UX를 구현하는 task는 `_workspace/17-functional-spec.md`의 해당 `#fragment` 섹션을 task `doc_refs`에 포함한다 (milestone-level 통째 참조 금지)

`CONTEXT.md`는 기본 7단계 startup read order에 승격하지 않는다. 대신 아래 중 하나에 해당하면 즉시 읽는다.

- 현재 milestone 또는 task의 `doc_refs`가 `CONTEXT.md`를 가리킬 때
- 수정 범위가 window / workspace / pane / surface / terminal panel / browser panel / notification 용어를 건드릴 때
- alias 충돌이나 용어 ambiguity를 풀어야 할 때

## 3. task selection 규칙

기본 선택 알고리즘은 아래와 같다.

1. `status = "ready"` 인 task만 후보로 삼는다.
2. 아래 두 조건을 **모두** 충족해야 선택 가능하다.
   - **milestone gate**: `index.json` milestones[]에서 해당 milestone의 `depends_on`에 있는 모든 선행 milestone의 status가 `done`
   - **task-level 의존성**: 현재 task의 `depends_on`에 있는 모든 task가 `done`
3. 같은 조건이면 현재 milestone의 가장 낮은 번호 task를 우선한다.
4. `blocked` task는 `blocked_by`와 `notes`를 확인한 뒤 재시도 여부를 결정한다.

> milestone gate는 "어떤 milestone을 착수할 수 있는가"를 결정하고, task-level 의존성은 "해당 milestone 내에서 어떤 순서로 진행하는가"를 결정한다. 두 조건은 AND 관계이며, task-level 의존성은 milestone gate 통과를 전제로 한 세부 순서다.

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
- `queue_number`
- `title`
- `status`
- `summary`
- `depends_on`
- `doc_refs`
- `touches`
- `acceptance_auto`
- `acceptance_manual`
- `commands`
- `outputs`
- `blocked_by`
- `notes`

JSON 필드 이름은 모두 `snake_case`를 사용한다.

`queue_number`의 허용 범위와 의미는 `.rules/agent-workflow.md`의 queue mapping이 authoritative source다.

## 6. handoff rules

세션 종료 전 에이전트는 `plans\session-state.md`에 아래를 반영한다.

- 현재 milestone
- 마지막 완료 task
- 현재 `in_progress` 또는 `blocked` task
- blocker 요약
- 다음 추천 task

세션 상태를 남기지 않고 종료하지 않는다.

### milestone 완료 시 필수 갱신

milestone의 마지막 task가 `done`이 될 때 아래를 모두 반영한다.

1. 완료된 milestone JSON의 모든 task가 `done`인지 확인
2. `plans\index.json`의 해당 milestone 항목에 `"status": "done"` 설정
3. 다음 착수 가능한 milestone을 결정해 `plans\index.json`의 `active_milestone` 값 갱신
4. 다음 milestone의 `status`를 `"ready"` 또는 `"pending"` 중 맞는 값으로 설정
5. `plans\session-state.md` 갱신

`active_milestone`과 milestone `status`는 `plans\index.json`이 authoritative source다. mN.json의 task status와 index.json의 milestone status가 불일치하면 task status를 기준으로 index.json을 수정한다.

phase 1의 `plans\session-state.md`는 Markdown snapshot을 유지한다. 기계 판독 handoff 레이어를 추가하더라도 phase 2 운영 레이어로 취급하며, 기존 Markdown snapshot을 암묵적으로 대체하지 않는다.

## 7. phase-1 exclusions

phase 1에서는 아래를 도입하지 않는다.

- `plans\leases\` 같은 ephemeral claim/heartbeat 파일
- task 상태를 외부 서비스에만 저장하는 경로
- Markdown과 JSON의 dual-authority 운용
- `plans\session-state.md`를 대체하는 별도 handoff JSON mirror

필요하면 phase 2에서 운영 레이어로 추가한다.

## 8. execution harness (cmux-plan)

자율 루프의 결정론적 기계 작업은 `.claude/skills/cmux-win-autonomous-execution/`의 `cmux-plan` CLI가 수행한다 (stdlib-only Python 3, 설치 불필요).

| subcommand | 역할 |
|------------|------|
| `next` | 다음 eligible task 선택 (milestone gate 전이폐쇄 + task deps + status) |
| `brief <id>` | merged `doc_refs`를 `#fragment` 단위로 슬라이스한 컴팩트 task brief (whole-file은 heading index로 캡) |
| `validate` | schema(Test-Json) + 의존성·순환·전이폐쇄 gate·outputs⊆touches·tc↔ctest·doc-linter |
| `check-docs <id>` | 단일 task의 doc_ref `#fragment` 해소 검증 (doc-freeze acceptance) |
| `verify <id>` | `commands` 실행 → `auto_pass` + `manual_pending` (빌드 부재 시 graceful) |
| `status <id> <state>` | atomic 상태 변경 + index rollup + pending→ready 승격 + session-state 핸드오프 |

- 에이전트는 이 명령들을 도구로 호출하고 **구현 단계만 직접 수행**한다 (LLM을 호출하는 자율 daemon이 아니다).
- `plans/*.json` 또는 `_workspace/*.md`를 수정하면 `cmux-plan validate`가 **0 error**여야 한다.
- 골든 테스트: `python -m unittest discover .claude/skills/cmux-win-autonomous-execution/tests`.
