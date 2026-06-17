"""Select the next eligible task. stdlib-only.

Eligibility (two-stage AND, per .rules/agent-workflow.md):
  1. milestone gate: every milestone in the task's milestone transitive
     depends_on closure is `done`;
  2. task-level: task.status == "ready" and every task in depends_on is `done`.
Ordering: active_milestone first, then milestone number, then task number.
"""
from __future__ import annotations

import json
import sys

import repo


def milestone_status_map(index):
    return {m["milestone_id"]: m.get("status") for m in index["milestones"]}


def milestone_deps_map(index):
    return {m["milestone_id"]: list(m.get("depends_on", [])) for m in index["milestones"]}


def gate_ok(mid, mstatus, mdeps):
    seen, stack = set(), list(mdeps.get(mid, []))
    while stack:
        d = stack.pop()
        if d in seen:
            continue
        seen.add(d)
        if mstatus.get(d) != "done":
            return False
        stack.extend(mdeps.get(d, []))
    return True


def _task_num(task_id):
    try:
        return int(task_id.split("-", 1)[1])
    except (IndexError, ValueError):
        return 0


def candidates(index=None, milestones=None):
    index = index if index is not None else repo.load_index()
    milestones = milestones if milestones is not None else repo.all_milestones()
    mstatus = milestone_status_map(index)
    mdeps = milestone_deps_map(index)
    tstatus = {}
    for data in milestones.values():
        for t in data.get("tasks", []):
            tstatus[t["task_id"]] = t["status"]
    active = index.get("active_milestone")
    out = []
    for mid, data in milestones.items():
        if not gate_ok(mid, mstatus, mdeps):
            continue
        for t in data.get("tasks", []):
            if t["status"] != "ready":
                continue
            if all(tstatus.get(d) == "done" for d in t.get("depends_on", [])):
                out.append((mid, t))
    out.sort(key=lambda it: (0 if it[0] == active else 1, int(it[0][1:]), _task_num(it[1]["task_id"])))
    return out


def pick(index=None, milestones=None):
    c = candidates(index, milestones)
    return c[0] if c else (None, None)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    mid, task = pick()
    if task is None:
        print("(no eligible task)")
        return 0
    if "--json" in argv:
        print(json.dumps({
            "milestone": mid,
            "task_id": task["task_id"],
            "title": task["title"],
            "queue_number": task["queue_number"],
            "depends_on": task["depends_on"],
        }, ensure_ascii=False, indent=2))
    else:
        print(task["task_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
