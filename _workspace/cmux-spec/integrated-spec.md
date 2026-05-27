# cmux 통합 참조 스펙 (Windows 포트 관점)

> **대상**: cmux-win 에이전트·개발자  
> **기준**: `cmux/` read-only 소스 트리 + `_workspace/17-functional-spec.md` + `_workspace/18-cmux-parity.md`  
> **갱신**: 2026-06 (초기 에이전트 작성)  
> **원칙**: `cmux/`는 절대 수정하지 않는다. Windows 포트 구현은 `cmux-win/src/`에만 작성.

---

## 1. cmux란 무엇이며 cmux-win에 왜 중요한가

**cmux**는 AI 코딩 에이전트(Claude Code, OpenCode, Codex 등)를 위해 설계된 **네이티브 macOS 터미널 앱**이다. 핵심 가치는 다음 세 가지다.

1. **소켓 API 기반 자동화**: Unix 소켓(`/tmp/cmux*.sock`)을 통한 v1/v2 JSON 프로토콜로 에이전트가 터미널·브라우저·창을 프로그래매틱하게 제어한다.
2. **멀티 워크스페이스 사이드바**: git 브랜치·CWD·포트·알림을 탭 단위로 표시하는 수직 사이드바. 에이전트가 context를 잃지 않고 여러 작업을 병렬 실행할 수 있다.
3. **인앱 브라우저 + CDP 자동화**: WKWebView 패인을 터미널과 동일한 창 안에 배치하고, `cmux browser` 명령으로 DOM 상호작용·스냅샷·스크린샷을 에이전트가 직접 수행한다.

**cmux-win의 목표**는 이 기능 집합을 Windows 네이티브 스택(WinUI 3 + ConPTY + libvterm + D2D + WebView2 + Named Pipe)으로 동등하게 구현하는 것이다. macOS 구현은 **계약과 동작 정의의 원천**이고, 코드를 그대로 이식하는 대상이 아니다.

**라이선스**: AGPL-3.0-or-later  
**플랫폼 요건(원본)**: macOS 13+ — Windows 포트 최소 요건: Windows 10 1809+, 권장: Windows 11 22H2+

---

## 2. 최상위 아키텍처와 제품 기능

### 계층 구조

```
┌──────────────────────────────────────────────────────────────┐
│  cmux 앱 (Swift/SwiftUI + AppKit 어댑터)                       │
│  ┌──────────────┐  ┌───────────────────┐  ┌───────────────┐  │
│  │ 수직 사이드바 │  │  Bonsplit 레이아웃  │  │ 브라우저 패인  │  │
│  │  TabManager  │  │  (스플릿 패인 트리) │  │  WKWebView    │  │
│  └──────────────┘  └────────┬──────────┘  └───────────────┘  │
│                             │                                 │
│              ┌──────────────┴───────────┐                     │
│              │  GhosttyKit.xcframework   │ ← Zig 빌드         │
│              │  (libghostty, GPU 가속)   │                     │
│              └──────────────────────────┘                     │
│  TerminalController ──▶ Unix 소켓 /tmp/cmux.sock              │
└─────────────────────────────┬────────────────────────────────┘
                              │ IPC (v1/v2 JSON)
                         ┌────┴──────┐
                         │ cmux CLI  │  (CLI/cmux.swift, ~135KB)
                         └───────────┘
```

**Windows 포트 대응 스택**:

| 계층 | macOS | Windows (cmux-win) |
|------|-------|--------------------|
| UI 프레임워크 | SwiftUI + AppKit | WinUI 3 + C++/WinRT |
| 터미널 엔진 | GhosttyKit (Zig, Metal) | ConPTY + libvterm + Direct2D/DirectWrite |
| 브라우저 패인 | WKWebView | WebView2 + CDP |
| IPC transport | Unix socket | Named Pipe (`\\.\pipe\cmux-<session>-<pid>`) |
| 창 배경 | NSVisualEffectView | Mica (Win11) / Acrylic (Win10) |
| 자동 업데이트 | Sparkle | WinSparkle/MSIX (M7 예정) |

### 사용자 facing 핵심 기능

| 기능 | 설명 | v1 포함 여부 |
|------|------|-------------|
| 수직 사이드바 탭 | git 브랜치·CWD·포트·알림·진행률 표시 | ✅ M3 |
| 스플릿 패인 | 수평/수직 분할 (Bonsplit 레이아웃 엔진) | ✅ M2/M3 |
| 터미널 패인 | ConPTY + VT parsing + D2D 렌더링 | ✅ M2 |
| 브라우저 패인 | WebView2 + omnibar + CDP 자동화 | ✅ M4 |
| 알림 시스템 | OSC 9/99/777 + `cmux notify` + unread ring | ✅ M6 |
| IPC/CLI | Named Pipe v2 프로토콜 + `cmux.exe` | ✅ M3/M5 |
| 셸 통합 | PowerShell/CMD directory·git 자동 보고 | ✅ M6 |
| 설정 | `settings.json` atomic write + Ghostty config 보조 | ✅ M6 |
| 자동 업데이트 | Sparkle → Windows updater | ❌ M7 |
| PostHog 분석 | opt-in telemetry | ❌ v1 제외 |

---

## 3. 최상위 폴더 분류 및 Windows 포트 관련성 매트릭스

| # | 폴더 | 분류 | win-relevance | 요약 | 상세 문서 |
|---|------|------|---------------|------|-----------|
| 00 | `.claude/` | config | macos-only | Claude Code 슬래시 커맨드 설정 | [00-dot-claude.md](folders/00-dot-claude.md) |
| 01 | `.github/` | automation | needs-win-equiv | PR CI, 릴리즈, 나이틀리, Homebrew 갱신 워크플로 | [01-dot-github.md](folders/01-dot-github.md) |
| 02 | `Assets.xcassets/` | packaging | needs-win-equiv | Xcode 앱 아이콘·이미지 에셋 | [02-assets-xcassets.md](folders/02-assets-xcassets.md) |
| 03 | `CLI/` | primary source | **needs-win-equiv** | `cmux` CLI 전체 구현 (단일 Swift 파일 ~135KB) | [03-cli.md](folders/03-cli.md) |
| 04 | `docs/` | docs | **port-target** | 내부 기술 스펙 (알림 API, 브라우저, v2 마이그레이션, Ghostty 포크) | [04-docs.md](folders/04-docs.md) |
| 05 | `docs-site/` | docs | reference-only | 공개 문서 사이트 (Next.js + Vercel) | [05-docs-site.md](folders/05-docs-site.md) |
| 06 | `ghostty/` | external | needs-win-equiv | git 서브모듈: Zig 터미널 엔진 (macOS용, Windows 직접 사용 불가) | [06-ghostty.md](folders/06-ghostty.md) |
| 07 | `GhosttyTabs.xcodeproj/` | primary source | macos-only | 주 빌드 경로 — Xcode 프로젝트 | [07-ghosttytabs-xcodeproj.md](folders/07-ghosttytabs-xcodeproj.md) |
| 08 | `GhosttyTabsTests/` | tests | reference-only | Swift 유닛 테스트 | [08-ghosttytabstests.md](folders/08-ghosttytabstests.md) |
| 09 | `GhosttyTabsUITests/` | tests | reference-only | Swift UI 자동화 테스트 (VM 필수) | [09-ghosttytabsuitests.md](folders/09-ghosttytabsuitests.md) |
| 10 | `graphify-out/` | generated | macos-only | 생성된 지식 그래프 캐시 — **무시** | [10-graphify-out.md](folders/10-graphify-out.md) |
| 11 | `homebrew-cmux/` | external | macos-only | Homebrew Cask 정의 (릴리즈 자동 갱신) | [11-homebrew-cmux.md](folders/11-homebrew-cmux.md) |
| 12 | `node_modules/` | generated | macos-only | JS 의존성 — **무시** | [12-node-modules.md](folders/12-node-modules.md) |
| 13 | `Resources/` | packaging | **needs-win-equiv** | 셸 통합 스크립트, terminfo, Info.plist | [13-resources.md](folders/13-resources.md) |
| 14 | `scripts/` | support | needs-win-equiv | 빌드·개발·릴리즈·테스트 Shell 스크립트 | [14-scripts.md](folders/14-scripts.md) |
| 15 | `skills/` | docs | reference-only | AI 에이전트용 스킬 문서 | [15-skills.md](folders/15-skills.md) |
| 16 | `Sources/` | primary source | **port-target** | Swift 앱 소스 전체 — Windows 기능 계약의 핵심 참조 | [16-sources.md](folders/16-sources.md) |
| 17 | `tests/` | tests | reference-only | Python e2e v1 (레거시, VM 필수) | [17-tests.md](folders/17-tests.md) |
| 18 | `tests_v2/` | tests | reference-only | Python e2e v2 (현행, VM 필수) | [18-tests-v2.md](folders/18-tests-v2.md) |
| 19 | `vendor/` | external | reference-only | bonsplit 스플릿 레이아웃 엔진 서브모듈 | [19-vendor.md](folders/19-vendor.md) |
| 20 | `web/` | docs | reference-only | 마케팅·랜딩 사이트 (Next.js) | [20-web.md](folders/20-web.md) |

**win-relevance 정의**:
- `port-target`: 기능·계약을 Windows 포트가 직접 계승해야 하는 핵심 입력
- `needs-win-equiv`: 동등 기능은 필요하지만 구현 경로/자산은 새로 가져가야 함
- `reference-only`: 동작 참고용
- `macos-only`: 포팅 대상 아님

---

## 4. 핵심 런타임·빌드·테스트·릴리즈 플로우

### 4.1 macOS 빌드 플로우 (참조용, 실행 금지)

```
./scripts/setup.sh
  └─ git submodule update --init --recursive
  └─ cd ghostty && zig build -Demit-xcframework=true -Doptimize=ReleaseFast
      → GhosttyKit.xcframework 생성
xcodebuild -project GhosttyTabs.xcodeproj -scheme cmux -configuration Debug build
```

### 4.2 Windows 빌드 플로우 (cmux-win 표준)

```powershell
cmake --preset dev-x64       # vcpkg + NuGet 의존성 다운로드 포함
cmake --build --preset dev-x64
ctest --preset dev-x64 --output-on-failure
```

**빌드 타겟**: `cmux_app` (WinUI 3), `cmux_cli` (`cmux.exe`), `cmux_core`, `cmux_terminal`, `cmux_ipc`, `cmux_tests`

**의존성 소유권**:
- vcpkg overlay port: `libvterm`, `nlohmann-json`, `gtest`, `spdlog`
- NuGet central: `Microsoft.Windows.CppWinRT`, `Windows App SDK`, `WebView2 SDK`, `CommunityToolkit`
- vendor 복사 금지 — overlay port만 사용

### 4.3 테스트 플로우

| 종류 | 위치 | 실행 방법 | 비고 |
|------|------|-----------|------|
| Swift 유닛 | `GhosttyTabsTests/` | `xcodebuild … test` | macOS 호스트에서 가능 |
| Swift UI 자동화 | `GhosttyTabsUITests/` | `ssh cmux-vm '… test'` | **반드시 UTM VM** |
| Python e2e v1 | `tests/` | `./scripts/run-tests-v1.sh` (VM) | 레거시, v1 API |
| Python e2e v2 | `tests_v2/` | `./scripts/run-tests-v2.sh` (VM) | **현행 기준** |

> **규칙**: e2e·UI 테스트는 호스트 머신에서 실행하지 않는다.

### 4.4 macOS 릴리즈 파이프라인 (참조용)

1. `./scripts/bump-version.sh` → `CHANGELOG.md` + `docs-site/content/docs/changelog.mdx` 갱신
2. `git tag vX.Y.Z && git push origin vX.Y.Z` → GitHub Actions `release.yml` 트리거
3. Xcode 빌드 → Apple 공증 → `cmux-macos.dmg` GitHub Release 첨부
4. `update-homebrew.yml` → Homebrew Cask 자동 갱신
5. Sparkle appcast → 앱 내 자동 업데이트

Windows 포트의 릴리즈 파이프라인(WinSparkle/MSIX)은 **M7** 범위, v1에서는 미구현.

---

## 5. 먼저 읽어야 할 고가치 폴더 (우선순위 순)

### Windows 포트 에이전트 권장 읽기 순서

| 순위 | 대상 | 이유 |
|------|------|------|
| 1 | **`docs/agent-browser-port-spec.md`** | `window`/`workspace`/`pane`/`surface` 4계층 ID 체계, v2 API 용어 원천 정의 |
| 2 | **`docs/v2-api-migration.md`** | v1→v2 변경사항. Windows 포트는 v2 기준으로 구현 |
| 3 | **`docs/notifications.md`** | OSC 시퀀스 수신, `cmux notify` 동작, 에이전트 훅 패턴 |
| 4 | **`Sources/TerminalController.swift`** | IPC 서버 전체 구현 — 프로토콜 파싱·디스패치 계약 원천 |
| 5 | **`Sources/Workspace.swift`** + **`TabManager.swift`** | 워크스페이스 상태 모델, BonsplitController 소유 구조 |
| 6 | **`CLI/cmux.swift`** | CLI 명령 전체 표면 — 소켓 연결 bootstrap, v2 명령 카탈로그 |
| 7 | **`tests_v2/`** | 현행 동작의 실행 가능한 명세 (40+ 테스트 파일) |
| 8 | **`Resources/shell-integration/`** | 셸 통합 zsh/bash 스크립트 — PowerShell 동등물 설계 기준 |
| 9 | **`CLAUDE.md`** (루트) | 에이전트용 개발 워크플로 전체 요약 |
| 10 | **`Sources/Panels/`** | Panel 프로토콜, TerminalPanel/BrowserPanel 계약, reattach 패턴 |

---

## 6. 저가치·생성물·macOS 전용 영역 — 회피 또는 주의

| 영역 | 분류 | 취급 방법 |
|------|------|-----------|
| `node_modules/` | JS 의존성 생성물 | **완전 무시**. `bun install`로 재생성 |
| `graphify-out/` | 그래프 생성 출력물 | **완전 무시** |
| `GhosttyTabs.xcodeproj/` | macOS 전용 빌드 정의 | 읽기 참조만. Windows 빌드와 무관 |
| `ghostty/` (서브모듈 내부) | Zig 터미널 엔진 | 읽기 참조만. Windows에서 직접 사용 불가. 변경 시 `manaflow-ai/ghostty` 별도 PR |
| `homebrew-cmux/` | macOS 배포 자동화 | macOS 전용. Windows 포트와 무관 |
| `Assets.xcassets/` | Xcode 이미지 에셋 | 아이콘 디자인 참조용만 |
| `Package.swift` (루트) | 보조/레거시 SwiftPM | 주 빌드는 Xcode 사용. 현행과 불일치 가능 |
| `.claude/` | Claude Code 설정 | 코드 로직 무관 |
| `Sources/UITestRecorder.swift` | 테스트 훅 | 앱 소스에 포함되어 있으나 v1 포팅 대상 아님 |
| `Sources/PostHogAnalytics.swift` | 분석/프라이버시 경계 | 의도 없는 수정 금지. Windows 포트는 기본 off, opt-in 필수 |
| `Sources/Update/` | Sparkle 업데이터 | Windows v1 제외 (M7 예정) |
| `web/` | 마케팅 사이트 | 기능 구현과 무관 |
| `docs-site/` | 공개 문서 사이트 | 기능 구현과 무관. 사용자 문서 참고용 |

---

## 7. 포팅 핵심 주의사항

### 7.1 IPC Transport — Unix Socket → Named Pipe

| 항목 | macOS | Windows |
|------|-------|---------|
| transport | Unix socket `/tmp/cmux*.sock` | Named Pipe `\\.\pipe\cmux-<session>-<pid>` |
| mode | stream | `PIPE_TYPE_MESSAGE` + `PIPE_READMODE_MESSAGE` |
| max payload | 제한 없음 | **1 MiB** |
| security | 파일 시스템 권한 | **same-user ACL** 필수 |
| pipe discovery | 소켓 경로 환경 변수 | `--pipe` arg → `CMUX_PIPE_NAME` env → fallback default |
| socket_control mode | `off` / `notifications` / `full` | `off` / `readonly` / `full` |

CLI `cmux.swift`의 Unix 소켓 연결 bootstrap을 그대로 이식하면 **안 된다**. Named Pipe 연결 bootstrap으로 재작성 필요.

### 7.2 빌드 시스템 — Xcode/SwiftPM → CMake Presets + vcpkg + NuGet

- macOS: `xcodebuild`, `zig build`, Xcode 코드 사이닝, Apple 공증
- Windows: `cmake --preset dev-x64`, vcpkg overlay ports, NuGet central package management
- `scripts/` 하위 Shell 스크립트(`.sh`)는 Windows에서 직접 실행 불가. PowerShell 동등물 별도 작성 필요
- `vendor/` 복사 방식 금지, overlay port만 사용

### 7.3 셸 통합 — zsh/bash → PowerShell/CMD/WSL

| 환경 변수 | macOS | Windows |
|-----------|-------|---------|
| 소켓 경로 | `CMUX_SOCKET_PATH` | `CMUX_PIPE_NAME` |
| 워크스페이스 ID | `CMUX_WORKSPACE_ID` | `CMUX_PANE_ID` (`pane:<uuid>` 형식) |
| 서페이스 ID | `CMUX_SURFACE_ID` | `CMUX_SURFACE_ID` (동일) |
| 레거시 (주입 안 함) | — | `CMUX_PANEL_ID`, `CMUX_TAB_ID` |

`Resources/shell-integration/`의 zsh/bash 스크립트는 **그대로 재사용하지 않는다**.  
PowerShell 규칙: prompt blocking 금지, git branch 보고 비동기(`Start-ThreadJob`), `cwd_uri`는 RFC 8089 형식.  
ConPTY spawn 시 초기 환경 블록에만 주입 — pane/workspace 이동 시 **재주입 금지**.

### 7.4 터미널 스택 — GhosttyKit (Metal/Zig) → ConPTY + libvterm + D2D

macOS의 `GhosttyKit.xcframework`는 **Windows에서 직접 링크하지 않는다**. 동등 기능 재설계:

| 기능 | macOS | Windows |
|------|-------|---------|
| PTY | libghostty (내장) | ConPTY |
| VT parser | libghostty (내장) | libvterm (vcpkg overlay port) |
| renderer | Metal + GPU | Direct2D + DirectWrite |
| host surface | NSView | WinUI 3 `SwapChainPanel` |

**ConPTY 주의**:
- Win11 22H2+ (build ≥ 22621): passthrough 모드 지원, 아래에서 판정
- passthrough 판정은 세션 start 시 1회만 수행; `CMUX_CONPTY_MODE` env로 override 가능
- resize는 background enqueue + 50ms throttle
- 스레딩: VT parse·dirty region 계산·frame publish = background worker; D2D draw·IME rect·UIA event = UI thread
- frame handoff: `std::atomic<std::shared_ptr<TerminalFrame>>` immutable snapshot 패턴

**reattach_token 패턴**: split 이동·workspace 전환 시 panel을 재생성하지 않는다. `reattach_token` (uint64) 증가 → XAML binding 감지 → `SetSwapChain()` 재호출로 swapchain 재연결.

### 7.5 UI 스택 — SwiftUI/AppKit → WinUI 3/C++/WinRT

- `Sources/` 내 SwiftUI View를 그대로 WinUI 3 XAML로 변환하려 하지 않는다
- 기능 계약(API 스키마·상태 전이·acceptance criteria)만 이식하고 UI 구현은 WinUI 3 관용 방식으로 재설계
- 창 배경: Win11 Mica → Win10 Acrylic → 없을 시 solid 색상 (degrade 매트릭스 준수)
- 사이드바 ListView: 선택 source of truth는 `TabManager`. `ListView.SelectedItem`은 투영만

**의도적 차이점 (Intentional Divergences)**:

| 항목 | macOS cmux | Windows cmux-win |
|------|-----------|-----------------|
| IPC 전송 | Unix socket | Named Pipe |
| socket_control mode | `notifications` | `readonly` |
| 탭 닫기 후 선택 | 오른쪽 형제 우선 | **왼쪽 형제 우선** |
| 분석/텔레메트리 | RELEASE 빌드 기본 활성 | **기본 off, opt-in 필수** |
| 환경 변수 이름 | `CMUX_SOCKET_PATH`, `CMUX_WORKSPACE_ID` | `CMUX_PIPE_NAME`, `CMUX_PANE_ID` |
| 단축키 modifier | ⌘ (Command) | Ctrl/Win |
| 북마크 | 있음 | v1 없음 |

### 7.6 업데이트 파이프라인 — Sparkle → Windows updater (M7)

`Sources/Update/` 하위 Sparkle 관련 모든 컴포넌트(UpdateController, UpdateViewModel, UpdateDriver, UpdateBadge, UpdatePill, UpdatePopover 등)는 **v1 범위 아님**. M7에서 WinSparkle/MSIX 기반 Windows updater로 별도 설계 예정.

---

## 8. 대표 파일 맵

### 루트 주요 파일

| 파일 | 역할 | Windows 포트 관련성 |
|------|------|-------------------|
| `CLAUDE.md` | 에이전트용 개발 워크플로 전체 요약 | 필독 |
| `README.md` | 사용자 기능 조감, 키보드 단축키 | 기능 범위 파악 |
| `ghostty.h` | Ghostty C API 헤더 (Swift ↔ C 계약) | Windows 터미널 스택 설계 시 API 형태 참고 |
| `CHANGELOG.md` | 릴리즈 히스토리 | 기능 추가 흐름 파악 |
| `PROJECTS.md` / `TODO.md` | 완료/예정 작업 일람 | 구현 범위 파악 |
| `cmux.entitlements` | macOS 샌드박스 권한 선언 | Windows는 불필요 |
| `.gitmodules` | ghostty 서브모듈 참조 | 서브모듈 상태 확인용 |

### 필독 소스 파일

| 파일 | 역할 |
|------|------|
| `Sources/cmuxApp.swift` | `@main` 진입점 — bootstrap 순서 파악 |
| `Sources/AppDelegate.swift` | NSApplication delegate 어댑터 — activation·서비스·키 이벤트 라우팅 |
| `Sources/TerminalController.swift` | Unix 소켓 IPC 서버 — v1/v2 프로토콜 파싱·디스패치 계약 원천 |
| `Sources/TabManager.swift` | 워크스페이스 CRUD·선택·순서 상태 소유 |
| `Sources/Workspace.swift` | 탭 단위 모델 (BonsplitController + Panel 배열) |
| `Sources/Panels/Panel.swift` | Panel 프로토콜 정의 |
| `Sources/Panels/TerminalPanel.swift` | 터미널 패인 모델 (reattach, lifecycle) |
| `Sources/Panels/BrowserPanel.swift` | 브라우저 패인 모델 (WKWebView, CDP) |
| `Sources/Panels/BrowserPanelView.swift` | omnibar·내비게이션·포커스 UX |
| `Sources/TerminalNotificationStore.swift` | OSC 파싱, 알림 상태·읽음 관리 |
| `CLI/cmux.swift` | CLI 명령 전체 구현 (소켓 연결 bootstrap 포함, ~135KB) |
| `docs/agent-browser-port-spec.md` | 4계층 ID 체계 원천 정의 |
| `docs/v2-api-migration.md` | 소켓 API v2 변경 사항 |
| `docs/notifications.md` | 알림 CLI 사용법, 에이전트 훅 패턴 |
| `Resources/shell-integration/cmux-zsh-integration.zsh` | CWD·git 자동 보고 — PowerShell 동등물 설계 기준 |
| `tests_v2/cmux.py` | e2e 테스트 공통 헬퍼 — v2 API 사용 패턴 |

---

## 9. 폴더별 압축 요약

| 폴더 | 한 줄 요약 | Windows 포트 액션 |
|------|-----------|-------------------|
| `.claude/` | Claude Code 슬래시 커맨드 설정 | 무시 |
| `.github/` | CI/CD 워크플로 (PR, 릴리즈, 나이틀리, Homebrew) | cmux-win용 GitHub Actions 워크플로 별도 작성 |
| `Assets.xcassets/` | 앱 아이콘·이미지 에셋 | 아이콘 디자인 참조 후 Windows 리소스로 재작성 |
| `CLI/` | `cmux.swift` — Unix 소켓 기반 CLI 전체 (~135KB) | Named Pipe 기반 `cmux.exe`로 재구현 |
| `docs/` | 기술 스펙 (알림 API, 브라우저 포트, v2 마이그 가이드, Ghostty 포크) | **포팅 계약 원천** — 필독 |
| `docs-site/` | Next.js 공개 문서 사이트 (Vercel) | 기능 구현 무관. 사용자 문서 참고만 |
| `ghostty/` | Zig 터미널 엔진 서브모듈 (GhosttyKit.xcframework 원천) | 읽기 참조만. Windows 직접 사용 불가 |
| `GhosttyTabs.xcodeproj/` | macOS 주 빌드 정의 | macOS 전용, Windows에 무관 |
| `GhosttyTabsTests/` | Swift 유닛 테스트 | 테스트 케이스 설계 참고 |
| `GhosttyTabsUITests/` | Swift UI 자동화 (VM 필수) | e2e 커버리지 범위 파악 |
| `graphify-out/` | 지식 그래프 생성 캐시 | **완전 무시** |
| `homebrew-cmux/` | Homebrew Cask 정의 | macOS 전용, Windows에 무관 |
| `node_modules/` | JS 의존성 설치 산출물 | **완전 무시** |
| `Resources/` | 셸 통합 스크립트, terminfo, Info.plist | 셸 통합 동작 파악 후 PowerShell/CMD 동등물 재작성 |
| `scripts/` | 빌드·개발·릴리즈 Shell 스크립트 | PowerShell 빌드 스크립트 별도 작성 필요 |
| `skills/` | AI 에이전트용 스킬 문서 | cmux-win 스킬 문서 별도 작성 |
| `Sources/` | Swift 앱 소스 전체 (UI, IPC, 패인, 알림, 업데이트) | **포팅 계약 참조 원천** — 핵심 필독 |
| `tests/` | Python e2e v1 (레거시, VM 필수) | v2로 전환 추이 파악. v1 호환 범위 확인 |
| `tests_v2/` | Python e2e v2 (현행, VM 필수) | **현행 동작 명세** — 포팅 검증 기준 |
| `vendor/` | bonsplit 서브모듈 (스플릿 레이아웃 엔진) | split 레이아웃 로직 파악. Windows는 독립 구현 |
| `web/` | 마케팅·랜딩 사이트 (Next.js) | 무관 |

---

## 10. 미결 불확실성 / 후속 확인 사항

| # | 항목 | 불확실 이유 | 후속 조치 |
|---|------|-------------|-----------|
| 1 | `Package.swift` 실사용 여부 | SwiftTerm 의존을 선언하지만 앱은 Xcode 프로젝트로 빌드됨. 레거시이거나 대안 빌드 경로일 가능성 | `GhosttyTabs.xcodeproj` 빌드 단계에서 `Package.swift` 타겟 참조 여부 확인 |
| 2 | `ghostty/` 서브모듈 현재 체크아웃 상태 | Windows 환경에서 서브모듈 체크아웃 여부, `GhosttyKit.xcframework` 존재 여부 확인 불가 | `git submodule status` + `dir ghostty\macos\` 확인 |
| 3 | `cmuxd/` 디렉터리 위치 | `CLAUDE.md`에 `cd cmuxd && zig build` 명령이 있으나 최상위에 없음. ghostty 서브모듈 내부 또는 별도 서브모듈로 추정 | `ghostty/` 내부 또는 `.gitmodules` 재확인 |
| 4 | `Sources/Panels/bonsplit/`와 `vendor/bonsplit/`의 관계 | wrapper, 복사본, 또는 별도 포팅 계층인지 불명확 | split 로직 수정 전 양측 코드 비교 확인 |
| 5 | v1 소켓 API 폐기 시점 | `docs/agent-browser-port-spec.md`에서 v1 폐기 언급이 있으나 구체적 마일스톤 미정 | v1 호환이 필요한 테스트 케이스 수 파악 + `tests/`에서 v1 전용 API 목록 추출 |
| 6 | `web/` vs `docs-site/` 정확한 역할 분리 | 두 Next.js 앱의 역할이 `web/README.md`를 읽지 않아 불명확. 마케팅 vs 문서로 추정 | `web/README.md` 1회 확인으로 해소 가능 |
| 7 | parity gap 12개 task_missing 항목 등록 필요 | `_workspace/18-cmux-parity.md` 기준 v1 범위이나 `plans/`에 task 없는 기능 12개 존재 | `plans/milestones/*.json`에 task 추가 검토 (우선순위: Shared panel abstraction, Notifications page, Settings window) |
| 8 | partial 항목 9개 보강 필요 | `_workspace/18-cmux-parity.md` §5.2 — 브라우저 패널 UI, embedded webview wrapper, find overlay 등 | 각 항목별 설계 문서 및 acceptance criteria 보완 |

---

## 부록: v1 명시 제외 항목 목록

v1 범위에서 의도적으로 제외된 항목 — macOS에 있으나 Windows v1에서 구현하지 않는다:

- **Sparkle 업데이트 스택 전체** (M7 예정)
- **PostHog analytics 전송** (opt-in 기본 off만 구현)
- **Finder Services routing** (Windows 전용 대안 미정)
- **SwiftTerm legacy local-process terminal** (ConPTY 단일 경로)
- **UITestRecorder / UpdateTestSupport**
- **NSStatusItem menu bar extra** (Windows system tray 대응 미정)
- **workspace pinning** (`isPinned`)
- **탭 히스토리 back/forward** (max 50)
- **새 탭 삽입 위치 설정** (top/afterCurrent/end)
- **Ctrl+숫자(1~9) workspace 단축키**
- **창 간 drag detach/attach UX polish**
- **browser 북마크**

---

*이 문서는 per-folder 상세 분석 문서([`folders/`](folders/))의 합성 뷰다. 개별 폴더의 불확실성, 편집 지침, 의존성 상세는 해당 문서를 참조한다.*
