# 명세 누락 항목 검토 (Missing Items Review)

> **작성**: 2026-05-29  
> **기준 소스**: `cmux/` read-only 소스 트리 직접 분석  
> **기준 명세**: `_workspace/cmux-spec/` 전체 (integrated-spec.md, folders/00-20, spec-vs-source-gap-review.md)  
> **분석 범위**: 기존 gap review(`spec-vs-source-gap-review.md`)에서 다루지 않은 신규 누락 항목만 다룸  
> **검증 방법**: 실제 소스 코드 직접 읽기(TerminalController.swift, Workspace.swift, TabManager.swift, 셸 통합 스크립트)

---

## 종합 판정

| 구분 | 건수 | 최고 우선순위 |
|------|------|---------------|
| A. v1 사이드바 소켓 프로토콜 누락 | 15개 명령 | **Critical** |
| B. 환경 변수·설정 키 누락 | 3 | **High** |
| C. Workspace 상태 데이터 구조 누락 | 4 | Medium |
| D. v2 응답 스키마 상세 누락 | 1 | Medium |
| E. 테스트 파일 · 기능 신호 누락 | 7 | Low |
| F. 기타 소스 세부사항 누락 | 3 | Low |

---

## A. v1 사이드바 소켓 프로토콜 (Critical) ★★★

**소스**: `Sources/TerminalController.swift:296–339`  
**현재 명세**: 어떤 spec 문서에도 존재하지 않음

셸 통합 스크립트(`Resources/shell-integration/cmux-zsh-integration.zsh`)가 이 v1 명령들을 통해 사이드바 상태를 업데이트한다. v2 API에는 대응 메서드가 없는 **v1 전용** 프로토콜이다. Windows 포트에서 셸 통합(PowerShell)을 설계할 때 반드시 계승해야 할 동작 계약이다.

### A.1 상태(Status) 엔트리 관리

| 명령 | 문법 | 역할 |
|------|------|------|
| `set_status` | `set_status <key> <value> [--icon=X] [--color=#hex] [--tab=X]` | 워크스페이스 사이드바에 named status 항목 설정 |
| `clear_status` | `clear_status <key> [--tab=X]` | 특정 status 항목 삭제 |
| `list_status` | `list_status [--tab=X]` | 모든 status 항목 열람 |

- `--icon` = SF Symbol 이름(macOS) 또는 이모지 문자열
- `--color` = `#rrggbb` 형식 16진수 색상
- Claude Code 통합이 내부적으로 `set_status claude_code <value> --icon=... --color=... --tab=<id>` 패턴 사용 (CLI/cmux.swift:2811)

### A.2 로그(Log) 엔트리 관리

| 명령 | 문법 | 역할 |
|------|------|------|
| `log` | `log [--level=X] [--source=X] [--tab=X] -- <message>` | 사이드바 로그 스트림에 항목 추가 |
| `clear_log` | `clear_log [--tab=X]` | 로그 항목 전체 삭제 |
| `list_log` | `list_log [--tab=X]` | 로그 항목 열람 |

- `--level` 허용값: `info`(기본) · `progress` · `success` · `warning` · `error`
- `--source` = 알림 출처 라벨(예: `"claude"`)

### A.3 진행률(Progress) 관리

| 명령 | 문법 | 역할 |
|------|------|------|
| `set_progress` | `set_progress <0.0–1.0> [--label=X] [--tab=X]` | 사이드바 진행률 바 설정 |
| `clear_progress` | `clear_progress [--tab=X]` | 진행률 바 제거 |

### A.4 Git 브랜치 보고 (셸 통합이 자동 호출)

| 명령 | 문법 | 역할 |
|------|------|------|
| `report_git_branch` | `report_git_branch <branch> [--dirty] [--tab=X] [--panel=X]` | 현재 git 브랜치와 dirty 상태 보고 |
| `clear_git_branch` | `clear_git_branch [--tab=X]` | git 브랜치 표시 제거 |

- `--dirty` 플래그 존재 시 `SidebarGitBranchState.isDirty = true`
- zsh 통합이 HEAD mtime 기반으로 변경 감지, 비동기 `git branch --show-current` 실행

### A.5 리스닝 포트 보고 (셸 통합이 자동 호출)

| 명령 | 문법 | 역할 |
|------|------|------|
| `report_ports` | `report_ports <port1> [port2 ...] [--tab=X] [--panel=X]` | 현재 TTY에서 수신 중인 TCP 포트 목록 보고 |
| `clear_ports` | `clear_ports [--tab=X] [--panel=X]` | 포트 표시 제거 |

- zsh 통합이 `lsof -nP -a -p <tty_pids> -iTCP -sTCP:LISTEN` 사용
- 포트 스캔: 명령 실행 후 0.5 → 1.0 → 1.5 → 2.0 → 2.5 → 2.5초 간격으로 6회 재스캔 (느린 서버 대응)
- TTY 기반 스코핑: 현재 셸의 제어 TTY 하위 PID만 포트 확인

### A.6 현재 작업 디렉터리 보고 (셸 통합이 자동 호출)

| 명령 | 문법 | 역할 |
|------|------|------|
| `report_pwd` | `report_pwd <path> [--tab=X] [--panel=X]` | 현재 작업 디렉터리 보고 |

- `chpwd` hook에서 호출; path는 RFC 8089 URI(`file:///...`) 형식 권장

### A.7 사이드바 전체 상태 조회/초기화

| 명령 | 문법 | 역할 |
|------|------|------|
| `sidebar_state` | `sidebar_state [--tab=X]` | 워크스페이스의 전체 사이드바 상태(status/log/progress/git/ports) JSON 반환 |
| `reset_sidebar` | `reset_sidebar [--tab=X]` | 모든 사이드바 상태(status/log/progress/git/ports) 초기화 |

### Windows 포트 설계 함의

- `CMUX_TAB_ID` / `CMUX_PANEL_ID` 가 `--tab` / `--panel` 타겟팅에 사용됨 (v1 ID 체계)
- v2 환경에서는 `CMUX_PANE_ID` (`pane:<uuid>` 형식)가 상위 버전이나, 셸 통합이 v1 명령을 사용하므로 Windows PowerShell 통합도 이 명령들과 호환되어야 함
- `report_ports`의 포트 스캔은 `lsof` 대신 Windows에서 `netstat -an` + PID 필터링 또는 PowerShell `Get-NetTCPConnection` 으로 재구현 필요
- 소켓 연결 도구: zsh 통합은 `ncat`(1순위) → `socat`(2순위) → `nc`(fallback) 순으로 시도. Windows Named Pipe에서는 별도 접근 필요

---

## B. 환경 변수·설정 키 누락 (High)

### B.1 `CMUX_TAG` 환경 변수 ★

**소스**: `Sources/TerminalNotificationStore.swift:18` (`TaggedRunBadgeSettings.environmentKey`)  
**현재 명세**: `integrated-spec.md §7.3` 환경 변수 표에 없음

| 항목 | 내용 |
|------|------|
| 변수명 | `CMUX_TAG` |
| 최대 길이 | 10자 (초과 시 truncate) |
| 효과 | Dock 아이콘 배지에 태그 표시: 미읽음이 있으면 `"tag:N"`, 없으면 `"tag"` |
| 용도 | `./scripts/reload.sh --tag <name>` 사용 시 앱이 격리된 소켓·DerivedData·번들 ID로 실행될 때 어느 인스턴스인지 Dock에서 식별 |
| 예시 | `CMUX_TAG=fix` → 3개 미읽음 시 Dock 배지 `"fix:3"` 표시 |

### B.2 `notificationDockBadgeEnabled` UserDefaults 키 ★

**소스**: `Sources/TerminalNotificationStore.swift:6-14` (`NotificationBadgeSettings`)  
**현재 명세**: 어디에도 없음

| 항목 | 내용 |
|------|------|
| 키 | `notificationDockBadgeEnabled` |
| 타입 | Boolean |
| 기본값 | `true` |
| 효과 | Dock 아이콘 배지에 미읽음 알림 수 표시 토글 |
| 배지 포맷 | 미읽음 99 이하: 숫자, 99 초과: `"99+"` |

Windows 포트에서는 Taskbar 배지(Windows 11 `IBadgeWindow`)로 대응 가능.

### B.3 `newWorkspacePlacement` UserDefaults 키

**소스**: `Sources/TabManager.swift:43-80` (`WorkspacePlacementSettings`)  
**현재 명세**: integrated-spec.md §부록에 "새 탭 삽입 위치 설정 (top/afterCurrent/end)"을 v1 제외 항목으로 기재했으나, UserDefaults 키·기본값 미기재

| 항목 | 내용 |
|------|------|
| 키 | `newWorkspacePlacement` |
| 허용값 | `"top"` / `"afterCurrent"` / `"end"` |
| 기본값 | `"afterCurrent"` |
| 효과 | 새 워크스페이스 삽입 위치: 목록 최상위 / 현재 다음 / 목록 끝 |
| 주의 | 고정(pinned) 워크스페이스는 항상 목록 상단 그룹에 유지 |

---

## C. Workspace 상태 데이터 구조 누락 (Medium)

**소스**: `Sources/Workspace.swift:6-37`

아래 데이터 구조가 `Workspace` 객체에 `@Published` 프로퍼티로 존재하나, 명세 어디에도 설명이 없다. v2 API의 사이드바 상태 응답 스키마나 Windows 포트 데이터 모델 설계 시 필요하다.

| 구조체 | 필드 | 용도 |
|--------|------|------|
| `SidebarStatusEntry` | `key: String`, `value: String`, `icon: String?`, `color: String?`, `timestamp: Date` | `set_status` 명령으로 설정되는 named 상태 항목. 딕셔너리 `[String: SidebarStatusEntry]`로 워크스페이스에 저장 |
| `SidebarLogEntry` | `message: String`, `level: SidebarLogLevel`, `source: String?`, `timestamp: Date` | `log` 명령으로 추가되는 로그 스트림 엔트리 |
| `SidebarLogLevel` | `info` / `progress` / `success` / `warning` / `error` | 로그 레벨 enum |
| `SidebarProgressState` | `value: Double`, `label: String?` | `set_progress` 명령으로 설정되는 진행률 (0.0–1.0) |
| `SidebarGitBranchState` | `branch: String`, `isDirty: Bool` | `report_git_branch` 명령으로 설정되는 git 상태 |

**Workspace 추가 필드 (`customTitle`)**:
- `customTitle: String?` — 사용자가 직접 지정한 탭 제목 override. `hasCustomTitle: Bool` 프로퍼티로 유효 여부 판정
- 현재 spec의 탭 타이틀 해석 체인(OSC 0 → CWD → 탭 번호)에 `customTitle`이 실제로는 최상위 우선순위이나 누락됨

---

## D. v2 API 응답 스키마 상세 누락 (Medium)

### D.1 `workspace.list` 응답에 `pinned` 필드 포함

**소스**: `Sources/TerminalController.swift:1379`

```swift
"pinned": ws.isPinned   // v2 workspace.list 응답에 포함
```

`workspace.list` 응답의 각 워크스페이스 객체에는 다음 필드가 있다:

```json
{
  "id": "<uuid>",
  "ref": "workspace:1",
  "index": 0,
  "title": "Terminal",
  "selected": true,
  "pinned": false
}
```

integrated-spec.md §부록의 "workspace pinning (isPinned) = v1 제외" 기재는 UI 기능 구현을 제외한다는 의미지만, `workspace.list` API 응답 스키마에는 이미 포함되어 있다. Windows 포트의 API 구현 시 이 필드를 응답에 포함해야 한다.

---

## E. 테스트 파일·기능 신호 누락 (Low)

### E.1 `tests_v2/`에만 있는 신규 테스트 파일 (v1 대비)

현재 `18-tests-v2.md`에 없거나 "기타 40여 개" 뭉뚱그려진 파일 중 기능 시사 가치가 높은 것:

| 파일 | 시사 기능 |
|------|-----------|
| `test_windows_api.py` | 창(window) 계층 API 전체 검증 (`window.list`, `window.create`, `window.focus`, `window.close`) |
| `test_surface_move_reorder_api.py` | 서피스 이동·재정렬 API (`surface.move`, `surface.reorder`) |
| `test_cli_id_format_defaults.py` | CLI `--id-format` 기본값(refs vs uuids) 동작 |
| `test_cli_identify_ref_resolution.py` | `system.identify` ref 해석 로직 (짧은 ref `workspace:1` 등) |
| `test_browser_api_unsupported_matrix.py` | WKWebView에서 미지원(혹은 부분 지원) 브라우저 API 목록 |
| `test_browser_open_split_reuse_policy.py` | `browser open-split` 시 기존 패널 재사용 정책 |
| `test_trigger_flash.py` | `surface.trigger_flash` / `debug.flash.count` 동작 |

### E.2 CPU 성능 임계값 명세

**소스**: `tests/test_cpu_notifications.py:28-35`, `tests/test_cpu_usage.py`

앱 성능 계약이 테스트 코드에 기재되어 있으나 spec에 없음:

| 지표 | 임계값 |
|------|--------|
| 알림 처리 후 유휴 CPU | ≤ 20% |
| 알림 burst 직후 CPU | ≤ 30% |
| 정착(settle) 대기시간 | 2.0초 |
| CPU 모니터 기간 | 3.0초 |

Windows 포트의 성능 검증 기준으로 사용 가능.

---

## F. 기타 소스 세부사항 누락 (Low)

### F.1 v1 DEBUG 전용 `simulate_file_drop` 명령

**소스**: `Sources/TerminalController.swift:352-353`

```swift
case "simulate_file_drop":
    return simulateFileDrop(args)
```

DEBUG 빌드 전용. 파일 드롭 기능(기존 B2 갭 항목) 테스트에 사용. `test_file_drop_paths.py`가 이 명령으로 드롭을 시뮬레이션한다.

### F.2 셸 통합 소켓 연결 도구 fallback 체인

**소스**: `Resources/shell-integration/cmux-zsh-integration.zsh:4-25`

zsh 통합이 소켓 통신에 사용하는 도구 우선순위:
1. `ncat` (nmap package, 가장 안정적)
2. `socat`
3. `nc` (macOS/BSD `nc`는 `-N` 플래그로 EOF 후 연결 종료; `-w 1` fallback)

Windows Named Pipe에서는 `System.IO.Pipes.NamedPipeClientStream`(PowerShell) 또는 `WriteFile`+`ReadFile`(C++) 사용.

### F.3 `TerminalNotificationStore`의 알림 억제 조건

**소스**: `Sources/TerminalNotificationStore.swift:148-155`

현재 spec(`04-docs.md`)에는 "앱이 포커스되면 알림 억제"라고만 기재되어 있으나, 실제 억제 조건은 더 세밀하다:

```
억제 조건 (모두 충족 시):
1. 앱이 Active(isActive == true)
2. keyWindow.identifier가 "cmux.main" 또는 "cmux.main."으로 시작
3. 해당 탭(tabId)이 현재 선택된 탭(isActiveTab)
4. 해당 서피스(surfaceId)가 포커스된 서피스(isFocusedSurface)
```

Settings/About/debug 패널이 keyWindow인 경우 앱이 active여도 알림 표시됨.  
Windows 포트에서 `IBadgeWindow`, WinUI 3 포커스 상태, `GetForegroundWindow()` 조합으로 유사 억제 로직 구현 필요.

---

## 처리 권고

| # | 항목 | 우선순위 | 권고 액션 |
|---|------|----------|-----------|
| A | v1 사이드바 소켓 프로토콜 15개 명령 | **Critical** | `folders/03-cli.md`에 v1 사이드바 명령 섹션 추가, `integrated-spec.md §7.3`에 `CMUX_TAB_ID`/`CMUX_PANEL_ID` 타겟팅 설명 추가 |
| B1 | `CMUX_TAG` 환경 변수 | **High** | `integrated-spec.md §7.3` 환경 변수 표에 행 추가 |
| B2 | `notificationDockBadgeEnabled` UserDefaults | **High** | `integrated-spec.md §7.8` 설정 섹션에 추가 |
| B3 | `newWorkspacePlacement` UserDefaults | Medium | `integrated-spec.md §부록` 수정: 키 이름·기본값 기재 |
| C | Workspace 상태 데이터 구조 | Medium | `folders/16-sources.md`에 `Workspace.swift` 데이터 구조 표 추가 |
| D | `workspace.list` 응답 `pinned` 필드 | Medium | `folders/16-sources.md` 소켓 v2 카탈로그에 응답 스키마 예시 추가 |
| E | tests_v2 신규 테스트 파일 | Low | `folders/18-tests-v2.md` 파일 목록 갱신 |
| F | 기타 세부사항 | Low | 해당 폴더 spec에 한 줄씩 추가 |

---

*이 문서는 2026-05-29 기준 소스 직접 읽기로 작성되었다. 기존 `spec-vs-source-gap-review.md`의 후속이며 해당 문서에서 다룬 B1–B7, A1–A3 항목과 중복하지 않는다.*
