# cmux Parity Gap 분석

> [!NOTE]
> 이 문서 `_workspace\18-cmux-parity.md`는 Phase 1-1 확정 기능 인벤토리를 기준으로 macOS cmux와 Windows 포트 설계 문서(`_workspace\02-core-app.md`~`_workspace\11-build-release.md`) 및 milestone 계획(`plans\milestones\m0.json`~`plans\milestones\m6.json`)을 대조해 v1 범위(M0~M6)의 패리티 갭을 정리한다.

## 1. 검토 범위와 판정 기준

- v1 포팅 범위는 `M0~M6`이다. 즉 **bootstrap/app shell(M0~M1) → terminal core(M2) → split/sidebar/IPC foundation(M3) → browser panel(M4) → CLI/automation(M5) → settings/notifications/shell integration(M6)** 까지를 Windows 기본 제품 범위로 본다.
- 기본 Windows 대체 스택은 **WinUI 3 + `AppWindow` + ConPTY + libvterm + Direct2D/DirectWrite + WebView2 + Named Pipe + `settings.json` + AppNotification** 이다.
- 명시적 v1 제외 항목은 **Sparkle update stack 전체, PostHog analytics 전송, Finder Services routing, SwiftTerm legacy local-process terminal, UITestRecorder, UpdateTestSupport, `NSStatusItem` menu bar extra** 이다.
- 추가로 현재 설계 문서에서 v1 제외가 명시된 항목은 **workspace pinning, tab history back/forward, 새 탭 삽입 위치 설정, 창 간 drag detach/attach UX polish, Cmd+숫자 workspace 단축키** 다.

## 2. 요약 통계

| 전체 기능 수 | ✅ covered 항목 수 | ⚠️ partial 항목 수 | ❌ missing 항목 수 |
|---|---:|---:|---:|
| 55 | 18 | 9 | 28 |

- 통계는 아래 패리티 표의 `Gap 상태` 행 수를 직접 재집계한 값이다.
- `Milestone`은 `M0~M7` 축약 표기만 사용하고, `_workspace 참조`는 파일명만 사용한다.

## 3. 패리티 갭 분석표

### 애플리케이션 라이프사이클

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| App bootstrap + env setup | `cmuxApp`, `configureGhosttyEnvironment()`, `UserDefaults` | `wWinMain` + WinUI 3 `App` + `settings.json` + process env block | Med | M1+M2+M6 | 02-core-app, 03-terminal-engine, 09-config-settings, 10-shell-integration | ✅ covered |
| App commands + auxiliary windows | `SwiftUI Commands`, `SettingsWindowController`, `AboutWindowController` | secondary `AppWindow` + command surface + settings/about windows | Med | — | — | ❌ missing |
| App delegate orchestration + shortcut routing | `AppDelegate`, `UNUserNotificationCenterDelegate`, `NSMenuItemValidation` | activation/notification routing + app-wide shortcut router + `DispatcherQueue` | Med | M1+M6 | 02-core-app, 07-notification, 09-config-settings | ⚠️ partial |

### 패널 인프라

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Shared panel abstraction | `Panel` protocol | 공통 panel lifecycle contract + reusable panel host interface | Med | — | 03-terminal-engine, 04-split-pane, 06-browser-panel | ❌ missing |
| Panel content router | `PanelContentView` | XAML content presenter + panel-type routing layer | Med | — | 02-core-app, 04-split-pane | ❌ missing |

### 워크스페이스

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Workspace model + split/tab state | `ObservableObject`, `BonsplitController` | `TabManager` + `BonsplitController` + XAML projection | Med | M3 | 04-split-pane, 05-sidebar-tabs | ✅ covered |
| Workspace metadata tracking | shell-reported dir / git / progress / status / logs / ports | direct-pipe shell report + `TabManager` metadata batching | Med | M3+M6 | 05-sidebar-tabs, 08-ipc-cli, 10-shell-integration | ✅ covered |
| Workspace rendering + panel badges | `SwiftUI View`, `BonsplitView` | WinUI 3 sidebar/list item projection + unread ring/badge | Med | M3+M6 | 04-split-pane, 05-sidebar-tabs, 07-notification | ✅ covered |
| Workspace sidebar / tab selection | `SwiftUI`, `VerticalTabsSidebar` | WinUI 3 `ListView`/custom sidebar + `TabManager` | Med | M3 | 05-sidebar-tabs | ✅ covered |
| Sidebar selection state | `ObservableObject` | `TabManager` source-of-truth + projected selection state | Low | M3 | 05-sidebar-tabs | ✅ covered |
| Tab/workspace management | placement/pinning, selection/history, split focus, browser opens, window title updates | `TabManager` + split focus restore + CLI/window routing | High | M3+M5 | 04-split-pane, 05-sidebar-tabs, 08-ipc-cli | ⚠️ partial |

### 터미널 패널

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Terminal panel wrapper + search state | `TerminalSurface`, `ObservableObject` | `terminal_panel` host + overlay state + `reattach_token` | Med | M2 | 03-terminal-engine, 04-split-pane | ⚠️ partial |
| Terminal panel lifecycle / reattach handling | reattach token, surface reparent | lifecycle state machine + `reattach_token` + `SwapChainPanel` rebind | High | M2 | 03-terminal-engine, 04-split-pane | ✅ covered |
| Terminal panel rendering | `TerminalPanelView`, unfocused overlay, unread indicator | Direct2D renderer + XAML dim overlay + unread ring | Med | M2+M6 | 03-terminal-engine, 04-split-pane, 07-notification | ✅ covered |
| Ghostty-backed terminal view | Ghostty C API, clipboard, scroll, focus, lag logging | ConPTY + libvterm + Direct2D/DirectWrite + WinUI host | High | M2 | 03-terminal-engine, 04-split-pane | ⚠️ partial |
| Terminal IME / text-input support | `NSTextInputClient`, marked text, composition, dead keys | TSF (`CoreTextServicesManager` / `ITfTextEditSink`) + cursor rect updates | High | M2 | 03-terminal-engine | ✅ covered |
| Legacy local-process terminal view | `SwiftTerm`, `LocalProcessTerminalView` | 없음 (`ConPTY` 단일 경로) | — | — | — | ❌ missing |

### 브라우저 패널

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Browser panel model + navigation | `WKWebView`, history, UA, search settings | `WebView2` panel host + environment pool + navigation state | High | M4 | 06-browser-panel | ✅ covered |
| Browser history + omnibar suggestions | local history ranking, remote suggestions | JSON history store + frecency + remote suggestion timeout | Med | M4 | 06-browser-panel | ✅ covered |
| Browser panel UI | address bar, suggestions, navigation buttons, focus flash | WinUI 3 omnibar + nav controls + focus management | Med | M4 | 06-browser-panel | ⚠️ partial |
| Embedded web view wrapper | `WKWebView` wrapper with shortcut preservation/focus tracking/context tweaks | XAML `WebView2` host wrapper | High | M4 | 06-browser-panel | ⚠️ partial |

### 찾기

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| In-terminal find overlay | `SurfaceSearchOverlay`, `TerminalPanel.searchState` | terminal overlay (`Popup`/`Canvas`) + per-panel search state | Med | — | 04-split-pane | ❌ missing |

### 알림

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Terminal notification store | `TerminalNotificationStore`, `UNUserNotificationCenter` | `NotificationStore` + `AppNotification` + taskbar badge | Med | M6 | 07-notification | ✅ covered |
| Notifications page | `NotificationsPage` | WinUI 3 notifications page/list view | Med | — | 07-notification | ❌ missing |
| Titlebar notifications popover | `showNotificationsPopover()`, `NSPopover` | `AppWindowTitleBar` anchored flyout/popover | Med | — | — | ❌ missing |

### 셸 통합

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Shell/terminal environment setup | `TERM`, `TERM_PROGRAM`, `XDG_DATA_DIRS`, `MANPATH`, Ghostty resource path | ConPTY spawn env injection + PowerShell/CMD/WSL scripts | Med | M2+M6 | 03-terminal-engine, 08-ipc-cli, 10-shell-integration | ✅ covered |
| Ghostty clipboard/pasteboard integration | clipboard mode mapping, file URL shell-escaping | Windows Clipboard + shell-safe file URL escaping | Low | — | — | ❌ missing |

### 자동화 / IPC

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Socket control settings | socket access mode, path overrides | `socket_control.mode` + Named Pipe naming/override | Med | M0+M3 | 08-ipc-cli, 09-config-settings | ✅ covered |
| Socket automation / v1+v2 control API | Unix socket server, newline-delimited JSON, text+JSON commands, terminal/browser/window/workspace automation, shell metadata reception | Named Pipe message transport + protocol v2 + CLI + CDP automation + shell auto-report | High | M3+M4+M5+M6 | 06-browser-panel, 08-ipc-cli, 10-shell-integration | ✅ covered |

### 설정 / 구성

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Keyboard shortcut persistence | `KeyboardShortcutSettings` | `settings.json` shortcut schema + routing engine + accelerator handling | Low | M0+M6 | 02-core-app, 09-config-settings | ✅ covered |
| Settings window + preferences UI | `SettingsWindowController`, `SettingsView` | WinUI 3 settings window/page | Med | — | — | ❌ missing |
| Ghostty config parsing + theme resolution | `GhosttyConfig` | Ghostty config parser + `settings.json` precedence | Low | M6 | 09-config-settings | ✅ covered |

### 창 관리

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Multi-window support + Finder Services routing | multiple main windows, window↔tab manager mapping, Finder Services open/focus, window close | `WindowManager` + multi-window CLI/window routing | High | M1 | 02-core-app, 08-ipc-cli | ⚠️ partial |

### 창 장식

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Window chrome customization | glass/blur background, tint fallback | `SystemBackdrop` (Mica/Acrylic) + `AppWindowTitleBar` | Med | M1 | 02-core-app, 09-config-settings | ✅ covered |
| Draggable titlebar handle | background drag without content interference | custom titlebar drag region | Med | — | — | ❌ missing |
| Window accessor hook | underlying window exposure for config | `AppWindow` / `HWND` accessor seam | Low | — | — | ❌ missing |
| Titlebar decorations controller | traffic-light hide/offset equivalent | `AppWindowTitleBar` button/title region customization | Med | M1 | 02-core-app, 09-config-settings | ⚠️ partial |
| Toolbar controller | custom toolbar, command/tab title display | WinUI titlebar command host / toolbar region | Med | — | — | ❌ missing |
| Titlebar controls + shortcut hints | sidebar/new-tab/notification buttons, hint placement | titlebar command buttons + keyboard hint layer | Med | — | — | ❌ missing |
| Backport helpers | SwiftUI key-press / pointer-style backports | 없음 (WinUI 3 기본 입력 경로) | Low | — | — | ❌ missing |

### 메뉴 바

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Menu bar extra / unread badge | `NSStatusItem`, unread badge, recent notifications, update/prefs/quit | system tray `SystemTrayIcon` + flyout | — | — | — | ❌ missing |

### 업데이트

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| Update controller / Sparkle integration | `UpdateController` | WinSparkle/MSIX/custom updater orchestration | — | M7 | 11-build-release | ❌ missing |
| Sparkle user driver | `UpdateDriver` | WinSparkle/custom event bridge | — | M7 | 11-build-release | ❌ missing |
| Update state view model | `UpdateViewModel` | WinUI update state VM | — | M7 | 11-build-release | ❌ missing |
| Update pill | `UpdatePill` | WinUI pill/button | — | M7 | 11-build-release | ❌ missing |
| Update popover | `UpdatePopoverView` | WinUI flyout/dialog | — | M7 | 11-build-release | ❌ missing |
| Update badge | `UpdateBadge` | badge/progress ring UI | — | M7 | 11-build-release | ❌ missing |
| Update channel settings | `UpdateChannelSettings` | settings enum + feed selector | — | M7 | 11-build-release | ❌ missing |
| Update timing constants | `UpdateTiming` | updater timing config | — | M7 | 11-build-release | ❌ missing |
| Update log store | `UpdateLogStore` | local update log store | — | M7 | 11-build-release | ❌ missing |
| Update titlebar accessory integration | `UpdateTitlebarAccessoryController` | titlebar/flyout integration | — | M7 | 11-build-release | ❌ missing |
| Update test support | `UpdateTestSupport`, `UpdateTestURLProtocol` | updater test harness / mock feed support | — | M7 | 11-build-release | ❌ missing |

### 분석 / 테스트

| 기능 | macOS 구현 | Windows 대체 | 포팅 난이도 | Milestone | _workspace 참조 | Gap 상태 |
|---|---|---|---|---|---|---|
| PostHog analytics | `PostHogAnalytics` | opt-in telemetry only (`analytics.enabled=false` 기본) | — | M5 | 09-config-settings | ❌ missing |
| UI test recorder | `UITestRecorder` | 없음 | — | — | — | ❌ missing |
| Update/focus debug logging | `UpdateLogStore`, focus log hooks | generic logging/redaction policy + debug log hooks | Low | M5 | 07-notification, 09-config-settings | ⚠️ partial |

## 4. 범위 제외 항목

- **Sparkle 기반 update stack 전체**: `_workspace\11-build-release.md`에서 updater/appcast를 `M7` release-only backlog로 분리했다. v1에는 update controller, pill, popover, badge, test support가 들어오지 않는다.
- **PostHog analytics 전송**: `_workspace\09-config-settings.md`는 `analytics.enabled=false` 기본값만 고정한다. 실제 telemetry 파이프라인은 v1 범위가 아니다.
- **Finder Services routing**: multi-window 기반은 범위 안이지만 Finder Services에 대응하는 Windows 전용 라우팅은 별도 v1 목표로 잡지 않았다.
- **SwiftTerm legacy local-process terminal**: Windows v1 terminal stack은 ConPTY + libvterm + Direct2D 단일 경로로 고정되어 있다.
- **UITestRecorder / UpdateTestSupport**: milestone JSON과 `_workspace\02-core-app.md`~`_workspace\11-build-release.md` 어디에도 v1 구현 계약이 없다.
- **`NSStatusItem` menu bar extra**: Windows tray 대응 기능은 현재 v1 범위에 포함되지 않는다.
- **추가 문서상 제외 항목**: `_workspace\05-sidebar-tabs.md` 기준으로 workspace pinning, tab history back/forward, 새 탭 삽입 위치 설정, 창 간 detach/attach UX, Cmd+숫자 workspace shortcut은 의도적으로 제외됐다.

## 5. 누락/미흡 항목 요약

### 5.1 ❌ missing

- **App commands + auxiliary windows**: settings/about 보조 창과 command surface에 대한 문서 계약과 milestone task를 추가해야 한다.
- **Shared panel abstraction**: terminal/browser 공통 panel host 인터페이스와 lifecycle 책임 분리를 문서화해야 한다.
- **Panel content router**: panel type별 XAML host 선택과 content presenter 라우팅 규칙을 정의해야 한다.
- **Legacy local-process terminal view**: v1 제외 항목으로 유지하되, parity 범위를 재확장할 경우 별도 terminal backend 전략이 필요하다.
- **In-terminal find overlay**: terminal 검색 오버레이 UI, search state 저장 위치, shortcut 연결 task를 계획에 추가해야 한다.
- **Notifications page**: `_workspace\07-notification.md`의 projection을 실제 WinUI page/list 설계와 task로 구체화해야 한다.
- **Titlebar notifications popover**: titlebar anchored flyout 구조, unread 상태 연결, 포커스 복귀 규칙을 새로 정의해야 한다.
- **Ghostty clipboard/pasteboard integration**: clipboard mode 매핑과 file URL shell-escaping 규칙을 셸 통합 계약에 추가해야 한다.
- **Settings window + preferences UI**: settings page/window 정보 구조, navigation, 저장 흐름을 문서와 milestone에 반영해야 한다.
- **Draggable titlebar handle**: custom drag region의 hit-test 규칙과 콘텐츠 충돌 회피 동작을 정의해야 한다.
- **Window accessor hook**: `AppWindow`/`HWND` 노출 범위와 사용 제한을 명시한 accessor seam이 필요하다.
- **Toolbar controller**: titlebar/toolbar 영역의 명령 배치와 상태 동기화 규칙을 설계해야 한다.
- **Titlebar controls + shortcut hints**: titlebar command 버튼, hint 표시 위치, shortcut 시각화 규칙을 추가해야 한다.
- **Backport helpers**: WinUI 기본 입력 경로로 대체할지, 완전 제거할지를 문서에서 명확히 정리해야 한다.
- **Menu bar extra / unread badge**: v1 제외 항목으로 유지하되, tray parity를 목표로 할 경우 별도 tray 모델과 unread 동기화가 필요하다.
- **Update controller / Sparkle integration**: `M7`에서 사용할 Windows updater orchestration 계약을 별도 문서로 분리해야 한다.
- **Sparkle user driver**: 업데이트 UI 이벤트 브리지와 사용자 상호작용 흐름을 `M7` 범위로 정의해야 한다.
- **Update state view model**: 업데이트 상태 모델, progress 노출, 오류 상태 표현을 설계해야 한다.
- **Update pill**: titlebar 또는 설정 화면에 노출할 update pill UI 계약이 필요하다.
- **Update popover**: update 상세 정보와 action 버튼을 담는 flyout/dialog 설계가 필요하다.
- **Update badge**: unread/progress 성격의 update badge 상태 모델을 정의해야 한다.
- **Update channel settings**: 업데이트 채널 enum과 feed 선택 정책을 settings schema에 연결해야 한다.
- **Update timing constants**: 업데이트 검사 주기와 지연 정책을 별도 상수 계약으로 고정해야 한다.
- **Update log store**: update 관련 진단 로그 저장 위치와 보존 정책을 정의해야 한다.
- **Update titlebar accessory integration**: update UI를 titlebar에 결합하는 조건과 상태 전이를 설계해야 한다.
- **Update test support**: updater mock feed, test harness, 자동화 검증 경로를 `M7` 이후로 분리 정의해야 한다.
- **PostHog analytics**: v1 제외 항목으로 유지하되, telemetry를 도입할 경우 opt-in 수집 범위와 privacy gate를 별도 설계해야 한다.
- **UI test recorder**: v1 제외 항목으로 유지하되, 자동화 기록 도구가 필요하면 별도 테스트 지원 설계를 추가해야 한다.

### 5.2 ⚠️ partial

- **App delegate orchestration + shortcut routing**: shortcut routing 외에 activation, notification delegate, app-wide command 위임 흐름을 보강해야 한다.
- **Tab/workspace management**: pinning, history, insert-position, browser-open, window title parity 중 v1 포함 항목을 선별해 설계와 task를 보강해야 한다.
- **Terminal panel wrapper + search state**: panel wrapper는 있으나 terminal search state 저장/복원과 overlay 연결이 빠져 있다.
- **Ghostty-backed terminal view**: core terminal stack은 정의됐지만 clipboard, scroll/focus polish, lag logging 대응이 더 필요하다.
- **Browser panel UI**: omnibar 기본 UX는 있으나 focus flash, suggestion polish, command button 디테일을 보완해야 한다.
- **Embedded web view wrapper**: shortcut preservation, focus tracking, context-menu tweak 같은 host wrapper 세부 계약을 추가해야 한다.
- **Multi-window support + Finder Services routing**: 다중 창 기본 구조는 있으나 Finder Services 대응과 고급 window command 범위는 분리 정리해야 한다.
- **Titlebar decorations controller**: backdrop/title region 기본 계약은 있으나 button hide/offset 수준의 세부 제어가 부족하다.
- **Update/focus debug logging**: 공통 logging/privacy 정책은 있으나 update/focus 전용 debug hook과 진단 포인트가 비어 있다.
## 6. 검증 결과

> 검증 기준: plans\milestones\m0~m6.json task 목록과 패리티 표 Milestone 컬럼의 실제 매핑 일치 여부 확인.
> 검증 일시: 2026-05-24T20:59:30.0536370+09:00

### 6.1 태스크 커버리지 요약

| 구분 | 건수 |
|------|------|
| task_exists (task 확인됨) | 18 |
| task_partial (부분 커버) | 9 |
| task_missing (v1 범위이나 task 없음) | 12 |
| out_of_scope | 16 |

### 6.2 task_missing 항목 (plans 등록 필요)

| 기능 | 컴포넌트 그룹 | 권장 Milestone | 비고 |
|------|--------------|---------------|------|
| App commands + auxiliary windows | 앱 쉘/윈도우 | M1 | settings/about 보조 창과 command surface 미정의 |
| Shared panel abstraction | 패널 인프라 | M2/M3 | terminal/browser 공통 panel host 계약 필요 |
| Panel content router | 패널 인프라 | M1/M3 | XAML content presenter 라우팅 규칙 없음 |
| In-terminal find overlay | 터미널 패널 | M2 | 검색 오버레이/UI 상태 task 없음 |
| Notifications page | 알림 | M6 | WinUI notifications page/list task 없음 |
| Titlebar notifications popover | 알림/타이틀바 | M6 | titlebar anchored popover task 없음 |
| Ghostty clipboard/pasteboard integration | 셸 통합 | M6 | clipboard mode mapping/file URL escaping 누락 |
| Settings window + preferences UI | 설정 UI | M6 | settings page/window task 없음 |
| Draggable titlebar handle | 창 장식 | M1 | custom drag region hit-test 정의 없음 |
| Window accessor hook | 창 장식 | M1 | AppWindow/HWND accessor seam 없음 |
| Toolbar controller | 창 장식 | M1 | titlebar toolbar region task 없음 |
| Titlebar controls + shortcut hints | 창 장식 | M1/M6 | command buttons/hint layer task 없음 |
| Backport helpers | 창 장식 | — | WinUI 기본 경로 대체 여부만 문서상 남음 |

### 6.3 task_partial 항목 (task 보강 필요)

- App delegate orchestration + shortcut routing: m1-1/m1-2/m6-3가 bootstrap, window lifecycle, shortcut routing은 다루지만 activation, notification delegate, app-wide command 위임 흐름은 부족함.
- Tab/workspace management: m3-3/m3-4가 workspace lifecycle은 다루지만 pinning, history, insert-position, browser-open, window title parity가 빠짐.
- Terminal panel wrapper + search state: m2-4는 panel host만 있고 search state 저장/복원 및 overlay 연결이 없음.
- Ghostty-backed terminal view: m2-1/m2-2는 core terminal은 있으나 clipboard, scroll/focus polish, lag logging이 없음.
- Browser panel UI: m4-1/m4-2는 기본 omnibar만 있고 focus flash, suggestion polish, command button 디테일이 부족함.
- Embedded web view wrapper: m4-1은 WebView2 host는 있으나 shortcut preservation, focus tracking, context-menu tweak 계약이 없음.
- Multi-window support + Finder Services routing: m1-2/m5-2는 다중 창/라우팅 기본만 있고 Finder Services 대응이 부족함.
- Titlebar decorations controller: m1-3는 backdrop/titlebar 기본만 있고 button hide/offset 세부 제어가 부족함.
- Update/focus debug logging: 별도 task는 없고 m5-3가 로그 정책만 freeze하므로 update/focus 전용 hook이 없음.

### 6.4 검증 결론

- 총 v1 범위 기능 수: 39
- plans에 task가 없는 기능 수: 12
- plans 보강이 필요한 최우선 항목: App commands + auxiliary windows, Shared panel abstraction, Notifications page, Settings window + preferences UI, Ghostty clipboard/pasteboard integration
