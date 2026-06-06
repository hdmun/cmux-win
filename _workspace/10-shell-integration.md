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

## 9. file URL / 경로 shell-escaping

> macOS Ghostty의 file URL shell-escaping 대응. terminal에 파일을 드롭하거나 `file://` URL/경로를 paste할 때, shell command line에 안전하게 삽입할 수 있도록 escaping한다. clipboard ↔ terminal 경로는 `_workspace/03-terminal-engine.md` §14가 소유하며, 이 섹션은 셸별 escaping 규칙을 소유한다.

### 9.1 입력 정규화

1. 입력이 `file://` URI(RFC 8089)면 먼저 OS 파일 경로로 디코드한다 (percent-decoding, `file:///C:/...` → `C:\...`).
2. 여러 파일이 드롭되면 각 경로를 개별 escaping한 뒤 공백 한 칸으로 join한다.
3. 경로 끝에 셸 메타문자를 임의로 덧붙이지 않는다 (개행/세미콜론 미삽입). 결과는 항상 단일 토큰(들)이며, 명령 실행은 사용자가 직접 트리거한다.

### 9.2 셸별 escaping 규칙

| 셸 | quoting 방식 | escape 대상 |
|----|--------------|-------------|
| PowerShell | 작은따옴표(`'...'`)로 감쌈 | 내부 `'`는 `''`로 이중화 |
| CMD | 큰따옴표(`"..."`)로 감쌈 | 내부 `"`는 `""`로, `%`는 paste 컨텍스트에서 그대로(전개는 입력 시점 아님) |
| WSL (bash 계열) | 작은따옴표(`'...'`)로 감쌈 | 내부 `'`는 `'\''`로 치환, 경로는 `/mnt/<drive>/...` POSIX 형태로 변환 |

- 셸 종류는 현재 terminal panel이 spawn한 셸(`terminal.default_shell` 또는 실제 child process)을 기준으로 선택한다.
- 공백·`(`·`)`·`&`·`;`·`$`·백틱 등은 위 quoting으로 모두 보호되므로 개별 escape를 추가하지 않는다 (이중 escaping 금지).

### 9.3 WSL 경로 변환

- Windows 경로 `C:\path\to\file`는 WSL 셸 대상일 때 `/mnt/c/path/to/file`로 변환한 뒤 작은따옴표로 감싼다.
- 변환이 불가능한 경로(UNC 등)는 원본 Windows 경로를 그대로 quoting하여 전달하고, verbose log를 남긴다.

### 9.4 수락 hook

- 공백/작은따옴표가 포함된 경로를 PowerShell 셸에 paste하면 단일 인자로 해석되는 `'...'` 토큰이 생성된다.
- `file:///C:/My%20Docs/a.txt` paste 시 PowerShell에서 `'C:\My Docs\a.txt'`로 변환된다.
- WSL 셸 대상에서 `C:\src\x.txt`가 `'/mnt/c/src/x.txt'`로 변환된다.
- 다중 파일 드롭 시 각 경로가 개별 quoting되어 공백으로 join된다.
- 결과 문자열에 개행/세미콜론 등 명령 구분자가 삽입되지 않는다.

## 10. M6 검증 기준

- PowerShell prompt blocking 없음
- ThreadJob 미지원 환경에서 graceful degrade
- CMD 최소 기능 유지
- WSL relay 부재 시 제한 지원이 명시적으로 동작
- direct pipe payload가 `08-ipc-cli.md`와 동일 스키마를 사용
- file URL/경로 escaping이 셸별 규칙대로 단일 토큰을 생성 (§9.4)
