"""Golden tests for the cmux-plan harness, run against the committed registry.

stdlib unittest only. Run from the repo root or anywhere:
    python -m unittest discover .claude/skills/cmux-win-autonomous-execution/tests
"""
import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import repo                # noqa: E402
import next_task           # noqa: E402
import build_brief         # noqa: E402
import validate_plans      # noqa: E402
import run_acceptance      # noqa: E402
import update_status       # noqa: E402


class TestNextTask(unittest.TestCase):
    def test_next_is_m0_1(self):
        _mid, task = next_task.pick()
        self.assertIsNotNone(task)
        self.assertEqual(task["task_id"], "m0-1")


class TestValidate(unittest.TestCase):
    def test_zero_semantic_errors(self):
        errors, _warnings = validate_plans.validate()
        self.assertEqual(errors, [], "validate errors:\n" + "\n".join(errors))


class TestBrief(unittest.TestCase):
    def setUp(self):
        self.brief = build_brief.build("m2-2")

    def test_relevant_sections_present(self):
        self.assertIn("11-libvterm-wrapper-api", self.brief)
        self.assertIn("adr-0003", self.brief)

    def test_compact_no_full_spec_dump(self):
        # Full 17-functional-spec is ~1000+ lines; a correct brief never inlines it.
        self.assertLess(len(self.brief.splitlines()), 700)


class TestRunAcceptance(unittest.TestCase):
    def test_not_buildable_graceful(self):
        res = run_acceptance.run("m0-1", execute=True)
        self.assertFalse(res["buildable"])
        self.assertFalse(res["auto_pass"])
        self.assertIn("not-buildable", res["reason"])


class TestUpdateStatusDryRun(unittest.TestCase):
    def test_dry_run_emits_handoff_without_writing(self):
        before = (repo.PLANS / "session-state.md").read_text(encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = update_status.apply("m0-1", "in_progress", dry_run=True)
        out = buf.getvalue()
        after = (repo.PLANS / "session-state.md").read_text(encoding="utf-8")
        self.assertEqual(rc, 0)
        self.assertIn("DRY RUN", out)
        self.assertIn("Next recommended task", out)
        self.assertEqual(before, after, "dry-run must not mutate session-state.md")


class TestAtomicWrite(unittest.TestCase):
    def test_roundtrip(self):
        d = tempfile.mkdtemp()
        p = pathlib.Path(d) / "x.json"
        repo.dump_json_atomic(p, {"a": 1, "b": [1, 2]})
        self.assertEqual(repo.load_json(p), {"a": 1, "b": [1, 2]})


if __name__ == "__main__":
    unittest.main()
