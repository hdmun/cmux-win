---
name: cmux-win-autonomous-execution
description: Resume autonomous cmux-win implementation. Use to pick the next ready task from plans/milestones, build a compact task brief, implement it, verify acceptance, and leave a correct session-state handoff. Backed by the cmux-plan Python CLI (next / brief / validate / check-docs / verify / status).
---

# cmux-win Autonomous Execution

Drive implementation through the **`cmux-plan`** CLI. Deterministic loop mechanics
(task selection, validation, verification, status rollup, handoff) are done by the
scripts — you do only the implementation reasoning and read only the generated brief.

`cmux-plan` = `python .claude/skills/cmux-win-autonomous-execution/scripts/cmux_plan.py`
(run from the repo root; stdlib-only Python 3, no install).

## The loop

1. `cmux-plan next` → the next eligible `task_id` (milestone gate + task deps satisfied).
2. `cmux-plan status <task_id> in_progress` → claim it; handoff is refreshed automatically.
3. `cmux-plan brief <task_id>` → read the compact brief: task fields, the queue-mapped
   operating rule, and the *sliced* `doc_refs` sections. **This is the only context you
   need** — do not pre-load whole `_workspace` docs.
4. Implement the task, writing only inside its `touches` paths. Honor
   `.rules/repository-scope.md` (no code under `cmux/`, `ghostty/`, `_workspace/`, `plans/`).
5. `cmux-plan verify <task_id>` → runs `commands`; reports `auto_pass` + `manual_pending`.
   Iterate until `auto_pass` is true. If the project isn't configured yet (no
   `CMakeCache.txt`) and `commands` includes a cmake *configure* call (not
   `cmake --build` / `ctest`), verify runs it anyway — that's how the cache gets
   created for a bootstrap task. Exit code is 1 when `auto_pass` is false (0 for
   `--dry-run` or a pass), so you can gate a shell chain on it.
6. `cmux-plan validate` → must report **0 errors** (schema + deps + gate closure +
   doc-linter + tc↔ctest + acceptance_auto↔commands drift).
7. `cmux-plan status <task_id> done` → mark done. Milestone rollup, `active_milestone`,
   pending→ready promotion, and `plans/session-state.md` are all updated for you
   (its `## Notes for next session` section is preserved, not overwritten). If the
   task has `commands`, a non-blocking warning reminds you to confirm `verify`
   reported `auto_pass=true` before this transition — honor system, not a gate.
8. Handle `manual_pending`: do the checks if you can; otherwise they stay queued in the
   task's `acceptance_manual` for a batched human/AT pass.

## Authority

- `_workspace/*.md` = contracts / architecture. `plans/*.json` = machine task state.
  `.rules/*.md` = operating rules. `CONTEXT.md` = canonical glossary.
- If Markdown and JSON disagree: **Markdown for contract meaning, JSON for execution state**.
- Never end a session with stale `plans/session-state.md` (status writes refresh it).

## Acceptance model

- `acceptance_auto` = machine-gating (`commands`, `tc-*`). `verify` checks these.
- `acceptance_manual` = human / accessibility-tool checks, non-gating, queued.
- doc / policy-freeze tasks gate on `cmux-plan check-docs <task_id>` (doc-linter anchor
  check); contract completeness is a `manual` item.

## When you change plans or docs

- After editing `plans/*` or `_workspace/*`, run `cmux-plan validate` (0 errors required).
- Follow the `.rules/docs-sync.md` co-update matrix (terminology → `CONTEXT.md`, etc.).

## CLI reference

| command | purpose |
|---|---|
| `next [--json]` | select the next eligible task |
| `brief <id>` | compact per-task brief (sliced doc_refs) |
| `validate` | schema (Test-Json) + semantic + doc-linter |
| `check-docs <id>` | verify one task's doc_refs resolve |
| `verify <id> [--dry-run]` | run a task's auto acceptance; exit 1 if `auto_pass` is false, else 0 |
| `status <id> <state> [--dry-run]` | set status + refresh handoff (preserves Notes; warns on `done` if unverified) |

Scripts live in `scripts/`; golden tests in `tests/`
(`python -m unittest discover .claude/skills/cmux-win-autonomous-execution/tests`).
