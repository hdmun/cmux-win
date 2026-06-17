# plans

`plans\`는 `_workspace\`를 보완하는 기계 판독 task/state 레이어다.

## authority split

| 경로 | 역할 |
|------|------|
| `_workspace\*.md` | 아키텍처, gate, 도메인 계약 |
| `plans\index.json` | milestone registry, read order, 상태 enum |
| `plans\milestones\*.json` | task 정의, 상태, 의존성, acceptance |
| `plans\schema\task-registry.schema.json` | milestone/task registry schema |
| `plans\session-state.md` | 세션 간 handoff snapshot |

## update rule

1. task 상태가 바뀌면 관련 milestone JSON을 먼저 갱신한다.
2. milestone이 완료되면 `plans\index.json`의 해당 milestone `status`를 `done`으로, `active_milestone`을 다음 milestone으로 갱신한다.
3. 계약이나 범위가 바뀌면 `_workspace\` 문서를 함께 갱신한다.
4. `plans\index.json` 또는 `plans\milestones\*.json`을 바꿨으면 `plans\schema\task-registry.schema.json` 기준 validation을 수행한다.
5. 세션 종료 전 `plans\session-state.md`를 최신 상태로 남긴다.
6. JSON은 `_workspace`의 설명을 복제하지 않고 실행 메타데이터만 담는다.

## `doc_refs` resolution rule

- merge order: `active_milestone.doc_refs` → `selected_task.doc_refs`
- dedupe: 앞에서부터 첫 항목만 유지
- string format: `relative/path.md` 또는 `relative/path.md#heading-slug`
- `#fragment`는 같은 Markdown 파일의 heading slug를 뜻한다
- user-facing behavior, command catalog, settings UX를 구현하는 task는 `_workspace/17-functional-spec.md`의 해당 `#fragment` 섹션을 task `doc_refs`에 포함한다 (milestone-level 통째 참조 금지 — build_brief가 whole-file을 heading index로 캡한다)
- glossary-owned terminology를 직접 다루는 milestone 또는 task는 `CONTEXT.md`를 `doc_refs`에 포함한다

## `commands` vs `acceptance_auto` / `acceptance_manual`

- `commands`는 에이전트가 실행하는 ordered validation commands다
- `acceptance_auto`는 **기계 검증 done criteria(gating)**, `acceptance_manual`은 **사람/AT 확인(비-gating, 큐잉)** 이다. 자율 루프는 `acceptance_auto`만으로 done을 판정한다 (`cmux-plan verify`의 `auto_pass`)
- `acceptance_auto` 항목은 literal command string 또는 `tc-*` test case identifier만 사용한다 (`manual:` 항목 금지 — `validate`가 강제)
- `tc-*` acceptance를 쓰면 그 test case를 포함해 검증하는 command가 `commands`에 있어야 한다
- doc/policy freeze task는 `acceptance_auto`를 `cmux-plan check-docs <task_id>`(doc-linter anchor 검사)로 채우고 완성도는 `acceptance_manual`에 둔다. 이때 `commands`도 같은 check-docs 명령을 가진다
- release-only task(m7 등)는 외부 CI/CD 파이프라인에서만 실행되는 특성상 `commands`를 비울 수 있다. 이 경우 task의 `notes`에 "commands: [] — release-only task; executed via external CI/CD pipeline" 이유를 명시한다

## validation command

`plans\` JSON을 수정했으면 최소 아래 명령으로 schema validation을 수행한다.

```powershell
Get-ChildItem .\plans\milestones\*.json |
  ForEach-Object {
    Get-Content -Raw $_.FullName | Test-Json -SchemaFile .\plans\schema\task-registry.schema.json
  }
```

## phase-1 scope

- committed JSON만 사용
- lease/heartbeat 파일 없음
- `snake_case` + `schema_version` 고정
- `plans\session-state.md`는 Markdown handoff snapshot으로 유지
- machine-readable handoff mirror는 phase 2 운영 레이어로만 검토
