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

## 10. 검색 오버레이

terminal 패널에는 찾기 오버레이를 제공한다.

- 오버레이는 패널 위에 float으로 표시 (XAML `Popup` 또는 `Canvas` 오버레이)
- 드래그로 패널 내 위치 변경 가능
- 4개 코너(좌상/우상/좌하/우하)에 snap 지원
- 현재 N번째 / 전체 M개 매치 카운터 표시

## 11. M3 검증 기준

- split/close/move 후 `layout_version` 일관성 유지
- pane focus 복원 규칙 준수
- panel reparent 시 runtime 유지
- overlay UI가 terminal/browser panel 위에 정상 표시
- reparent 후 SwapChainPanel swapchain 정상 재연결 확인
- 비포커스 패널 dim overlay 표시/제거 확인
