# Settings / Analytics / Logging / Graceful Degrade

## settings.json 규칙

- authoritative 파일: `%APPDATA%\cmux\settings.json`
- atomic write: temp file write → flush → replace
- migration: schema_version이 낮으면 migration 수행, 원본을 settings.json.bak으로 백업
- UI 변경은 ViewModel에 즉시 반영, 파일 쓰기는 **250ms debounce**
- write 실패는 조용히 삼키지 않음

### settings 로드 precedence 순서

1. built-in defaults
2. Ghostty config parse (terminal rendering defaults 보조 입력)
3. `settings.json` explicit overrides
4. runtime-detected `support_matrix` recompute

### Ghostty config 역할

`%APPDATA%\ghostty\config` (또는 `config.ghostty`)는 terminal rendering defaults 보조 입력이다.

- `settings.json`의 source of truth를 대체하지 않는다.
- 읽는 필드: `font-family`, `font-size`, `theme`, `scrollback-limit`, `background`, `foreground`, `cursor-color`, `cursor-text`, `selection-background`, `selection-foreground`, `palette`, `unfocused-split-opacity`, `unfocused-split-fill`, `split-divider-color`
- `settings.json`에 명시된 값이 있으면 Ghostty config 값을 덮어쓴다.

---

## analytics 정책

기본값은 반드시 false.

- 사용자가 **명시적으로 opt-in**해야만 전송.
- macOS cmux처럼 RELEASE 빌드에서 자동 전송하지 않는다.
- 이를 어기면 개인정보처리방침 위반이다.

---

## 로그 redaction 규칙

기본 로그에 아래는 절대 남기지 않는다.

- terminal 출력 전문
- browser DOM / page HTML
- notification body 원문
- 인증 토큰, 쿠키, Authorization 헤더

기록해도 되는 것: error code, notification_id, workspace_id, surface_id, action type.

### 로그 파일 위치 및 rotation

| 항목 | 규칙 |
|------|------|
| file sink | %LOCALAPPDATA%\cmux\logs\cmux.log |
| rotation | cmux.log + 최대 5개 rolled file, 각 10 MiB 상한 |
| debug sink | Debug 빌드에서 OutputDebugString mirror 허용 |

---

## Graceful degrade 규칙

다음 실패는 앱 전체 실패로 번지지 않아야 한다.

| 실패 상황 | 처리 방식 |
|-----------|-----------|
| ConPTY passthrough 미지원 | standard 모드로 fallback, 로그만 기록 |
| AppNotification(toast) 등록 실패 | toast만 disable, in-app notification 유지 |
| toast show 실패 | 로그 기록 후 계속 진행 |
| WSL relay 부재 | 제한 지원으로 명시, 앱 핵심 기능 유지 |
| WebView2/WinAppSDK 미설치 | bootstrap 단계에서 즉시 fail, 부분 설치를 성공처럼 처리하지 않음 |
| settings 쓰기 실패 | 이전 값 유지, UI에 명시적 실패 노출 |
| OS 알림 권한 거부 | Windows 설정 > 알림 페이지 안내 UI 표시, in-app 알림은 유지 |

---

## Notification 정책

### 알림 억제 (suppression) 규칙

아래 세 조건을 **모두** 만족할 때만 in-app 알림을 생성하지 않는다.

1. 앱이 cmux 메인 창 기준으로 포커스된 상태 (Settings, About 같은 보조 창은 포커스로 간주하지 않음)
2. 해당 workspace가 활성 workspace
3. 해당 surface가 현재 포커스된 surface

`notifications.suppress_when_focused = false`로 설정하면 조건 충족 시에도 항상 알림을 생성한다.

### 중복 알림 억제

동일한 `(workspace_id, surface_id)` 조합으로 새 알림이 추가될 때, 해당 조합의 기존 알림을 먼저 제거한 후 새 알림을 추가한다.

### Toast 정책

- toast action은 모두 **foreground activation**으로 고정한다.
- 배경 COM activation path는 채택하지 않는다.

### Taskbar badge

| 조건 | 표시 |
|------|------|
| unread > 0 | unread 개수 |
| unread > 99 | `"99+"` |
| `CMUX_TAG` 환경변수 설정 시 | `"<tag>:<count>"` 또는 `"<tag>"` (count=0) |
| unread = 0 | badge 제거 |

구현: `BadgeNotification` 또는 taskbar overlay icon.

### Notification GC 기본값

| 항목 | 값 |
|------|-----|
| GC 주기 | 10분 |
| read 알림 만료 | 24시간 |
| 최대 보관 개수 | 200개 |