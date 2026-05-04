# 명명 규칙 / IPC / Shell Integration

## 명명 규칙 및 ID 형식

| 대상 | 규칙 |
|------|------|
| JSON 필드 | snake_case |
| C++ 타입 | PascalCase |
| IPC / settings 필드 | snake_case |

### ID 형식

```
window:<uuid>
workspace:<uuid>
pane:<uuid>
surface:<uuid>
notification:<uuid>
```

UUID는 canonical lowercase 8-4-4-4-12 형식을 사용한다.

---

## IPC 계약

| 항목 | 규칙 |
|------|------|
| transport | Named Pipe (PIPE_TYPE_MESSAGE + PIPE_READMODE_MESSAGE) |
| max payload | 1 MiB |
| security | same-user ACL |
| naming | \\.\pipe\cmux-<session>-<pid> |
| 인코딩 | UTF-8 only |
| field naming | snake_case |
| protocol version | 2 |

### 보안 규칙

- pipe 생성 시 same-user ACL을 적용한다.
- helper가 ACL 생성에 실패하면 pipe 생성도 실패한다.
- 보안 실패를 무시하고 약한 descriptor로 생성하지 않는다.

### capabilities handshake

새 연결은 첫 응답으로 반드시 `capabilities`를 반환해야 한다.

```json
{
  "type": "capabilities",
  "version": 2,
  "platform": "win32",
  "features": ["split_pane", "browser_panel", "notifications", "shell_report"]
}
```

shell auto-report payload(`shell.directory`, `shell.git_branch`)는 capabilities handshake 예외 경로다. 대신 `version` 필드를 필수로 포함하고, 서버는 mismatch 시 `unsupported_version`을 반환한다.

### command routing 우선순위

1. protocol handshake
2. shell auto-report payloads
3. global app commands
4. workspace/split commands
5. panel-specific commands
6. browser automation commands

### error code 표준

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
| `not_found` | 요청한 리소스가 존재하지 않음 | no |
| `browser_cdp_unavailable` | CDP session 없음 | no |
| `browser_cdp_failed` | CDP 호출 실패 | depends |
| `settings_write_failed` | settings persistence 실패 | yes |

모든 error payload는 최소 `{ "type": "error", "code": "...", "message": "..." }` 구조를 가진다.

### pipe discovery 순서 (CLI)

1. --pipe 플래그
2. CMUX_PIPE_NAME 환경 변수
3. \\.\pipe\cmux-default-<username> fallback

### `socket_control.mode`

`socket_control.mode`는 IPC server의 노출 수준을 제어한다.

| mode | 동작 |
|------|------|
| `full` | capabilities, shell auto-report, read/write command 모두 허용 |
| `readonly` | capabilities, shell auto-report, read-only query command만 허용. state mutation command는 `not_supported` 반환 |
| `off` | Named Pipe server를 생성하지 않음. direct pipe와 CLI 연결 모두 불가 |

#### 분류 규칙

- **read-only query command**: 상태 조회, capability 조회, metadata 조회
- **state mutation command**: workspace/pane 생성, split/close/move, browser automation, 설정 변경
- shell auto-report payload는 `full`, `readonly`에서 허용되고, `off`에서는 서버 자체가 없으므로 허용되지 않는다
- `readonly`에서 mutation command를 받으면 transport는 유지하고 `not_supported`를 반환한다.

> **macOS와의 차이**: macOS cmux는 `notifications` 모드(알림 명령만 허용)를 사용하지만, Windows 포트의 `readonly`는 모든 read-only 조회를 허용하는 더 넓은 범위다. 두 개념은 동등하지 않다.

---

## Shell integration

### 환경 변수 주입 (terminal spawning path 책임)

| 변수 | 값 |
|------|----|
| CMUX_PIPE_NAME | 현재 app instance의 Named Pipe 경로 |
| CMUX_PANE_ID | 현재 pane의 pane:<uuid> |
| CMUX_SURFACE_ID | 현재 surface의 surface:<uuid> |

shell integration 스크립트는 이 값을 **생성하지 않고 소비만** 한다.

### shell auto-report payload (v1)

v1에서 shell integration이 직접 전송하는 payload 타입은 아래 둘뿐이다.

- shell.directory — version, pane_id, cwd_uri (RFC 8089 file:// URI)
- shell.git_branch — version, pane_id, branch

### failure 규칙

- CMUX_PIPE_NAME 없음: silent no-op
- pipe write 실패: 로그만, shell prompt는 유지
- PowerShell prompt blocking 금지
- WSL 미지원이 앱 전체 실패로 이어지면 안 됨

### PowerShell 버전 규칙

1. `Start-ThreadJob` 사용 가능하면 async branch reporting 사용
2. 불가능하면 branch reporting을 disable하거나 lightweight fallback으로 축소
3. 어떤 경우에도 prompt를 느리게 만드는 동기 polling은 금지

### direct pipe vs CLI 구분

| 경로 | 기본 사용처 |
|------|-------------|
| direct pipe | shell metadata auto-report |
| `cmux.exe` | 사용자 명시 명령, 스크립트 진입점 |
