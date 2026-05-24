---
name: cmux-win-autonomous-execution
description: Continue autonomous implementation work in cmux-win using the committed `_workspace`, `plans`, and `.rules` execution model. Use when Codex needs to resume project work, pick the next ready task from `plans/milestones/*.json`, follow the canonical read order, keep docs and task state in sync, and leave a correct handoff in `plans/session-state.md`.
---

# Cmux Win Autonomous Execution

## Overview

Use the repository's autonomous-execution setup exactly as documented. Read the canonical files in order, pick the next eligible task from `plans\`, execute only within allowed write zones, and treat docs-sync plus session handoff as part of done.

## Fast Start

1. Read these files in order:
   - `../../_workspace/00-overview.md`
   - `../../_workspace/12-tasks.md`
   - `../../plans/index.json`
   - the active milestone file from `../../plans/milestones/`
   - `../../plans/session-state.md`
   - `../../.rules/agent-workflow.md`, then the `.rules/*.md` files mapped from the selected task
   - the selected task's `doc_refs`
2. Select the next task with `status = "ready"` whose `depends_on` tasks are all `done`.
3. Set that task to `in_progress` in the milestone JSON and update `../../plans/session-state.md`.
4. Implement the task, run its `commands`, and satisfy every `acceptance` item.
5. Update all required `_workspace` and `plans` docs before ending the session.
6. Mark the task `done` or `blocked`, then leave a fresh handoff in `../../plans/session-state.md`.

## Authority Rules

- `../../_workspace/*.md` is authoritative for architecture, intent, gates, and domain contracts.
- `../../plans/index.json` and `../../plans/milestones/*.json` are authoritative for task status, dependencies, commands, and acceptance.
- `../../.rules/*.md` is authoritative for operating constraints, queue mapping, and docs-sync.
- `../../plans/session-state.md` is the cross-session baton. Never end a session without updating it.

If Markdown and JSON disagree, follow Markdown for contract meaning and JSON for current execution state.

## Task Selection

- Work only from the active milestone unless `plans/index.json` or `session-state.md` clearly advances the milestone.
- Ignore `pending` tasks until their dependencies are `done`.
- Revisit `blocked` tasks only after reading `blocked_by` and `notes`.
- Among multiple eligible tasks, prefer the lowest-numbered `task_id`.

## Before Editing

- Read every file in the task's `doc_refs`.
- Inspect every path in the task's `touches`.
- Confirm the target path is writable under `../../.rules/repository-scope.md`.
- Do not place implementation code under `cmux\`, `ghostty\`, `_workspace\`, or `plans\`.

## While Executing

- Run the task's `commands` when they exist.
- Treat each `acceptance` entry as required. `manual:` entries still must be checked and reflected in `notes` if relevant.
- Keep `_workspace` and `plans` synchronized as you go; implementation is not done until docs-sync is complete.
- Use `.rules/docs-sync.md` every time you touch build/bootstrap, task registry, ADR/gate, IPC, settings, panel lifecycle, or shell integration behavior.

## Session-End Checklist

1. Update the task status in the milestone JSON.
2. Update `../../plans/session-state.md`:
   - current milestone
   - last completed task
   - any active or blocked tasks
   - blocker summary
   - next recommended task
3. Update every required `_workspace` document and `plans` file from `.rules/docs-sync.md`.
4. If you changed `.rules`, update `../../AGENTS.md`.
5. Do not exit with stale state.

## Deep-Dive References

| File | Use |
|------|-----|
| [`../../_workspace/13-autonomous-execution.md`](../../_workspace/13-autonomous-execution.md) | authority model, startup read order, status semantics |
| [`../../plans/index.json`](../../plans/index.json) | milestone registry and machine-readable startup sequence |
| [`../../plans/README.md`](../../plans/README.md) | update rules for the `plans\` layer |
| [`../../.rules/agent-workflow.md`](../../.rules/agent-workflow.md) | queue mapping and autonomous session read order |
| [`../../.rules/docs-sync.md`](../../.rules/docs-sync.md) | mandatory co-update matrix |
| [`../../.rules/repository-scope.md`](../../.rules/repository-scope.md) | writable vs read-only paths and milestone prerequisites |
