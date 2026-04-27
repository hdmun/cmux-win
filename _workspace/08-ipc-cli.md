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
2. global app commands
3. workspace/split commands
4. panel-specific commands
5. browser automation commands

## 9. 테스트 기준

M3 이후 최소 아래 케이스를 자동화한다.

- same-user ACL pass/fail
- oversized payload
- unsupported version
- unknown command
- UI state conflict
- browser automation unavailable
