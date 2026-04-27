# 10. Shell Integration

> [!IMPORTANT]
> v1 shell integration의 주 경로는 PowerShell이다. CMD는 경량 경로, WSL은 제한 지원으로 명시한다.

## 1. 지원 범위

| 환경 | v1 상태 | 비고 |
|------|----------|------|
| PowerShell 7.2+ | 지원 | 권장 경로 |
| Windows PowerShell 5.1 | 제한 지원 | async job 기능 축소 가능 |
| CMD | 지원 | OSC 7 중심 |
| WSL | 제한 지원 | relay 없으면 일부 기능만 제공 |

## 2. PowerShell 규칙

### 목표

- prompt blocking 금지
- directory 보고는 항상 lightweight
- git branch 보고는 비동기
- port/process polling은 shell script에서 하지 않음

### 버전 규칙

1. `Start-ThreadJob` 사용 가능하면 async branch reporting 사용
2. 불가능하면 branch reporting을 disable하거나 lightweight fallback으로 축소
3. 어떤 경우에도 prompt를 느리게 만드는 동기 polling은 금지

## 3. direct pipe vs CLI

| 경로 | 기본 사용처 |
|------|-------------|
| direct pipe | shell metadata auto-report |
| `cmux.exe` | 사용자 명시 명령, 스크립트 진입점 |

### direct pipe auto-report payload

shell metadata auto-report는 `08-ipc-cli.md`의 shell payload 규칙을 그대로 사용한다.

v1에서 shell integration이 직접 전송하는 payload는 아래 둘뿐이다.

1. `shell.directory`
2. `shell.git_branch`

예시:

```json
{
  "type": "shell.git_branch",
  "version": 2,
  "pane_id": "pane:11111111-1111-1111-1111-111111111111",
  "branch": "main"
}
```

### environment variable source

이 payload를 만들기 위한 환경 변수는 terminal spawning path가 shell process 생성 시 주입한다.

- `CMUX_PIPE_NAME`
- `CMUX_PANE_ID`
- `CMUX_SURFACE_ID`

shell integration 스크립트는 이 값을 **생성하지 않고 소비만** 한다.

## 4. PowerShell failure 규칙

- `CMUX_PIPE_NAME` 없음: silent no-op
- `CMUX_PANE_ID` 없음: silent no-op
- pipe write 실패: verbose log만 남김
- shell prompt 동작은 유지

## 5. CMD 규칙

CMD는 아래만 기본 지원한다.

- OSC 7 current directory 보고
- 최소 환경 변수 전달

git branch 비동기 보고 같은 무거운 기능은 v1 필수 범위가 아니다.

## 6. WSL 범위 규칙

WSL은 **옵션 기능** 으로 취급한다.

- relay 도구가 있으면 pipe bridging 가능
- relay가 없으면 directory/local shell UX만 유지
- WSL 미지원이 앱 전체 기능 실패로 이어지지 않음

## 7. backend polling 위임

다음 기능은 shell script가 아니라 app backend가 책임진다.

- open port detection
- child process inspection
- metadata coalescing

## 8. direct pipe validation 규칙

- `pane_id` 없는 payload는 보내지 않는다
- `version` 없는 payload는 보내지 않는다
- `cwd_uri`는 RFC 8089 형태의 `file://` URI를 사용한다
- branch 보고는 best-effort이며 실패 시 prompt를 block하지 않는다

## 9. M6 검증 기준

- PowerShell prompt blocking 없음
- ThreadJob 미지원 환경에서 graceful degrade
- CMD 최소 기능 유지
- WSL relay 부재 시 제한 지원이 명시적으로 동작
- direct pipe payload가 `08-ipc-cli.md`와 동일 스키마를 사용
