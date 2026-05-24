# plans

`plans\`는 `_workspace\`를 보완하는 기계 판독 task/state 레이어다.

## authority split

| 경로 | 역할 |
|------|------|
| `_workspace\*.md` | 아키텍처, gate, 도메인 계약 |
| `plans\index.json` | milestone registry, read order, 상태 enum |
| `plans\milestones\*.json` | task 정의, 상태, 의존성, acceptance |
| `plans\session-state.md` | 세션 간 handoff snapshot |

## update rule

1. task 상태가 바뀌면 관련 milestone JSON을 먼저 갱신한다.
2. 계약이나 범위가 바뀌면 `_workspace\` 문서를 함께 갱신한다.
3. 세션 종료 전 `plans\session-state.md`를 최신 상태로 남긴다.
4. JSON은 `_workspace`의 설명을 복제하지 않고 실행 메타데이터만 담는다.

## phase-1 scope

- committed JSON만 사용
- lease/heartbeat 파일 없음
- `snake_case` + `schema_version` 고정
