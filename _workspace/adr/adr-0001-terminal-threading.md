# ADR-0001: Terminal Threading Model

- Status: accepted
- Related docs: `_workspace/02-core-app.md`, `_workspace/03-terminal-engine.md`
- Related tasks: m0-4, m2-1, m2-3

## Context

ConPTY I/O와 VT 파싱은 차단(blocking) 특성이 강하고, Direct2D 드로우와 IME 업데이트는 반드시 UI 스레드에서 실행해야 한다. 스레드 경계를 명시하지 않으면 다음 문제가 발생한다.

- UI 스레드에서 ConPTY read loop를 실행 → 앱 전체 freeze
- background 스레드에서 XAML 객체 접근 → MTA/STA 위반 크래시
- dirty region 계산과 D2D draw가 같은 스레드에서 경쟁 → 렌더 찢어짐(tearing)

## Decision

아래 표가 v1의 유일한 스레딩 할당이다. 이 표와 다른 경로는 허용하지 않는다.

| 작업 | 스레드 | 비고 |
|------|--------|------|
| ConPTY read loop | background worker | UI 직접 접근 금지 |
| VT parse (libvterm) | background worker | `TerminalBuffer`만 갱신 |
| dirty region 계산 | background worker | frame publish 직전 |
| frame publish | background → atomic handoff | `std::atomic` 또는 lock-free queue |
| swapchain invalidate enqueue | background | coalescing 필수 |
| Direct2D draw | UI thread | `DispatcherQueue.TryEnqueue` 경유 |
| IME rect 계산/업데이트 | UI thread | DPI 변경 즉시 재계산 |
| UIA event raise | UI thread | accessibility 이벤트 |
| Named Pipe accept/read/write | background / threadpool | UI 반영은 DispatcherQueue 경유 |
| Settings file I/O | background worker | UI 반영만 enqueue |

### DispatcherQueue 규칙

1. background code는 XAML 객체를 직접 만지지 않는다.
2. UI 반영은 항상 `DispatcherQueue.TryEnqueue`를 경유한다.
3. `TryEnqueue` 실패는 조용히 무시하지 않고 로그를 남긴다.

### TerminalBuffer handoff 규칙

1. parser는 `TerminalBuffer`만 갱신한다.
2. renderer는 published frame만 읽는다. parser 내부를 직접 읽지 않는다.
3. invalidate는 한 프레임 안에 coalescing한다. 매 VT sequence마다 D2D draw를 트리거하지 않는다.
4. UI 코드는 parser internals를 직접 읽지 않는다.

## Consequences

- ConPTY read loop와 libvterm VT parse는 **동일한 background 스레드**에서 직렬 실행한다. 별도 스레드로 분리할 경우 양쪽 lock이 필요하므로 v1에서는 단순화한다.
- background-to-UI handoff용 `DispatcherQueue` 헬퍼를 `src/utils/dispatcher_queue_helper.h`에 제공한다.
- frame publish에는 `std::atomic<std::shared_ptr<TerminalFrame>>`을 사용한다. 복사 비용을 피하기 위해 immutable snapshot 패턴을 적용한다.

## Verification impact

- M2 수락 기준: ConPTY read와 libvterm parse가 UI thread와 분리된 worker에서 실행되는지 로그로 확인
- M2 수락 기준: `DispatcherQueue.TryEnqueue` 실패 시 로그 항목 존재
- M3 수락 기준: reparent 중 background read loop가 중단되지 않음
