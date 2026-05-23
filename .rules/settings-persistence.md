# Settings persistence

## settings.json 규칙

- authoritative 파일: `%APPDATA%\cmux\settings.json`
- atomic write: temp file write → flush → replace
- migration: schema_version이 낮으면 migration 수행, 원본을 settings.json.bak으로 백업 (1개만 유지; migration 재실행 시 덮어씀)
- UI 변경은 ViewModel에 즉시 반영, 파일 쓰기는 **250ms debounce** (마지막 변경으로부터 250ms 경과 후 단 1회 atomic write 수행; 대기 중 추가 변경이 발생하면 타이머 리셋; 여러 필드 변경은 단일 write에 통합)
- write 실패는 조용히 삼키지 않음: in-app notification으로 실패 사실을 표시하고 (toast 아님), 이전 값은 in-memory로 유지하며 수동 재시도가 가능해야 한다

## settings 로드 precedence 순서

1. built-in defaults
2. Ghostty config parse (terminal rendering defaults 보조 입력)
3. `settings.json` explicit overrides
4. runtime-detected `support_matrix` recompute

## Ghostty config 역할

`%APPDATA%\ghostty\config` (또는 `config.ghostty`)는 terminal rendering defaults 보조 입력이다.

- `settings.json`의 source of truth를 대체하지 않는다.
- 읽는 필드: `font-family`, `font-size`, `theme`, `scrollback-limit`, `background`, `foreground`, `cursor-color`, `cursor-text`, `selection-background`, `selection-foreground`, `palette`, `unfocused-split-opacity`, `unfocused-split-fill`, `split-divider-color`
- `settings.json`에 명시된 값이 있으면 Ghostty config 값을 덮어쓴다.
- parse 실패 시 해당 단계를 건너뛰고 built-in defaults를 유지한다. 실패 사실은 Warning 로그에 기록하며 앱 시작을 중단하지 않는다.
