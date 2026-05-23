# Shell integration

## 환경 변수 주입

terminal spawning path는 아래 환경 변수를 child process에 주입한다.

| 변수 | 값 |
|------|----|
| `CMUX_PIPE_NAME` | 현재 app instance의 Named Pipe 경로 |
| `CMUX_PANE_ID` | 현재 pane의 `pane:<uuid>` |
| `CMUX_SURFACE_ID` | 현재 surface의 `surface:<uuid>` |

shell integration 스크립트는 이 값을 **생성하지 않고 소비만** 한다.

---

## shell auto-report payload (v1)

v1에서 shell integration이 직접 전송하는 payload 타입은 아래 둘뿐이다.

- `shell.directory` — `version`, `pane_id`, `cwd_uri` (RFC 8089 `file://` URI)
- `shell.git_branch` — `version`, `pane_id`, `branch`

shell auto-report는 shell prompt 렌더링 직전마다 전송한다. 이전 값과 동일하면 전송을 생략할 수 있다 (client-side dedup 허용).

---

## failure 규칙

- `CMUX_PIPE_NAME` 없음: silent no-op
- pipe write 실패: 로그만, shell prompt는 유지
- PowerShell prompt blocking 금지
- WSL 미지원이 앱 전체 실패로 이어지면 안 됨

---

## PowerShell 버전 규칙

1. `Start-ThreadJob` 사용 가능하면 async branch reporting 사용
2. 불가능하면 branch reporting을 disable한다 (캐시된 이전 값을 사용하는 동기 경로도 금지)
3. 어떤 경우에도 prompt를 느리게 만드는 동기 polling은 금지

---

## direct pipe vs CLI 구분

| 경로 | 기본 사용처 |
|------|-------------|
| direct pipe | shell metadata auto-report |
| `cmux.exe` | 사용자 명시 명령, 스크립트 진입점 |
