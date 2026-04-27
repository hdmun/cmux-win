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

| 필드 | 형식 |
|------|------|
| `window_id` | `window:<uuid>` |
| `workspace_id` | `workspace:<uuid>` |
| `pane_id` | `pane:<uuid>` |
| `surface_id` | `surface:<uuid>` |
| `notification_id` | `notification:<uuid>` |

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

## 10. 테스트 기준

M3 이후 최소 아래 케이스를 자동화한다.

- same-user ACL pass/fail
- oversized payload
- unsupported version
- unknown command
- UI state conflict
- browser automation unavailable
- shell auto-report payload validation
- shell auto-report version mismatch
