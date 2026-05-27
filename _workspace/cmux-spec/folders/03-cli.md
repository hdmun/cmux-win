# `CLI`

## 역할 / 목적

`cmux` CLI 도구의 Swift 소스를 담는 폴더. 단일 파일(`cmux.swift`)로 CLI 명령 전체를 구현한다. Unix 소켓(`/tmp/cmux.sock`)을 통해 실행 중인 cmux 앱과 통신한다.

## 주요 내용

```
CLI/
└── cmux.swift     # CLI 구현 전체 (~135 KB, 단일 파일)
```

`cmux.swift`는 다음 CLI 서브커맨드 전체를 포함한다:
- `cmux notify` — 알림 전송 (OSC 시퀀스 에이전트용)
- `cmux open` / `cmux new-tab` / `cmux split` — workspace/pane 제어
- `cmux list` / `cmux identify` — 상태 조회 (v2 API 기반)
- `cmux browser` — 브라우저 패인 제어
- `cmux send` — 터미널 입력 전송
- `cmux screenshot` — 시각 캡처
- 기타 소켓 API v2 명령 전체

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
