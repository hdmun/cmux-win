# 02. Core App

> [!IMPORTANT]
> 이 문서는 WinUI 3 app bootstrap, UI thread 경계, window lifecycle의 기준 문서다.

## 1. app startup 기준

v1의 앱 시작 경로는 다음 순서 하나로 고정한다.

1. `wWinMain`
2. `winrt::init_apartment(single_threaded)`
3. Windows App SDK bootstrap initialize
4. `Microsoft::UI::Xaml::Application::Start`
5. `App::OnLaunched`
6. `WindowManager`가 첫 `MainWindow` 생성

## 2. 스레딩 계약

| 영역 | 실행 스레드 | 비고 |
|------|-------------|------|
| XAML object 생성/접근 | UI thread only | STA 필수 |
| window creation / titlebar / backdrop | UI thread only | cross-thread 금지 |
| ConPTY read/write | background worker | UI 직접 접근 금지 |
| Named Pipe accept/read/write | background worker / threadpool | UI는 DispatcherQueue 경유 |
| Settings file I/O | background worker | UI 반영만 enqueue |
| Notification activation routing | parse는 background 허용, state update는 UI enqueue | |

### DispatcherQueue 규칙

1. background code는 XAML object를 직접 만지지 않는다.
2. UI 반영은 항상 `DispatcherQueue.TryEnqueue`를 거친다.
3. enqueue 실패는 조용히 무시하지 않고 로그를 남긴다.

## 3. window lifecycle

`WindowManager`는 아래 상태를 관리한다.

- create
- shown
- activated
- deactivated
- closing
- closed

마지막 window가 닫히면 app 종료를 시작한다.

## 4. 종료 순서

정상 종료 시 순서를 고정한다.

1. 새 IPC 연결 차단
2. shell / notification background callbacks 차단
3. panels detach
4. terminal / browser runtime dispose
5. settings flush 대기
6. windows close
7. bootstrap shutdown

종료 중에는 새 workspace/pane 생성 요청을 받지 않는다.

## 5. ID와 source of truth

| 값 | source of truth |
|----|-----------------|
| active window | `WindowManager` |
| active workspace | `TabManager` |
| active pane / surface | `BonsplitController` + panel container |

모든 selection state는 UI control이 아니라 core model이 보유한다.

## 6. MainWindow 책임

`MainWindow`는 아래만 책임진다.

- title bar / backdrop 초기화
- sidebar, content region, overlays의 XAML composition
- keyboard accelerators의 UI 라우팅
- active panel host 표시

반대로 아래 책임은 갖지 않는다.

- terminal parsing
- settings persistence
- IPC protocol parsing
- workspace business rule 결정

## 7. App command surface + 보조 창 (auxiliary windows)

> macOS `SwiftUI Commands` / `SettingsWindowController` / `AboutWindowController` 대응. app-level 명령을 라우팅하는 command surface와, 메인 창과 분리된 보조 `AppWindow`(Settings, About)의 소유·포커스·종료 규칙을 정의한다.

### 7.1 app command surface

- app-level 명령(예: open-settings, open-about, new-workspace, toggle-sidebar, show-notifications)은 단일 **app command surface** 를 통해 라우팅한다.
- command 라우팅은 `_workspace/09-config-settings.md` §6의 shortcut scope 규칙을 따른다. app reserved command가 panel shortcut보다 우선한다.
- command surface는 명령을 받아 `WindowManager`/`TabManager`/보조 창 컨트롤러로 위임만 한다. business rule을 직접 수행하지 않는다 (§6 MainWindow 비책임 원칙과 동일).

### 7.2 보조 창 소유 규칙

Settings 창과 About 창은 메인 `MainWindow`와 별개의 secondary `AppWindow`다.

| 규칙 | 내용 |
|------|------|
| 생성 | 요청 시 1개만 생성. 이미 열려 있으면 새로 만들지 않고 기존 창을 activate(foreground)한다 (single-instance) |
| 소유 | `WindowManager`가 보조 창 핸들을 보유한다. 메인 창과 동일한 lifecycle 추적(§3)을 받는다 |
| 포커스 | 보조 창 포커스는 §7 notification suppression의 "메인 창 포커스"로 간주하지 않는다 (`_workspace/07-notification.md` §7과 일치) |
| 종료 | 보조 창 close는 app 종료를 트리거하지 않는다. app 종료는 마지막 **메인** window가 닫힐 때만 시작한다(§3) |

### 7.3 Settings 창 / About 창 content

- Settings 창의 page content / 정보 구조(IA)는 `_workspace/09-config-settings.md` 및 `_workspace/17-functional-spec.md`가 소유한다. 본 문서는 창 셸(생성·소유·포커스)만 정의하고 page 내용은 재정의하지 않는다.
- About 창 content는 본 문서가 정의한다: 앱 이름, 버전, 빌드 식별자, 저작권/라이선스 링크, 1줄 설명. About 창은 modal이 아니며 read-only다.

### 7.4 수락 hook

- open-settings 명령을 두 번 호출하면 창이 1개만 존재하고 두 번째는 기존 창을 activate한다 (About도 동일).
- 보조 창을 닫아도 메인 창이 살아 있으면 app은 종료되지 않는다.
- About 창에 버전/빌드 식별자가 표시된다.

## 8. Draggable titlebar handle (drag region)

> macOS 배경 드래그 대응. custom titlebar의 drag region hit-test 규칙과 interactive content 충돌 회피를 정의한다. titlebar 확장/backdrop 자체는 §6 및 `_workspace/09-config-settings.md`가 다루므로 중복하지 않는다.

### 8.1 hit-test 규칙

- titlebar 영역에서 interactive control(버튼, 입력 박스, 탭, popover 트리거 등)이 차지하지 않은 나머지 영역을 drag region으로 지정한다 (`AppWindowTitleBar.SetDragRectangles` 또는 `InputNonClientPointerSource` passthrough region).
- interactive content 위에서는 드래그가 시작되지 않는다 (해당 영역을 drag rectangle에서 제외).
- drag region은 더블클릭 시 maximize/restore 시스템 동작을 보존한다.

### 8.2 동적 갱신

- titlebar control 레이아웃이 바뀌면(예: 버튼 표시/숨김, sidebar 토글) drag rectangle을 재계산한다.
- DPI/크기 변경 시 drag rectangle을 재계산한다.

### 8.3 수락 hook

- titlebar 빈 영역 드래그로 창이 이동한다.
- titlebar 버튼/입력 박스 위 드래그는 창을 이동시키지 않고 해당 control이 입력을 받는다.
- titlebar 빈 영역 더블클릭으로 maximize/restore가 동작한다.

## 9. Window accessor hook (`AppWindow`/`HWND` seam)

> macOS underlying-window 노출 대응. config/backdrop/titlebar 설정에 필요한 최소한의 native window 접근만 노출하는 bounded seam이다.

### 9.1 노출 범위

- `WindowManager`(또는 `MainWindow`)는 다음만 노출한다: 현재 `AppWindow` 참조, 필요한 경우 `HWND`(backdrop/titlebar/interop 한정).
- 노출은 read-mostly다. seam을 통해 임의의 윈도우 메시지 후킹이나 lifecycle 우회를 허용하지 않는다.

### 9.2 사용 제한

1. UI thread에서만 접근한다 (§2 스레딩 계약).
2. window lifecycle 상태(§3)의 source of truth는 여전히 `WindowManager`다. seam 소비자는 상태를 직접 바꾸지 않는다.
3. seam은 backdrop/titlebar/interop 설정 적용 외 용도로 사용하지 않는다.

### 9.3 수락 hook

- backdrop/titlebar 설정 코드가 seam을 통해 `AppWindow`/`HWND`를 얻어 적용한다.
- seam 접근이 UI thread 밖에서 호출되면 로그/assert로 위반을 드러낸다.

## 10. Toolbar controller (titlebar command region)

> macOS custom toolbar / command·tab title display 대응. titlebar의 command 영역에 명령 버튼을 배치하고 상태를 동기화하는 컨트롤러다.

### 10.1 역할

- titlebar 내 command region(좌측 시스템 버튼과 우측 시스템 캡션 버튼 사이)에 app command 버튼/표시를 배치한다.
- 현재 active workspace title 등 표시 텍스트를 titlebar에 반영한다 (source: `TabManager`).

### 10.2 명령 배치와 상태 동기화 규칙

1. command region에 올라가는 버튼은 §7.1 app command surface의 명령에 1:1로 바인딩한다.
2. 버튼 enabled/pressed/visible 상태는 core model(`WindowManager`/`TabManager`/`NotificationStore`)의 projection이다. 버튼 자체가 상태를 보유하지 않는다.
3. command region이 차지하는 영역은 §8 drag region에서 제외된다 (drag rectangle 재계산 트리거).

### 10.3 수락 hook

- workspace 전환 시 titlebar title 표시가 active workspace로 갱신된다.
- command 버튼 상태가 core model 변경에 따라 동기화된다.

## 11. Titlebar controls + shortcut hints

> macOS sidebar/new-tab/notification 버튼 + hint placement 대응. titlebar의 구체 command 버튼과 키보드 단축키 hint 표시 위치를 정의한다.

### 11.1 titlebar 버튼

| 버튼 | 바인딩 action | 비고 |
|------|---------------|------|
| sidebar 토글 | `toggle_sidebar` | sidebar visible 상태를 projection (§10.2) |
| new-workspace | `new_workspace` | `TabManager.CreateWorkspace` |
| notifications | `show_notifications` | `_workspace/07-notification.md` §11 popover의 open trigger |

- 각 버튼은 §10 toolbar controller의 command region에 배치된다.
- notifications 버튼은 unread count badge를 표시할 수 있다 (`NotificationStore` projection, taskbar badge와 동일 source).

### 11.2 shortcut hint 표시

- 각 버튼 tooltip에 현재 매핑된 단축키 hint를 표시한다. hint 문자열은 `_workspace/09-config-settings.md`의 `shortcuts` 스키마에서 해당 action 키 매핑을 읽어 생성한다 (본 문서는 키를 정의하지 않음).
- 단축키가 비어 있거나 미매핑이면 hint를 생략한다.

### 11.3 수락 hook

- titlebar에 sidebar/new-workspace/notifications 버튼이 표시되고 각 action을 트리거한다.
- 버튼 tooltip에 09 스키마 기준 단축키 hint가 표시되고, 매핑 변경 시 hint도 갱신된다.
- notifications 버튼이 unread > 0일 때 badge를 표시한다.

> [!NOTE]
> macOS의 SwiftUI key-press/pointer-style backport helper는 Windows 포트에서 별도 계층으로 이식하지 않는다. WinUI 3 기본 입력 경로(keyboard accelerator + pointer event)가 이를 대체한다.

## 12. M1 검증 기준

- 첫 window가 STA에서 정상 생성됨
- title bar 확장과 backdrop fallback이 동작함
- `WindowManager`가 active window를 추적함
- shutdown path가 고정된 순서로 동작함
- Settings/About 보조 창이 single-instance로 생성·activate되고 close가 app을 종료시키지 않음 (§7.4)
- titlebar drag region hit-test가 interactive content를 회피함 (§8.3)
- window accessor seam이 UI thread 한정으로 동작함 (§9.3)
- titlebar command 버튼 상태/title 동기화 및 shortcut hint 표시 (§10.3, §11.3)
