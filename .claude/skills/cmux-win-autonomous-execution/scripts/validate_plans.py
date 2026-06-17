"""Validate the plan registry: structure (pwsh Test-Json) + semantics. stdlib-only.

Semantic checks (errors unless noted):
  - milestone/task depends_on targets exist
  - no dependency cycles
  - cross-milestone task deps stay within the milestone's transitive gate closure
  - tc-* acceptance has a covering ctest command
  - acceptance_auto carries no `manual:` item
  - every doc_ref path exists and every #fragment resolves to a heading (doc-linter)
  - outputs not covered by touches  -> warning
  - empty acceptance_auto (not machine-verifiable) -> warning
"""
from __future__ import annotations

import subprocess
import sys

import repo
from next_task import milestone_deps_map


def schema_validate():
    """Run pwsh Test-Json per milestone file -> [(name, ok|None, msg)]."""
    results = []
    for p in sorted(repo.MILESTONES.glob("m*.json")):
        cmd = ["pwsh", "-NoProfile", "-Command",
               f"Get-Content -Raw '{p}' | Test-Json -SchemaFile '{repo.SCHEMA}'"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            ok = r.stdout.strip().lower().startswith("true")
            results.append((p.name, ok, (r.stdout or r.stderr).strip()))
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            results.append((p.name, None, f"pwsh unavailable: {e}"))
    return results


def _gate_closure(mid, mdeps):
    seen, stack = set(), list(mdeps.get(mid, []))
    while stack:
        d = stack.pop()
        if d in seen:
            continue
        seen.add(d)
        stack.extend(mdeps.get(d, []))
    return seen


def validate():
    index = repo.load_index()
    milestones = repo.all_milestones()
    errors, warnings = [], []

    tasks, task_mid = {}, {}
    for mid, data in milestones.items():
        for t in data.get("tasks", []):
            tasks[t["task_id"]] = t
            task_mid[t["task_id"]] = mid

    mdeps = milestone_deps_map(index)
    index_mids = set(mdeps)
    for mid, deps in mdeps.items():
        for d in deps:
            if d not in index_mids:
                errors.append(f"{mid}: milestone depends_on '{d}' not in index")

    for tid, t in tasks.items():
        mid = task_mid[tid]
        closure = _gate_closure(mid, mdeps)
        for d in t.get("depends_on", []):
            if d not in tasks:
                errors.append(f"{tid}: depends_on '{d}' does not exist")
                continue
            dmid = task_mid[d]
            if dmid != mid and dmid not in closure:
                errors.append(
                    f"{tid}: cross-milestone dep '{d}' ({dmid}) outside {mid} gate closure {sorted(closure)}")

    # cycle detection (DFS over task deps)
    color = {tid: 0 for tid in tasks}  # 0 white, 1 grey, 2 black

    def dfs(u, path):
        color[u] = 1
        for v in tasks[u].get("depends_on", []):
            if v not in tasks:
                continue
            if color[v] == 1:
                errors.append("dependency cycle: " + " -> ".join(path + [u, v]))
            elif color[v] == 0:
                dfs(v, path + [u])
        color[u] = 2

    for tid in tasks:
        if color[tid] == 0:
            dfs(tid, [])

    for tid, t in tasks.items():
        touches = [x.rstrip("/") for x in t.get("touches", [])]
        for o in t.get("outputs", []):
            if not any(o == x or o.startswith(x + "/") for x in touches):
                warnings.append(f"{tid}: output '{o}' not covered by touches")
        auto = t.get("acceptance_auto", [])
        if any(a.startswith("tc-") for a in auto) and not any("ctest" in c for c in t.get("commands", [])):
            errors.append(f"{tid}: has tc-* acceptance but no ctest in commands")
        for a in auto:
            if a.startswith("manual:"):
                errors.append(f"{tid}: acceptance_auto contains a 'manual:' item")
        if not auto:
            warnings.append(f"{tid}: empty acceptance_auto (not machine-verifiable)")

    def check_refs(owner, reflist):
        for ref in reflist:
            path, frag = repo.split_ref(ref)
            fp = repo.ROOT / path
            if not fp.is_file():
                errors.append(f"{owner}: doc_ref path missing: {path}")
                continue
            if frag and repo.extract_section(fp.read_text(encoding="utf-8"), frag) is None:
                errors.append(f"{owner}: doc_ref fragment unresolved: {path}#{frag}")

    for mid, data in milestones.items():
        check_refs(mid, data.get("doc_refs", []))
    for tid, t in tasks.items():
        check_refs(tid, t.get("doc_refs", []))

    return errors, warnings


def check_task_docs(task_id):
    """Verify a single task's merged doc_refs all resolve (anchor check)."""
    _mid, task, mdata = repo.find_task(task_id)
    if task is None:
        return [f"task not found: {task_id}"]
    errs = []
    for ref in repo.merged_doc_refs(mdata, task):
        path, frag = repo.split_ref(ref)
        fp = repo.ROOT / path
        if not fp.is_file():
            errs.append(f"{task_id}: doc_ref path missing: {path}")
        elif frag and repo.extract_section(fp.read_text(encoding="utf-8"), frag) is None:
            errs.append(f"{task_id}: doc_ref fragment unresolved: {path}#{frag}")
    return errs


def check_docs_main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: cmux_plan.py check-docs <task_id>")
        return 2
    errs = check_task_docs(argv[0])
    for e in errs:
        print(f"  ERROR  {e}")
    if not errs:
        print(f"OK: all doc_refs for {argv[0]} resolve")
    return 1 if errs else 0


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    errors, warnings = validate()
    print("== schema (Test-Json) ==")
    for name, ok, msg in schema_validate():
        tag = "PASS" if ok else ("WARN" if ok is None else "FAIL")
        print(f"  [{tag}] {name}" + (f" — {msg}" if ok is not True else ""))
        if ok is False:
            errors.append(f"schema fail: {name}")
    print(f"== semantic: {len(errors)} error(s), {len(warnings)} warning(s) ==")
    for e in errors:
        print(f"  ERROR  {e}")
    for w in warnings:
        print(f"  warn   {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
