# 09. Config and Settings

> [!IMPORTANT]
> `settings.json`은 cmux-win의 유일한 설정 source of truth다. Ghostty config는 terminal rendering defaults를 보조하는 입력일 뿐이다.

## 1. authoritative files

| 파일 | 역할 |
|------|------|
| `%APPDATA%\cmux\settings.json` | source of truth |
| `%APPDATA%\ghostty\config` 등 | terminal defaults 보조 입력 |
| `settings.json.bak` | migration backup |

## 2. precedence 규칙

설정 로드 순서는 아래로 고정한다.

1. built-in defaults
2. Ghostty config parse
3. `settings.json` explicit overrides
4. runtime-detected `support_matrix` recompute

### Ghostty config에서 읽는 보조 필드

Ghostty config 파싱은 아래 필드를 terminal defaults로 제공한다.

| Ghostty 키 | 설명 |
|-----------|------|
| `font-family` | 폰트 이름 |
| `font-size` | 폰트 크기 |
| `theme` | 테마 이름 |
| `scrollback-limit` | 스크롤백 라인 수 |
| `background`, `foreground` | 배경/전경 색상 |
| `cursor-color`, `cursor-text` | 커서 색상 |
| `selection-background`, `selection-foreground` | 선택 영역 색상 |
| `palette` | 0~15 색상 팔레트 |
| `unfocused-split-opacity` | 비포커스 split 투명도 |
| `unfocused-split-fill` | 비포커스 split 채움 색 |
| `split-divider-color` | split 구분선 색상 |

Ghostty config 탐색 순서:
1. `%APPDATA%\ghostty\config`
2. `%APPDATA%\ghostty\config.ghostty`

`settings.json`에 명시된 값이 있으면 위 Ghostty config 값을 덮어쓴다.

> **⚠️ analytics.enabled 주의**: macOS cmux는 RELEASE 빌드에서 항상 analytics를 전송한다. Windows 포트는 반드시 `analytics.enabled = false`(기본값)를 지키고, 사용자가 명시적으로 opt-in해야만 전송해야 한다. 이를 어기면 개인정보처리방침 위반이 된다.

## 3. v1 `settings.json` 필드 스키마

v1에서 아래 필드는 이름, 타입, 기본값을 고정한다.

| 필드 | 타입 | 기본값 | 비고 |
|------|------|--------|------|
| `schema_version` | integer | `1` | migration 기준 |
| `socket_control.mode` | string | `"full"` | `"full"`, `"readonly"`, `"off"` |
| `sidebar.visible` | boolean | `true` | |
| `sidebar.width` | integer | `220` | pixel |
| `sidebar.resizable` | boolean | `true` | |
| `appearance.theme` | string | `"auto"` | `"auto"`, `"light"`, `"dark"` |
| `appearance.titlebar_style` | string | `"auto"` | `"auto"`, `"mica"`, `"acrylic"`, `"none"` |
| `terminal.default_shell` | string | `"powershell"` | `"powershell"`, `"cmd"`, `"wsl"` |
| `terminal.scrollback_limit` | integer | `10000` | |
| `terminal.cursor_blink` | boolean | `true` | |
| `terminal.font_family` | string | `"Cascadia Code"` | settings가 Ghostty보다 우선 |
| `browser.search_engine` | string | `"google"` | v1은 string enum |
| `browser.restore_session` | boolean | `true` | |
| `notifications.toast_enabled` | boolean | `true` | |
| `notifications.suppress_when_focused` | boolean | `true` | |
| `analytics.enabled` | boolean | `false` | **opt-in 전송만 허용** — 반드시 사용자가 명시적으로 활성화해야 한다

### shortcut 필드 규칙

`shortcuts`는 action name을 key로 갖는 object이고, 각 값은 아래 필드를 가진다.

| 필드 | 타입 | 비고 |
|------|------|------|
| `key` | string | virtual key name |
| `ctrl` | boolean | optional, default `false` |
| `shift` | boolean | optional, default `false` |
| `alt` | boolean | optional, default `false` |
| `win` | boolean | optional, default `false` |
| `scope` | string | `"global"`, `"workspace"`, `"surface"` |

예시:

```json
{
  "schema_version": 1,
  "sidebar": {
    "visible": true,
    "width": 220,
    "resizable": true
  },
  "terminal": {
    "default_shell": "powershell",
    "scrollback_limit": 10000,
    "cursor_blink": true,
    "font_family": "Cascadia Code"
  },
  "shortcuts": {
    "toggle_sidebar":    { "key": "B", "ctrl": true, "scope": "global" },
    "new_workspace":     { "key": "N", "ctrl": true, "scope": "global" },
    "close_workspace":   { "key": "W", "ctrl": true, "scope": "global" },
    "split_right":       { "key": "D", "ctrl": true, "scope": "surface" },
    "split_down":        { "key": "D", "ctrl": true, "shift": true, "scope": "surface" },
    "next_surface":      { "key": "OEM_6", "ctrl": true, "shift": true, "scope": "surface" },
    "prev_surface":      { "key": "OEM_4", "ctrl": true, "shift": true, "scope": "surface" },
    "focus_left":        { "key": "Left", "ctrl": true, "alt": true, "scope": "surface" },
    "focus_right":       { "key": "Right", "ctrl": true, "alt": true, "scope": "surface" },
    "focus_up":          { "key": "Up", "ctrl": true, "alt": true, "scope": "surface" },
    "focus_down":        { "key": "Down", "ctrl": true, "alt": true, "scope": "surface" },
    "open_browser":      { "key": "L", "ctrl": true, "shift": true, "scope": "global" },
    "show_notifications":{ "key": "I", "ctrl": true, "scope": "global" },
    "jump_to_unread":    { "key": "U", "ctrl": true, "shift": true, "scope": "global" },
    "trigger_flash":     { "key": "H", "ctrl": true, "shift": true, "scope": "global" }
  }
}
```

### `appearance.titlebar_style` 해석 규칙

> 지원 floor는 Win11 22H2+ (00 §4)이므로 OS 버전 분기는 없다. 아래는 effect 가용성 기준 해석이다.

| 값 | 해석 | 비고 |
|----|------|------|
| `auto` | Mica 우선, 불가하면 `none` | |
| `mica` | Mica 강제, 불가 시 `none` | unsupported error로 앱을 막지 않음 |
| `acrylic` | Acrylic 적용 | |
| `none` | effect 비활성화 | |

`support_matrix`는 effect 가능 여부를 계산하지만, `appearance.titlebar_style`의 저장 값 자체를 수정하지는 않는다. 런타임에서만 위 표에 따라 해석한다.

## 4. atomic write 규칙

settings 저장은 아래 순서로만 수행한다.

1. temp file write
2. flush
3. replace
4. old file backup 유지 조건 판단

실패 시 이전 값을 유지하고, UI에 명시적 실패를 노출한다.

## 5. migration 규칙

- `schema_version`이 낮으면 migration 수행
- migration 전 원본을 `settings.json.bak`로 백업
- migration 실패 시 새 파일로 덮어쓰지 않음

## 6. shortcut scope 규칙

| scope | 의미 |
|-------|------|
| `global` | app-wide command |
| `workspace` | active workspace 범위 command |
| `surface` | 현재 focus된 terminal/browser surface 범위 command |

### conflict 해결 규칙

1. text input control이 먼저 consume
2. app reserved command가 panel shortcut보다 우선
3. shortcut scope가 현재 focus(surface/workspace)와 맞을 때만 동작
4. 동일 조합 중복은 validation error

## 7. debounced persistence

- UI 변경은 ViewModel에 즉시 반영
- 파일 쓰기는 250ms debounce
- write 실패는 조용히 삼키지 않음

## 8. 지원 매트릭스 필드

`support_matrix`는 아래처럼 runtime이 계산한다.

- terminal backend
- browser automation availability
- Windows 11 visual effects
- passthrough support

사용자가 직접 편집해도 다음 start에서 다시 계산할 수 있다.

## 9. M6 검증 기준

- precedence 결과가 결정적임
- atomic write가 깨진 JSON을 남기지 않음
- migration backup이 생성됨
- shortcut conflict 검증이 UI 저장 전에 수행됨
- field 이름과 타입이 ViewModel / persistence / CLI import 경로에서 동일하게 유지됨
