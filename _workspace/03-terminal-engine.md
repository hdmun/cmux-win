# 03. Terminal Engine

> [!IMPORTANT]
> 이 문서는 terminal runtime, parser, renderer, passthrough detection, IME, UIA의 구현 계약을 정의한다.

## 1. v1 terminal stack

| 계층 | 선택 |
|------|------|
| PTY | ConPTY |
| parser | libvterm |
| renderer | Direct2D + DirectWrite |
| host surface | WinUI 3 `SwapChainPanel` |

v1에서는 custom VT parser를 만들지 않는다. libvterm가 기본 경로다.

## 2. 의존성 위치

`libvterm`의 authoritative source는 아래 하나로 고정한다.

- `ports\libvterm\`

별도 `vendor\libvterm` 복사는 허용하지 않는다. patch가 필요하면 overlay port에 포함한다.

## 3. ConPTY mode detection

지원 모드는 두 가지다.

- `standard`
- `passthrough`

### detection 규칙

1. session start 시 1회만 판정한다.
2. OS build gate를 확인한다.
3. `CreatePseudoConsole` passthrough 초기화가 실패하면 즉시 `standard`로 고정한다.
4. 실행 중 재상향(upgrade)은 하지 않는다.

### fallback 규칙

- passthrough 미지원은 에러가 아니라 **정상 fallback** 이다.
- fallback 사실은 로그에 남기되, 사용자에게 과장된 오류 UI를 띄우지 않는다.

## 4. 스레딩 계약

| 작업 | 스레드 |
|------|--------|
| ConPTY read loop | background |
| VT parse | background |
| dirty region 계산 | background |
| frame publish | background -> atomic handoff |
| swapchain invalidate enqueue | background |
| Direct2D draw | UI thread |
| IME rect update | UI thread |
| UIA event raise | UI thread |

### handoff 규칙

1. parser는 `TerminalBuffer`만 갱신한다.
2. renderer는 published frame만 읽는다.
3. invalidate는 coalescing 한다.
4. UI는 parser internals를 직접 읽지 않는다.

## 5. terminal panel lifecycle

공통 panel lifecycle은 아래 상태를 따른다.

- `created`
- `attached`
- `focused`
- `blurred`
- `hidden`
- `detached`
- `disposed`

### terminal-specific 규칙

1. `created`: panel object 생성, runtime 아직 idle 가능
2. `attached`: XAML host와 swapchain 연결
3. `focused`: input routing 활성화
4. `hidden`: session 유지, ConPTY 종료 금지
5. `detached`: reparent 직전 상태, session 유지
6. `disposed`: ConPTY / parser / renderer 순서로 해제

split 이동이나 workspace 전환은 `hidden` 또는 `detached`만 사용한다. `disposed`로 가면 안 된다.

## 6. shell environment injection

terminal host가 새 shell process를 생성할 때 아래 환경 변수를 **process start 시점에 주입**한다.

| 변수 | 값 |
|------|----|
| `CMUX_PIPE_NAME` | 현재 app instance의 Named Pipe 경로 |
| `CMUX_PANE_ID` | 현재 pane의 `pane:<uuid>` |
| `CMUX_SURFACE_ID` | 현재 surface의 `surface:<uuid>` |

### 주입 규칙

1. 변수 주입 책임은 ConPTY child process를 시작하는 terminal spawning path가 가진다.
2. 값은 shell 프로세스의 초기 environment block에 포함된다.
3. pane/surface identity는 새 shell spawn 시점에 고정되며, 같은 shell 세션 도중 다른 pane으로 재배치되어도 값을 다시 주입하지 않는다.
4. cmux 밖에서 실행된 shell은 이 변수를 갖지 않을 수 있으며, shell integration은 그 경우 no-op 이어야 한다.

## 7. IME 기준

v1은 TSF 우선 경로를 사용한다.

- composition rect는 terminal cursor의 pixel rect 기준
- DPI 변경 시 rect를 즉시 다시 계산
- split resize / monitor move 후에도 rect가 갱신되어야 함

IME 실패 시 조용히 삼키지 않고, fallback 경로로 전환 사실을 로그에 남긴다.

## 8. UIA 기준

v1 terminal은 최소 아래를 만족한다.

- visible text를 TextPattern으로 노출
- caret 이동 event 발행
- viewport 변경 event 발행
- screen reader가 현재 line과 selection을 읽을 수 있음

## 9. M2 검증 기준

- Win10: standard ConPTY 동작
- Win11 22H2+: passthrough gate 판정
- dirty region 기반 redraw
- IME candidate window 위치 정상
- Narrator/NVDA로 텍스트 이동 확인
- 새 shell spawn 시 `CMUX_PIPE_NAME`, `CMUX_PANE_ID`, `CMUX_SURFACE_ID`가 예상 값으로 주입됨

---

## 10. ConPTY Spawn Contract

> M2 구현 계약. `_workspace/adr/adr-0002-conpty-passthrough-fallback.md` 결정에 따름.

### 10.1 API 호출 순서

```cpp
// (1) pipe 쌍 생성
HANDLE h_pipe_in_read,  h_pipe_in_write;
HANDLE h_pipe_out_read, h_pipe_out_write;
CreatePipe(&h_pipe_in_read,  &h_pipe_in_write,  nullptr, 0);
CreatePipe(&h_pipe_out_read, &h_pipe_out_write, nullptr, 0);

// (2) ConPTY 생성
HPCON hpc{};
HRESULT hr = CreatePseudoConsole(size, h_pipe_in_read, h_pipe_out_write, flags, &hpc);
// flags: 0 (standard) 또는 PSEUDOCONSOLE_PASSTHROUGH_MODE (passthrough, adr-0002 탐지 결과 사용)

// (3) STARTUPINFOEX 조립
SIZE_T attr_list_size{};
InitializeProcThreadAttributeList(nullptr, 2, 0, &attr_list_size);
LPPROC_THREAD_ATTRIBUTE_LIST attr_list = /* heap alloc attr_list_size */;
InitializeProcThreadAttributeList(attr_list, 2, 0, &attr_list_size);
UpdateProcThreadAttribute(attr_list, 0, PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE, hpc, sizeof(HPCON), nullptr, nullptr);
// 환경 변수 주입은 §6 참조

// (4) CreateProcess
STARTUPINFOEXW si{};
si.StartupInfo.cb = sizeof(STARTUPINFOEXW);
si.lpAttributeList = attr_list;
CreateProcessW(shell_exe, nullptr, nullptr, nullptr, FALSE,
               EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT,
               env_block, nullptr, &si.StartupInfo, &pi);

// (5) 사용한 read/write 핸들 닫기
CloseHandle(h_pipe_in_read);
CloseHandle(h_pipe_out_write);
// h_pipe_in_write (stdin feed), h_pipe_out_read (stdout drain) 은 I/O loop에서 사용
```

### 10.2 핸들 수명

| 핸들 | 소유자 | 해제 시점 |
|------|--------|-----------|
| `hpc` | `ConPtySession` | `disposed` 전이 시 `ClosePseudoConsole(hpc)` |
| `h_pipe_in_write` | `ConPtySession` | `disposed` 전이 시 `CloseHandle` |
| `h_pipe_out_read` | `ConPtySession` | `disposed` 전이 시 `CloseHandle` |
| Process/Thread handles | `ConPtySession` | process exit 감지 후 `CloseHandle` |

### 10.3 리사이즈 프로토콜

- 리사이즈는 UI 스레드에서 감지하되, `ResizePseudoConsole` 호출은 background 스레드에 enqueue한다.
- `ResizePseudoConsole` 호출 빈도를 throttle한다: 50ms 이내 연속 호출은 마지막 값 하나만 전달.

---

## 11. libvterm Wrapper API

> M2 구현 계약. `_workspace/adr/adr-0003-parser-selection.md` 결정에 따름.

### 11.1 `VtermWrapper` 최소 인터페이스

```cpp
// src/terminal/engine/vterm_wrapper.h
class VtermWrapper {
public:
    explicit VtermWrapper(int rows, int cols);
    ~VtermWrapper();  // vterm_free()

    // I/O
    void PushBytes(const char* data, size_t len);  // vterm_input_write()

    // 리사이즈 (ConPTY resize와 쌍으로 호출)
    void Resize(int rows, int cols);               // vterm_set_size()

    // 버퍼 접근 (background thread에서 호출)
    const TerminalBuffer& Buffer() const;

    // 스크린 콜백 (내부 등록, 외부 노출 금지)
private:
    VTerm*         vterm_{nullptr};
    VTermScreen*   screen_{nullptr};
    TerminalBuffer buffer_;
    // callbacks_ registered via vterm_screen_set_callbacks
};
```

### 11.2 스레드 소유권

- `VtermWrapper`의 모든 메서드는 **background worker 스레드**에서만 호출한다.
- `Buffer()` const 접근도 background에서만 한다. UI는 published frame snapshot을 읽는다.

### 11.3 `TerminalBuffer` 최소 구조

```cpp
// src/terminal/engine/terminal_buffer.h
struct TermCell {
    char32_t codepoint;
    VTermColor fg, bg;
    uint8_t    attrs;  // bold/italic/underline/blink/reverse
};

struct CursorState {
    int row, col;
    bool visible;
};

class TerminalBuffer {
public:
    int Rows() const;
    int Cols() const;
    const TermCell& CellAt(int row, int col) const;
    CursorState     Cursor() const;
    // dirty region tracking
    std::vector<TerminalRect> TakeDirtyRegions();
};
```

---

## 12. Direct2D SwapChainPanel Renderer

> M2 구현 계약. D2D/DWrite 렌더링 계층.

### 12.1 렌더 루프

```
[background]                         [UI thread]
PushBytes() → VtermWrapper           DispatcherQueue.TryEnqueue()
           → TerminalBuffer dirty    → SwapChainPanel.Invalidate()
           → atomic publish frame    → D2DRenderer.DrawFrame()
```

1. `PushBytes()` 후 dirty region이 있으면 immutable `TerminalFrame` snapshot을 atomic publish한다.
2. background가 `DispatcherQueue.TryEnqueue`로 swapchain invalidate를 enqueue한다.
3. UI 스레드에서 `D2DRenderer::DrawFrame()`이 최신 published frame snapshot을 읽어 D2D draw를 실행한다.
4. 한 프레임 내에 여러 dirty region은 coalescing한다.

### 12.2 글자 타일 캐시

- `IDWriteTextLayout` 재생성은 비싸므로 `(codepoint, font_size, attrs)` 키로 `IDWriteGlyphRun` 결과를 캐시한다.
- 캐시 크기 상한: **4096 슬롯**. LRU 교체.
- DPI 변경 시 캐시를 전체 무효화한다.

### 12.3 DPI 변경 처리

1. `SwapChainPanel.DpiChanged` 이벤트를 UI 스레드에서 수신한다.
2. `IDXGISwapChain::ResizeBuffers()`를 호출한다.
3. 글자 타일 캐시를 무효화한다.
4. IME rect를 즉시 재계산한다.

---

## 13. reattach_token Binding

> M2/M3 구현 계약. `_workspace/adr/adr-0004-panel-lifecycle.md` §SwapChainPanel reattach_token 참조.

### 13.1 token 흐름

```
BonsplitController.MovePane()
    └→ TerminalPanel.Detach()           // ++reattach_token_
        └→ RaisePropertyChanged("ReattachToken")
            └→ XAML Binding 감지
                └→ OnReattachTokenChanged()
                    └→ SetSwapChain(swapchain_)  // D2D swapchain 재연결
```

### 13.2 구현 스케치

```cpp
// TerminalPanel (XAML codebehind / WinRT component)
// XAML: <SwapChainPanel x:Name="swapPanel" />
// Binding: {x:Bind ViewModel.ReattachToken, Mode=OneWay}

void TerminalPanel::OnReattachTokenChanged(uint64_t /*token*/) {
    // UI thread에서 호출됨
    if (swapchain_) {
        // ISwapChainPanelNative 경유
        winrt::com_ptr<ISwapChainPanelNative> native;
        swapPanel().as(native);
        native->SetSwapChain(swapchain_.get());
    }
}
```

### 13.3 규칙

1. `reattach_token`은 **UI thread**에서만 읽는다. XAML binding이 UI thread에서 실행되므로 자연스럽게 보장된다.
2. `++reattach_token_`은 `Detach()` 메서드 내에서만 호출한다.
3. `Detach()` 후 XAML tree 재연결(reparent) 전에 token이 증가해야 한다. 순서를 바꾸면 재연결이 누락될 수 있다.
4. browser 패널(`WebView2`)은 이 패턴을 사용하지 않는다.
