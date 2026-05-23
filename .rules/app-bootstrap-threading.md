# App bootstrap / threading / shutdown / source-of-truth

## App bootstrap 경로

앱 시작 순서는 아래로 고정한다.

1. `wWinMain`
2. `winrt::init_apartment(single_threaded)`
3. Windows App SDK bootstrap initialize
4. `Microsoft::UI::Xaml::Application::Start`
5. `App::OnLaunched`
6. `WindowManager`가 첫 `MainWindow` 생성

---

## UI 스레드 전용 규칙

다음 작업은 **UI 스레드(STA)에서만** 실행한다.

- XAML object 생성/접근
- window creation / titlebar / backdrop
- Direct2D 그리기
- IME rect 업데이트
- UIA 이벤트 발행

다음 작업은 **background worker / threadpool**에서 실행한다.

- ConPTY read/write
- Named Pipe accept/read/write
- Settings file I/O
- VT parse, dirty region 계산

background 코드는 XAML object를 직접 만지지 않는다. UI 반영은 항상 `DispatcherQueue.TryEnqueue`를 거친다. enqueue 실패는 조용히 무시하지 않고 Warning 레벨 앱 로그에 작업명과 함께 기록한다. 재시도는 하지 않는다.

---

## 종료 순서

정상 종료 시 순서를 고정한다.

1. 새 IPC 연결 차단
2. shell / notification background callbacks 차단
3. panels detach
4. terminal / browser runtime dispose
5. settings flush 대기 (debounce 대기 중인 write는 즉시 flush로 승격; 최대 5초 대기 후 초과 시 Warning 로그 기록 후 계속 진행)
6. windows close
7. bootstrap shutdown

종료 중에는 새 workspace/pane 생성 요청을 받지 않는다.

---

## Source-of-truth 계약

| 값 | source of truth |
|----|-----------------|
| active window | WindowManager |
| active workspace | TabManager |
| active pane / surface | BonsplitController + panel container (BonsplitController: split tree 상태 및 레이아웃 버전 관리; panel container: active panel을 실제 host하는 XAML element) |
| split tree / layout version | BonsplitController |
| unread count | NotificationStore |
| settings | `%APPDATA%\cmux\settings.json` |

UI control은 결과를 반영할 뿐 source of truth가 아니다.

---

## MainWindow 책임 경계

`MainWindow`는 아래만 책임진다.

- title bar / backdrop 초기화
- sidebar, content region, overlays의 XAML composition
- keyboard accelerators의 UI 라우팅
- active panel host 표시

`MainWindow`는 아래를 하지 않는다.

- terminal parsing
- settings persistence
- IPC protocol parsing
- workspace business rule 결정
