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

- M1 착수 전: M0 완료
- M2 착수 전: M0, M1 완료
- M3 착수 전: M1, M2 완료
- M4 착수 전: M1, M3 완료
- M5 착수 전: M3, M4 완료
- M6 착수 전: M3, M5 완료
- M7 착수 전: 기능 범위 잠금 및 release-only backlog 분리 완료

## 3. M0 상세 작업

### M0-1. Build bootstrap skeleton

**산출물**

- `CMakeLists.txt`
- `CMakePresets.json`
- `src\CMakeLists.txt`
- `cli\CMakeLists.txt`
- `Directory.Packages.props`
- `NuGet.config`

**완료 기준**

- `dev-x64`, `dev-arm64` preset 정의
- configure/build/test entrypoint가 하나로 정리됨

### M0-2. Dependency pinning and overlay ports

**산출물**

- `vcpkg.json`
- `vcpkg-configuration.json`
- `ports\libvterm\...`

**완료 기준**

- libvterm overlay port 경로 고정
- vcpkg와 NuGet 책임 분리 완료

### M0-3. Runtime manifest and resources

**산출물**

- `resources\app.manifest`
- `.rc` resource skeleton

**완료 기준**

- DPI awareness, compatibility, icon/version resource 기준 확정

### M0-4. ADR freeze

**산출물**

- terminal threading contract
- passthrough fallback contract
- parser selection rationale
- panel lifecycle contract

**완료 기준**

- `_workspace\03`, `04`, `06`, `08`, `09`에 교차 참조 가능한 규약이 고정됨

### M0-5. Shared utilities

**산출물**

- logging skeleton
- string/encoding helper
- dispatcher helper

**완료 기준**

- background -> UI 경계 처리 유틸 확보

### M0-6. Settings and shortcut schema

**산출물**

- `settings.json` schema draft
- shortcut scopes and reserved actions

**완료 기준**

- precedence, atomic write, migration 규칙 문서화 완료

### M0-7. Release prework

**산출물**

- signing prerequisites checklist
- release infra backlog

**완료 기준**

- release-only 작업이 구현 착수 범위에서 분리됨

## 4. M1~M6 핵심 작업

| ID | 작업 | 선행 |
|----|------|------|
| M1-1 | WinUI 3 app + main window bootstrap | M0-1 |
| M1-2 | WindowManager and window lifecycle | M1-1 |
| M1-3 | titlebar / backdrop / fallback | M1-1 |
| M2-1 | ConPTY process and I/O pipeline | M0-4, M1-1 |
| M2-2 | libvterm wrapper + terminal buffer | M2-1 |
| M2-3 | Direct2D renderer | M1-1 |
| M2-4 | SwapChainPanel host integration | M2-3 |
| M2-5 | IME + UIA | M2-4 |
| M3-1 | ControlServer foundation | M1-2 |
| M3-2 | split layout controller + XAML projection | M2-4 |
| M3-3 | sidebar/workspace state projection | M1-2 |
| M3-4 | tab/workspace lifecycle rules | M3-2, M3-3 |
| M3-5 | IPC TDD for split/focus/state conflict | M3-1, M3-4 |
| M4-1 | browser panel host | M1-1 |
| M4-2 | omnibar and navigation UX | M4-1 |
| M4-3 | CDP automation contract | M4-1, M3-1 |
| M5-1 | `cmux.exe` CLI + capabilities handshake | M3-1 |
| M5-2 | workspace/panel control commands | M5-1 |
| M5-3 | crash/log/privacy policy freeze | M0-6 |
| M5-4 | crash capture integration | M5-3 |
| M6-1 | NotificationStore + toast | M3-3 |
| M6-2 | settings persistence and migration | M0-6 |
| M6-3 | shortcut routing engine | M6-2 |
| M6-4 | shell integration scripts | M5-1 |

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

## 7. release-only backlog

아래 항목은 구현 착수 범위와 분리한다.

- Azure Trusted Signing
- symbol upload backend
- Inno Setup polish
- `winget` manifest
- `scoop` manifest
- updater / appcast

## 8. 문서와 구현 동기화 규칙

기능 구현 시 아래 문서는 함께 수정한다.

- bootstrap 변경: `01`, `11`, `12`
- protocol 변경: `08`, `12`
- settings 변경: `09`, `12`
- panel lifecycle 변경: `03`, `04`, `06`
