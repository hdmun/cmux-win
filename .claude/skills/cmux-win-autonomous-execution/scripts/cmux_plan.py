"""cmux-plan: the harness CLI dispatcher. stdlib-only.

Usage:
  python cmux_plan.py next [--json]
  python cmux_plan.py brief <task_id>
  python cmux_plan.py validate
  python cmux_plan.py check-docs <task_id>
  python cmux_plan.py verify <task_id> [--dry-run]
  python cmux_plan.py status <task_id> <state> [--dry-run]
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import next_task          # noqa: E402
import build_brief        # noqa: E402
import validate_plans     # noqa: E402
import run_acceptance     # noqa: E402
import update_status      # noqa: E402

USAGE = __doc__

_COMMANDS = {
    "next": next_task.main,
    "brief": build_brief.main,
    "validate": validate_plans.main,
    "check-docs": validate_plans.check_docs_main,
    "verify": run_acceptance.main,
    "status": update_status.main,
}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    cmd, rest = argv[0], argv[1:]
    handler = _COMMANDS.get(cmd)
    if handler is None:
        print(f"unknown command: {cmd}\n{USAGE}")
        return 2
    return handler(rest)


if __name__ == "__main__":
    raise SystemExit(main())
