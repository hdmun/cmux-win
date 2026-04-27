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

### 해석 규칙

- Ghostty config는 terminal theme/font 계열 기본값만 제공한다.
- `settings.json`에 명시된 값이 있으면 항상 우선한다.
- `support_matrix`는 사용자가 수동 편집하는 필드가 아니다.

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
| `analytics.enabled` | boolean | `false` | opt-in 전송만 허용 |

### shortcut 필드 규칙

`shortcuts`는 action name을 key로 갖는 object이고, 각 값은 아래 필드를 가진다.

| 필드 | 타입 | 비고 |
|------|------|------|
| `key` | string | virtual key name |
| `ctrl` | boolean | optional, default `false` |
| `shift` | boolean | optional, default `false` |
| `alt` | boolean | optional, default `false` |
| `win` | boolean | optional, default `false` |
| `scope` | string | `"global"`, `"terminal"`, `"browser"` |

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
    "toggle_sidebar": { "key": "B", "ctrl": true, "scope": "global" },
    "new_workspace": { "key": "N", "ctrl": true, "scope": "global" }
  }
}
```

### `appearance.titlebar_style` 해석 규칙

| 값 | Win11 | Win10 | 비고 |
|----|-------|-------|------|
| `auto` | Mica 우선 | Acrylic 우선 | 둘 다 불가하면 `none` |
| `mica` | Mica 강제 | Acrylic로 degrade, 불가 시 `none` | unsupported error로 앱을 막지 않음 |
| `acrylic` | Acrylic 허용 | Acrylic 허용 | |
| `none` | effect 비활성화 | effect 비활성화 | |

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
| `terminal` | terminal panel focused |
| `browser` | browser panel focused |

### conflict 해결 규칙

1. text input control이 먼저 consume
2. app reserved command가 panel shortcut보다 우선
3. panel scope가 현재 focus와 맞을 때만 동작
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
