"""Run a task's auto acceptance and report manual items separately. stdlib-only.

`auto_pass` is the machine done-signal: every command in `commands` exits 0.
`acceptance_manual` is returned as `manual_pending` for a batched human/AT pass.
When the project is not configured yet (no CMakeLists.txt / CMakeCache.txt) the
runner reports `buildable=false` gracefully instead of failing.
"""
from __future__ import annotations

import json
import subprocess
import sys

import repo

_BUILD_DIRS = ("build", "out", "cmake-build-debug", "cmake-build-release")


def buildable():
    if not (repo.ROOT / "CMakeLists.txt").is_file():
        return False, "no CMakeLists.txt at repo root"
    for d in _BUILD_DIRS:
        bd = repo.ROOT / d
        if bd.is_dir() and any(bd.glob("**/CMakeCache.txt")):
            return True, ""
    return False, "no CMakeCache.txt under build/out (project not configured)"


def run(task_id, execute=True):
    _mid, task, _ = repo.find_task(task_id)
    if task is None:
        return {"task_id": task_id, "error": "task not found"}
    cmds = task.get("commands", [])
    res = {
        "task_id": task_id,
        "manual_pending": task.get("acceptance_manual", []),
        "command_results": [],
    }
    needs_build = any(("cmake" in c or "ctest" in c) for c in cmds)
    ok, reason = buildable()
    res["buildable"] = ok
    if needs_build and not ok:
        res["auto_pass"] = False
        res["reason"] = f"not-buildable: {reason}"
        return res
    if not execute:
        res["auto_pass"] = None
        res["reason"] = "dry-run (commands not executed)"
        return res
    if not cmds:
        res["auto_pass"] = False
        res["reason"] = "no commands to run"
        return res
    all_ok = True
    for c in cmds:
        r = subprocess.run(c, shell=True, cwd=str(repo.ROOT), capture_output=True, text=True)
        ok_c = r.returncode == 0
        all_ok = all_ok and ok_c
        res["command_results"].append({"command": c, "exit": r.returncode, "ok": ok_c})
    res["auto_pass"] = all_ok
    return res


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: run_acceptance.py <task_id> [--dry-run]")
        return 2
    res = run(argv[0], execute="--dry-run" not in argv)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
