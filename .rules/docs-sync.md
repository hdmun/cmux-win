# 문서 동기화 & 참조 문서

## 문서 동기화 규칙

코드를 변경할 때 아래 문서를 함께 수정한다.

| 변경 유형 | 함께 수정할 문서 |
|-----------|-----------------|
| bootstrap / 빌드 구조 변경 | _workspace/01-project-structure.md, _workspace/11-build-release.md, _workspace/12-tasks.md |
| IPC protocol / schema 변경 | _workspace/08-ipc-cli.md, _workspace/12-tasks.md |
| settings 필드/schema 변경 | _workspace/09-config-settings.md, _workspace/12-tasks.md |
| panel lifecycle 변경 | _workspace/03-terminal-engine.md, _workspace/04-split-pane.md, _workspace/06-browser-panel.md |
| sidebar / workspace lifecycle 변경 | _workspace/05-sidebar-tabs.md, _workspace/12-tasks.md |
| notification 변경 | _workspace/07-notification.md, _workspace/12-tasks.md |
| shell integration 변경 | _workspace/10-shell-integration.md, _workspace/08-ipc-cli.md, _workspace/12-tasks.md |

구현보다 문서가 뒤처진 상태를 허용하지 않는다.

---

## 참조 문서

| 문서 | 내용 |
|------|------|
| _workspace/00-overview.md | 프로젝트 전체 개요, 용어, ID 규칙 |
| _workspace/01-project-structure.md | 저장소 구조, 디렉터리 역할 |
| _workspace/02-core-app.md | App bootstrap, UI 스레드 경계, window lifecycle |
| _workspace/03-terminal-engine.md | ConPTY, libvterm, Direct2D, IME, UIA |
| _workspace/04-split-pane.md | BonsplitController, layout snapshot, reparenting |
| _workspace/05-sidebar-tabs.md | TabManager, workspace lifecycle, sidebar |
| _workspace/06-browser-panel.md | WebView2, CDP automation, browser lifecycle |
| _workspace/07-notification.md | NotificationStore, toast, degrade 정책 |
| _workspace/08-ipc-cli.md | Named Pipe transport, JSON schema, error code |
| _workspace/09-config-settings.md | settings.json, precedence, atomic write, migration |
| _workspace/10-shell-integration.md | PowerShell/CMD/WSL integration, env var 주입 |
| _workspace/11-build-release.md | 빌드 부트스트랩, dependency pinning, CI 원칙 |
| _workspace/12-tasks.md | milestone 작업 목록, gate 정의, 검증 기준 |
