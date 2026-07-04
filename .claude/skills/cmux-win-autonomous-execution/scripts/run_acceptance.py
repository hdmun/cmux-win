"""Run a task's auto acceptance and report manual items separately. stdlib-only.

`auto_pass` is the machine done-signal: every command in `commands` exits 0.
`acceptance_manual` is returned as `manual_pending` for a batched human/AT pass.
When the project is not configured yet (no CMakeLists.txt / CMakeCache.txt) the
runner reports `buildable=false` gracefully instead of failing — unless the
task's own `commands` include a cmake *configure* call (not `cmake --build` /
`ctest`), in which case running it is exactly how the cache gets created
(bootstrap task, chicken-and-egg with the cache-existence check).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys

import repo

_BUILD_DIRS = ("build", "out", "cmake-build-debug", "cmake-build-release")
COMMAND_TIMEOUT_SEC = 600


class _TimedOutResult:
    def __init__(self):
        self.returncode = 1
        self.stdout = ""
        self.stderr = f"timed out after {COMMAND_TIMEOUT_SEC}s"


def _is_configure_cmd(c: str) -> bool:
    return "cmake" in c and "--build" not in c and "ctest" not in c


def _pwsh_path():
    return shutil.which("pwsh")


def _run_command(c: str):
    """Run one command via pwsh (consistent with the registry docs' PowerShell
    examples and validate's Test-Json invocation); fall back to shell=True
    (cmd.exe) with a warning if pwsh is unavailable. Bounded by
    COMMAND_TIMEOUT_SEC so a hung build/test process can't wedge the harness."""
    pwsh = _pwsh_path()
    try:
        if pwsh:
            r = subprocess.run([pwsh, "-NoProfile", "-Command", c],
                                cwd=str(repo.ROOT), capture_output=True, text=True,
                                timeout=COMMAND_TIMEOUT_SEC)
            return r, None
        r = subprocess.run(c, shell=True, cwd=str(repo.ROOT), capture_output=True, text=True,
                            timeout=COMMAND_TIMEOUT_SEC)
        return r, "pwsh not found on PATH; fell back to shell=True (cmd.exe)"
    except subprocess.TimeoutExpired:
        warn = None if pwsh else "pwsh not found on PATH; fell back to shell=True (cmd.exe)"
        return _TimedOutResult(), warn


def buildable(cmds=()):
    if not (repo.ROOT / "CMakeLists.txt").is_file():
        return False, "no CMakeLists.txt at repo root"
    for d in _BUILD_DIRS:
        bd = repo.ROOT / d
        if bd.is_dir() and any(bd.glob("**/CMakeCache.txt")):
            return True, ""
    if any(_is_configure_cmd(c) for c in cmds):
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
    ok, reason = buildable(cmds)
    res["buildable"] = ok
    if not execute:
        res["auto_pass"] = None
        res["reason"] = "dry-run (commands not executed)"
        if needs_build and not ok:
            res["reason"] += f"; note: not-buildable: {reason}"
        return res
    if needs_build and not ok:
        res["auto_pass"] = False
        res["reason"] = f"not-buildable: {reason}"
        return res
    if not cmds:
        res["auto_pass"] = False
        res["reason"] = "no commands to run"
        return res
    all_ok = True
    warning = None
    for c in cmds:
        r, warn = _run_command(c)
        warning = warning or warn
        ok_c = r.returncode == 0
        all_ok = all_ok and ok_c
        entry = {"command": c, "exit": r.returncode, "ok": ok_c}
        if getattr(r, "stderr", ""):
            entry["stderr"] = r.stderr
        res["command_results"].append(entry)
    if warning:
        res["warning"] = warning
    res["auto_pass"] = all_ok
    return res


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: run_acceptance.py <task_id> [--dry-run]")
        return 2
    res = run(argv[0], execute="--dry-run" not in argv)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 1 if res.get("auto_pass") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
