# `docs`

## 역할 / 목적

cmux 앱의 기술 스펙 문서 모음. 개발자·에이전트가 참조하는 내부 API 설계 문서와 포크 노트를 포함한다. `docs-site/`의 공개 사용자 문서와 구별된다.

## 주요 내용

```
docs/
├── notifications.md               # 알림 API 가이드 (OSC 9/99/777, CLI 사용법, 에이전트 훅 패턴)
├── agent-browser-port-spec.md     # 브라우저 포트 스펙 (v1/v2 API 용어 정의: window/workspace/pane/surface)
├── v2-api-migration.md            # 소켓 API v1 → v2 마이그레이션 가이드
├── ghostty-fork.md                # ghostty 포크 diff 노트 (upstream 대비 변경사항)
└── assets/                        # 문서 내 이미지 에셋
```

## 알림 API 핵심 (notifications.md / osc-sequences.mdx)

Windows 포트가 동등 구현해야 할 알림 계약 세부:

- **OSC 99 (Kitty)**: `ESC ] 99 ; <params> ; <payload> ST`. 파라미터 `i`(id), `e`(event, 1=new), `d`(done, 0/1), `p`(payload type: `title`/`body`/`subtitle`). 멀티파트(d=0…d=1) 누적 가능.
- **OSC 777 (RXVT)**: `ESC ] 777 ; notify ; <title> ; <body> BEL`. 단순 title+body, subtitle/id 없음.
- **OSC 0 (타이틀)**: `ESC ] 0 ; <title> BEL` — 탭 타이틀 설정. (이전 명세의 "OSC 9"는 osc-sequences.mdx에 상세가 없으므로 99/777/0 기준으로 구현.)
- **전달 경로**: tmux passthrough(`set -g allow-passthrough on` + `\ePtmux;…\e\\` 래핑), SSH OSC 패스스루.
- **`cmux notify` 옵션**: `--title` `--subtitle` `--body` `--tab <id|index>` `--panel <id|index>`.
- **멀티 에이전트 연동 패턴**: Claude Code 훅(`~/.claude/settings.json`), OpenAI Codex(`~/.codex/config.toml`의 `notify`), OpenCode 플러그인(`.opencode/plugins/cmux-notify.js`). 모두 `command -v cmux` 가용성 체크 + macOS `osascript` fallback 패턴 사용.

**알림 억제 조건** (출처: `Sources/TerminalNotificationStore.swift:148–155`):

알림은 아래 **4가지 조건을 모두 충족할 때만** 억제된다:

1. 앱이 Active (`isActive == true`)
2. `keyWindow.identifier`가 `"cmux.main"` 또는 `"cmux.main."` 으로 시작
3. 해당 탭(`tabId`)이 현재 선택된 탭 (`isActiveTab`)
4. 해당 서피스(`surfaceId`)가 포커스된 서피스 (`isFocusedSurface`)

Settings/About/debug 패널이 keyWindow인 경우 앱이 active여도 알림이 표시된다. Windows 포트에서는 `IBadgeWindow` + WinUI 3 포커스 상태 + `GetForegroundWindow()` 조합으로 동등 억제 로직 구현 필요.

## 저장소 상호작용 / 의존성

- `CLI/cmux.swift`와 `Sources/TerminalController.swift`의 동작 계약을 정의한다.
- `tests/` 및 `tests_v2/`의 e2e 테스트가 이 스펙을 기준으로 검증한다.
- `ghostty-fork.md`는 `ghostty/` 서브모듈 수정 시 업스트림 diff 추적 근거가 된다.
- Windows 포트(`_workspace/`)의 설계 문서들이 이 문서들을 참조한다.

## 편집 지침

**1차 소스**. IPC API, 알림 시퀀스, 브라우저 포트 동작을 변경할 때는 이 폴더의 관련 문서도 함께 갱신해야 한다. `agent-browser-port-spec.md`는 에이전트가 cmux를 이해하는 데 가장 중요한 문서이다.

## 불확실성

없음.
