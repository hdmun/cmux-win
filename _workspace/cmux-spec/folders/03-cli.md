# `CLI`

## 역할 / 목적

`cmux` CLI 도구의 Swift 소스를 담는 폴더. 단일 파일(`cmux.swift`)로 CLI 명령 전체를 구현한다. Unix 소켓(`/tmp/cmux.sock`)을 통해 실행 중인 cmux 앱과 통신한다.

## 주요 내용

```
CLI/
└── cmux.swift     # CLI 구현 전체 (~135 KB, 단일 파일)
```

`cmux.swift`는 약 50개의 top-level 명령을 포함한다 (출처: `CLI/cmux.swift:482-928` 디스패치). 각 명령은 대응하는 소켓 v2 메서드를 호출한다 (메서드 카탈로그는 [16-sources.md](16-sources.md) 참조).

**Top-level 명령 (네임스페이스별)**

| 그룹 | 명령 |
|------|------|
| system | `ping` · `capabilities` · `identify` |
| window | `list-windows` · `current-window` · `new-window` · `focus-window` · `close-window` · `move-workspace-to-window` |
| workspace | `list-workspaces` · `new-workspace` · `close-workspace` · `select-workspace` · `current-workspace` · `reorder-workspace` |
| pane | `list-panes` · `list-pane-surfaces` · `focus-pane` · `new-pane` · `list-panels` · `focus-panel` |
| surface | `new-surface` · `close-surface` · `new-split` · `move-surface` · `reorder-surface` · `drag-surface-to-split` · `refresh-surfaces` · `surface-health` · `trigger-flash` |
| input | `send` · `send-key` · `send-panel` · `send-key-panel` |
| notify | `notify` · `list-notifications` · `clear-notifications` |
| agent | `claude-hook` · `set-app-focus` · `simulate-app-active` |
| browser | `browser` (+서브커맨드) · `open-browser` · `navigate` · `browser-back` · `browser-forward` · `browser-reload` · `get-url` · `focus-webview` · `is-webview-focused` |
| misc | `help` |

**`browser` 서브커맨드** (출처: `CLI/cmux.swift:1354-2100+`)

`identify` · `open`\|`open-split`\|`new` · `goto`\|`navigate` · `back`\|`forward`\|`reload` · `url`\|`get-url` · `focus-webview` · `is-webview-focused` · `snapshot` · `eval` · `wait` · `click`\|`dblclick`\|`hover`\|`focus`\|`check`\|`uncheck`\|`scrollintoview` · `type`\|`fill` · `press`\|`key`\|`keydown`\|`keyup` · `select` · `scroll` · `screenshot` · `get {url|title|text|html|value|attr|count|box|styles}` · `is {visible|enabled|checked}` · `find {role|text|label|placeholder|alt|title|testid|first|last|nth}` · `frame {select|main}` · `dialog {accept|dismiss}` · `download` · `cookies {get|set|clear}` · `storage {get|set|clear}`

> **명세 정정**: 이전 판의 예시 `new-tab` / `split` / `list` / `screenshot`는 top-level 명령으로 존재하지 않는다. 실제로는 각각 `new-workspace`·`new-surface` / `new-split` / `list-workspaces` / `browser screenshot`이다.

## 저장소 상호작용 / 의존성

- `Sources/TerminalController.swift`와 소켓 프로토콜 계약(v1/v2)을 공유한다.
- `tests/` 및 `tests_v2/`의 Python e2e 테스트가 CLI를 통해 앱을 제어한다.
- `GhosttyTabs.xcodeproj`에서 별도 타겟으로 빌드된다.
- `docs/v2-api-migration.md` 및 `docs/agent-browser-port-spec.md`가 이 CLI의 동작을 정의한다.

> **Windows 포트 주의**: 이 CLI는 Unix 소켓(`/tmp/cmux.sock`)을 전제로 한다. cmux-win에서는 동일 계약을 유지하되 transport는 Named Pipe로 바뀌므로, 경로 상수와 연결 bootstrap을 그대로 이식하면 안 된다.

## 편집 지침

**1차 소스**. IPC 프로토콜 변경 시 `Sources/TerminalController.swift`와 함께 수정해야 한다. 파일이 매우 크므로 수정 전 전체 구조를 파악하는 것이 중요하다. v1/v2 이중 프로토콜 지원이 현재 유지되고 있으므로 v1 호환성을 무심코 제거하지 않도록 주의한다.

## 불확실성

없음.
