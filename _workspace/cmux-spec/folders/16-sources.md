# `Sources`

## 역할 / 목적

**cmux macOS 앱의 핵심 Swift 소스 트리**. SwiftUI + AppKit 어댑터 계층, GhosttyKit 통합, IPC 서버, 탭/워크스페이스 상태 관리, 브라우저 패인, 알림 시스템, 자동 업데이트, 검색 오버레이가 모두 여기에 있다.

## 주요 내용

```
Sources/
├── cmuxApp.swift                  # @main 진입점 (SwiftUI App lifecycle)
├── AppDelegate.swift              # NSApplication delegate: Finder 통합, 서비스 라우팅, 키 이벤트, Sentry SDK 초기화(crash reporting)
├── TabManager.swift               # 윈도우 전체 워크스페이스 상태 소유 (CRUD, 선택, 순서)
├── Workspace.swift                # 탭 단위 모델 (BonsplitController + Panel 배열)
├── TerminalController.swift       # Unix 소켓 IPC 서버 (v1/v2 프로토콜 파싱·디스패치)
├── TerminalNotificationStore.swift# OSC 시퀀스 파싱, 알림 상태·읽음 관리
├── GhosttyTerminalView.swift      # Ghostty C API ↔ SwiftUI 브리지 (스크롤 랙 감지 시 Sentry 메시지 캡처)
├── GhosttyConfig.swift            # Ghostty 설정 로딩·환경 변수 주입
├── ContentView.swift              # 최상위 UI 레이아웃 (사이드바 + 콘텐츠 영역)
├── WorkspaceContentView.swift     # 워크스페이스 콘텐츠 렌더링
├── PostHogAnalytics.swift         # 운영 분석 이벤트 전송 (opt-in, 프라이버시 경계)
├── SidebarSelectionState.swift    # 사이드바 선택 상태 ObservableObject
├── SocketControlSettings.swift    # 소켓 IPC 설정
├── KeyboardShortcutSettings.swift # 키보드 단축키 설정 모델
├── NotificationsPage.swift        # 알림 패널 UI
├── TerminalView.swift             # 터미널 뷰 컨테이너
├── UITestRecorder.swift           # UI 테스트용 자동화 훅 (앱 번들 포함)
├── WindowAccessor.swift           # NSWindow 접근 SwiftUI 브리지
├── WindowDecorationsController.swift # 창 데코레이션 제어
├── WindowDragHandleView.swift     # 드래그 핸들 뷰
├── WindowToolbarController.swift  # 툴바 제어
├── Backport.swift                 # SwiftUI/AppKit backport 유틸
│
├── Panels/                        # 패인 타입 구현
│   ├── Panel.swift                # Panel 프로토콜 정의
│   ├── PanelContentView.swift     # 패인 타입별 콘텐츠 라우터
│   ├── TerminalPanel.swift        # 터미널 패인 모델
│   ├── TerminalPanelView.swift    # 터미널 패인 SwiftUI 뷰
│   ├── BrowserPanel.swift         # 브라우저 패인 모델 (WKWebView)
│   ├── BrowserPanelView.swift     # 브라우저 패인 UI (주소창, 내비게이션)
│   └── CmuxWebView.swift          # WKWebView 래퍼 (포커스·단축키 보존)
│
├── Find/                          # 검색 오버레이 전용 하위 모듈
│   └── SurfaceSearchOverlay.swift # 패널 위 플로팅 검색 UI, 매치 카운터/이동/닫기 처리
│
└── Update/                        # Sparkle 자동 업데이트 서브시스템
    ├── UpdateController.swift
    ├── UpdateViewModel.swift
    ├── UpdateDriver.swift
    ├── UpdateDelegate.swift
    ├── UpdateBadge.swift
    ├── UpdatePill.swift
    ├── UpdatePopoverView.swift
    ├── UpdateTitlebarAccessory.swift
    ├── UpdateLogStore.swift
    ├── UpdateTiming.swift
    ├── UpdateTestSupport.swift     # 테스트 지원 (v1 포팅 대상 아님)
    └── UpdateTestURLProtocol.swift # 테스트 지원 (v1 포팅 대상 아님)
```

> **명세 정정**: `SurfaceSearchOverlay.swift`는 `Sources/Find/`에만 존재한다 (`Sources/Panels/`에는 없음). 이전 판은 양쪽에 중복 기재했다.

## Workspace.swift 데이터 구조 (사이드바 상태 모델)

**소스**: `Sources/Workspace.swift:6–37`

`Workspace` 객체에 `@Published` 프로퍼티로 존재하는 사이드바 상태 구조체들. v2 API 응답 스키마 설계와 Windows 포트 데이터 모델 구현 시 기준이 된다.

| 구조체 | 필드 | 용도 |
|--------|------|------|
| `SidebarStatusEntry` | `key: String`, `value: String`, `icon: String?`, `color: String?`, `timestamp: Date` | `set_status` v1 명령으로 설정되는 named 상태 항목. `[String: SidebarStatusEntry]` 딕셔너리로 저장 |
| `SidebarLogEntry` | `message: String`, `level: SidebarLogLevel`, `source: String?`, `timestamp: Date` | `log` v1 명령으로 추가되는 로그 스트림 엔트리 |
| `SidebarLogLevel` | `info` / `progress` / `success` / `warning` / `error` | 로그 레벨 enum |
| `SidebarProgressState` | `value: Double`, `label: String?` | `set_progress` v1 명령으로 설정되는 진행률 (0.0–1.0) |
| `SidebarGitBranchState` | `branch: String`, `isDirty: Bool` | `report_git_branch` v1 명령으로 설정되는 git 상태 |

**추가 필드**:
- `customTitle: String?` — 사용자가 직접 지정한 탭 제목 override. `hasCustomTitle: Bool`로 유효 여부 판정. 탭 타이틀 해석 체인에서 최상위 우선순위 (v1 사이드바 명령 목록은 [03-cli.md](03-cli.md) §v1 사이드바 소켓 프로토콜 참조).

## 소켓 API v2 메서드 카탈로그

`TerminalController.swift`의 v2 디스패치 테이블에는 약 100개의 메서드가 네임스페이스별로 존재한다 (출처: `Sources/TerminalController.swift:504-806`). `CLI/cmux.swift`의 명령이 이 메서드들을 호출한다. `socket_control` 모드(`off`/`readonly`/`full`)별 허용 범위를 정의하려면 전체 카탈로그가 기준이 된다.

**`workspace.list` 응답 스키마** (출처: `Sources/TerminalController.swift:1379`):

```json
{
  "id": "<uuid>",
  "ref": "workspace:1",
  "index": 0,
  "title": "Terminal",
  "selected": true,
  "pinned": false
}
```

`pinned` 필드는 부록의 "workspace pinning v1 제외" 항목과 무관하게 API 응답 스키마에 이미 포함된다. Windows 포트의 `workspace.list` 구현 시 이 필드를 반드시 포함해야 한다.

| 네임스페이스 | 메서드 |
|--------------|--------|
| `system` | ping, capabilities, identify |
| `window` | list, current, focus, create, close |
| `workspace` | list, create, select, current, close, reorder, move_to_window |
| `surface` | list, current, focus, split, create, close, move, reorder, refresh, health, send_key, send_text, trigger_flash, drag_to_split |
| `pane` | list, focus, surfaces, create |
| `notification` | create, create_for_surface, create_for_target, list, clear |
| `app` | focus_override.set, simulate_active |
| `browser` (기본) | navigate, back, forward, reload, snapshot, eval, wait, click, dblclick, hover, focus, type, fill, press, keydown, keyup, check, uncheck, select, scroll, scroll_into_view, screenshot, highlight, focus_webview, is_webview_focused, open_split, input_mouse, input_keyboard, input_touch, addinitscript, addscript, addstyle |
| `browser.url` | get |
| `browser.get` | text, html, value, attr, title, count, box, styles |
| `browser.is` | visible, enabled, checked |
| `browser.find` | role, text, label, placeholder, alt, title, testid, first, last, nth |
| `browser.frame` | select, main |
| `browser.dialog` | accept, dismiss |
| `browser.download` | wait |
| `browser.cookies` | get, set, clear |
| `browser.storage` | get, set, clear |
| `browser.tab` | new, list, switch, close |
| `browser.console` | list, clear |
| `browser.errors` | list |
| `browser.state` | save, load |
| `browser.viewport` | set |
| `browser.geolocation` | set |
| `browser.offline` | set |
| `browser.trace` | start, stop |
| `browser.network` | route, unroute, requests |
| `browser.screencast` | start, stop |
| `debug` | shortcut.set, shortcut.simulate, type, app.activate, layout, notification.focus, flash.count, flash.reset, window.screenshot, terminal.is_focused, terminal.read_text, terminal.render_stats, bonsplit_underflow.count, bonsplit_underflow.reset, empty_panel.count, empty_panel.reset, panel_snapshot, panel_snapshot.reset |

> `debug.*` 네임스페이스는 테스트/디버그 지원 명령(단축키 시뮬레이션·레이아웃 덤프·flash 카운터·창 스크린샷)으로, 포트의 e2e 하니스 설계 시 참조한다.
> 브라우저 고급 자동화(tab/console/errors/state/trace/network/screencast/geolocation/viewport/offline)는 `BrowserPanel.swift`가 구현한다. 사이드바(git branch·CWD·listening ports·최신 알림 텍스트)의 동작 계약은 [integrated-spec.md](../integrated-spec.md) §2를 참조한다.

## 저장소 상호작용 / 의존성

- `CLI/cmux.swift`와 Unix 소켓 IPC 프로토콜(v1/v2)을 공유한다. `TerminalController.swift`가 서버 측 구현이다.
- `vendor/bonsplit/`(서브모듈)의 레이아웃 엔진을 `Workspace.swift`에서 `BonsplitController`로 사용한다.
- `GhosttyKit.xcframework`를 `GhosttyTerminalView.swift`에서 직접 사용한다.
- `Resources/shell-integration/`의 스크립트들을 실행 중에 참조한다.
- `tests_v2/`의 Python e2e 테스트가 이 코드의 동작을 소켓 API를 통해 검증한다.
- `docs/`의 기술 스펙 문서들이 이 코드의 계약을 정의한다.
- **크래시 리포팅**: `sentry-cocoa` SwiftPM 패키지(`getsentry/sentry-cocoa`)를 사용한다. 의존성은 `Package.swift`가 아니라 `GhosttyTabs.xcodeproj`(XCRemoteSwiftPackageReference)에 선언된다. `AppDelegate.swift`가 `SentrySDK.start(...)`로 초기화(DSN 하드코딩)하고, `GhosttyTerminalView.swift`가 스크롤 랙 감지 시 `SentrySDK.capture(message:)`를 호출한다. PostHog(사용 분석)와 별도 운영. Windows 포트 v1 포함 여부는 미결.

> **Windows 포트 주의**: `Sources/`는 가장 중요한 참조 입력이지만, 여기의 AppKit/SwiftUI 구현을 그대로 옮기지는 않는다. 특히 `Find/`, `Panels/`, 창 장식, Ghostty 연동은 Windows 전용 UI/터미널 스택으로 동등 기능을 다시 설계해야 한다.

## 편집 지침

**1차 소스 — 가장 중요한 폴더**. IPC 프로토콜 변경은 `TerminalController.swift` + `CLI/cmux.swift`를 함께 수정한다. `PostHogAnalytics.swift`(사용 분석)와 `AppDelegate.swift`/`GhosttyTerminalView.swift`의 Sentry(크래시 리포팅) 코드는 프라이버시·텔레메트리 민감 경계이므로 의도하지 않은 수정을 피한다. `UITestRecorder.swift`는 테스트 훅이지만 앱 소스에 포함되므로 주의한다.

## 불확실성

- `vendor/bonsplit/`과 `Sources/` 내 Bonsplit 사용 계층의 정확한 관계(래퍼 vs 직접 사용)는 split 로직 수정 전 별도 확인이 필요하다.
