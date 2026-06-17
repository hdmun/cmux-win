# 17. Functional Specification

> [!IMPORTANT]
> 이 문서는 macOS cmux 참조 구현(`cmux\Sources`)을 기반으로 cmux-win v1이 Windows에서 구현해야 하는 기능을 정의한다. 각 기능은 macOS 참조 행동, Windows 구현 계획, 인수 기준 세 항목을 포함한다. 구현 우선순위는 milestone 순서를 따른다.

---

## 1. 앱 부트스트랩 및 lifecycle (M0/M1)

### 1.1 단일 부트스트랩 경로

**macOS 참조**: `cmuxApp.swift` — SwiftUI `@main`, init()에서 Ghostty 환경변수 주입 + AppDelegate 설정

**Windows 구현**:
- `wWinMain` → `winrt::init_apartment(single_threaded)` → Windows App SDK bootstrap → `Application::Start` → `App::OnLaunched` → `WindowManager`가 첫 `MainWindow` 생성
- unpackaged desktop app, Windows App SDK bootstrap 필수

**인수 기준**:
- `cmake --preset dev-x64 && cmake --build --preset dev-x64` 성공
- 첫 창이 STA에서 정상 생성됨
- Windows App SDK bootstrap 실패 시 즉시 fail (부분 설치 무시 금지)

### 1.2 window lifecycle

**macOS 참조**: `AppDelegate.swift` — NSWindow 이벤트 처리, 창 생성/닫기/포커스 라우팅

**Windows 구현**:
`WindowManager`가 아래 상태를 추적한다: `create` → `shown` → `activated` → `deactivated` → `closing` → `closed`

마지막 창이 닫히면 앱 종료를 시작한다.

**종료 순서** (고정):
1. 새 IPC 연결 차단
2. shell/notification background callbacks 차단
3. panels detach
4. terminal/browser runtime dispose
5. settings flush 대기
6. windows close
7. bootstrap shutdown

**인수 기준**:
- `WindowManager`가 active window를 추적함
- shutdown path가 고정된 순서로 동작함
- 종료 중 새 workspace/pane 생성 요청 거부됨

### 1.3 titlebar / backdrop

**macOS 참조**: AppKit NSWindow setTitlebarAppearsTransparent, NSVisualEffectView

**Windows 구현**:
- WinUI 3 extended titlebar 커스터마이징
- Win11: Mica 기본값
- Win10: Acrylic fallback
- `appearance.titlebar_style` 설정에 따라 `auto`/`mica`/`acrylic`/`none` 적용

**degradation matrix**:

| OS | Backdrop setting | Actual effect |
|----|------------------|---------------|
| Win11 22H2+ | `mica` | Mica applied |
| Win11 22H2+ | `acrylic` | Acrylic applied |
| Win11 22H2+ | `none` | Solid color |
| Win10 | `mica` | Falls back to `none` (solid) |
| Win10 | `acrylic` | Acrylic applied (if DWM composition active) |
| Win10 | `none` | Solid color |

**인수 기준**:
- backdrop fallback이 지원 매트릭스와 일치함
- DPI 변경 시 titlebar/backdrop 정상 재렌더링

---

## 2. workspace / tab 관리 (M1/M3)

### 2.1 workspace model

**macOS 참조**: `Workspace.swift` — BonsplitController + panel map, `typealias Tab = Workspace`

각 workspace는 다음을 소유한다:
- `workspace_id`: `workspace:<uuid>` 형식
- title (optional)
- working directory summary
- branch summary (branch name + dirty flag)
- unread notification count
- `BonsplitController` (split layout engine)
- panel map (pane_id → surface 매핑)

IPC를 통해 추가로 관리되는 rich 메타데이터:

| 필드 | 타입 | 설명 |
|------|------|------|
| `status_entries` | `map<string, SidebarStatusEntry>` | AI agent 상태 등 key-value |
| `log_entries` | `SidebarLogEntry[]` | 로그 스트림 (최신 N개) |
| `progress` | `SidebarProgressState?` | 진행률 바 |
| `git_branch` | `SidebarGitBranchState?` | branch name + isDirty |
| `listening_ports` | `int[]` | shell이 listen 중인 포트 목록 |

### 2.2 TabManager

**macOS 참조**: `TabManager.swift` — workspace 배열 관리, 선택 상태, 탭 히스토리, cross-workspace 포커스 복원

**Windows 구현**: `TabManager` 최소 public interface:
```cpp
class TabManager {
public:
    std::vector<WorkspaceState> ListWorkspaces() const;
    WorkspaceId GetActiveWorkspaceId() const;
    std::optional<WorkspaceState> GetWorkspace(WorkspaceId workspace_id) const;

    WorkspaceId CreateWorkspace(NewWorkspaceOptions const& options);
    bool ActivateWorkspace(WorkspaceId workspace_id);
    CloseWorkspaceResult CloseWorkspace(WorkspaceId workspace_id);

    void ApplyWorkspaceMetadata(WorkspaceId workspace_id, WorkspaceMetadataUpdate const& update);
    void SetUnreadCount(WorkspaceId workspace_id, uint32_t unread_count);
};
```

`active workspace`의 source of truth는 `TabManager`이다. `ListView.SelectedItem`은 결과 투영이다.

### 2.3 workspace lifecycle

상태 전이: `create` → `activate` → `deactivate` → `close-requested` → `closed`

**close 후 선택 규칙** (macOS와 다름):
1. 왼쪽 인접 항목
2. 오른쪽 인접 항목
3. 없으면 window 종료 경로

> macOS cmux는 `min(index, count-1)` (오른쪽 우선) 방식이지만, Windows 포트는 왼쪽 우선으로 명시적 설계 결정.

### 2.4 sidebar 투영

**macOS 참조**: `WorkspaceContentView.swift`, `NotificationsPage.swift` — sidebar ListView 투영

**업데이트 batching**:
- 기본 batch window: 100ms
- 최대 UI 반영 지연: 250ms
- unread / active 상태는 일반 메타데이터보다 우선

**UIA 최소 노출**:
- workspace item: title, active 여부, unread count, branch/directory summary

**v1 제외 기능** (macOS에는 있지만 Windows v1에서 제외):
- 탭 히스토리 back/forward (max 50)
- 워크스페이스 핀 고정 (`isPinned`)
- 새 탭 삽입 위치 설정 (top/afterCurrent/end)
- Ctrl+숫자(1~9) workspace 단축키

> 창 간 workspace/surface 이동은 v1 CLI 명령(`move-workspace-to-window`, `move-surface`)으로 지원한다. 다만 drag/drop detach UX polish는 후속 개선 범위다.

**인수 기준**:
- active workspace source of truth가 `TabManager`에 고정됨
- batch update가 전체 list rebuild 없이 동작
- close 후 selection 규칙이 일관되게 적용됨

---

## 3. split pane 레이아웃 (M2/M3)

### 3.1 BonsplitController

**macOS 참조**: `Workspace.swift` 내 BonsplitController 인스턴스화 — split tree, pane order, focus, layout version을 source of truth로 보유

**Windows 구현**: `BonsplitController` 최소 public interface:
```cpp
class BonsplitController {
public:
    LayoutSnapshot GetSnapshot() const;
    uint64_t GetLayoutVersion() const;
    PaneId GetActivePaneId() const;
    std::optional<SurfaceId> GetSurfaceId(PaneId pane_id) const;

    SplitResult SplitPane(PaneId target, SplitOrientation orientation);
    CloseResult ClosePane(PaneId target);
    MoveResult MovePane(PaneId source, PaneId destination, DropPosition position);
    bool FocusPane(PaneId target);

    void AttachSurface(PaneId pane_id, SurfaceId surface_id);
    void DetachSurface(PaneId pane_id);
};
```

UI는 controller가 내보낸 `LayoutSnapshot`만 반영한다. 모든 구조 변경은 `layout_version`을 증가시킨다.

### 3.2 `LayoutSnapshot` 계약

```cpp
struct LayoutSnapshot {
    uint64_t layout_version;
    PaneId active_pane_id;
    PaneNode root;
    std::vector<PanePresentation> panes;
};
```

- `Leaf` 노드: `pane_id` 필수, children 없음
- `Split` 노드: `orientation`, `primary_ratio`(첫 번째 child 비율), children 2개
- `panes` 컬렉션: XAML projection 계층이 pane/surface binding과 active state를 빠르게 읽을 수 있도록 제공

### 3.3 reparenting 규칙

split 이동이나 workspace 전환 시 panel instance를 **재생성하지 않는다**.

허용: container 교체, visibility 변경, logical parent 변경  
금지: move만으로 terminal/browser runtime dispose, focus 이동 중 panel recreate

**reattach_token 패턴** (terminal panel 전용):
- `TerminalPanel`은 `reattach_token` (uint64) 카운터 보유
- `Detach()` 호출 시 `++reattach_token_`
- XAML binding이 token 변화 감지 → `SetSwapChain()` 재호출로 D2D swapchain 재연결
- macOS `requestViewReattach()` 에 대응하는 패턴

### 3.4 focus 복원 규칙

1. split 직후 새 pane가 focus를 가짐
2. pane close 시 가장 가까운 sibling 우선
3. sibling 없으면 parent tree의 인접 pane
4. workspace 전환 시 마지막 active pane 복원

### 3.5 비포커스 패널 UX

- dim overlay: opacity = `unfocused-split-opacity` (기본 0.15), fill = `unfocused-split-fill` (기본 검정)
- unread 알림이 있는 패널: 파란색 테두리 링 표시

### 3.6 찾기 오버레이

**macOS 참조**: TerminalPanel의 search 기능 (find overlay)

- XAML Popup 또는 Canvas 오버레이로 패널 위 float 표시
- 드래그로 패널 내 위치 변경 가능
- 4개 코너(좌상/우상/좌하/우하)에 snap 지원
- 현재 N번째 / 전체 M개 매치 카운터 표시

### 3.7 Grid 구성

- XAML `Grid` + `GridSplitter` (CommunityToolkit)
- splitter drag는 UI가 처리하되, 최종 ratio source of truth는 controller

**인수 기준**:
- split/close/move 후 `layout_version` 일관성 유지
- pane focus 복원 규칙 준수
- panel reparent 시 runtime(ConPTY/WebView2) 유지
- reattach_token 증가 → SwapChainPanel swapchain 정상 재연결 확인

### 3.8 pane 내 surface 탭 바

> [!NOTE]
> macOS cmux의 pane 내 가로 surface 탭 바 + `+` 메뉴 대응. sidebar(workspace 단위, §2)와 구분되는, **하나의 pane 안에서 여러 surface(터미널/브라우저)를 전환**하는 affordance다. 상세 UX 계약은 task `m3-9`에서 확정하는 스텁이다.

- 각 pane 상단에 surface 탭 바를 둔다. 탭은 surface 제목(터미널 cwd/명령 또는 브라우저 페이지 제목)을 표시한다.
- `+` 버튼은 새 surface 생성 메뉴를 연다: `새 터미널`, `새 브라우저`(URL 입력). CLI `new-surface`(08 §10)와 동일 동작.
- 탭 선택은 pane의 active surface를 변경한다(레이아웃/포커스 규칙은 §3.3/§3.4).
- 탭 재정렬은 `reorder-surface`, 탭 닫기는 `close-surface`에 대응한다.
- surface가 1개뿐인 pane에서 탭 바 표시 여부는 `m3-9`에서 확정한다.

---

## 4. terminal panel (M2)

### 4.1 terminal stack

| 계층 | 선택 |
|------|------|
| PTY | ConPTY |
| VT parser | libvterm (vcpkg overlay port) |
| renderer | Direct2D + DirectWrite |
| host surface | WinUI 3 `SwapChainPanel` |

v1에서 custom VT parser는 작성하지 않는다.

### 4.2 ConPTY spawn

**Windows Terminal 참조**: `ConptyConnection::_LaunchAttachedClient()` — `PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE` + `CreateProcessW`

**API 호출 순서**:
1. pipe 쌍 생성 (`CreatePipe`)
2. `CreatePseudoConsole(size, h_pipe_in_read, h_pipe_out_write, flags, &hpc)` — flags: 0(standard) 또는 passthrough
3. `STARTUPINFOEXW` 조립 (`UpdateProcThreadAttribute`)
4. 환경 변수 주입: `CMUX_PIPE_NAME`, `CMUX_PANE_ID`, `CMUX_SURFACE_ID`
5. `CreateProcessW` (EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT)
6. 사용한 read/write 핸들 닫기

**Windows 환경 변수 rename note**:
- macOS `CMUX_SOCKET_PATH` → Windows `CMUX_PIPE_NAME`
- macOS `CMUX_WORKSPACE_ID` → Windows `CMUX_PANE_ID`
- macOS `CMUX_SURFACE_ID` → Windows `CMUX_SURFACE_ID` (unchanged)
- macOS legacy `CMUX_PANEL_ID` / `CMUX_TAB_ID` → Windows v1에서 주입 안 함

> **Note**: These values are fixed in the initial process environment block at ConPTY spawn time and are **not reinjected** on pane/workspace moves or reparents.

**passthrough 탐지 (ADR-0002)**:
- 세션 start 시 1회만 판정
- Win11 22H2+ (build ≥ 22621): passthrough 초기화 시도
- 실패하면 standard로 고정 (INFO 로그, UI 없음)
- `CMUX_CONPTY_MODE` 환경변수로 override 가능 (테스트용)
- `CMUX_CONPTY_MODE=standard` 강제 시 gate 무시

**resize 규칙**:
- UI 스레드에서 감지, `ResizePseudoConsole`은 background에 enqueue
- 50ms 이내 연속 호출은 마지막 값 하나만 전달 (throttle)

### 4.3 libvterm wrapper

**`VtermWrapper` 최소 인터페이스** (src/terminal/engine/vterm_wrapper.h):
```cpp
class VtermWrapper {
public:
    explicit VtermWrapper(int rows, int cols);
    ~VtermWrapper();
    void PushBytes(const char* data, size_t len);
    void Resize(int rows, int cols);
    const TerminalBuffer& Buffer() const;
private:
    VTerm* vterm_{nullptr};
    VTermScreen* screen_{nullptr};
    TerminalBuffer buffer_;
};
```

모든 메서드는 background worker 스레드에서만 호출한다.

### 4.4 터미널 스레딩 (ADR-0001)

| 작업 | 스레드 |
|------|--------|
| ConPTY read loop | background worker |
| VT parse (libvterm) | background worker |
| dirty region 계산 | background worker |
| frame publish | background → atomic handoff |
| swapchain invalidate enqueue | background |
| Direct2D draw | UI thread |
| IME rect 계산/업데이트 | UI thread |
| UIA event raise | UI thread |
| Named Pipe accept/read/write | background/threadpool |
| Settings file I/O | background worker |

**handoff**: `std::atomic<std::shared_ptr<TerminalFrame>>` — immutable snapshot 패턴

### 4.5 Direct2D 렌더러

**Windows Terminal 참조**: `BackendD2D::Render()` — background/cursor/text passes, `CreateDxgiSurfaceRenderTarget`

**render loop**:
```
[background]                         [UI thread]
PushBytes() → VtermWrapper           DispatcherQueue.TryEnqueue()
           → TerminalBuffer dirty    → SwapChainPanel.Invalidate()
           → atomic publish frame    → D2DRenderer.DrawFrame()
```

**글자 타일 캐시**:
- 키: `(codepoint, font_size, attrs)`
- 상한: 4096 슬롯, LRU 교체
- DPI 변경 시 전체 무효화

**DPI 변경 처리**:
1. `SwapChainPanel.DpiChanged` 수신 (UI thread)
2. `IDXGISwapChain::ResizeBuffers()` 호출
3. 글자 타일 캐시 무효화
4. IME rect 즉시 재계산

### 4.6 IME 지원

**Windows Terminal 참조**: `tsf/Implementation.cpp` — `GetTextExt()`/`GetScreenExt()`, TSF TS_SS_TRANSITORY

- TSF 우선 경로
- composition rect: terminal cursor의 pixel rect 기준
- DPI 변경/split resize/monitor move 후 rect 즉시 재계산
- IME 실패 시 silent drop 금지, fallback 로그 필수

### 4.7 UIA 접근성

**Windows Terminal 참조**: `WindowUiaProvider`, `ScreenInfoUiaProvider`, `TermControlAutomationPeer`, `UiaRenderer`

v1 최소 요구:
- visible text를 TextPattern으로 노출
- caret 이동 event 발행
- viewport 변경 event 발행
- Narrator/NVDA가 현재 line/selection 읽기 가능

### 4.8 panel lifecycle

공통 lifecycle (ADR-0004): `created` → `attached` → `focused` → `blurred` → `hidden` → `detached` → `disposed`

terminal 특이 사항:
- `hidden`: ConPTY 종료 금지
- `disposed`: ConPTY → libvterm → D2D 순서로 해제
- split 이동/workspace 전환은 `hidden` 또는 `detached`만 사용

**isDirty 억제**: 항상 `false` 반환 (VT 기반 오탐 방지). 실제 close 확인은 `needsConfirmClose()`.

**인수 기준**:
- Win10: standard ConPTY 동작
- Win11 22H2+: passthrough gate 판정 로그 존재
- dirty region 기반 redraw (전체 화면 clear 시 변경 없는 셀 재렌더링 금지)
- IME candidate window 위치 정상 (cursor pixel rect 기준)
- Narrator/NVDA로 텍스트 이동 확인
- 새 shell spawn 시 환경 변수 세 개 정상 주입 확인

### 4.9 파일 드롭 수신

> [!NOTE]
> macOS Ghostty의 터미널 파일 드롭 대응. drop **수신**(drag-enter/drop 이벤트 → 경로 추출)은 이 절이, escaping은 `10-shell-integration.md §9`가 소유한다. 상세는 task `m6-11`에서 확정하는 스텁이다.

- terminal panel은 파일 드롭 대상으로 등록된다(WinUI `DragEnter`/`Drop`, `DataPackageView` `StorageItems`).
- drop된 항목의 OS 경로를 추출해 `10 §9`의 셸별 escaping을 적용한 뒤, 현재 surface 입력 라인에 **paste만** 한다(자동 실행 없음).
- 다중 파일은 각 경로를 개별 escaping 후 공백으로 join한다(`10 §9.1`).
- IPC `simulate_file_drop`(08 §13.2)은 이 경로를 테스트에서 주입하는 진입점이다.

---

## 5. browser panel (M4)

### 5.1 기본 구성

| 요소 | 선택 |
|------|------|
| host | WinUI 3 XAML |
| browser control | WebView2 |
| automation channel | CDP |
| UI composition | XAML tree 안에서 처리 |

### 5.2 WebViewEnvironmentPool

**macOS 참조**: `BrowserPanel.swift` — NSWKWebView pool 없음 (macOS는 WKWebView 직접 사용, pool 불필요)

- profile / privacy mode 단위로 environment 재사용
- 최초 warm-up 허용
- panel close 시 environment는 pool에 반환
- split 이동/workspace 전환만으로 environment를 다시 만들지 않음 (`EnsureCoreWebView2Async()` 재실행 금지)

### 5.3 browser panel lifecycle

공통 lifecycle 그대로 (ADR-0004):
- `hidden`/`detached`에서 WebView2 session 유지
- `disposed`에서만 event token, CDP session, control 정리

### 5.4 omnibar

**macOS 참조**: `BrowserPanelView.swift:18-196` — omnibar/address bar UX, search suggestions, inline completion, focus flash

규칙:
- URL에 스킴 없으면 `https://` 보정
- 공백 포함 시 search engine query로 전환
- `Ctrl+L`: omnibar focus + 전체 선택

**인라인 자동완성/제안 소스**:
- browser history, open tabs, remote suggestions를 사용한다
- open-tab suggestion은 navigation이 아니라 전용 **switch-to-tab** action으로 표시하며 distinct UI label을 사용한다
- `Tab`으로 수락, `Backspace`로 취소

**원격 검색 제안**:
- Google, DuckDuckGo, Bing 병렬 지원
- 요청 timeout: 0.65초; timeout 초과 시 remote suggestion만 생략하고 로컬 browser history/open tab suggestion은 유지

### 5.5 히스토리 관리

- 저장: `%APPDATA%\cmux\browser_history.json`
- 최대 5000개, 초과 시 오래된 항목 자동 삭제
- 정렬: frecency score (방문 횟수 + 최근성 가중치)
- 파비콘: URL별 캐시

### 5.6 페이지 표시 규칙

| 항목 | 규칙 |
|------|------|
| 페이지 줌 | 0.25x ~ 5.0x 범위, `Ctrl++`/`Ctrl+-`/`Ctrl+0` |
| 로딩 최소 표시 시간 | 0.35초 (flicker 방지) |
| 파비콘 | FaviconChanged 이벤트, omnibar와 탭 레이블에 표시 |

### 5.7 CDP automation

v1은 CDP 우선, silent JS fallback 없음:
- `snapshot`, `click`, `fill`, `network` 계열: CDP
- `evaluate`: 명시적 JavaScript API

error contract: `08-ipc-cli.md` error code 표 사용 (`browser_cdp_unavailable`, `browser_cdp_failed`)

**인수 기준**:
- WebView2 host가 workspace/split 전환 후 browsing session 유지
- CDP unavailable 시 명시적 error 반환
- omnibar URL normalization 및 Ctrl+L 동작
- 로딩 최소 표시 시간 0.35초 준수
- 원격 검색 제안 timeout 0.65초 준수

---

## 6. IPC / CLI (M3/M5)

### 6.1 transport

| 항목 | 규칙 |
|------|------|
| transport | Named Pipe |
| mode | `PIPE_TYPE_MESSAGE` + `PIPE_READMODE_MESSAGE` |
| max payload | 1 MiB |
| security | same-user ACL |
| naming | `\\.\pipe\cmux-<session>-<pid>` |

**macOS와의 차이**: macOS는 Unix socket (`/tmp/cmux*.sock`) 사용. Windows는 Named Pipe.

**pipe discovery precedence**:
1. `--pipe <path>` CLI argument
2. `CMUX_PIPE_NAME` environment variable
3. `\\.\pipe\cmux-default-<username>` (fallback default)

**transport 관련 환경 변수**:
- `CMUX_PIPE_ENABLE`: `0`이면 pipe server 비활성화
- `CMUX_PIPE_MODE`: transport mode override
- `CMUXTERM_CLI_RESPONSE_TIMEOUT_SEC`: client response timeout (default: 15초)

### 6.2 프로토콜

- version: 2
- field naming: `snake_case`, UTF-8
- request/response: 각각 하나의 complete message

**capabilities handshake**:
```json
{
  "type": "capabilities",
  "version": 2,
  "platform": "win32",
  "features": ["split_pane", "browser_panel", "notifications", "shell_report"]
}
```

### 6.3 ID 규칙

| 필드 | 전체 형식 | 단축 참조 |
|------|-----------|-----------|
| `window_id` | `window:<uuid>` | `window:N` |
| `workspace_id` | `workspace:<uuid>` | `workspace:N` |
| `pane_id` | `pane:<uuid>` | `pane:N` |
| `surface_id` | `surface:<uuid>` | `surface:N` |
| `notification_id` | `notification:<uuid>` | — |

`--id-format refs|uuids|both` 플래그로 응답 형식 선택. 단축 참조는 연결 세션 내에서만 유효.

### 6.4 error code 표준

| code | 의미 | Retry? |
|------|------|--------|
| `unsupported_version` | protocol version 미지원 | no |
| `not_supported` | 기능/플랫폼 미지원 | no |
| `invalid_request` | schema/필수 필드 오류 | no |
| `unknown_command` | 존재하지 않는 command | no |
| `payload_too_large` | 1 MiB 초과 | no |
| `acl_denied` | same-user ACL 실패 | no |
| `pipe_connect_failed` | pipe 연결 실패 | yes |
| `pipe_read_failed` | pipe read I/O error | yes |
| `pipe_write_failed` | pipe write I/O error | yes |
| `state_conflict` | 앱 상태와 충돌 | depends |
| `not_found` | 리소스 없음 | no |
| `browser_cdp_unavailable` | CDP session 없음 | no |
| `browser_cdp_failed` | CDP command execution failed | depends |
| `settings_write_failed` | settings 저장 실패 | yes |

### 6.5 socket_control.mode

| mode | 동작 |
|------|------|
| `full` | capabilities, shell auto-report, read/write 모두 허용 |
| `readonly` | capabilities, shell auto-report, read-only query만 허용 |
| `off` | Named Pipe server 생성 안 함 |

> macOS cmux의 `notifications` 모드(알림 명령만)와 달리, Windows의 `readonly`는 모든 read-only 조회를 허용.

### 6.6 CLI 명령 카탈로그

**macOS 참조**: `CLI/cmux.swift` — `SocketClient`, v2 JSON commands, window/workspace/pane/surface 관리, browser 제어

`cmux.exe [global-flags] <command> [args]` 형식.

**전역 플래그**: `--pipe`, `--id-format refs|uuids|both`, `--window`

**command 그룹**:

| 그룹 | 주요 명령 |
|------|-----------|
| System | `ping`, `capabilities`, `identify`, `session_info` |
| Windows | `list-windows`, `current-window`, `new-window`, `focus-window`, `close-window` |
| Workspaces | `list-workspaces`, `new-workspace`, `select-workspace`, `current-workspace`, `close-workspace`, `move-workspace-to-window`, `reorder-workspace` |
| Panes/Surfaces | `list-panes`, `list-pane-surfaces`, `focus-pane`, `new-pane`, `new-surface`, `close-surface`, `move-surface`, `reorder-surface`, `drag-surface-to-split`, `trigger-flash`, `refresh-surfaces` |
| Input | `send`, `send-key` |
| Notifications | `notify`, `list-notifications`, `clear-notifications` |
| App Control | `set-app-focus` |
| claude-hook | `session-start`, `session-stop`, `notification`, `active`, `idle` |
| Browser | `cmux browser <subcommand>` |

**browser subcommand 그룹**:

| 카테고리 | subcommand |
|----------|-----------|
| 탐색 | `open`, `open-split`, `goto`, `navigate`, `back`, `forward`, `reload`, `url` |
| 페이지 정보 | `snapshot`, `screenshot`, `get`, `is`, `state` |
| 상호작용 | `click`, `dblclick`, `hover`, `focus`, `check`, `uncheck`, `type`, `fill`, `press`, `key`, `keydown`, `keyup`, `select`, `scroll`, `scroll-into-view` |
| 기다리기 | `wait` |
| 검색 | `find`, `eval` |
| 프레임 | `frame` |
| 다이얼로그 | `dialog` |
| 다운로드 | `download` |
| 쿠키 / 스토리지 | `cookies`, `storage` |
| 탭 관리 | `tab` |
| 네트워크 | `network` |
| 콘솔 / 오류 | `console`, `errors` |
| 스크립트 | `addinitscript`, `addscript`, `addstyle` |
| 뷰포트 / 환경 | `viewport`, `geolocation`, `offline` |
| 디버깅 | `trace`, `screencast`, `highlight` |
| 식별 | `identify` |

`--snapshot-after` 플래그는 `navigate`, `click`, `type` 등 동작 완료 후 DOM 스냅샷을 응답에 포함한다.

**claude-hook 특이 사항**:
- stdin으로 JSON payload 수신
- 세션 상태: `%APPDATA%\cmux\claude-hook-sessions.json`
- 파일 잠금: Windows `LockFileEx`
- `set_status`/`clear_status`로 workspace 상태 badge 설정

### 6.7 shell auto-report payload

IPC와 별도 경로. v1 지원 타입:

```json
{ "type": "shell.directory", "version": 2, "pane_id": "pane:<uuid>", "cwd_uri": "file:///C:/..." }
{ "type": "shell.git_branch", "version": 2, "pane_id": "pane:<uuid>", "branch": "main" }
```

**인수 기준**:
- capabilities response가 protocol version 2와 일치
- same-user ACL 적용됨 (ACL 실패 시 pipe 생성도 실패)
- oversized payload, unknown command, state conflict 자동화 테스트
- claude-hook sessions.json LockFileEx 파일 잠금 동작

---

## 7. 알림 (M6)

### 7.1 notification model

**macOS 참조**: `TerminalNotificationStore.swift` — `TerminalNotification` 스키마, dock badge, suppress 규칙

```cpp
// src/notification/notification_store.h
struct Notification {
    NotificationId id;       // notification:<uuid>
    WorkspaceId workspace_id;
    std::optional<SurfaceId> surface_id;
    std::string title;
    std::optional<std::string> subtitle;
    std::string body;
    std::chrono::system_clock::time_point created_at;
    bool is_read;
};
```

### 7.2 NotificationStore 최소 interface

```cpp
NotificationId AddNotification(NewNotificationOptions const& opts);
void MarkRead(NotificationId id);
void MarkUnread(NotificationId id);
void ClearNotifications(WorkspaceId workspace_id, std::optional<SurfaceId> surface_id = std::nullopt);
uint32_t GetUnreadCount(WorkspaceId workspace_id) const;
```

**unread source of truth**: `NotificationStore`가 계산. sidebar/panel ring은 projection만.

**중복 억제**: 동일 `(workspace_id, surface_id)` 조합의 기존 알림을 먼저 제거 후 새 알림 추가.

### 7.3 toast 정책

- v1: 모든 toast action은 foreground activation (background COM activation 없음)
- payload: `notification_id`, `workspace_id`, optional `surface_id`, `action`
- Notification toast activation payload는 originating workspace/surface로 focus를 복원할 수 있도록 파싱한다. payload schema: `{ "workspace_id": "<uuid>", "surface_id": "<uuid>" }`
- payload 필드가 누락돼도 graceful handling 해야 하며 crash하면 안 된다

**degrade 규칙**:
- AppNotification 등록 실패: toast만 disable, in-app 알림 유지
- toast show 실패: 로그 + 계속 진행
- OS 알림 권한 거부: Windows 설정 안내 UI + in-app 알림 유지

### 7.4 suppress 규칙

**macOS 참조**: `TerminalNotificationStore.swift:145-156` — app focused + active pane 시 suppress

suppress 조건 (모두 만족 시 알림 생성 안 함):
1. 앱이 메인 창 기준 포커스된 상태 (Settings/About 같은 보조 창은 포커스로 간주 안 함)
2. 해당 workspace가 활성 workspace
3. 해당 surface가 현재 포커스된 surface

`notifications.suppress_when_focused = false` 시 항상 알림 생성.

### 7.5 taskbar badge

**macOS 참조**: `NotificationBadgeSettings` + `CMUX_TAG` 환경변수 — dock badge 포함

| 조건 | 표시 |
|------|------|
| unread > 0 | unread 개수 |
| unread > 99 | `"99+"` |
| `CMUX_TAG` 환경 변수 설정 시 | `"<tag>:<count>"` 또는 `"<tag>"` |
| unread = 0 | badge 제거 |

`BadgeNotification` 또는 taskbar overlay icon으로 구현.

### 7.6 보존 및 GC

- GC 주기: 10분
- read notification 만료: 24시간
- 최대 보관 개수: 200

**인수 기준**:
- toast 실패 시 앱 기능 유지
- Notification toast activation payload가 `{ "workspace_id": "<uuid>", "surface_id": "<uuid>" }` 스키마로 파싱되어 originating workspace/surface focus 복원에 사용됨
- payload 필드 누락 시 graceful handling 되며 crash하지 않음
- 동일 (workspace_id, surface_id) 중복 알림 억제
- taskbar badge 카운트 정확성 및 99+ 캡
- suppress 조건 정확히 동작

---

## 8. 설정 / config (M6)

### 8.1 source of truth

**macOS 참조**: `cmuxApp.swift @AppStorage` + `KeyboardShortcutSettings.swift` + `SocketControlSettings.swift`

| 파일 | 역할 |
|------|------|
| `%APPDATA%\cmux\settings.json` | source of truth |
| `%APPDATA%\ghostty\config` 등 | terminal defaults 보조 입력 |
| `settings.json.bak` | migration backup |

### 8.2 precedence 규칙

1. built-in defaults
2. Ghostty config parse (`font-family`, `font-size`, `theme`, `scrollback-limit`, 색상 팔레트, split opacity 등)
3. `settings.json` explicit overrides
4. runtime-detected `support_matrix` recompute

### 8.3 v1 필드 스키마 (고정)

| 필드 | 타입 | 기본값 |
|------|------|--------|
| `schema_version` | integer | `1` |
| `socket_control.mode` | string | `"full"` |
| `sidebar.visible` | boolean | `true` |
| `sidebar.width` | integer | `220` |
| `sidebar.resizable` | boolean | `true` |
| `appearance.theme` | string | `"auto"` |
| `appearance.titlebar_style` | string | `"auto"` |
| `terminal.default_shell` | string | `"powershell"` |
| `terminal.scrollback_limit` | integer | `10000` |
| `terminal.cursor_blink` | boolean | `true` |
| `terminal.font_family` | string | `"Cascadia Code"` |
| `browser.search_engine` | string | `"google"` |
| `browser.restore_session` | boolean | `true` |
| `notifications.toast_enabled` | boolean | `true` |
| `notifications.suppress_when_focused` | boolean | `true` |
| `analytics.enabled` | boolean | `false` |

> ⚠️ `analytics.enabled`는 반드시 `false`(기본값). 사용자가 명시적으로 opt-in해야만 전송. macOS cmux는 RELEASE 빌드에서 항상 전송하지만 Windows 포트는 금지.

### 8.4 atomic write 규칙

1. temp file write
2. flush
3. replace
4. old file backup 유지 조건 판단

실패 시: 이전 값 유지 + UI에 명시적 실패 노출 (silent fail 금지)

### 8.5 migration 규칙

- `schema_version`이 낮으면 migration 수행
- migration 전 원본을 `settings.json.bak`으로 백업
- migration 실패 시 새 파일로 덮어쓰지 않음

### 8.6 shortcut scope 규칙

**macOS 참조**: `KeyboardShortcutSettings.swift:6-33` — toggle sidebar, new tab/window, notifications, flash, surface nav, split, browser, focus directions

| scope | 의미 |
|-------|------|
| `global` | app-wide command |
| `workspace` | active workspace 범위 command |
| `surface` | 현재 focus된 terminal/browser surface 범위 command |

**shortcut JSON schema**:

```json
"shortcuts": {
  "<action_name>": {
    "key": "<key>",
    "ctrl": false,
    "shift": false,
    "alt": false,
    "win": false,
    "scope": "global|workspace|surface"
  }
}
```

**기본 shortcut 목록** (Windows 키 이름):

| action | 기본 shortcut | scope |
|--------|--------------|-------|
| `toggle_sidebar` | Ctrl+B | global |
| `new_workspace` | Ctrl+N | global |
| `close_workspace` | Ctrl+W | global |
| `split_right` | Ctrl+D | surface |
| `split_down` | Ctrl+Shift+D | surface |
| `next_surface` | Ctrl+Shift+] | surface |
| `prev_surface` | Ctrl+Shift+[ | surface |
| `focus_left` | Ctrl+Alt+Left | surface |
| `focus_right` | Ctrl+Alt+Right | surface |
| `focus_up` | Ctrl+Alt+Up | surface |
| `focus_down` | Ctrl+Alt+Down | surface |
| `open_browser` | Ctrl+Shift+L | global |
| `show_notifications` | Ctrl+I | global |
| `jump_to_unread` | Ctrl+Shift+U | global |
| `trigger_flash` | Ctrl+Shift+H | global |

**conflict 해결**: text input control 우선 → app reserved → 현재 scope 일치 여부 확인 → 동일 조합 중복 validation error

**debounced persistence**: UI 변경은 ViewModel에 즉시 반영, 파일 쓰기는 250ms debounce

**인수 기준**:
- precedence 결과가 결정적임
- atomic write가 깨진 JSON을 남기지 않음
- migration backup 생성됨
- shortcut conflict 검증이 UI 저장 전에 수행됨

### 8.7 settings window / preferences UI

**macOS 참조**: `SettingsWindowController`, `SettingsView` — 단일 설정 창 + 카테고리 navigation

`settings.json`은 source of truth로 유지하되(§8.1), 사용자는 전용 settings window에서 주요 필드를 편집할 수 있다. settings window의 창 lifecycle(생성/소유/포커스/닫기)은 `02-core-app.md` §7 "App command surface + 보조 창"이 소유한다. 이 절은 그 창 안의 정보 구조(IA)와 저장 흐름만 고정한다.

**navigation 카테고리** (좌측 nav, 단일 창):

| 카테고리 | 편집 대상 필드 (§8.3) |
|----------|------------------------|
| General | `appearance.theme`, `appearance.backdrop` |
| Terminal | `terminal.default_shell`, `terminal.scrollback_limit`, `terminal.cursor_blink`, `terminal.font_family`, `terminal.paste_confirm` |
| Browser | `browser.search_engine`, `browser.restore_session` |
| Shortcuts | `shortcuts.*` (§8.6 scope/conflict 규칙 적용) |
| Advanced | `socket_control.mode`, `analytics.enabled` (read-mostly, 위험 필드는 확인 dialog) |

**편집 가능 범위**:
- UI는 §8.3 v1 필드 스키마에 존재하는 필드만 노출한다. 스키마에 없는 필드는 UI에서 편집하지 않는다.
- UI에서 다루지 않는 고급 키는 "open settings.json" 동작으로 raw 편집을 유도한다(파일을 기본 편집기로 연다).

**저장 흐름**:
1. UI 변경은 settings ViewModel에 즉시 반영한다.
2. 파일 쓰기는 §8.6과 동일하게 250ms debounce 후 §8.4 atomic write 규칙으로 기록한다.
3. shortcut 편집 저장 전에는 §8.6 conflict 검증을 먼저 수행하고, 실패 시 저장하지 않고 inline validation error를 표시한다.
4. 외부에서 `settings.json`이 바뀌면(파일 watch) UI는 현재 미저장 편집과 충돌하지 않는 범위에서 갱신한다. 충돌 시 사용자에게 reload/keep 선택을 제시한다.

**인수 기준**:
- settings window가 단일 인스턴스로 열리고 재요청 시 기존 창에 포커스한다(02 §7 계약 위임)
- 각 카테고리에서 편집한 값이 §8.4 atomic write로 `settings.json`에 반영됨
- shortcut conflict가 UI 저장 전에 차단됨
- 스키마에 없는 필드는 UI에 노출되지 않음

---

## 9. shell integration (M6)

### 9.1 지원 범위

| 환경 | v1 상태 |
|------|---------|
| PowerShell 7.2+ | 지원 (권장) |
| Windows PowerShell 5.1 | 제한 지원 |
| CMD | 지원 (OSC 7 중심) |
| WSL | 제한 지원 (relay 없으면 제한) |

### 9.2 환경 변수 주입

terminal spawning path가 shell process 생성 시 주입:
- `CMUX_PIPE_NAME`: app instance의 Named Pipe 경로
- `CMUX_PANE_ID`: 현재 pane의 `pane:<uuid>`
- `CMUX_SURFACE_ID`: 현재 surface의 `surface:<uuid>`

**Windows rename note**:
- macOS `CMUX_SOCKET_PATH` → Windows `CMUX_PIPE_NAME`
- macOS `CMUX_WORKSPACE_ID` → Windows `CMUX_PANE_ID`
- macOS `CMUX_SURFACE_ID` → Windows `CMUX_SURFACE_ID` (unchanged)
- macOS legacy `CMUX_PANEL_ID` / `CMUX_TAB_ID` → Windows v1에서 주입 안 함

> **Note**: These values are fixed in the initial process environment block at ConPTY spawn time and are **not reinjected** on pane/workspace moves or reparents.

shell integration 스크립트는 이 값을 **소비만** 한다 (생성 금지).

### 9.3 PowerShell 규칙

- prompt blocking 금지
- directory 보고: 항상 lightweight (`shell.directory` payload)
- git branch 보고: 비동기 (`Start-ThreadJob` 가능 시), 불가 시 disable 또는 lightweight fallback
- port/process polling: shell script에서 하지 않음 (app backend가 책임)
- `cwd_uri`는 RFC 8089 형식(`file:///C:/Users/...`)을 따라야 함

**failure 처리**: `CMUX_PIPE_NAME` 없음 → silent no-op, `CMUX_PANE_ID` 없음 → auto-report no-op (pipe connection 시도 금지), pipe write 실패 → verbose log만

### 9.4 CMD 규칙

- OSC 7 current directory 보고만
- git branch 비동기 보고: v1 필수 범위 아님

### 9.5 WSL 범위

- relay 도구 없으면 directory/local shell UX만 유지
- WSL 미지원이 앱 전체 기능 실패로 이어지지 않음

**payload 예시**:
```json
{ "type": "shell.directory", "version": 2, "pane_id": "pane:<uuid>", "cwd_uri": "file:///C:/..." }
{ "type": "shell.git_branch", "version": 2, "pane_id": "pane:<uuid>", "branch": "main" }
```

**인수 기준**:
- PowerShell prompt blocking 없음
- ThreadJob 미지원 환경에서 graceful degrade
- CMD 최소 기능 유지
- `CMUX_PANE_ID`가 없으면 auto-report가 no-op이며 pipe connection을 시도하지 않음
- `cwd_uri`가 RFC 8089 형식(`file:///C:/Users/...`)을 따름
- direct pipe payload가 `08-ipc-cli.md`와 동일 스키마

---

## 10. 빌드 및 의존성 (M0)

### 10.1 단일 부트스트랩 경로

Visual Studio 2022 + CMake Presets + vcpkg manifest mode + NuGet central package management

**표준 명령**:
```powershell
cmake --preset dev-x64
cmake --build --preset dev-x64
ctest --preset dev-x64 --output-on-failure
```

### 10.2 target 이름

| target | 의미 |
|--------|------|
| `cmux_app` | WinUI 3 app binary |
| `cmux_cli` | `cmux.exe` CLI |
| `cmux_core` | 공유 core/model 라이브러리 |
| `cmux_terminal` | terminal runtime 계층 |
| `cmux_ipc` | IPC/runtime 계층 |
| `cmux_tests` | test aggregate target |

### 10.3 의존성 소유권

| 의존성 | 관리 방식 | authoritative 위치 |
|--------|-----------|---------------------|
| libvterm | vcpkg overlay port | `ports/libvterm/` + `vcpkg.json` |
| nlohmann-json | vcpkg | `vcpkg.json` |
| gtest | vcpkg | `vcpkg.json` |
| spdlog | vcpkg | `vcpkg.json` (`src/utils/logger.h` logging subsystem용) |
| Microsoft.Windows.CppWinRT | NuGet | `Directory.Packages.props` |
| Windows App SDK | NuGet | `Directory.Packages.props` |
| WebView2 SDK | NuGet | `Directory.Packages.props` |
| CommunityToolkit | NuGet | `Directory.Packages.props` |

**vendor 금지**: `vendor/libvterm` 등 별도 복사 금지. overlay port만 사용.

---

## 11. namespace 및 디렉터리 구조

### 11.1 C++ namespace

| 계층 | namespace |
|------|-----------|
| app/ui | `cmux::app`, `cmux::ui`, `cmux::panels` |
| core model | `cmux::core` |
| terminal | `cmux::terminal` |
| IPC | `cmux::ipc` |
| notification | `cmux::notification` |
| config | `cmux::config` |
| utils | `cmux::utils` |

### 11.2 디렉터리 구조

```text
src/
├── app/         (WinUI 3 app, MainWindow, WindowManager)
├── core/        (BonsplitController, TabManager, core model)
├── panels/      (TerminalPanel, BrowserPanel, panel lifecycle)
├── terminal/
│   ├── engine/  (ConPTY, VtermWrapper, TerminalBuffer)
│   ├── renderer/ (D2DRenderer, GlyphCache, TerminalFrame)
│   ├── ime/     (ImeHandler)
│   └── uia/     (UiaProvider)
├── ui/          (XAML controls, titlebar, backdrop, omnibar)
├── ipc/         (ControlServer, pipe transport, command dispatcher)
├── notification/ (NotificationStore, ToastBridge)
├── config/      (SettingsStore, SettingsMigration, ShortcutRegistry)
└── utils/       (logger, dispatcher_queue_helper, string_encoding)
```

---

## 12. 플랫폼 지원 매트릭스

| 기능 | Windows 10 1809+ | Windows 11 22H2+ |
|------|------------------|-----------------|
| WinUI 3 기본 UI | ✅ | ✅ |
| Title bar customization | ✅ | ✅ |
| Acrylic backdrop | ✅ | ✅ |
| Mica backdrop | ❌ | ✅ |
| ConPTY standard mode | ✅ | ✅ |
| ConPTY passthrough | ❌ | ✅ |
| WebView2 browser panel | ✅ (Evergreen 필요) | ✅ |
| AppNotification toast | ✅ (실패 시 degrade) | ✅ |

---

## 13. 로그 / 개인정보 정책

**로그에 허용**:
- notification id, workspace id, surface id
- action type, error code

**로그에 불허**:
- notification body 원문
- 페이지 본문 / terminal 출력 전문
- 사용자 개인정보

**analytics**: 기본값 `false`. 사용자가 명시적으로 opt-in해야만 전송.

---

## 14. macOS cmux와의 주요 차이점 요약

| 항목 | macOS cmux | Windows cmux-win |
|------|-----------|-----------------|
| transport | Unix socket (`/tmp/cmux*.sock`) | Named Pipe (`\\.\pipe\cmux-...`) |
| socket_control mode 종류 | `off`, `notifications`, `full` | `off`, `readonly`, `full` |
| close 후 탭 선택 | 오른쪽 우선 (`min(index, count-1)`) | 왼쪽 우선 (명시적 결정) |
| analytics | RELEASE 빌드에서 항상 전송 | 기본 off, opt-in 필요 |
| terminal renderer | Ghostty (Metal + libvterm) | Direct2D + DirectWrite + libvterm |
| app framework | SwiftUI + AppKit | WinUI 3 + C++/WinRT |
| IPC client | `cmux` (macOS CLI) | `cmux.exe` (Windows CLI) |

---

## 15. 문서 갱신 규칙

이 문서가 변경되면 아래도 함께 수정한다:
- 관련 도메인 `_workspace/*.md` 문서
- `plans/milestones/*.json` (acceptance criteria 변경 시)
- `_workspace/12-tasks.md` (milestone 범위 변경 시)

---

## 18. macOS→Windows 의도적 차이점 (Intentional Divergences)

| 항목 | macOS cmux | Windows cmux-win | 근거 |
|------|-----------|-----------------|------|
| IPC 전송 | Unix socket | Named Pipe (`\\.\pipe\cmux-<session>-<pid>`) | Windows transport |
| socket_control mode | `notifications` | `readonly` | 기능 범위 확장 |
| 탭 닫기 선택 | 오른쪽 형제 우선 | 왼쪽 형제 우선 | 명시적 설계 결정 |
| 분석/텔레메트리 | 릴리스 빌드 기본 활성 | 기본 비활성, opt-in 필수 | `.rules/logging-privacy.md` |
| 환경 변수 | `CMUX_SOCKET_PATH`, `CMUX_WORKSPACE_ID` | `CMUX_PIPE_NAME`, `CMUX_PANE_ID` | 전송 방식 일치 |
| 북마크 | 있음 (source 기준) | v1 없음 | 범위 축소 |
| 숏컷 기본값 | macOS modifier (⌘) | Windows modifier (Ctrl/Win) | OS 규약 |
