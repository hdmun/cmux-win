# 문서 동기화 & 참조 문서

## 문서 동기화 규칙

코드를 변경할 때 아래 문서를 함께 수정한다.

> `12-tasks.md`는 milestone 작업 목록과 gate 정의를 담는다. 모든 기능 변경은 해당 milestone task의 완료 여부에 영향을 미치므로, 아래 표에서 포함된 항목은 항상 함께 수정한다.

| 변경 유형 | 함께 수정할 문서 |
|-----------|-----------------|
| bootstrap / 빌드 구조 변경 | _workspace/01-project-structure.md, _workspace/11-build-release.md, _workspace/12-tasks.md |
| autonomous execution / task registry 변경 | _workspace/13-autonomous-execution.md, _workspace/session-state.md, plans/index.json, plans/milestones/*.json, _workspace/12-tasks.md |
| ADR / gate contract 변경 | _workspace/14-adr-guide.md, _workspace/12-tasks.md, 관련 도메인 _workspace 문서 |
| scaffolding / test strategy 변경 | _workspace/15-scaffolding.md, _workspace/16-test-strategy.md, _workspace/11-build-release.md, _workspace/12-tasks.md |
| IPC protocol / schema 변경 | _workspace/08-ipc-cli.md, _workspace/12-tasks.md |
| settings 필드/schema 변경 | _workspace/09-config-settings.md, _workspace/12-tasks.md |
| panel lifecycle 변경 | _workspace/03-terminal-engine.md, _workspace/04-split-pane.md, _workspace/06-browser-panel.md |
| sidebar / workspace lifecycle 변경 | _workspace/05-sidebar-tabs.md, _workspace/12-tasks.md |
| notification 변경 | _workspace/07-notification.md, _workspace/12-tasks.md |
| shell integration 변경 | _workspace/10-shell-integration.md, _workspace/08-ipc-cli.md, _workspace/12-tasks.md |
| `.rules` 파일 추가/변경/삭제 | AGENTS.md (인덱스 테이블) |

구현보다 문서가 뒤처진 상태를 허용하지 않는다.

---

## PR 머지 전 체크리스트

- [ ] 변경 유형을 위 표에서 확인했는가?
- [ ] 해당하는 `_workspace/` 및 `plans/` 문서를 모두 수정했는가?
- [ ] 관련 `plans/milestones/*.json`와 `_workspace/session-state.md` 상태를 업데이트했는가?
- [ ] `12-tasks.md`의 관련 milestone/gate 설명을 업데이트했는가?
- [ ] `.rules` 파일을 변경했다면 `AGENTS.md` 인덱스를 갱신했는가?

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
| _workspace/13-autonomous-execution.md | `_workspace` / `plans` / `.rules` authority split, read order |
| _workspace/14-adr-guide.md | ADR 위치, 템플릿, M0-4 필수 ADR |
| _workspace/15-scaffolding.md | bootstrap starter file, target naming, scaffold 규칙 |
| _workspace/16-test-strategy.md | test layout, task acceptance, mocking seam |
| _workspace/session-state.md | 세션 handoff snapshot |
| plans/index.json | milestone registry, status enum, startup read order |
| plans/milestones/*.json | machine-readable task 상태, 의존성, acceptance |
