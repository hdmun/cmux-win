"""Set a task status atomically and refresh index + session-state handoff.

Writes go through repo's temp-file + os.replace path so a crash can never leave
a half-written milestone JSON (the failure mode that once lost m5-2). Milestone
rollup is fully recomputed from task status every call (not just promoted): a
milestone is `done` when all its tasks are done, else `ready`/`pending` by gate —
so reopening a task on a done milestone demotes it back, which cascades into
downstream gates; `active_milestone` advances to the lowest non-done milestone
whose gate is satisfied.
"""
from __future__ import annotations

import sys

import repo
import next_task as nt

VALID = ["pending", "ready", "in_progress", "blocked", "done"]


def _recompute_index(index, milestones):
    mdeps = nt.milestone_deps_map(index)
    for m in index["milestones"]:  # m0..m7 order => deps settle before dependents
        mid = m["milestone_id"]
        data = milestones.get(mid)
        if not data:
            continue
        tasks = data.get("tasks", [])
        cur = {x["milestone_id"]: x["status"] for x in index["milestones"]}
        if tasks and all(t["status"] == "done" for t in tasks):
            m["status"] = "done"
        else:
            m["status"] = "ready" if nt.gate_ok(mid, cur, mdeps) else "pending"
    cur = {x["milestone_id"]: x["status"] for x in index["milestones"]}
    nondone = sorted(
        (m["milestone_id"] for m in index["milestones"]
         if m["status"] != "done" and nt.gate_ok(m["milestone_id"], cur, mdeps)),
        key=lambda x: int(x[1:]))
    if nondone:
        index["active_milestone"] = nondone[0]
    return index


def _promote_tasks(index, milestones):
    """Flip non-terminal tasks pending<->ready by gate+deps, so the loop never
    stalls once a milestone opens. Returns the set of milestone ids changed."""
    mstatus = {m["milestone_id"]: m["status"] for m in index["milestones"]}
    mdeps = nt.milestone_deps_map(index)
    tstatus = {t["task_id"]: t["status"]
               for data in milestones.values() for t in data.get("tasks", [])}
    changed = set()
    for mid, data in milestones.items():
        gate = nt.gate_ok(mid, mstatus, mdeps)
        for t in data.get("tasks", []):
            if t["status"] in ("done", "in_progress", "blocked"):
                continue
            startable = gate and all(tstatus.get(d) == "done" for d in t.get("depends_on", []))
            new = "ready" if startable else "pending"
            if t["status"] != new:
                t["status"] = new
                changed.add(mid)
    return changed


def _render_session_state(index, milestones, last_done, previous_text=None):
    active = index.get("active_milestone")
    inprog, blocked = [], []
    for data in milestones.values():
        for t in data.get("tasks", []):
            if t["status"] == "in_progress":
                inprog.append(t["task_id"])
            elif t["status"] == "blocked":
                blocked.append((t["task_id"], t.get("blocked_by", []), t.get("notes", [])))
    _nmid, ntask = nt.pick(index, milestones)
    L = ["# Session State", "",
         "> 세션 간 handoff snapshot. 최소 상태만 유지한다. 변경 이력은 git에 남긴다.", "",
         "## Current milestone", "",
         f"- milestone: `{active}`",
         f"- active_task_ids: `{inprog or []}`", "",
         "## Last completed task", "",
         f"- task_id: `{last_done or '-'}`", "",
         "## Blocked tasks", "",
         "| task_id | blocked_by | notes |",
         "|---------|-----------|-------|"]
    if blocked:
        for tid, bb, notes in blocked:
            L.append(f"| {tid} | {', '.join(bb) or '-'} | {notes[0] if notes else '-'} |")
    else:
        L.append("| - | - | - |")
    L += ["", "## Next recommended task", ""]
    if ntask:
        L += [f"- task_id: `{ntask['task_id']}`",
              "- reason: `status ready, deps done, milestone gate satisfied`"]
    else:
        L += ["- task_id: `-`", "- reason: `no eligible task`"]
    L.append("")
    notes = repo.extract_section(previous_text, "notes-for-next-session") if previous_text else None
    L.append(notes if notes else "## Notes for next session\n\n(none)")
    return "\n".join(L).rstrip() + "\n"


def apply(task_id, status, dry_run=False):
    if status not in VALID:
        print(f"invalid status '{status}'; choose from {VALID}")
        return 2
    mid, task, mdata = repo.find_task(task_id)
    if task is None:
        print(f"task not found: {task_id}")
        return 2
    task["status"] = status
    milestones = repo.all_milestones()
    milestones[mid] = mdata  # use the mutated copy
    index = _recompute_index(repo.load_index(), milestones)
    changed = _promote_tasks(index, milestones)
    changed.add(mid)
    last_done = task_id if status == "done" else None
    state_path = repo.PLANS / "session-state.md"
    previous_text = state_path.read_text(encoding="utf-8") if state_path.is_file() else None
    session_text = _render_session_state(index, milestones, last_done, previous_text)
    warn = None
    if status == "done" and task.get("commands"):
        warn = f"WARNING: {task_id} -> done — confirm `cmux-plan verify {task_id}` reported auto_pass=true before this transition."
    if dry_run:
        print("DRY RUN — no files written")
        print(f"would set {task_id} -> {status}")
        print(f"active_milestone -> {index['active_milestone']}")
        print(f"milestone files that would change: {sorted(changed)}")
        if warn:
            print(warn)
        print("--- session-state.md ---")
        print(session_text)
        return 0
    for cmid in sorted(changed):
        repo.dump_json_atomic(repo.MILESTONES / f"{cmid}.json", milestones[cmid])
    repo.dump_json_atomic(repo.PLANS / "index.json", index)
    repo.write_text_atomic(repo.PLANS / "session-state.md", session_text)
    print(f"set {task_id} -> {status}; active_milestone={index['active_milestone']}; changed={sorted(changed)}")
    if warn:
        print(warn)
    return 0


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    pos = [a for a in argv if not a.startswith("--")]
    if len(pos) < 2:
        print("usage: update_status.py <task_id> <status> [--dry-run]")
        return 2
    return apply(pos[0], pos[1], dry_run="--dry-run" in argv)


if __name__ == "__main__":
    raise SystemExit(main())
