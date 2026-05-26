# 14. ADR Guide

> [!IMPORTANT]
> M0-4의 산출물은 `_workspace\adr\` 아래 ADR 문서로 남긴다. 다른 경로에 흩어진 메모를 authoritative 산출물로 취급하지 않는다.

## 1. location

ADR은 아래 경로를 사용한다.

```text
_workspace\
└─ adr\
   ├─ README.md
   ├─ adr-0001-terminal-threading.md
   ├─ adr-0002-conpty-passthrough-fallback.md
   ├─ adr-0003-parser-selection.md
   └─ adr-0004-panel-lifecycle.md
```

## 2. naming rule

- 파일명은 `adr-<4digit>-<slug>.md`
- slug는 소문자 kebab-case
- ADR 번호는 재사용하지 않는다

## 3. writing rule and minimum template

새 ADR은 아래 세 조건이 모두 맞을 때만 만든다.

1. 뒤집기 비용이 크다.
2. 문맥이 없으면 미래 독자가 "왜 이렇게 했지?"라고 묻는다.
3. 실제 대안 비교가 있었고, 특정 이유로 하나를 골랐다.

셋 중 하나라도 빠지면 새 ADR보다 관련 `_workspace` 문서를 직접 갱신하는 편이 낫다.

ADR은 길게 쓰지 않는다. 기본값은 짧은 결정 기록이며, 전체 배경 설명을 복제하지 않는다.

```markdown
# ADR-0001: Title

- Status: proposed | accepted | superseded
- Related docs:
- Related tasks:

{1-3문장: 어떤 문맥에서 무엇을 결정했고 왜 그렇게 했는지}
```

필요할 때만 아래 섹션을 추가한다.

- `## Context`
- `## Consequences`
- `## Verification impact`

기존 full-section ADR은 계속 유효하다. 새 ADR은 짧은 형식을 기본으로 하고, 추가 섹션은 실제로 설명 가치가 있을 때만 쓴다.

## 4. M0-4 required ADRs

| ADR | 목적 | 최소 연계 문서 |
|-----|------|----------------|
| `adr-0001-terminal-threading.md` | terminal threading contract 확정 | `_workspace/02-core-app.md`, `_workspace/03-terminal-engine.md` |
| `adr-0002-conpty-passthrough-fallback.md` | passthrough detection/fallback 정책 확정 | `_workspace/03-terminal-engine.md` |
| `adr-0003-parser-selection.md` | libvterm 선택 근거와 대안 기각 근거 고정 | `_workspace/03-terminal-engine.md`, `_workspace/11-build-release.md` |
| `adr-0004-panel-lifecycle.md` | terminal/browser 공통 lifecycle 계약 고정 | `_workspace/04-split-pane.md`, `_workspace/06-browser-panel.md` |

## 5. lifecycle

1. `proposed` 상태로 초안 작성
2. 관련 `_workspace` 문서와 교차 참조 추가
3. gate 합의 후 `accepted`로 승격
4. 대체 결정이 생기면 `superseded` 처리하고 후속 ADR에서 참조

## 6. docs-sync

ADR이 승인되면 최소 아래를 함께 갱신한다.

- 해당 도메인 `_workspace` 문서
- `_workspace/12-tasks.md`
- 관련 `plans\milestones\mN.json`
