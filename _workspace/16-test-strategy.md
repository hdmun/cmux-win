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

각 `plans\milestones\mN.json` task는 `acceptance` 배열을 가져야 한다.

- build/test 명령이 있으면 command string을 그대로 적는다
- 수동 확인이 필요하면 `manual:` prefix로 기록한다
- acceptance가 비어 있는 task를 `done`으로 올리지 않는다

예시:

```json
[
  "cmake --preset dev-x64",
  "cmake --build --preset dev-x64",
  "manual: verify first MainWindow creation on STA thread"
]
```

## 5. mocking seams

초기 구현에서 mock 또는 fake가 필요한 경계는 아래를 우선한다.

- Named Pipe server/client
- ConPTY process launcher
- settings file I/O
- notification platform adapter
- browser CDP transport

## 6. docs-sync

test 전략이 바뀌면 아래도 함께 본다.

- `_workspace/12-tasks.md`
- `plans\milestones\mN.json`
- `.rules/docs-sync.md`
