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

## 3. atomic write 규칙

settings 저장은 아래 순서로만 수행한다.

1. temp file write
2. flush
3. replace
4. old file backup 유지 조건 판단

실패 시 이전 값을 유지하고, UI에 명시적 실패를 노출한다.

## 4. migration 규칙

- `schema_version`이 낮으면 migration 수행
- migration 전 원본을 `settings.json.bak`로 백업
- migration 실패 시 새 파일로 덮어쓰지 않음

## 5. shortcut scope 규칙

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

## 6. debounced persistence

- UI 변경은 ViewModel에 즉시 반영
- 파일 쓰기는 250ms debounce
- write 실패는 조용히 삼키지 않음

## 7. 지원 매트릭스 필드

`support_matrix`는 아래처럼 runtime이 계산한다.

- terminal backend
- browser automation availability
- Windows 11 visual effects
- passthrough support

사용자가 직접 편집해도 다음 start에서 다시 계산할 수 있다.

## 8. M6 검증 기준

- precedence 결과가 결정적임
- atomic write가 깨진 JSON을 남기지 않음
- migration backup이 생성됨
- shortcut conflict 검증이 UI 저장 전에 수행됨
