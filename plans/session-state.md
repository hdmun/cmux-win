# Session State

> [!IMPORTANT]
> 이 문서는 세션 간 handoff를 위한 snapshot이다. 장문의 작업 일지를 쓰지 말고, 다음 에이전트가 바로 이어받을 수 있는 최소 상태만 유지한다.

## Current milestone

- milestone: `M0`
- active_task_ids: `[]`

## Last completed task

- task_id: `m0-7` (+ parity task registration, this session)
- summary: `Registered tasks for the 12 previously-missing v1 features (m1-4, m1-5, m2-6, m2-7, m3-6, m6-5, m6-6, m6-7), folded session_info into m3-1, fixed the m2-4 doc_ref fragment, and recounted 18-cmux-parity coverage. All 8 milestone JSONs validate.`

## Blocked tasks

| task_id | blocker | next action |
|---------|---------|-------------|
| - | - | - |

## Next recommended task

- task_id: `m0-1`
- reason: `M0 has 4 ready tasks (m0-1, m0-2, m0-3, m0-5). m0-1 builds the CMake/vcpkg skeleton; everything else depends on it.`

## Notes for next session

- **Parity task registration completed (this session)**:
  - 12 previously task_missing v1 features now have contract sections + registered tasks: `m1-4` (app command surface + Settings/About windows), `m1-5` (titlebar drag region + accessor seam + toolbar + command buttons), `m2-6` (in-terminal find overlay), `m2-7` (`IPanel` shared abstraction), `m3-6` (panel content router), `m6-5` (notifications page + titlebar popover), `m6-6` (settings window/preferences UI), `m6-7` (terminal clipboard + file-URL shell escaping).
  - `session_info` IPC command folded into `m3-1` acceptance (`tc-session-info`); ADR-0002 added to `m3-1` doc_refs for `pty_mode` exposure.
  - Fixed `m2-4` doc_ref fragment `#13-reattach-token-binding` → `#13-reattach_token-binding` (underscore preserved).
  - Contradiction fixes from the prior contract pass landed: scope enum, command timeout, history filename, retry policy, `session_info`, `IPanel` lifecycle decision (ADR-0004 D5).
  - `_workspace/18-cmux-parity.md` recounted: covered 18→30, missing 28→16 (partial 9 unchanged, total 55); §6 task_missing 12→0 (Backport helpers confirmed out_of_scope).
  - All 8 milestone JSONs pass `Test-Json` against `task-registry.schema.json`.
  - These new tasks sit in gated milestones (M1/M2/M3/M6); current milestone stays `M0` and next recommended task is still `m0-1`.
- **Autonomy structure hardening completed (earlier session)**:
  - `queue_number` is now required in both authority docs and `plans/schema/task-registry.schema.json`.
  - `doc_refs` resolution is normalized: read `active_milestone.doc_refs` first, then `selected_task.doc_refs`; treat `#fragment` as a Markdown heading slug, not part of the file path.
  - `plans/schema/task-registry.schema.json` now allows non-ASCII Markdown heading slugs in `doc_refs` fragments, so Korean section links validate correctly.
  - `_workspace/17-functional-spec.md` and `CONTEXT.md` are now expected in milestone/task `doc_refs` when user-facing behavior or glossary-owned terminology is in scope.
  - `plans/README.md` now makes schema validation part of the operating loop and clarifies `commands` vs `acceptance`.
  - `plans/session-state.md` remains the phase-1 Markdown handoff snapshot; no parallel handoff JSON layer was introduced.
  - `plans/milestones/m7.json` now owns release-only machine-readable backlog state.
- Startup read order: `_workspace/00-overview.md` → `_workspace/12-tasks.md` → `plans/index.json` → `plans/milestones/m0.json` → `plans/session-state.md` → queue rules from `.rules/agent-workflow.md` → merged `doc_refs` (`active_milestone.doc_refs` then `selected_task.doc_refs`). Read `CONTEXT.md` immediately when the task touches canonical terminology or glossary-owned aliases.
- **Plan metadata cleanup completed (this session)**:
  - Every milestone task now has a `queue_number` (see `.rules/agent-workflow.md` queue table).
  - All build targets use canonical names: `cmux_app` / `cmux_cli` (not `cmux-win`).
  - `m5.json` was fully rewritten to restore the missing `m5-2` task (was lost to duplicate-key bug).
  - `m0-4` (ADR freeze), `m0-6` (settings schema), `m0-7` (release prework) marked `done` — outputs already existed.
- **Functional spec created (this session)**:
  - `_workspace/17-functional-spec.md` — comprehensive Windows v1 feature spec covering all 15 domains.
  - Reviewed and corrected by sub-agents: IPC catalog expanded, error codes completed, pipe discovery flow added, env-var rename map documented, cross-window move contradiction resolved, titlebar/backdrop matrix inlined, shortcut JSON schema added, appendix 18 (intentional divergences) added.
  - `.rules/docs-sync.md` updated to reference this file.
- **Milestone quality improvements completed (this session)**:
  - **Area A — acceptance/commands sync**: 11 tasks (m0-5, m1-2, m2-1~m2-3, m2-5, m4-3, m6-1~m6-4) now have matching `ctest --preset dev-x64 -R ...` entries in both `commands` and `acceptance`.
  - **Area B — m3 file-level outputs + tc- tests**: m3-1~m3-4 `outputs` expanded to exact file paths; `commands` populated; acceptance enriched with `tc-*` test cases (total: 14 new tc- cases across 4 tasks).
  - **Area C — m2-4 depends_on**: Fixed `["m2-3"]` → `["m2-1", "m2-2", "m2-3"]` to enforce ConPTY/vterm/D2D ordering.
  - All 8 milestone JSONs validated (JSON parse OK).
- **Hybrid documentation overlay added (this session)**:
  - Root `CONTEXT.md` now owns canonical terminology for window / workspace / pane / surface / panel usage.
  - `.rules/docs-sync.md`, `_workspace/00-overview.md`, and `_workspace/12-tasks.md` now require terminology / naming / ID-rule changes to stay in sync with `CONTEXT.md`.
  - `_workspace/adr/` remains the canonical ADR home; `_workspace/14-adr-guide.md` now favors shorter ADRs for hard-to-reverse trade-offs instead of long boilerplate.
- **Remaining plan quality issues** *(none — all 3 identified issues resolved)*.
