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
