# cmux-win: Windows Port Overview

> [!NOTE]
> 이 문서는 `cmux-win`의 Windows 구현을 시작하기 전에 반드시 고정해야 하는 기준 문서다. 목표 설명이 아니라, 구현 순서와 경계 조건을 잠그는 문서로 취급한다.

## 1. 현재 상태와 목표 상태

| 구분 | 현재 저장소 상태 | 목표 상태 |
|------|------------------|-----------|
| 기준 구현 | `cmux\` 아래 macOS Swift 구현 | 루트 `src\`, `cli\`, `resources\` 아래 Windows 구현 |
| 역할 | 기능/UX 참조본 | 실제 Windows 산출물 |
| 변경 원칙 | `cmux\`는 참조 전용 | 새 Windows 코드는 `cmux\` 아래에 추가하지 않음 |

### 저장소 전환 원칙

1. `cmux\`는 **참조 전용(reference only)** 이며, **git submodule로 upstream `ee5902de`(v1.38.1)에 고정**한다. 패리티 판정 기준은 `_workspace\18-cmux-parity.md` §1을 따른다.
2. Windows 구현은 루트 기준 `src\`, `cli\`, `resources\`, `tests\`, `ports\`에만 추가한다.
3. 포팅 초기에 macOS 코드를 삭제하지 않는다.
4. 동작 parity 판단은 `cmux\`의 UX와 구조를 참고하되, Windows 설계 결정은 `_workspace\` 문서를 기준으로 한다.

## 2. v1 제품 목표

cmux-win v1은 macOS판의 핵심 작업 흐름을 Windows에서 자연스럽게 재현하는 것을 목표로 한다.

- 다중 workspace / vertical tabs
- split panes
- terminal panel + browser panel
- local IPC / CLI control
- notification ring + Windows toast
- PowerShell 중심 shell integration

다만 v1은 모든 플랫폼별 세부 동작까지 1:1 복제하지 않는다. **핵심 UX parity** 가 우선이며, 구현 복잡도가 큰 항목은 명시적으로 후순위로 미룬다.

## 3. 패키징과 배포 모델

v1의 기본 패키징 모델은 아래 하나로 고정한다.

- **Primary packaging model**: unpackaged desktop app
- **Runtime bootstrap**: Windows App SDK bootstrap
- **Installer**: Inno Setup
- **MSIX**: v1의 주 경로가 아님

이 결정은 다음 항목에도 영향을 준다.

- App startup bootstrap 순서
- AppNotification 등록 방식
- WebView2 / Windows App SDK 설치 검증
- 릴리스 파이프라인 구성

## 4. 지원 범위 매트릭스

> 2026-07-04: v1 지원 floor를 **Windows 11 22H2+ (build ≥ 22621)** 로 상향했다. Windows 10 지원 주장은 제거한다 (Win10 EOL + AT 검증 환경 부재). ConPTY passthrough가 기본 경로가 되고, standard 모드는 초기화 실패 폴백 및 `CMUX_CONPTY_MODE` override 경로로만 유지한다 (`adr-0002` 개정 참조).

| 항목 | Windows 11 22H2+ | 비고 |
|------|------------------|------|
| WinUI 3 기본 UI | 지원 | 필수 |
| Title bar customization | 지원 | |
| Mica backdrop | 지원 | 기본 backdrop |
| Acrylic backdrop | 지원 | `appearance.titlebar_style` 선택지 |
| ConPTY standard mode | 지원 | passthrough 실패 폴백 + env override 경로 |
| ConPTY passthrough | 지원 | 기본 경로 |
| WebView2 browser panel | 지원 | Evergreen runtime 필요 |
| AppNotification toast | 지원 | 등록 실패 시 degrade |

## 5. 공통 용어와 명명 규칙

> canonical glossary는 루트 `CONTEXT.md`가 소유한다. 이 섹션은 요약 규칙과 ID 형식을 유지하며, 용어/alias 변경 시 `CONTEXT.md`와 함께 갱신한다.

| 대상 | 규칙 |
|------|------|
| 사용자-facing 용어 | `CONTEXT.md`의 canonical term을 사용 (`window`, `workspace`, `pane`, `surface`, `browser panel`, `terminal panel`, `notification`) |
| IPC / settings JSON | `snake_case` |
| C++ types | `PascalCase` |
| C++ methods / fields | 기존 코드 스타일을 따르되, public API는 명확한 명사/동사 조합 유지 |

### ID 규칙

ID 형식은 전 문서에서 동일하게 쓴다.

- `window:<uuid>`
- `workspace:<uuid>`
- `pane:<uuid>`
- `surface:<uuid>`
- `notification:<uuid>`

UUID는 canonical lowercase string (`8-4-4-4-12`)를 사용한다.

## 6. 구현 착수 전 고정 사항

아래 다섯 항목이 고정되기 전에는 M1 이후 기능 구현에 들어가지 않는다.

1. 빌드 부트스트랩 단일 경로 (`11-build-release.md`)
2. 저장소 구조 전환 규칙 (`01-project-structure.md`)
3. 외부 의존성 pinning 위치와 정책 (`11-build-release.md`, `03-terminal-engine.md`)
4. IPC ID / error schema (`08-ipc-cli.md`)
5. 설정 precedence / migration / atomic write (`09-config-settings.md`)

## 7. 단계별 구현 범위

| Milestone | 목표 | 착수 조건 |
|-----------|------|-----------|
| M0 | 부트스트랩, 규약 고정, 기본 인프라 | 없음 |
| M1 | WinUI app / main window | M0 완료 |
| M2 | terminal core / renderer / IME / UIA | M0, M1 완료 |
| M3 | split, sidebar, IPC foundation | M1, M2 완료 |
| M4 | browser panel | M1, M3 완료 |
| M5 | CLI / automation / crash pipeline | M3, M4 완료 |
| M6 | settings / notifications / shell integration | M3, M5 완료 |
| M7 | release pipeline | M0 기반 완료 후 별도 gate |

## 8. G0 gate

M0 종료 시점에 아래가 모두 충족되어야 한다.

- bootstrap path가 문서 하나로 재현 가능
- `cmux\`와 새 Windows tree의 역할이 분리됨
- dependency pinning의 authoritative file이 정해짐
- terminal parser / passthrough / threading ADR이 확정됨
- IPC naming / error / payload 한도가 확정됨

## 9. 문서 운영 원칙

1. `_workspace\*.md`는 구현과 함께 갱신한다.
2. 규약이 바뀌면 관련 문서 전체를 같이 수정한다.
3. 구현보다 문서가 뒤처진 상태를 허용하지 않는다.
4. M7 release infra는 기능 문서와 분리해서 관리한다.
5. 용어/alias 변경은 `CONTEXT.md`와 이 문서를 함께 갱신한다.
6. durable task 상태는 `plans\` JSON과 `plans\session-state.md`에 남긴다.

## 10. autonomous execution layer

완전 자율 구현에서는 아래 authority split을 사용한다.

| 경로 | 역할 |
|------|------|
| `CONTEXT.md` | canonical user-facing terminology glossary |
| `_workspace\*.md` | 아키텍처, milestone, gate, 도메인 계약 |
| `plans\index.json`, `plans\milestones\*.json`, `plans\schema\task-registry.schema.json` | 기계 판독 task 상태, 의존성, acceptance, schema |
| `.rules\*.md` | 에이전트 운영 규칙 |
| `plans\session-state.md` | 세션 handoff snapshot |

새 세션의 기본 읽기 순서는 아래를 따른다.

1. `_workspace\00-overview.md`
2. `_workspace\12-tasks.md`
3. `plans\index.json`
4. 해당 milestone의 `plans\milestones\mN.json`
5. `plans\session-state.md`
6. 현재 task의 queue-number에 대응하는 `.rules\*.md` (`.rules\agent-workflow.md`의 queue mapping 기준)
7. 현재 milestone의 `doc_refs`, 다음에 선택한 task의 `doc_refs`

step 7의 `doc_refs`는 `active_milestone.doc_refs` 뒤에 `selected_task.doc_refs`를 merge하고, 중복은 앞에서부터 하나만 유지한다. `#fragment`는 Markdown heading slug를 뜻하며 파일 경로의 일부가 아니다.

`CONTEXT.md`는 기본 7단계에 넣지 않는다. 다만 용어/alias 변경, panel/workspace/notification naming, 또는 ambiguity 해소가 현재 작업에 포함되면 즉시 읽는다.

`_workspace/17-functional-spec.md`는 user-facing behavior, command catalog, settings UX를 구현하는 **task의** `doc_refs`에 해당 `#fragment` 섹션으로 포함한다. milestone-level 통째 참조는 두지 않는다(brief 토큰 절약 — whole-file 참조는 build_brief가 heading index로 캡한다).
