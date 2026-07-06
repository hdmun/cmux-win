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

**인라인 조합 필수 (플로팅 창 강등 불허, 2026-07-05 grill-me 확정)**: 한글 등 조합형 IME의 composition string은 candidate window와 별개로 terminal 커서 셀 위치에 인라인으로 표시되어야 한다. TSF composition 실패 시에도 별도 플로팅 조합 창으로 강등(degrade)하지 않고, §9 fallback 경로(standard 모드 등)와 무관하게 인라인 표시 계약을 유지한다.

## 8. UIA 기준

v1 terminal은 최소 아래를 만족한다.

- visible text를 TextPattern으로 노출
- caret 이동 event 발행
- viewport 변경 event 발행
- screen reader가 현재 line과 selection을 읽을 수 있음

## 9. M2 검증 기준

- 기본 경로: passthrough 초기화 성공 + gate 판정 로그 존재 (지원 floor Win11 22H2+)
- 폴백 경로: passthrough 초기화 실패 또는 `CMUX_CONPTY_MODE=standard` 강제 시 standard ConPTY 동작
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

---

## 14. Clipboard 통합 (terminal 측)

> M6 구현 계약. macOS Ghostty의 clipboard mode mapping 대응. terminal panel의 copy/paste를 Windows Clipboard로 매핑한다. 파일 경로/URL의 shell escaping 규칙은 `_workspace/10-shell-integration.md` §9가 소유하며, 이 섹션은 clipboard ↔ terminal 경로만 다룬다.

### 14.1 clipboard target 매핑

Ghostty/libvterm은 OSC 52 등에서 system clipboard와 primary selection을 구분하나, Windows에는 X11 스타일 primary selection이 없다. 따라서 다음으로 고정한다.

| 논리 target | Windows 매핑 |
|-------------|--------------|
| system clipboard (`c`) | Windows Clipboard (`CF_UNICODETEXT`) |
| primary selection (`p`) | Windows Clipboard로 동일 매핑 (별도 primary 미구현) |

- copy/paste는 항상 UI thread에서 Windows Clipboard API를 호출한다 (clipboard는 STA 의존).

### 14.2 copy 경로

1. 사용자 selection 또는 OSC 52 copy 요청 시 선택 텍스트를 `CF_UNICODETEXT`로 Windows Clipboard에 쓴다.
2. 줄바꿈은 `\r\n`으로 정규화한다.
3. trailing whitespace 처리는 terminal selection 규칙을 따른다 (rectangular selection 시 라인별 trim).

### 14.3 paste 경로와 bracketed paste

1. paste는 Windows Clipboard `CF_UNICODETEXT`를 읽어 ConPTY stdin feed(`h_pipe_in_write`, §10)로 보낸다.
2. terminal이 **bracketed paste mode**(`ESC[?2004h`)를 활성화한 경우, paste 데이터를 `ESC[200~` … `ESC[201~`로 감싸 전송한다. 비활성 시 raw 전송한다.
3. paste 데이터 내에 bracketed paste 종료 시퀀스(`ESC[201~`)가 포함되면 제거하여 escape injection을 방지한다.

### 14.4 paste 확인 (paste confirmation)

macOS Ghostty의 paste 경고에 대응한다.

- paste 데이터에 개행(`\n`/`\r`)이 포함되고 bracketed paste mode가 **비활성** 인 경우, paste 전에 확인 dialog를 표시한다 (의도치 않은 다중 명령 실행 방지).
- bracketed paste mode가 활성이면 셸이 paste를 단일 입력으로 처리하므로 확인을 생략한다.
- 확인 동작은 `terminal.paste_confirm` 설정으로 끌 수 있다 (기본 `true`). 이 설정 키 정의는 `_workspace/09-config-settings.md`가 소유하며, 본 문서는 동작만 정의한다.
- 파일을 terminal에 드롭/붙여넣어 경로로 변환하는 경우의 shell escaping은 `_workspace/10-shell-integration.md` §9의 file URL escaping 규칙을 적용한 뒤 paste 경로로 보낸다.

### 14.5 수락 hook

- selection copy 후 Windows Clipboard에서 `CF_UNICODETEXT`로 동일 텍스트를 읽을 수 있다.
- bracketed paste mode 활성 시 paste가 `ESC[200~`/`ESC[201~`로 감싸여 stdin에 전달된다.
- 개행 포함 + bracketed paste 비활성 시 확인 dialog가 뜨고, `terminal.paste_confirm=false`면 생략된다.
- paste 데이터 내 `ESC[201~`가 제거되어 전달된다.
- copy 대상 텍스트는 §16 selection model이 반환하는 selection text를 그대로 사용한다 (§16.3 rectangular trim 규칙 포함).

---

## 15. Scrollback buffer

> M2 구현 계약. 2026-07-05 grill-me 확정: libvterm은 scrollback을 제공하지 않으므로(embedder 책임) 아래를 최소 계약으로 고정한다.

### 15.1 소유권과 API

- scrollback은 libvterm 밖에서 `ScrollbackBuffer`가 소유한다. libvterm의 `screen callbacks` 중 `sb_pushline`/`sb_popline`을 구현해 연결한다.

```cpp
// src/terminal/engine/scrollback_buffer.h
class ScrollbackBuffer {
public:
    explicit ScrollbackBuffer(size_t limit_lines);

    // vterm_screen_set_callbacks의 sb_pushline에서 호출된다.
    void PushLine(int cols, const VTermScreenCell* cells);
    // sb_popline에서 호출된다 (alt-screen 진입/스크롤 역방향 시 libvterm이 요청).
    bool PopLine(int cols, VTermScreenCell* cells);

    size_t LineCount() const;
    void SetLimit(size_t limit_lines);  // terminal.scrollback_limit 변경 반영
};
```

### 15.2 limit 연결

- 상한은 `terminal.scrollback_limit`(기본 10000, `_workspace/09-config-settings.md` §3)을 그대로 사용한다.
- limit 초과 시 가장 오래된 라인을 버린다(FIFO). limit이 설정 변경으로 줄어들면 즉시 초과분을 버린다.

### 15.3 alt-screen 규칙

- alt-screen 진입 시 scrollback push를 일시 정지한다(libvterm이 alt-screen 콘텐츠에 대해 `sb_pushline`을 호출하지 않는 것이 기본 동작이므로 별도 억제 로직은 필요 없으나, 뷰포트 상태는 별도로 저장한다).
- alt-screen에서 primary screen으로 복귀하면 뷰포트 오프셋을 alt-screen 진입 직전 값으로 복원한다.

### 15.4 M2 검증 기준

- `sb_pushline`으로 밀려난 라인이 버퍼에 캡처되고 `terminal.scrollback_limit` 초과분은 버려짐
- mouse wheel 스크롤이 뷰포트 오프셋을 갱신하고 buffer 범위를 벗어나지 않음
- alt-screen 전환/복귀 시 뷰포트 오프셋이 진입 전 값으로 복원됨

---

## 16. Mouse selection

> M2 구현 계약. §14 clipboard copy 경로가 이 섹션의 selection text를 소비한다.

### 16.1 선택 모델

```cpp
// src/terminal/engine/selection_model.h
struct SelectionRange {
    int start_row, start_col;
    int end_row, end_col;
    bool rectangular;  // Alt+드래그 시 true
};

class SelectionModel {
public:
    void BeginDrag(int row, int col, bool rectangular);
    void UpdateDrag(int row, int col);
    void EndDrag();
    void Clear();

    bool                 HasSelection() const;
    const SelectionRange& Range() const;
    std::wstring          SelectedText(const TerminalBuffer& buffer) const;
};
```

### 16.2 셀 단위 선택

- 선택은 셀(row, col) 좌표 기준이며, scrollback 라인도 선택 대상에 포함한다(뷰포트가 scrollback을 보고 있을 때).
- 드래그 중 뷰포트 밖으로 포인터가 나가면 자동 스크롤한다.

### 16.3 rectangular trim 규칙

- 일반 드래그 선택은 라인별 trailing whitespace를 유지한 채 이어붙인다.
- rectangular(Alt+드래그) 선택은 라인별로 trailing whitespace를 trim한 뒤 개행으로 이어붙인다 (§14.2와 동일 규칙 공유).

### 16.4 무효화 규칙

- `TerminalBuffer`가 갱신되어(새 출력, resize) 선택 범위의 셀 내용이 바뀌면 선택은 즉시 해제된다. stale selection을 유지하지 않는다.

### 16.5 M2 검증 기준

- 드래그로 선택한 텍스트가 `SelectedText()`로 정확히 반환됨 (§16.2)
- 버퍼 갱신 시 선택이 무효화됨 (§16.4)
- rectangular 선택의 trim 결과가 §14.2 clipboard copy 규칙과 일치함
