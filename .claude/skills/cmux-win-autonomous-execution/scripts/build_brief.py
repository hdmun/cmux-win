"""Generate a compact per-task brief from the registry. stdlib-only.

The brief is the only context an implementing session needs to read: the task
fields, the queue-mapped operating rule, and the *sliced* doc_ref sections.
Whole-file doc_refs are dropped when the same file also has #fragment refs, and
large whole-file refs collapse to a heading index so a parser-wrapper task does
not pull all 1000+ lines of the functional spec.
"""
from __future__ import annotations

import sys

import repo

# queue_number -> primary operating rule(s); mirrors .rules/agent-workflow.md table.
QUEUE_RULES = {
    1: ["AGENTS.md", ".rules/docs-sync.md"],
    2: [".rules/repository-scope.md"],
    3: [".rules/build-dependencies.md"],
    4: [".rules/app-bootstrap-threading.md"],
    5: [".rules/terminal-browser-panel.md"],
    6: [".rules/terminal-browser-panel.md"],
    7: [".rules/ipc-contract.md"],
    8: [".rules/shell-integration.md"],
    9: [".rules/settings-persistence.md"],
    10: [".rules/logging-privacy.md", ".rules/notifications-degrade.md"],
    11: [".rules/docs-sync.md"],
}
FULL_INCLUDE_CAP = 120  # whole-file refs longer than this become a heading index


def _bullets(items, indent=""):
    return "\n".join(f"{indent}- {i}" for i in items) if items else f"{indent}- (none)"


def build(task_id: str) -> str:
    mid, task, mdata = repo.find_task(task_id)
    if task is None:
        return f"# Task Brief: {task_id}\n\n(ERROR: task not found)\n"

    refs = repo.merged_doc_refs(mdata, task)
    frags, wholes = {}, []
    for ref in refs:
        path, frag = repo.split_ref(ref)
        if frag:
            frags.setdefault(path, []).append(frag)
        else:
            wholes.append(path)
    wholes = [p for p in dict.fromkeys(wholes) if p not in frags]

    out = [
        f"# Task Brief: {task_id} — {task['title']}",
        f"_milestone {mid} · queue {task['queue_number']} · status {task['status']}_",
        "",
        "## Task",
        f"- summary: {task['summary']}",
        f"- depends_on: {', '.join(task['depends_on']) or '(none)'}",
        "- touches:",
        _bullets(task["touches"], "  "),
        "- outputs:",
        _bullets(task["outputs"], "  "),
        "",
        "## Commands",
        _bullets(task["commands"]),
        "",
        "## Acceptance — auto (gating)",
        _bullets(task["acceptance_auto"]),
        "",
        "## Acceptance — manual (queued, non-gating)",
        _bullets(task["acceptance_manual"]),
        "",
    ]

    for rule in QUEUE_RULES.get(task["queue_number"], []):
        rp = repo.ROOT / rule
        if rp.is_file():
            out.append(f"## Operating rule (queue {task['queue_number']}): {rule}")
            out.append(rp.read_text(encoding="utf-8").rstrip())
            out.append("")

    out.append("## Doc refs")
    for path, fl in frags.items():
        fp = repo.ROOT / path
        text = fp.read_text(encoding="utf-8") if fp.is_file() else ""
        for frag in dict.fromkeys(fl):
            sec = repo.extract_section(text, frag) if text else None
            out.append(f"### {path}#{frag}")
            out.append(sec if sec else f"(ERROR: section '#{frag}' not found in {path})")
            out.append("")
    for path in wholes:
        fp = repo.ROOT / path
        if not fp.is_file():
            out.append(f"### {path}")
            out.append(f"(ERROR: file not found: {path})")
            out.append("")
            continue
        text = fp.read_text(encoding="utf-8")
        n = len(text.splitlines())
        if n <= FULL_INCLUDE_CAP:
            out.append(f"### {path}")
            out.append(text.rstrip())
        else:
            out.append(f"### {path} (heading index — {n} lines; use #fragment refs for detail)")
            out += [f"{'  ' * (lvl - 1)}- #{slug}" for lvl, _t, slug, _i in repo.headings(text)]
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: build_brief.py <task_id>")
        return 2
    sys.stdout.write(build(argv[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
