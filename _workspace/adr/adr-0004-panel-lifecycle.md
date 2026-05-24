# ADR-0004: Common Panel Lifecycle Contract

- Status: accepted
- Related docs: `_workspace/04-split-pane.md`, `_workspace/06-browser-panel.md`, `_workspace/03-terminal-engine.md`
- Related tasks: m0-4, m2-5, m3-2, m4-1

## Context

terminal 패널(ConPTY + D2D)과 browser 패널(WebView2)은 split 이동, workspace 전환, 닫기 등의 동일한 레이아웃 이벤트를 받는다. 공통 lifecycle을 정의하지 않으면 다음 문제가 발생한다.

- split 이동 중 ConPTY가 종료되어 세션 끊김
- WebView2 reparent 시 `EnsureCoreWebView2Async()` 재실행 → 페이지 재로드
- layout 코드가 terminal/browser cleanup 로직을 직접 알아야 하는 결합

## Decision

terminal과 browser 패널이 공통으로 구현해야 하는 lifecycle 상태를 7단계로 고정한다.

```
created → attached → focused
                  ↘ blurred → hidden → detached → disposed
```

### 상태 정의

| 상태 | 의미 | ConPTY/D2D | WebView2 |
|------|------|------------|----------|
| `created` | 객체 생성, runtime idle 가능 | ConPTY 미시작 | CoreWebView2 미초기화 |
| `attached` | XAML host 연결 완료 | swapchain 연결 | WebView2 초기화 완료 |
| `focused` | 입력 라우팅 활성 | input 수신 | focus 이벤트 전달 |
| `blurred` | 입력 라우팅 비활성 | input 수신 중단 | focus 이벤트 중단 |
| `hidden` | 세션 유지, 화면 미표시 | ConPTY **종료 금지** | WebView2 session 유지 |
| `detached` | reparent 직전 상태 | 세션 유지 | session 유지 |
| `disposed` | 완전 해제 | ConPTY → libvterm → D2D 순서 해제 | event token, CDP session, control 정리 |

### 전이 규칙

1. split 이동과 workspace 전환은 `hidden` 또는 `detached`만 사용한다. `disposed`로 전이하지 않는다.
2. `disposed` 상태에서는 어떤 전이도 없다. 객체를 삭제한다.
3. 다음 전이만 허용한다.

```
created    → attached
attached   → focused | disposed
focused    → blurred
blurred    → focused | hidden | disposed
hidden     → attached | detached | disposed
detached   → attached | disposed
```

4. layout code는 `attach()`, `focus()`, `blur()`, `hide()`, `detach()`, `dispose()` 메서드만 호출한다. terminal/browser-specific cleanup을 직접 실행하지 않는다.

### SwapChainPanel reattach_token 규칙

terminal 패널을 다른 XAML container로 이동할 때, Direct2D swapchain 연결이 끊겨 보일 수 있다.

- `TerminalPanel`은 `reattach_token` (uint64) 카운터를 보유한다.
- `detach()` 직후 reparent 전에 `reattach_token`을 증가시킨다.
- `SwapChainPanel`의 XAML binding이 token 변화를 감지하면 `SetSwapChain()`을 재호출하여 D2D swapchain을 다시 연결한다.

```cpp
// TerminalPanel.h (sketch)
class TerminalPanel {
    uint64_t reattach_token_{0};  // XAML binding source
public:
    uint64_t ReattachToken() const { return reattach_token_; }
    void Detach() {
        // ...
        ++reattach_token_;  // triggers XAML notify
        RaisePropertyChanged(L"ReattachToken");
    }
};
```

## Consequences

- 두 패널 타입은 공통 `IPanel` 인터페이스 또는 `PanelBase` CRTP를 구현한다 (구체 구조는 M2/M4에서 결정).
- browser 패널은 `hidden` / `detached` 상태에서 `EnsureCoreWebView2Async()`를 재실행하지 않는다.
- ConPTY 해제는 반드시 `disposed` 전이에서만 발생한다. 다른 상태에서 ConPTY를 종료하는 코드는 버그다.
- `reattach_token`은 terminal 패널 전용이다. browser 패널은 이 패턴을 사용하지 않는다 (WebView2 reparent는 XAML 레이어가 자동 처리).

## Verification impact

- M2 수락 기준: split 이동 후 terminal session이 유지됨 (ConPTY 재시작 없음)
- M3 수락 기준: reparent 후 SwapChainPanel swapchain 정상 재연결 (`reattach_token` 증가 확인)
- M4 수락 기준: workspace/split 전환 후 WebView2 browsing session 유지
- M4 수락 기준: `EnsureCoreWebView2Async()` 재실행 없이 reparent 완료
