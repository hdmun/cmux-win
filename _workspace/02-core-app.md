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

## 7. M1 검증 기준

- 첫 window가 STA에서 정상 생성됨
- title bar 확장과 backdrop fallback이 동작함
- `WindowManager`가 active window를 추적함
- shutdown path가 고정된 순서로 동작함
