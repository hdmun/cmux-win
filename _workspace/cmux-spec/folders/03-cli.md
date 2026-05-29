# `CLI`

## 역할 / 목적

`cmux` CLI 도구의 Swift 소스를 담는 폴더. 단일 파일(`cmux.swift`)로 CLI 명령 전체를 구현한다. Unix 소켓(`/tmp/cmux.sock`)을 통해 실행 중인 cmux 앱과 통신한다.

## 주요 내용

```
CLI/
└── cmux.swift     # CLI 구현 전체 (~135 KB, 단일 파일)
```

`cmux.swift`는 약 50개의 top-level 명령을 포함한다 (출처: `CLI/cmux.swift:482-928` 디스패치). 각 명령은 대응하는 소켓 v2 메서드를 호출한다 (메서드 카탈로그는 [16-sources.md](16-sources.md) 참조).

**Top-level 명령 (네임스페이스별)**

| 그룹 | 명령 |
|------|------|
| system | `ping` · `capabilities` · `identify` |
| window | `list-windows` · `current-window` · `new-window` · `focus-window` · `close-window` · `move-workspace-to-window` |
| workspace | `list-workspaces` · `new-workspace` · `close-workspace` · `select-workspace` · `current-workspace` · `reorder-workspace` |
| pane | `list-panes` · `list-pane-surfaces` · `focus-pane` · `new-pane` · `list-panels` · `focus-panel` |
| surface | `new-surface` · `close-surface` · `new-split` · `move-surface` · `reorder-surface` · `drag-surface-to-split` · `refresh-surfaces` · `surface-health` · `trigger-flash` |
| input | `send` · `send-key` · `send-panel` · `send-key-panel` |
| notify | `notify` · `list-notifications` · `clear-notifications` |
| agent | `claude-hook` · `set-app-focus` · `simulate-app-active` |
| browser | `browser` (+서브커맨드) · `open-browser` · `navigate` · `browser-back` · `browser-forward` · `browser-reload` · `get-url` · `focus-webview` · `is-webview-focused` |
| misc | `help` |

**`browser` 서브커맨드** (출처: `CLI/cmux.swift:1354-2400+`)

`identify` · `open`\|`open-split`\|`new` · `goto`\|`navigate` · `back`\|`forward`\|`reload` · `url`\|`get-url` · `focus-webview` · `is-webview-focused` · `snapshot` · `eval` · `wait` · `click`\|`dblclick`\|`hover`\|`focus`\|`check`\|`uncheck`\|`scrollintoview`\|`scrollinto`\|`scroll-into-view` · `type`\|`fill` · `press`\|`key`\|`keydown`\|`keyup` · `select` · `scroll` · `screenshot` · `get {url|title|text|html|value|attr|count|box|styles}` · `is {visible|enabled|checked}` · `find {role|text|label|placeholder|alt|title|testid|first|last|nth}` · `frame {select|main}` · `dialog {accept|dismiss}` · `download` · `cookies {get|set|clear}` · `storage {get|set|clear}` · `tab {new|list|switch|close}` · `console {list|clear}` · `errors {list|clear}` · `highlight` · `state {save|load}` · `addinitscript` · `addscript` · `addstyle` · `viewport` · `geolocation`\|`geo` · `offline` · `trace {start|stop}` · `network {route|unroute|requests}` · `screencast {start|stop}` · `input {mouse|keyboard|touch}`\|`input_mouse`\|`input_keyboard`\|`input_touch`

> **명세 정정**: 이전 판의 예시 `new-tab` / `split` / `list` / `screenshot`는 top-level 명령으로 존재하지 않는다. 실제로는 각각 `new-workspace`·`new-surface` / `new-split` / `list-workspaces` / `browser screenshot`이다.

## v1 사이드바 소켓 프로토콜 (셸 통합 전용)

**소스**: `Sources/TerminalController.swift:296–339`

셸 통합 스크립트(`Resources/shell-integration/cmux-zsh-integration.zsh`)가 소켓을 통해 직접 호출하는 v1 전용 명령 집합. v2 API에는 대응 메서드가 없다. Windows PowerShell 통합을 설계할 때 반드시 계승해야 할 동작 계약이다.

**공통 옵션**: 대부분의 명령이 `--tab=<id>` / `--panel=<id>` 옵션을 지원한다 (v1 ID 체계). `CMUX_TAB_ID` / `CMUX_PANEL_ID` 환경 변수가 기본 타겟으로 사용된다.

### 상태(Status) 엔트리 관리

| 명령 | 문법 | 역할 |
|------|------|------|
| `set_status` | `set_status <key> <value> [--icon=X] [--color=#hex] [--tab=X]` | 워크스페이스 사이드바에 named status 항목 설정 |
| `clear_status` | `clear_status <key> [--tab=X]` | 특정 status 항목 삭제 |
| `list_status` | `list_status [--tab=X]` | 모든 status 항목 열람 |

- `--icon` = SF Symbol 이름(macOS) 또는 이모지 문자열
- `--color` = `#rrggbb` 형식 16진수 색상
- Claude Code 통합이 `set_status claude_code <value> --icon=... --color=... --tab=<id>` 패턴으로 사용 (출처: `CLI/cmux.swift:2811`)

### 로그(Log) 엔트리 관리

| 명령 | 문법 | 역할 |
|------|------|------|
| `log` | `log [--level=X] [--source=X] [--tab=X] -- <message>` | 사이드바 로그 스트림에 항목 추가 |
| `clear_log` | `clear_log [--tab=X]` | 로그 항목 전체 삭제 |
| `list_log` | `list_log [--tab=X]` | 로그 항목 열람 |

- `--level` 허용값: `info`(기본) · `progress` · `success` · `warning` · `error`
- `--source` = 알림 출처 라벨(예: `"claude"`)

### 진행률(Progress) 관리

| 명령 | 문법 | 역할 |
|------|------|------|
| `set_progress` | `set_progress <0.0–1.0> [--label=X] [--tab=X]` | 사이드바 진행률 바 설정 |
| `clear_progress` | `clear_progress [--tab=X]` | 진행률 바 제거 |

### Git 브랜치 보고 (셸 통합이 자동 호출)

| 명령 | 문법 | 역할 |
|------|------|------|
| `report_git_branch` | `report_git_branch <branch> [--dirty] [--tab=X] [--panel=X]` | 현재 git 브랜치와 dirty 상태 보고 |
| `clear_git_branch` | `clear_git_branch [--tab=X]` | git 브랜치 표시 제거 |

- `--dirty` 플래그 존재 시 `SidebarGitBranchState.isDirty = true`
- zsh 통합이 HEAD mtime 기반으로 변경 감지, 비동기 `git branch --show-current` 실행

### 리스닝 포트 보고 (셸 통합이 자동 호출)

| 명령 | 문법 | 역할 |
|------|------|------|
| `report_ports` | `report_ports <port1> [port2 ...] [--tab=X] [--panel=X]` | 현재 TTY에서 수신 중인 TCP 포트 목록 보고 |
| `clear_ports` | `clear_ports [--tab=X] [--panel=X]` | 포트 표시 제거 |

- zsh 통합이 `lsof -nP -a -p <tty_pids> -iTCP -sTCP:LISTEN` 사용
- 포트 스캔: 명령 실행 후 0.5 → 1.0 → 1.5 → 2.0 → 2.5 → 2.5초 간격으로 6회 재스캔 (느린 서버 대응)
- TTY 기반 스코핑: 현재 셸의 제어 TTY 하위 PID만 포트 확인
- Windows 포트: `netstat -an` + PID 필터링 또는 `Get-NetTCPConnection`으로 재구현

### 현재 작업 디렉터리 보고 (셸 통합이 자동 호출)

| 명령 | 문법 | 역할 |
|------|------|------|
| `report_pwd` | `report_pwd <path> [--tab=X] [--panel=X]` | 현재 작업 디렉터리 보고 |

- `chpwd` hook에서 호출; path는 RFC 8089 URI(`file:///...`) 형식 권장

### 사이드바 전체 상태 조회/초기화

| 명령 | 문법 | 역할 |
|------|------|------|
| `sidebar_state` | `sidebar_state [--tab=X]` | 워크스페이스의 전체 사이드바 상태(status/log/progress/git/ports) JSON 반환 |
| `reset_sidebar` | `reset_sidebar [--tab=X]` | 모든 사이드바 상태(status/log/progress/git/ports) 초기화 |

### DEBUG 전용 명령

DEBUG 빌드에서만 등록되는 v1 소켓 명령(`#if DEBUG`, 출처: `Sources/TerminalController.swift:342–402`). e2e 테스트 하니스가 사용하는 테스트 지원 명령으로, 프로덕션(Release) 빌드에는 존재하지 않는다. v2 프로토콜에서는 `debug.*` 네임스페이스(18개 메서드, [16-sources.md](16-sources.md) 참조)로 대응한다. Windows 포트는 v1 계약 자체보다는 **e2e 테스트 하니스 설계 시** 참조한다.

| 명령 | 역할 |
|------|------|
| `set_shortcut` | 단축키 바인딩 주입 (테스트용) |
| `simulate_shortcut` | 단축키 입력 시뮬레이션 |
| `simulate_type` | 키 입력(타이핑) 시뮬레이션 |
| `simulate_file_drop` | 파일 드롭 시뮬레이션 (`test_file_drop_paths.py`가 사용) |
| `activate_app` | 앱 활성화 시뮬레이션 |
| `is_terminal_focused` | 현재 터미널 포커스 여부 조회 |
| `read_terminal_text` | 터미널 텍스트 버퍼 읽기 |
| `read_screen` | 화면 내용(스크린 셀) 읽기 |
| `render_stats` | 렌더링 통계 조회 |
| `layout_debug` | 레이아웃 트리 덤프 |
| `bonsplit_underflow_count` / `reset_bonsplit_underflow_count` | Bonsplit arranged-subview underflow 카운터 조회/리셋 |
| `empty_panel_count` / `reset_empty_panel_count` | 빈 패널 발생 카운터 조회/리셋 |
| `focus_notification` | 알림으로부터 포커스 이동 시뮬레이션 |
| `flash_count` / `reset_flash_counts` | split flash 카운터 조회/리셋 |
| `panel_snapshot` / `panel_snapshot_reset` | 패널 스냅샷 조회/리셋 |
| `screenshot` | 화면 캡처 (DEBUG) |

> **정정 (2026-05-29)**: 이전 판은 DEBUG 전용 명령으로 `simulate_file_drop` 1개만 기재했으나, 실제로는 위 20개 명령이 `#if DEBUG` 블록에 등록되어 있다.

> **Windows 포트 주의**: zsh 통합이 소켓 연결에 사용하는 도구 우선순위는 `ncat` → `socat` → `nc` 순. Windows Named Pipe에서는 `System.IO.Pipes.NamedPipeClientStream`(PowerShell) 또는 `WriteFile`+`ReadFile`(C++) 사용.

## 저장소 상호작용 / 의존성

- `Sources/TerminalController.swift`와 소켓 프로토콜 계약(v1/v2)을 공유한다.
- `tests/` 및 `tests_v2/`의 Python e2e 테스트가 CLI를 통해 앱을 제어한다.
- `GhosttyTabs.xcodeproj`에서 별도 타겟으로 빌드된다.
- `docs/v2-api-migration.md` 및 `docs/agent-browser-port-spec.md`가 이 CLI의 동작을 정의한다.

> **Windows 포트 주의**: 이 CLI는 Unix 소켓(`/tmp/cmux.sock`)을 전제로 한다. cmux-win에서는 동일 계약을 유지하되 transport는 Named Pipe로 바뀌므로, 경로 상수와 연결 bootstrap을 그대로 이식하면 안 된다.

## 편집 지침

**1차 소스**. IPC 프로토콜 변경 시 `Sources/TerminalController.swift`와 함께 수정해야 한다. 파일이 매우 크므로 수정 전 전체 구조를 파악하는 것이 중요하다. v1/v2 이중 프로토콜 지원이 현재 유지되고 있으므로 v1 호환성을 무심코 제거하지 않도록 주의한다.

## 불확실성

없음.
