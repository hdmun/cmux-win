"""Shared helpers for the cmux-win plan harness. stdlib-only.

Resolves the repo root by walking up to the directory that contains
plans/index.json, then exposes JSON load / atomic-write helpers, task lookup,
doc_refs merge, and the markdown heading-slug machinery used by build_brief
and the validate doc-linter. The slug rule mirrors the existing doc_ref
`#fragment` convention (GitHub-style: lowercase, drop punctuation, spaces ->
hyphens, preserve underscores and non-ASCII letters such as Korean).
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

_HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def find_repo_root(start: str | None = None) -> Path:
    base = Path(start) if start else Path(__file__).resolve()
    for cand in [base, *base.parents]:
        if (cand / "plans" / "index.json").is_file():
            return cand
    raise FileNotFoundError(f"repo root not found (no plans/index.json above {base})")


ROOT = find_repo_root()
PLANS = ROOT / "plans"
MILESTONES = PLANS / "milestones"
WORKSPACE = ROOT / "_workspace"
SCHEMA = PLANS / "schema" / "task-registry.schema.json"


def load_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_atomic(path, text: str) -> None:
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def dump_json_atomic(path, data) -> None:
    _write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_text_atomic(path, text: str) -> None:
    _write_atomic(path, text)


def load_index() -> dict:
    return load_json(PLANS / "index.json")


def load_milestone(mid: str) -> dict:
    return load_json(MILESTONES / f"{mid}.json")


def all_milestones() -> dict:
    return {p.stem: load_json(p) for p in sorted(MILESTONES.glob("m*.json"))}


def find_task(task_id: str):
    """Return (milestone_id, task_dict, milestone_data) or (None, None, None)."""
    for p in sorted(MILESTONES.glob("m*.json")):
        data = load_json(p)
        for t in data.get("tasks", []):
            if t.get("task_id") == task_id:
                return p.stem, t, data
    return None, None, None


def merged_doc_refs(milestone_data: dict, task: dict) -> list:
    """Milestone doc_refs first, then task doc_refs; dedupe keeping first."""
    seen, out = set(), []
    for ref in list(milestone_data.get("doc_refs", [])) + list(task.get("doc_refs", [])):
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


def split_ref(ref: str):
    if "#" in ref:
        path, frag = ref.split("#", 1)
        return path, frag
    return ref, None


def slugify(heading: str) -> str:
    # Mirror GitHub's anchor rule: strip the heading marker, lowercase, drop
    # punctuation, then turn EACH remaining whitespace char into a hyphen
    # (no collapsing) so "a / b" -> "a--b", matching existing doc_ref fragments.
    s = re.sub(r"^#{1,6}\s*", "", heading.strip()).strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s", "-", s.strip())


def headings(md_text: str):
    """Yield (level, title, slug, lineno) for each markdown heading."""
    for i, line in enumerate(md_text.splitlines()):
        m = _HEAD_RE.match(line)
        if m:
            yield len(m.group(1)), m.group(2), slugify(m.group(2)), i


def extract_section(md_text: str, slug: str):
    """Return the section body for the heading whose slug matches, else None."""
    lines = md_text.splitlines()
    start = level = None
    for lvl, _title, hslug, i in headings(md_text):
        if hslug == slug:
            start, level = i, lvl
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = _HEAD_RE.match(lines[j])
        if m and len(m.group(1)) <= level:
            end = j
            break
    return "\n".join(lines[start:end]).rstrip()
