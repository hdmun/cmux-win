# 에이전트 작업 운영 규칙

## queue-number 규칙

모든 작업 항목은 아래 형식의 `queue-number`를 포함한다.

```text
[QUEUE-N] <태스크 요약>
```

## 큐 분류

| Queue | 업무 범위 | 우선 참조 문서 |
|------|-----------|----------------|
| **1** | 전역 검토, 규칙 구조 정리, 리포지토리 전반 계획 | `AGENTS.md`, `.rules/docs-sync.md` |
| **2** | 저장소 경계, milestone gate, 착수 조건 정리 | `.rules/repository-scope.md`, `_workspace/12-tasks.md` |
| **3** | 빌드, 의존성, CI, 패키징 전제 정리 | `.rules/build-dependencies.md`, `_workspace/11-build-release.md` |
| **4** | app bootstrap, threading, shutdown, source-of-truth | `.rules/app-bootstrap-threading.md`, `_workspace/02-core-app.md` |
| **5** | terminal stack, panel lifecycle, focus/IME/UIA | `.rules/terminal-browser-panel.md`, `_workspace/03-terminal-engine.md`, `_workspace/04-split-pane.md` |
| **6** | browser panel host, automation, session retention | `.rules/terminal-browser-panel.md`, `_workspace/06-browser-panel.md` |
| **7** | IPC transport, schema, error code, CLI protocol 연동 | `.rules/ipc-contract.md`, `_workspace/08-ipc-cli.md` |
| **8** | shell integration, env var, auto-report, PowerShell/CMD/WSL | `.rules/shell-integration.md`, `_workspace/10-shell-integration.md` |
| **9** | settings schema, precedence, migration, persistence | `.rules/settings-persistence.md`, `_workspace/09-config-settings.md` |
| **10** | analytics, logging/privacy, graceful degrade, notification 정책 | `.rules/logging-privacy.md`, `.rules/notifications-degrade.md`, `_workspace/07-notification.md` |
| **11** | 문서 동기화, `_workspace` 문서 갱신, task 상태 반영 | `.rules/docs-sync.md`, `_workspace/12-tasks.md` |

## 작업 작성 원칙

1. 템플릿 안에서 규칙을 다시 길게 복제하지 않는다.
2. `docs-sync`, `milestone`, `dependency`, `verification`은 반드시 authoritative 문서를 가리킨다.
3. queue 선택은 “가장 먼저 읽어야 할 규칙 묶음” 기준으로 한다.
4. 여러 영역을 건드리더라도 대표 queue는 하나만 선택하고, 나머지 문서는 `authoritative-rules`에 열거한다.

## 에이전트 입력 템플릿

```markdown
# [QUEUE-N] <task summary>

- [ ] **task**: 태스크 상세 내용
- [ ] **trigger**: 트리거 방법 (issue, pull request, schedule, manual)
- [ ] **affected-files**: 수정 범위 (파일명, 경로)
- [ ] **authoritative-rules**: 먼저 확인할 `.rules/*.md`, `_workspace/*.md`
- [ ] **docs-sync**: `.rules/docs-sync.md` 기준으로 함께 갱신할 문서
- [ ] **milestone**: `.rules/repository-scope.md`, `_workspace/12-tasks.md` 기준 대상 milestone
- [ ] **verification**: `_workspace/12-tasks.md` 또는 관련 규칙 기준 검증 계획
- [ ] **dependencies**: `.rules/build-dependencies.md` 기준 빌드/런타임 의존성
- [ ] **manual-checkpoints**: 자동화로 대체되지 않는 수동 확인 항목
```

## 필드별 authoritative 위치

| 필드 | authoritative 위치 |
|------|--------------------|
| `authoritative-rules` | 현재 작업에 직접 연관된 `.rules/*.md`, `_workspace/*.md` |
| `docs-sync` | `.rules/docs-sync.md` |
| `milestone` | `.rules/repository-scope.md`, `_workspace/12-tasks.md` |
| `verification` | `_workspace/12-tasks.md`, 관련 도메인 `_workspace` 문서 |
| `dependencies` | `.rules/build-dependencies.md` |
