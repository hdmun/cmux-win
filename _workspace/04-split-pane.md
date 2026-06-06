# 04. Split Pane

> [!IMPORTANT]
> split layout은 XAML tree 안에서만 구성한다. child HWND 기반 pane tree는 v1에서 사용하지 않는다.

## 1. layout model

`BonsplitController`는 아래를 source of truth로 가진다.

- split tree
- pane order
- pane focus
- layout version

UI는 controller가 내보낸 snapshot만 반영한다.

### `BonsplitController` 최소 public interface

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

이 인터페이스는 구현 클래스 이름이나 내부 자료구조를 고정하려는 목적이 아니라, M1/M3에서 필요한 최소 public contract를 잠그기 위한 스케치다.

## 2. snapshot 계약

모든 구조 변경은 `LayoutSnapshot`으로 publish 한다.

- split / close / move / merge
- active pane 변경
- workspace 전환에 따른 root pane 교체

UI는 최신 `layout_version`만 적용한다.

### `LayoutSnapshot` 최소 필드

```cpp
struct LayoutSnapshot {
    uint64_t layout_version;
    PaneId active_pane_id;
    PaneNode root;
    std::vector<PanePresentation> panes;
};

enum class PaneNodeKind {
    Leaf,
    Split
};

struct PaneNode {
    PaneNodeKind kind;
    std::optional<PaneId> pane_id;
    std::optional<SplitOrientation> orientation;
    double primary_ratio;
    std::vector<PaneNode> children;
};

struct PanePresentation {
    PaneId pane_id;
    std::optional<SurfaceId> surface_id;
    double width_ratio;
    double height_ratio;
    bool is_active;
    bool is_leaf;
};
```

`PaneNode`는 publish되는 snapshot의 일부이므로 형태를 고정한다. v1에서 `Leaf` 노드는 `pane_id`를 가져야 하고 child가 없어야 하며, `Split` 노드는 `orientation`, `primary_ratio`, child 2개를 가져야 한다. `primary_ratio`는 **첫 번째 child의 비율** 을 의미한다. `panes` 컬렉션은 XAML projection 계층이 pane/surface binding과 active state를 빠르게 읽을 수 있도록 제공한다.

## 3. pane / surface ID 규칙

| 대상 | 의미 |
|------|------|
| `pane_id` | layout node identity |
| `surface_id` | panel instance identity |

pane는 layout의 좌표이고, surface는 실제 표시되는 panel instance다.

## 4. reparenting 규칙

split 조작이나 workspace 전환 시 panel instance를 재생성하지 않는다.

허용:

- container 교체
- visibility 변경
- logical parent 변경

금지:

- move만으로 terminal/browser runtime dispose
- focus 이동 중 panel recreate

### SwapChainPanel reparent 시 reattach token

terminal panel을 다른 XAML container로 이동할 때, `SwapChainPanel`은 새 XAML parent에 연결되었음에도 Direct2D swapchain 연결이 끊겨 보일 수 있다. 이를 방지하기 위해 **reattach token** 패턴을 사용한다.

- `TerminalPanel`은 내부적으로 `reattach_token` (uint64) 카운터를 보유한다.
- split/reparent 직후 `reattach_token`을 증가시킨다.
- `SwapChainPanel`의 XAML binding이 token 변화를 감지하면 `SetSwapChain()`을 재호출하여 D2D swapchain을 다시 연결한다.
- 이 패턴은 macOS의 `viewReattachToken`에 대응하는 Windows 구현이다.

## 5. 비포커스 패널 UX 규칙

비포커스 terminal/browser 패널에는 dim overlay를 적용한다.

- overlay opacity: Ghostty config의 `unfocused-split-opacity` 값 사용 (기본 0.15)
- overlay fill color: `unfocused-split-fill` 값 사용 (기본 검정)
- 포커스 이동 시 즉시 제거

unread 알림이 있는 패널에는 **파란색 테두리 링**을 표시한다.

## 6. isDirty 억제 정책

`TerminalPanel.isDirty`는 **close 직전 확인 창이 필요한지**를 나타낸다.

- `isDirty`는 항상 `false`를 반환하도록 고정한다.
- VT 시퀀스 파싱이나 process exit 감지 기반의 dirty 오탐을 억제하기 위함이다.
- close 확인은 `needsConfirmClose()` 메서드로 별도 처리한다.

### needsConfirmClose 규칙

`needsConfirmClose()`는 실제로 close 직전에만 호출한다.

- child process가 실행 중이고, 쉘이 아닌 사용자 프로세스가 foreground에 있을 때만 `true` 반환
- 주기적 polling이나 idle 상태에서 호출하지 않음

## 7. focus 복원 규칙

1. split 직후 새 pane가 focus를 가짐
2. pane close 시 가장 가까운 sibling 우선
3. sibling이 없으면 parent tree의 인접 pane
4. workspace 전환 시 마지막 active pane 복원

## 8. Grid / GridSplitter 규칙

- 화면 구성은 XAML `Grid`
- resize handle은 toolkit `GridSplitter`
- splitter drag는 UI에서 처리하되 최종 ratio source of truth는 controller

## 9. 공통 panel lifecycle 연결

layout 계층은 panel lifecycle을 아래처럼만 호출한다.

- attach
- focus
- blur
- hide
- detach
- dispose

layout code는 terminal/browser-specific cleanup을 직접 실행하지 않는다.

## 10. 터미널 찾기 오버레이 (in-terminal find overlay)

> macOS `SurfaceSearchOverlay` / `TerminalPanel.searchState` 대응. terminal panel 한정 기능이다. browser panel은 WebView2 내장 검색을 사용하므로 이 오버레이를 띄우지 않는다.

### 10.1 오버레이 UI

- 오버레이는 활성 terminal panel 위에 float으로 표시한다 (XAML `Popup` 또는 패널 위 `Canvas` 오버레이).
- 드래그로 패널 내 위치 변경이 가능하다.
- 4개 코너(좌상/우상/좌하/우하)에 snap을 지원한다.
- 구성 요소: 검색 입력 박스, `현재 N번째 / 전체 M개` 매치 카운터, prev/next 버튼, case-sensitivity 토글, regex 토글, 닫기 버튼.

### 10.2 per-panel 검색 상태

검색 상태는 **terminal panel 인스턴스마다** 보유한다. 오버레이 UI가 아니라 panel이 source of truth다.

```cpp
struct TerminalSearchState {
    std::wstring query;
    int          match_index;   // 현재 강조 매치 (0-based, 매치 없으면 -1)
    int          match_count;   // 전체 매치 수
    bool         case_sensitive;
    bool         use_regex;
    bool         overlay_visible;
};
```

- 상태는 `TerminalPanel`이 보유하며, 오버레이가 숨겨져도(`overlay_visible = false`) `query`/`match_index`/플래그가 유지된다.
- panel이 `hidden`/`detached` 상태로 가도 검색 상태는 보존된다 (panel lifecycle은 §9, ADR-0004 참조). `disposed`에서만 해제된다.

### 10.3 동작 (open / close / next / prev)

| 동작 | 효과 |
|------|------|
| open | `overlay_visible = true`, 입력 박스에 포커스, 이전 `query`가 있으면 복원하고 즉시 재검색 |
| close | `overlay_visible = false`, panel에 포커스 복귀, 검색 상태는 유지 |
| next | `match_index = (match_index + 1) % match_count`, 강조 매치를 viewport로 스크롤 |
| prev | `match_index = (match_index - 1 + match_count) % match_count`, 강조 매치를 viewport로 스크롤 |
| query 변경 | 매치 재계산 후 `match_count` 갱신, `match_index`는 0으로(매치 없으면 -1) 리셋 |

- 매치 계산은 terminal scrollback buffer 텍스트를 대상으로 한다. case/regex 플래그가 계산 방식을 결정한다.
- 매치 강조는 §5의 dim overlay/unread ring과 독립적인 별도 highlight 레이어로 그린다.

### 10.4 shortcut 연결 hook

- 오버레이 open은 `find` action에 바인딩한다. action은 surface scope다.
- 실제 키 매핑은 `_workspace/09-config-settings.md`의 `shortcuts` 스키마가 소유한다. 이 문서는 `find` action 이름만 정의하며 키 자체는 09에서 추가한다.
- close는 `Escape` 키로도 가능하다 (오버레이 포커스 상태에서).

### 10.5 수락 hook (acceptance hooks)

- `find` action 트리거 시 활성 terminal panel 위에 오버레이가 표시되고 입력 박스가 포커스된다.
- query 입력 시 `match_count`가 갱신되고 카운터 표시가 `N / M` 형식으로 동기화된다.
- next/prev 시 `match_index`가 wrap-around로 갱신되고 강조 매치가 viewport에 보인다.
- 오버레이를 닫았다 다시 열면 직전 `query`와 플래그가 복원된다 (상태 보존).
- panel을 split 이동(`hidden`→`attached`)한 뒤 오버레이를 열면 검색 상태가 유지된다.

## 11. 공유 패널 추상화 (`IPanel`)

> ADR-0004 §공통 추상화 결정 (D5)의 구현 계약. terminal panel과 browser panel의 공통 추상 인터페이스를 고정한다.

### 11.1 인터페이스 정의

layout 계층은 panel을 항상 `IPanel`을 통해서만 다룬다. 구체 타입(`TerminalPanel`, `BrowserPanel`)을 직접 알지 않는다.

```cpp
// src/app/panel/i_panel.h
class IPanel {
public:
    virtual ~IPanel() = default;
    virtual void Attach() = 0;    // XAML host 연결, runtime 활성
    virtual void Focus() = 0;     // 입력 라우팅 활성
    virtual void Blur() = 0;      // 입력 라우팅 비활성
    virtual void Hide() = 0;      // 세션 유지, 화면 미표시
    virtual void Detach() = 0;    // reparent 직전, 세션 유지
    virtual void Dispose() = 0;   // 완전 해제

    // content router가 host 선택에 사용하는 식별자
    virtual SurfaceKind Kind() const = 0;   // Terminal | Browser
    virtual SurfaceId   Id() const = 0;
};

enum class SurfaceKind { Terminal, Browser };
```

### 11.2 구현 책임

| 구현체 | 6개 lifecycle 메서드 매핑 |
|--------|---------------------------|
| `TerminalPanel` | `Attach`=swapchain 연결, `Detach`=`++reattach_token_`(§4), `Dispose`=ConPTY→libvterm→D2D 순서 해제 |
| `BrowserPanel` | `Attach`=WebView2 초기화(이미 됐으면 재실행 금지), `Hide`/`Detach`=session 유지, `Dispose`=event token/CDP session 정리 |

- 상태 전이 규칙(created→attached→… )과 허용 전이는 ADR-0004가 단일 source of truth다. 이 문서는 중복 정의하지 않는다.
- layout code(`BonsplitController` 호출 측)는 §9 목록의 6개 동사만 호출하고 terminal/browser-specific cleanup을 직접 실행하지 않는다.

### 11.3 수락 hook

- `TerminalPanel`과 `BrowserPanel`이 동일한 `IPanel` 포인터 타입으로 단일 컬렉션에 저장 가능하다.
- layout 코드 어디에도 `dynamic_cast<TerminalPanel>` 류의 구체 타입 분기가 없다 (content router 제외, §12).

## 12. Panel content router

> macOS `PanelContentView` 대응. surface 타입에 따라 올바른 host XAML element를 선택하고 content를 라우팅하는 presenter 계층이다.

### 12.1 역할

- pane가 보유한 `SurfaceId` → `IPanel` 인스턴스를 조회한다.
- `IPanel::Kind()`에 따라 host element를 선택한다.
  - `SurfaceKind::Terminal` → `SwapChainPanel` 기반 terminal host
  - `SurfaceKind::Browser` → `WebView2` 기반 browser host
- 선택한 host element를 pane container에 attach한다.

### 12.2 라우팅 규칙

1. content router는 `std::shared_ptr<IPanel>`의 이질적 컬렉션(`surface_id → IPanel`)을 보유한다. 이 컬렉션이 panel instance ownership을 가진다.
2. host 선택은 `Kind()` 한 번으로 결정하며, 같은 surface_id는 항상 같은 host element로 라우팅된다 (host element 재사용, §4 reparent 규칙 준수).
3. router는 panel을 생성/파괴하지 않는다. lifecycle 전이(`Attach`/`Detach`/`Dispose`)는 §9 경로(layout → `IPanel`)가 담당하고, router는 어떤 host에 표시할지만 결정한다.
4. unknown `SurfaceKind`는 라우팅하지 않고 로그를 남긴다 (빈 placeholder 표시).

### 12.3 XAML 구성

- pane content 영역은 단일 content presenter다. presenter가 `Kind()`에 맞는 `DataTemplate`(terminal host / browser host)을 선택한다 (`DataTemplateSelector` 또는 명시적 분기).
- terminal host와 browser host는 동시에 같은 pane에 존재하지 않는다 (한 pane은 한 surface, CONTEXT.md).

### 12.4 수락 hook

- terminal surface가 attach된 pane는 `SwapChainPanel` host를, browser surface가 attach된 pane는 `WebView2` host를 표시한다.
- 같은 surface를 split 이동해도 동일 host element가 재사용되고 runtime이 유지된다 (§4, ADR-0004).
- 한 `BonsplitController` 트리 안에 terminal/browser panel이 섞여 있어도 각 pane가 올바른 host로 라우팅된다.

## 13. M3 검증 기준

- split/close/move 후 `layout_version` 일관성 유지
- pane focus 복원 규칙 준수
- panel reparent 시 runtime 유지
- overlay UI가 terminal/browser panel 위에 정상 표시
- reparent 후 SwapChainPanel swapchain 정상 재연결 확인
- 비포커스 패널 dim overlay 표시/제거 확인
- terminal find overlay open/next/prev/close 및 상태 보존 동작 (§10.5)
- terminal/browser panel이 `IPanel` 단일 컬렉션으로 저장되고 content router가 올바른 host로 라우팅 (§11.3, §12.4)
