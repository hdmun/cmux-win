# 터미널 / 브라우저 / 패널 라이프사이클

## 터미널 스택

| 계층 | 선택 |
|------|------|
| PTY | ConPTY |
| VT 파서 | libvterm (custom 파서 사용 안 함) |
| 렌더러 | Direct2D + DirectWrite |
| host surface | WinUI 3 `SwapChainPanel` |

### ConPTY passthrough fallback

- session start 시 1회만 판정한다.
- OS build gate를 확인하고, 실패하면 즉시 standard 모드로 고정한다.
- passthrough 미지원은 에러가 아니라 **정상 fallback**이다.
- fallback 사실은 로그에 남기되, 과장된 오류 UI를 표시하지 않는다.
- 실행 중 재상향(upgrade)은 하지 않는다.

### SwapChainPanel reattach token

terminal panel을 다른 XAML container로 이동할 때, `SwapChainPanel`은 새 XAML parent에 연결되었음에도 Direct2D swapchain 연결이 끊겨 보일 수 있다. 이를 방지하기 위해 **reattach token** 패턴을 사용한다.

- `TerminalPanel`은 내부적으로 `reattach_token` (uint64) 카운터를 보유한다.
- split/reparent 직후 `reattach_token`을 증가시킨다.
- `SwapChainPanel`의 XAML binding이 token 변화를 감지하면 `SetSwapChain()`을 재호출하여 D2D swapchain을 다시 연결한다.
- 이 패턴은 macOS의 `viewReattachToken`에 대응하는 Windows 구현이다.

---

## 브라우저 패널

| 요소 | 선택 |
|------|------|
| host | WinUI 3 XAML |
| browser control | WebView2 XAML control |
| automation channel | CDP 우선 |

- child HWND embedding을 기본 경로로 사용하지 않는다.
- snapshot, click, fill, network 계열은 CDP 사용.
- CDP 실패 시 조용한 JS fallback을 두지 않는다.
- split 이동/workspace 전환만으로 environment를 재생성하지 않는다.

---

## Panel lifecycle 계약

모든 panel(terminal, browser)은 아래 상태 순서를 따른다.

```text
created -> attached -> focused <-> blurred -> hidden <-> detached -> disposed
```

- split 이동/workspace 전환은 hidden 또는 detached만 사용한다.
- disposed로 전환하면 terminal/browser runtime이 해제된다. **move 중 dispose 금지.**
- layout 코드는 terminal/browser-specific cleanup을 직접 실행하지 않는다.

---

## IME / UIA 기준

### IME (TSF)

- v1은 TSF 우선 경로를 사용한다.
- composition rect는 terminal cursor의 pixel rect 기준으로 계산한다.
- DPI 변경 시 rect를 즉시 다시 계산한다.
- split resize / monitor move 후에도 rect가 갱신되어야 한다.
- IME fallback 전환 시 조용히 삼키지 않고 로그에 fallback 사실을 남긴다.

### UIA (UI Automation)

v1 terminal은 최소 아래를 만족한다.

- visible text를 `TextPattern`으로 노출
- caret 이동 이벤트 발행
- viewport 변경 이벤트 발행
- screen reader가 현재 line과 selection을 읽을 수 있음

---

## Split / Focus 규칙

### focus 복원 순서

1. split 직후 새 pane이 focus를 가짐
2. pane close 시 가장 가까운 sibling 우선
3. sibling이 없으면 parent tree의 인접 pane
4. workspace 전환 시 마지막 active pane 복원

### 비포커스 패널 UX

- dim overlay opacity: `unfocused-split-opacity` 값 사용 (기본 0.15)
- overlay fill color: `unfocused-split-fill` 값 사용 (기본 검정)
- 포커스 이동 시 즉시 제거
- unread 알림이 있는 패널: 파란색 테두리 링 표시

### isDirty 억제 정책

- `TerminalPanel.isDirty`는 항상 `false` 반환 (VT/process-exit 기반 오탐 억제)
- close 확인은 `needsConfirmClose()`로만 처리
- `needsConfirmClose()`는 child process가 실행 중이고 사용자 프로세스가 foreground에 있을 때만 `true` 반환
- 주기적 polling이나 idle 상태에서 호출하지 않음

---

## 브라우저 WebViewEnvironmentPool

- panel close 시 WebView2 environment를 풀에 반환한다.
- profile / privacy mode 단위로 environment를 재사용한다.
- split 이동/workspace 전환으로 `EnsureCoreWebView2Async()`를 재실행하지 않는다.
