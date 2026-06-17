# 16. Test Strategy

> [!IMPORTANT]
> 완전 자율 구현에서는 task별 acceptance와 milestone별 validation이 자동 검증 가능해야 한다. 이 문서는 test 구조와 기본 검증 경로를 고정한다.

## 1. test layout

```text
tests\
├─ unit\
│  ├─ core\
│  ├─ ipc\
│  ├─ config\
│  └─ notification\
├─ integration\
│  ├─ bootstrap\
│  ├─ terminal\
│  ├─ browser\
│  └─ shell\
└─ fixtures\
```

## 2. unit vs integration boundary

| 종류 | 대상 |
|------|------|
| unit | pure core model, schema validation, parser wrapper, settings merge logic, notification state |
| integration | ConPTY spawning, Named Pipe transport, WinUI bootstrap, WebView2 host, shell integration |

## 3. milestone verification mapping

| Milestone | 우선 test focus |
|-----------|-----------------|
| M0 | configure/build/test entrypoint, manifest/resource 존재, dependency pinning |
| M1 | window bootstrap, STA enforcement, shutdown order |
| M2 | terminal pipeline, renderer publish path, IME/UIA smoke |
| M3 | split state, IPC schema/error handling, focus restore |
| M4 | WebView2 host, session retention, CDP error handling |
| M5 | CLI handshake, command routing, crash/log policy |
| M6 | settings migration, notification degrade, shell non-blocking |

## 4. task acceptance rule

각 `plans\milestones\mN.json` task는 `acceptance_auto` / `acceptance_manual` 배열과 `commands` 배열을 함께 가진다.

- `commands`는 에이전트가 실행할 검증 명령의 ordered list다
- `acceptance_auto`는 **기계 검증 가능한 done criteria(gating)**, `acceptance_manual`은 **사람/AT 확인 항목(비-gating, 큐잉)** 이다
- 자율 루프는 `acceptance_auto`만으로 done을 판정하고(`cmux-plan verify`의 `auto_pass`), `acceptance_manual`은 `manual_pending`으로 큐잉한다
- `acceptance_auto`의 항목은 아래 둘 중 하나여야 한다:
  - `commands`에 들어 있는 literal command string
  - `tc-*` 형식의 test case identifier
- `tc-*` acceptance를 쓸 때는 해당 test case를 포함해 검증하는 command가 `commands`에 있어야 한다 (하네스 `validate`가 강제)
- 수동 확인 항목은 `acceptance_manual`에 `manual:` prefix로 기록한다 (`acceptance_auto`에 `manual:` 항목이 있으면 `validate` 오류)
- doc/policy freeze task는 `acceptance_auto`를 doc-linter anchor 검사(`cmux-plan check-docs <task_id>`)로 채우고, 완성도는 `acceptance_manual`로 둔다
- release-only task는 외부 CI 파이프라인에서만 실행되는 특성상 `commands`를 비울 수 있다 (m7 tasks 등). 이 경우 task의 `notes`에 CI-only 이유를 명시한다
- `acceptance_auto`와 `acceptance_manual`이 모두 비어 있는 task를 `done`으로 올리지 않는다

예시:

```json
"acceptance_auto": [
  "cmake --build --preset dev-x64 --target cmux_app",
  "tc-pipe-server-open: Named Pipe server opens with PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE",
  "ctest --preset dev-x64 -R ipc_server --output-on-failure"
],
"acceptance_manual": [
  "manual: verify first MainWindow creation on STA thread",
  "manual: verify same-user ACL and message-mode transport"
]
```

## 5. tc-* naming convention

`tc-{slug}` test case identifier는 아래 규칙으로 소스 파일과 함수명에 매핑된다.

| 요소 | 규칙 | 예시 |
|------|------|------|
| 파일 위치 | `tests/unit/{module}/test_{module}.cpp` (unit) 또는 `tests/integration/test_{scope}.cpp` (integration) | `tests/unit/core/test_bonsplit_controller.cpp` |
| 함수명 | `TEST({ModuleGroup}, {SlugInPascalCase})` (Google Test) | `TEST(BonsplitController, SplitHProduces2Panes)` |
| ctest 필터 | `-R {module_pattern}` 으로 해당 파일의 모든 tc-* 를 포함 | `ctest -R split_layout` |

변환 규칙:
- `tc-split-h-produces-2-panes` → slug: `split-h-produces-2-panes` → Pascal: `SplitHProduces2Panes`
- module group은 task의 `outputs`에서 primary source file의 모듈명을 따른다
- 같은 source module을 다루는 tc-* 는 같은 test file에 모은다

**예외 — TDD-only / multi-scope task:**
task의 `outputs`가 test 파일만 있거나 여러 모듈에 걸치는 경우(예: m3-5), `tc-*` 항목은 논리적으로 가장 가까운 test 파일에 직접 매핑한다. 이 경우 task JSON의 acceptance 항목 옆에 `// → test_file.cpp` 주석 대신 `outputs` 배열의 순서로 file→tc 대응을 암묵적으로 선언한다. 명확하지 않을 경우 task `notes[]`에 explicit mapping을 기록한다.

task에 `tc-*` acceptance 항목이 있으면 해당 test file 경로를 task의 `outputs`에 포함한다.

## 6. mocking seams

초기 구현에서 mock 또는 fake가 필요한 경계는 아래를 우선한다.

- Named Pipe server/client
- ConPTY process launcher
- settings file I/O
- notification platform adapter
- browser CDP transport

## 7. docs-sync

test 전략이 바뀌면 아래도 함께 본다.

- `_workspace/12-tasks.md`
- `plans/README.md`
- `plans\milestones\mN.json`
- `.rules/docs-sync.md`
