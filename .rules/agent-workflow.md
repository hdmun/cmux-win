# 에이전트 작업 운영 규칙

## queue-number 규칙

모든 작업 항목은 아래 형식의 `queue-number`를 포함한다.

```text
[QUEUE-N] <태스크 요약>
```

machine-readable source of truth는 `plans\milestones\mN.json`의 `queue_number`이며, 허용 값은 `plans\schema\task-registry.schema.json`에서 검증 가능해야 한다.

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

> 이 표의 `AGENTS.md`/`.rules/*.md` 열은 `.claude/skills/cmux-win-autonomous-execution/scripts/build_brief.py`의
> `QUEUE_RULES`와 동기 상태를 유지해야 한다(`_workspace/*.md` 열은 제외 — brief에는 doc_refs로 슬라이스되어 별도 포함됨).
> 표를 바꾸면 `QUEUE_RULES`도 갱신한다; golden test(`tests/test_harness.py`)가 드리프트를 검출한다.

## 작업 작성 원칙

1. 템플릿 안에서 규칙을 다시 길게 복제하지 않는다.
2. `docs-sync`, `milestone`, `dependency`, `verification`은 반드시 authoritative 문서를 가리킨다.
3. queue 선택은 “가장 먼저 읽어야 할 규칙 묶음” 기준으로 한다.
4. 여러 영역을 건드리더라도 대표 queue는 하나만 선택하고, 나머지 문서는 task의 `authoritative_rules` 배열과 `authoritative-rules` 템플릿 항목에 열거한다.
5. 완전 자율 구현 작업은 시작 전에 `plans\index.json`, 해당 milestone JSON, `plans\session-state.md`를 함께 읽는다.
6. `doc_refs`는 `active_milestone.doc_refs` 뒤에 `selected_task.doc_refs`를 merge해서 읽는다. `#fragment`는 같은 Markdown 파일의 heading slug다.
7. `plans\milestones\*.json` 또는 `plans\index.json`을 바꿨으면 `plans\schema\task-registry.schema.json` 기준 validation을 남긴다.
8. task 착수 조건은 **두 단계 AND**다: (1) `index.json` milestones[]의 milestone-level `depends_on`에 있는 모든 선행 milestone status가 `done`이어야 하고, (2) task JSON의 task-level `depends_on`에 있는 모든 task가 `done`이어야 한다. milestone gate가 먼저, task 순서가 그 다음이다.

## 에이전트 입력 템플릿

```markdown
# [QUEUE-N] <task summary>

- [ ] **task**: 태스크 상세 내용
- [ ] **trigger**: 트리거 방법 (issue, pull request, schedule, manual)
- [ ] **task-file**: `plans\milestones\mN.json` 안의 대상 task 경로
- [ ] **status-source**: 상태를 갱신할 JSON 파일과 `plans\session-state.md`
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
| `task-file` | `plans\milestones\mN.json` |
| `status-source` | `plans\milestones\mN.json`, `plans\session-state.md` |
| `docs-sync` | `.rules/docs-sync.md` |
| `milestone` | `.rules/repository-scope.md`, `_workspace/12-tasks.md` |
| `verification` | `_workspace/12-tasks.md`, 관련 도메인 `_workspace` 문서 |
| `dependencies` | `.rules/build-dependencies.md` |

## 자율 실행 시작 순서

새 세션의 기본 읽기 순서는 아래를 따른다.

1. `_workspace/00-overview.md`
2. `_workspace/12-tasks.md`
3. `plans/index.json`
4. 해당 milestone의 `plans/milestones/mN.json`
5. `plans/session-state.md`
6. 현재 task의 queue-number에 대응하는 `.rules/*.md` (`.rules/agent-workflow.md`의 queue mapping 기준)
7. 현재 milestone의 `doc_refs`, 다음에 선택한 task의 `doc_refs`

`CONTEXT.md`는 기본 시작 순서에는 넣지 않는다. 다만 용어/alias 판단이 필요한 작업이거나 merged `doc_refs`가 glossary를 요구하면 즉시 읽는다.

`_workspace/17-functional-spec.md`는 user-facing behavior, command catalog, settings UX를 구현하는 **task의** `doc_refs`에 해당 `#fragment` 섹션으로 포함한다(milestone-level 통째 참조 금지).
