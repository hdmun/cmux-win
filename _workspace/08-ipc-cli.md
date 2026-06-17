# 08. IPC and CLI

> [!IMPORTANT]
> 이 문서는 Named Pipe transport, JSON schema, ID 형식, error code를 고정한다. 구현자는 이 문서를 프로토콜 기준으로 사용한다.

## 1. transport

| 항목 | 규칙 |
|------|------|
| transport | Named Pipe |
| mode | `PIPE_TYPE_MESSAGE` + `PIPE_READMODE_MESSAGE` |
| max payload | 1 MiB |
| security | same-user ACL |
| naming | `\\.\pipe\cmux-<session>-<pid>` |

## 2. pipe discovery 순서

CLI는 아래 순서로 대상 pipe를 찾는다.

1. `--pipe`
2. `CMUX_PIPE_NAME`
3. `\\.\pipe\cmux-default-<username>` fallback

direct pipe write는 자동 보고용 shell integration에서만 기본 경로로 허용한다.

## 3. JSON 규칙

- protocol version: `2`
- field naming: `snake_case`
- UTF-8 only
- request/response는 각각 하나의 complete message

### shell auto-report payload 규칙

shell integration이 direct pipe로 보내는 자동 보고 payload는 아래 타입만 v1에서 지원한다.

| type | 필수 필드 | 설명 |
|------|-----------|------|
| `shell.directory` | `version`, `pane_id`, `cwd_uri` | OSC 7 기반 현재 디렉터리 보고 |
| `shell.git_branch` | `version`, `pane_id`, `branch` | 비동기 git branch 보고 |

예시:

```json
{
  "type": "shell.directory",
  "version": 2,
  "pane_id": "pane:11111111-1111-1111-1111-111111111111",
  "cwd_uri": "file:///C:/Users/hdmun/repo/cmux-win"
}
```

```json
{
  "type": "shell.git_branch",
  "version": 2,
  "pane_id": "pane:11111111-1111-1111-1111-111111111111",
  "branch": "main"
}
```

shell auto-report payload는 capabilities handshake를 수행하지 않는 예외 경로다. 대신 `version` 필드를 **필수** 로 포함하고, 서버는 mismatch 시 `unsupported_version`을 반환한다.

## 4. ID 규칙

| 필드 | 전체 형식 | 단축 참조 |
|------|----------|----------|
| `window_id` | `window:<uuid>` | `window:N` (1-based 정수) |
| `workspace_id` | `workspace:<uuid>` | `workspace:N` |
| `pane_id` | `pane:<uuid>` | `pane:N` |
| `surface_id` | `surface:<uuid>` | `surface:N` |
| `notification_id` | `notification:<uuid>` | — |

### ID 형식 옵션

CLI는 `--id-format` 플래그로 응답에서 ID 표현 방식을 선택할 수 있다.

| 값 | 동작 |
|----|------|
| `uuids` | 전체 UUID 형식만 반환 (기본값) |
| `refs` | 단축 정수 참조만 반환 |
| `both` | 두 형식 모두 반환 |

단축 참조(`pane:1`, `surface:2` 등)는 현재 연결 세션 내에서만 유효하다.

## 5. capabilities handshake

새 연결은 첫 응답으로 `capabilities`를 반환해야 한다.

```json
{
  "type": "capabilities",
  "version": 2,
  "platform": "win32",
  "features": [
    "split_pane",
    "browser_panel",
    "notifications",
    "shell_report"
  ]
}
```

## 6. error code 표준

| code | 의미 | retry |
|------|------|-------|
| `unsupported_version` | protocol version 미지원 | no |
| `not_supported` | 현재 기능/플랫폼 미지원 | no |
| `invalid_request` | schema 또는 필수 필드 오류 | no |
| `unknown_command` | 존재하지 않는 command | no |
| `payload_too_large` | 1 MiB 초과 | no |
| `acl_denied` | same-user ACL 또는 identity 검증 실패 | no |
| `pipe_connect_failed` | pipe 연결 실패 | yes |
| `pipe_read_failed` | read 실패 | yes |
| `pipe_write_failed` | write 실패 | yes |
| `state_conflict` | 현재 앱 상태와 충돌 | depends |
| `not_found` | 요청한 리소스(workspace/pane/surface 등)가 존재하지 않음 | no |
| `browser_cdp_unavailable` | CDP session 없음 | no |
| `browser_cdp_failed` | CDP 호출 실패 | depends |
| `settings_write_failed` | settings persistence 실패 | yes |

모든 error payload는 최소 아래 구조를 가진다.

```json
{
  "type": "error",
  "code": "invalid_request",
  "message": "missing workspace_id"
}
```

## 7. 인증과 보안 규칙

1. pipe 생성 시 same-user ACL 적용
2. helper가 ACL 생성에 실패하면 pipe 생성도 실패
3. 보안 실패를 무시하고 약한 descriptor로 생성하지 않음

## 8. command routing 우선순위

1. protocol handshake
2. shell auto-report payloads
3. global app commands
4. workspace/split commands
5. panel-specific commands
6. browser automation commands

## 9. `socket_control.mode` 동작 규칙

`socket_control.mode`는 IPC server의 노출 수준을 제어한다.

| mode | 동작 |
|------|------|
| `full` | capabilities, shell auto-report, read/write command 모두 허용 |
| `readonly` | capabilities, shell auto-report, read-only query command만 허용. state mutation command는 `not_supported` 반환 |
| `off` | Named Pipe server를 생성하지 않음. direct pipe와 CLI 연결 모두 불가 |

### 분류 규칙

- **read-only query command**: 상태 조회, capability 조회, metadata 조회
- **state mutation command**: workspace/pane 생성, split/close/move, browser automation, 설정 변경
- shell auto-report payload는 `full`, `readonly`에서 허용되고, `off`에서는 서버 자체가 없으므로 허용되지 않는다

`readonly`에서 mutation command를 받으면 transport는 유지하고 `not_supported`를 반환한다.

`readonly`에서 mutation command를 받으면 transport는 유지하고 `not_supported`를 반환한다.

> **macOS와의 차이**: macOS cmux는 `notifications` 모드(알림 명령만 허용)를 사용하지만, Windows 포트의 `readonly`는 모든 read-only 조회를 허용하는 더 넓은 범위다. 두 개념은 동등하지 않다.

## 10. CLI 명령 카탈로그

CLI는 `cmux.exe [global-flags] <command> [args]` 형식이다.

### 전역 플래그

| 플래그 | 설명 |
|--------|------|
| `--pipe <name>` | 연결할 Named Pipe 경로 override |
| `--id-format refs\|uuids\|both` | ID 표현 형식 선택 (기본: `uuids`) |
| `--window <window_id>` | 대상 window 지정 |

### System

| 명령 | 설명 |
|------|------|
| `ping` | 연결 확인 |
| `capabilities` | 서버 capabilities 반환 |
| `identify [--workspace] [--surface] [--no-caller]` | 현재 context ID 반환 |
| `session_info` | 현재 세션/창 상태 반환 (read-only) |

#### `session_info` 응답 형식

`session_info`는 read-only query command이며 `readonly` 모드에서도 허용된다. 현재 세션 식별자, ConPTY `pty_mode`, 활성 surface/workspace를 반환한다.

```json
{
  "type": "session_info",
  "session_id": "session:<uuid>",
  "pty_mode": "standard",
  "active_window_id": "window:<uuid>",
  "active_workspace_id": "workspace:<uuid>",
  "active_surface_id": "surface:<uuid>"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `session_id` | string | `session:<uuid>` 현재 세션 식별자 |
| `pty_mode` | string | ConPTY 모드 (`standard` \| `passthrough`, ADR-0002) |
| `active_window_id` | string | 현재 활성 window |
| `active_workspace_id` | string | 현재 활성 workspace |
| `active_surface_id` | string \| null | 현재 focus된 surface (없으면 `null`) |

### Windows

| 명령 | 설명 |
|------|------|
| `list-windows` | 열린 창 목록 |
| `current-window` | 현재 창 정보 |
| `new-window` | 새 창 생성 |
| `focus-window` | 창 포커스 |
| `close-window` | 창 닫기 |

### Workspaces

| 명령 | 설명 |
|------|------|
| `list-workspaces` | workspace 목록 |
| `new-workspace` | workspace 생성 |
| `select-workspace` | workspace 활성화 |
| `current-workspace` | 현재 workspace |
| `close-workspace` | workspace 닫기 |
| `move-workspace-to-window --workspace --window` | 창 간 이동 |
| `reorder-workspace --workspace (--index\|--before\|--after)` | 순서 변경 |

### Panes / Surfaces

| 명령 | 설명 |
|------|------|
| `list-panes` | pane 목록 |
| `list-pane-surfaces [--pane]` | pane 내 surface 목록 |
| `focus-pane --pane` | pane 포커스 |
| `new-pane [--type] [--direction] [--url]` | pane 생성 |
| `new-surface [--type] [--pane] [--url]` | surface 생성 |
| `close-surface` | surface 닫기 |
| `move-surface --surface [--pane\|--workspace\|--window] [--before\|--after\|--index] [--focus]` | surface 이동 |
| `reorder-surface --surface (--index\|--before\|--after)` | surface 순서 변경 |
| `drag-surface-to-split --surface <dir>` | split 방향으로 drag |
| `trigger-flash [--workspace] [--surface]` | 주의 flash 효과 |
| `refresh-surfaces` | surface 갱신 |

### Input

| 명령 | 설명 |
|------|------|
| `send <text>` | 현재 surface에 텍스트 전송 |
| `send-key <key>` | 현재 surface에 키 입력 |

### Notifications

| 명령 | 설명 |
|------|------|
| `notify --title <text> [--subtitle <text>] [--body <text>] [--workspace] [--surface]` | 알림 전송 |
| `list-notifications` | 알림 목록 |
| `clear-notifications` | 알림 삭제 |

### App Control

| 명령 | 설명 |
|------|------|
| `set-app-focus <active\|inactive\|clear>` | 앱 포커스 상태 강제 설정 (테스트용) |

### claude-hook

AI agent(Claude Code, Codex 등)의 세션 이벤트를 cmux에 전달한다.

```
cmux claude-hook <event> [--workspace <id>] [--surface <id>]
```

| event | 설명 |
|-------|------|
| `session-start` | AI 세션 시작 |
| `session-stop` | AI 세션 종료 |
| `notification` | AI가 알림 전송 (stdin으로 JSON) |
| `active` | AI 작업 중 상태 |
| `idle` | AI 대기 상태 |

- stdin으로 JSON payload를 수신한다.
- 세션 상태는 `%APPDATA%\cmux\claude-hook-sessions.json`에 저장한다.
- `set_status` / `clear_status` 메서드로 workspace 상태 badge를 설정한다.
- 파일 잠금은 Windows `LockFileEx`를 사용한다.

#### claude-hook event payloads

> [!NOTE]
> 아래는 5개 이벤트의 stdin JSON payload 계약 **스텁**이다. 필드 타입·필수 여부·에러 처리의 상세 확정은 task `m6-8`(contract freeze)에서 수행한다.

| event | 최소 필드 | 동작 |
|-------|-----------|------|
| `session-start` | `version`, `session_id`, `cwd_uri` | 세션 파일에 항목 생성, workspace status를 `running`으로 |
| `session-stop` | `version`, `session_id` | 세션 항목 제거, status badge `clear_status` |
| `notification` | `version`, `session_id`, `title`, `body` | 알림 ring에 전달 (stdin JSON) |
| `active` | `version`, `session_id` | status를 `active`(작업 중)로 `set_status` |
| `idle` | `version`, `session_id` | status를 `idle`(대기)로 `set_status` |

```json
{ "version": 2, "event": "session-start", "session_id": "session:<uuid>", "cwd_uri": "file:///C:/..." }
```

- `session_id` 미존재 시 `invalid_request` 반환.
- 상태 매핑(`active`/`idle`/`running`)은 `05-sidebar-tabs.md`의 `status_entries`로 투영된다.

### Browser

browser 명령은 `cmux browser <subcommand>` 형식이다.

| 카테고리 | subcommand |
|----------|-----------|
| 탐색 | `open`, `open-split`, `goto`, `navigate`, `back`, `forward`, `reload`, `url` |
| 페이지 정보 | `snapshot`, `screenshot`, `get <verb>`, `is <verb>`, `state` |
| 상호작용 | `click`, `dblclick`, `hover`, `focus`, `check`, `uncheck`, `type`, `fill`, `press`, `key`, `keydown`, `keyup`, `select`, `scroll`, `scroll-into-view` |
| 기다리기 | `wait` |
| 검색 | `find <locator>`, `eval` |
| 프레임 | `frame` |
| 다이얼로그 | `dialog` |
| 다운로드 | `download` |
| 쿠키 / 스토리지 | `cookies`, `storage` |
| 탭 관리 | `tab` |
| 네트워크 | `network` |
| 콘솔 / 오류 | `console`, `errors` |
| 스크립트 | `addinitscript`, `addscript`, `addstyle` |
| 뷰포트 / 환경 | `viewport`, `geolocation`, `offline` |
| 디버깅 | `trace`, `screencast`, `highlight` |
| 식별 | `identify` |

`--snapshot-after` 플래그: `navigate`, `click`, `type` 등 동작 완료 후 DOM 스냅샷을 응답에 포함한다.

## 11. 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `CMUX_PIPE_NAME` | `\\.\pipe\cmux-default-<username>` | Named Pipe 경로 override |
| `CMUX_PIPE_ENABLE` | `true` (release) | IPC server 활성화 여부 |
| `CMUX_PIPE_MODE` | `"full"` | IPC server 노출 수준 (`full`/`readonly`/`off`) |
| `CMUXTERM_CLI_RESPONSE_TIMEOUT_SEC` | `15` | CLI 응답 대기 timeout (초) |
| `CMUX_CLAUDE_HOOK_STATE_PATH` | `%APPDATA%\cmux\claude-hook-sessions.json` | claude-hook 세션 상태 파일 경로 |
| `CMUX_TAG` | (없음) | taskbar badge prefix (멀티 인스턴스 구분용) |

## 12. 테스트 기준

M3 이후 최소 아래 케이스를 자동화한다.
- oversized payload
- unsupported version
- unknown command
- UI state conflict
- browser automation unavailable
- shell auto-report payload validation
- shell auto-report version mismatch

## 13. Debug and automation IPC

> [!NOTE]
> macOS cmux의 `debug.*` / `read_terminal_text` / `simulate_*` 계열 대응. 이 군은 `tests_v2` 류 e2e 검증의 **관찰·주입 백본**이다. 아래는 명령 목록 **스텁**이며, 명령별 request/response 상세는 contract freeze task(`m3-7`)에서 확정한다. `socket_control.mode=readonly`에서 inspect 계열은 허용, simulate 계열은 mutation으로 분류되어 `not_supported`를 반환한다.

### 13.1 inspect (read-only)

| 명령 | 반환 | 비고 |
|------|------|------|
| `read_terminal_text` | 활성 surface의 가시 텍스트 | `--surface` 대상 지정 |
| `read_screen` | 화면 셀 그리드 스냅샷 | 행/열 + 셀 속성 |
| `render_stats` | 렌더 프레임/언더플로 카운터 | 성능 회귀 검출용 |
| `layout_debug` | 현재 split/pane 트리 덤프 | `layout_version` 포함 |
| `panel_snapshot` | panel 상태(타입/포커스/크기) | per-panel |
| `surface_health` | surface 생존/flash/underflow 상태 | health 진단 |

### 13.2 input simulation (mutation)

| 명령 | 동작 | 비고 |
|------|------|------|
| `simulate_type` | 대상 surface에 텍스트 입력 주입 | 테스트 자동화 |
| `simulate_file_drop` | 파일 드롭 이벤트 주입 | `10 §9` escaping 경유 |
| `simulate_shortcut` | 단축키 이벤트 주입 | accelerator 경로 |
| `is_terminal_focused` | 현재 터미널 포커스 여부 | read이나 입력 테스트와 함께 사용 |

## 14. Sidebar and status IPC commands

> [!NOTE]
> macOS cmux의 v1 sidebar/status 명령 계층 대응. shell integration과 claude-hook이 사용한다. 상세 인자/응답은 구현 task(`m5-6`)에서 확정하며, sidebar 메타데이터 투영은 `05-sidebar-tabs.md`가 소유한다.

| 명령 | 동작 |
|------|------|
| `set_status --key <k> --value <v> [--workspace]` | workspace `status_entries[k]` 설정 |
| `clear_status [--key <k>] [--workspace]` | 상태 항목 제거 (키 없으면 전체) |
| `report_git_branch --branch <name>` | branch 메타데이터 보고 (shell auto-report와 동일 효과) |
| `report_ports --ports <csv>` | listening 포트 보고 (백엔드 감지 결과 주입 경로, `10 §7`) |
| `sidebar_state` | 현재 sidebar 메타데이터 스냅샷 반환 (read-only) |

### 14.1 대상 지정 플래그

`--tab <workspace_ref>` / `--panel <surface_ref>`로 명령 대상을 명시한다. 미지정 시 현재 활성 workspace/surface를 대상으로 한다.
