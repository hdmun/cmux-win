# 12. Tasks, Milestones, and Gates

> [!IMPORTANT]
> 이 문서는 구현을 실제로 시작할 수 있도록 milestone, 산출물, 검증 기준을 작업 단위로 쪼갠 실행 문서다.

## 1. milestone 개요

| Milestone | 목표 |
|-----------|------|
| M0 | bootstrap + 규약 고정 |
| M1 | app/window shell |
| M2 | terminal engine |
| M3 | split/sidebar/IPC foundation |
| M4 | browser panel |
| M5 | CLI + automation + crash pipeline |
| M6 | settings + notifications + shell integration |
| M7 | release infrastructure |

## 2. milestone progression rule

> 의존성의 authoritative 소스는 `plans/index.json`의 `milestones[].depends_on`이다.

- M1 착수 전: M0 완료
- M2 착수 전: M0, M1 완료
- M3 착수 전: M1, M2 완료
- M4 착수 전: M1, M3 완료
- M5 착수 전: M3, M4 완료
- M6 착수 전: M3, M5 완료
- M7 착수 전: 기능 범위 잠금 및 release-only backlog 분리 완료

### machine-readable execution state

이 문서는 milestone/gate의 사람용 설명을 유지한다. durable task 상태와 의존성 해석은 아래 파일을 함께 사용한다.

- `plans\index.json`
- `plans\milestones\m0.json` ~ `m7.json`
- `plans\schema\task-registry.schema.json`
- `plans\session-state.md`

Markdown 설명과 JSON 상태가 충돌하면, 계약 내용은 `_workspace\*.md`가 우선이고 task 상태는 `plans\`가 우선이다.

## 3. M0 task 상세

> task 상세(산출물, acceptance, commands)는 `plans/milestones/m0.json`을 참조한다.

## 4. M1~M7 task 목록

> task 목록 및 선행 조건은 `plans/milestones/m1.json` ~ `m7.json`을 참조한다.

## 5. validation matrix

| Milestone | 필수 검증 |
|-----------|-----------|
| M0 | configure/build/test entrypoint 문서화, dependency pinning 경로 고정 |
| M1 | first window creation, STA enforcement, shutdown order |
| M2 | terminal output, passthrough fallback, IME, UIA |
| M3 | split/focus restore, IPC errors, ACL, payload limit |
| M4 | WebView2 host, CDP errors, session retention |
| M5 | CLI handshake, command routing, crash/log policy |
| M6 | settings atomic write, migration backup, toast degrade, shell non-blocking |
| M7 | signing, installer prerequisite, distribution manifests, updater/release channel |

## 6. gate 정의

### G0

- build path 단일화
- dependency ownership 고정
- terminal/runtime contracts 확정
- protocol/schema/error contract 확정

### G5

- crash / privacy / log redaction 정책 확정

### G7

- signing, installer, distribution manifests, updater를 release-only gate로 검토

### milestone AT gate (2026-07-04)

- 각 기능 milestone(M0~M6)은 마지막에 human/AT gate task를 가진다 (`plans/README.md` 'AT gate 규칙').
- gate task는 해당 milestone의 모든 `acceptance_manual` 항목을 사람이 체크리스트로 소진해야 done이 된다.
- M6 AT gate 통과 = "Windows 포팅 완료" 선언 시점 (`_workspace/18-cmux-parity.md` §1).

## 7. release-only backlog

아래 항목은 구현 착수 범위와 분리한다.

- Azure Trusted Signing
- symbol upload backend
- Inno Setup polish
- `winget` manifest
- `scoop` manifest
- updater / appcast

release-only backlog의 machine-readable 상태는 `plans/milestones/m7.json`이 소유한다. 다만 M7은 기능 구현 milestone과 별도 gate로 유지한다.

## 8. 문서와 구현 동기화 규칙

기능 구현 시 아래 문서는 함께 수정한다.

- bootstrap 변경: `01`, `11`, `12`
- task 상태 변경: `plans/milestones/*.json`, `plans/session-state.md`
- terminology / naming / ID rule 변경: `CONTEXT.md`, `00`, 관련 도메인 문서
- autonomous execution / task registry 변경: `00`, `13`, `.rules/agent-workflow.md`, `plans/README.md`, `plans/index.json`, `plans/schema/task-registry.schema.json`, `plans/milestones/*.json`, `plans/session-state.md`
- task `doc_refs` / spec / glossary 연결 변경: `CONTEXT.md`, `00`, `13`, `17`, `plans/README.md`, `plans/index.json`, `plans/milestones/*.json`
- ADR / gate contract 변경: `14`, 관련 도메인 문서, `12`
- protocol 변경: `08`, `12`
- settings 변경: `09`, `12`
- panel lifecycle 변경: `03`, `04`, `06`
- scaffolding / test strategy 변경: `15`, `16`, `12`
