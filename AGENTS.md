# AGENTS.md — cmux-win Windows 포트 에이전트 규칙

> AI 에이전트(GitHub Copilot, Codex 등)가 cmux-win 저장소에서 작업할 때 반드시 따라야 하는 규약 인덱스.  
> 상세 규칙은 `.rules\` 폴더의 각 파일에 있다. 규약이 바뀌면 해당 파일과 이 인덱스를 함께 수정한다.

---

## 규칙 파일 목록

| 파일 | 주제 |
|------|------|
| [`.rules/agent-workflow.md`](.rules/agent-workflow.md) | queue-number 규칙, 큐 분류, 에이전트 작업 템플릿, authoritative 문서 연결 |
| [`.rules/repository-scope.md`](.rules/repository-scope.md) | 저장소 역할 경계, 수정 금지 경로, 밀스톤 순서와 착수 조건 |
| [`.rules/build-dependencies.md`](.rules/build-dependencies.md) | 공식 빌드 경로(CMake Presets + vcpkg + NuGet), 의존성 pinning, vendor 금지 정책 |
| [`.rules/app-bootstrap-threading.md`](.rules/app-bootstrap-threading.md) | App bootstrap 순서, UI/background 스레드 경계, shutdown 순서, source-of-truth 계약 |
| [`.rules/terminal-browser-panel.md`](.rules/terminal-browser-panel.md) | 터미널 스택, 브라우저 패널, panel lifecycle, `reattach_token` 규칙 |
| [`.rules/ipc-contract.md`](.rules/ipc-contract.md) | 명명 규칙(snake_case / PascalCase), ID 형식(UUID), Named Pipe/프로토콜/error contract |
| [`.rules/shell-integration.md`](.rules/shell-integration.md) | shell integration 환경 변수, auto-report payload, PowerShell/CMD/WSL 규칙 |
| [`.rules/settings-persistence.md`](.rules/settings-persistence.md) | settings.json atomic write / migration, precedence, Ghostty config 보조 입력 규칙 |
| [`.rules/logging-privacy.md`](.rules/logging-privacy.md) | analytics opt-in 정책, 로그 redaction, log sink/rotation 규칙 |
| [`.rules/notifications-degrade.md`](.rules/notifications-degrade.md) | graceful degrade, notification suppression, toast, badge, GC 규칙 |
| [`.rules/docs-sync.md`](.rules/docs-sync.md) | 코드 변경 시 함께 수정해야 할 _workspace 문서 목록, 전체 참조 문서 |
