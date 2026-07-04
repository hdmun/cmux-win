"""Golden tests for the cmux-plan harness. stdlib unittest only.

Two kinds of test live here, kept deliberately separate:
  - Logic tests run against a synthetic registry (tmp dir, `repo.ROOT` /
    `repo.PLANS` / `repo.MILESTONES` patched via `_SyntheticRegistry`) so they
    stay green no matter how far the real `plans/` registry has progressed.
  - Live-registry tests run against the committed registry but assert only
    state-invariant properties (validate() == 0 errors; pick()'s result, if
    any, is `ready` with all deps `done`) — never a specific task_id or content.

Run from the repo root or anywhere:
    python -m unittest discover .claude/skills/cmux-win-autonomous-execution/tests
"""
import contextlib
import io
import pathlib
import re
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


def _sample_index():
    return {
        "active_milestone": "m0",
        "milestones": [
            {"milestone_id": "m0", "status": "ready", "depends_on": []},
            {"milestone_id": "m1", "status": "pending", "depends_on": ["m0"]},
        ],
    }


def _sample_task(task_id, status, depends_on=None, **overrides):
    t = {
        "task_id": task_id,
        "queue_number": 3,
        "title": f"Title for {task_id}",
        "status": status,
        "summary": "synthetic fixture task",
        "depends_on": depends_on or [],
        "doc_refs": [],
        "touches": ["a.txt"],
        "acceptance_auto": [],
        "acceptance_manual": [],
        "commands": [],
        "outputs": [],
        "authoritative_rules": [],
        "blocked_by": [],
        "notes": [],
    }
    t.update(overrides)
    return t


def _sample_milestones():
    return {
        "m0": {
            "milestone_id": "m0",
            "doc_refs": [],
            "tasks": [
                _sample_task("m0-1", "ready"),
                _sample_task("m0-2", "pending", depends_on=["m0-1"]),
            ],
        },
        "m1": {
            "milestone_id": "m1",
            "doc_refs": [],
            "tasks": [
                _sample_task("m1-1", "pending"),
            ],
        },
    }


class _SyntheticRegistry(unittest.TestCase):
    """Patches repo.ROOT/PLANS/MILESTONES to a throwaway tmp dir for the
    duration of a test, so logic tests never touch the real registry."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        root = pathlib.Path(self._tmpdir.name)
        (root / "plans" / "milestones").mkdir(parents=True)
        self._orig = (repo.ROOT, repo.PLANS, repo.MILESTONES)
        repo.ROOT, repo.PLANS, repo.MILESTONES = root, root / "plans", root / "plans" / "milestones"

    def tearDown(self):
        repo.ROOT, repo.PLANS, repo.MILESTONES = self._orig
        self._tmpdir.cleanup()

    def write_registry(self, index, milestones):
        repo.dump_json_atomic(repo.PLANS / "index.json", index)
        for mid, data in milestones.items():
            repo.dump_json_atomic(repo.MILESTONES / f"{mid}.json", data)


# ---------------------------------------------------------------------------
# next_task logic (synthetic)
# ---------------------------------------------------------------------------

class TestNextTaskLogic(_SyntheticRegistry):
    def test_picks_ready_task_with_satisfied_deps_over_blocked_ones(self):
        self.write_registry(_sample_index(), _sample_milestones())
        mid, task = next_task.pick()
        self.assertEqual(mid, "m0")
        self.assertEqual(task["task_id"], "m0-1")

    def test_gate_blocks_dependent_milestone_even_if_task_status_says_ready(self):
        index = _sample_index()
        milestones = _sample_milestones()
        # m1's milestone gate (depends_on m0) is not satisfied even though the
        # task itself is marked ready — gate must win.
        milestones["m1"]["tasks"][0]["status"] = "ready"
        self.write_registry(index, milestones)
        mid, task = next_task.pick()
        self.assertEqual(task["task_id"], "m0-1")

    def test_after_dependency_done_next_candidate_becomes_eligible(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["status"] = "done"
        milestones["m0"]["tasks"][1]["status"] = "ready"
        self.write_registry(index, milestones)
        mid, task = next_task.pick()
        self.assertEqual(task["task_id"], "m0-2")

    def test_no_eligible_task_returns_none(self):
        index = _sample_index()
        milestones = _sample_milestones()
        for data in milestones.values():
            for t in data["tasks"]:
                t["status"] = "blocked"
        self.write_registry(index, milestones)
        mid, task = next_task.pick()
        self.assertIsNone(task)


# ---------------------------------------------------------------------------
# validate() semantics (synthetic + live invariant)
# ---------------------------------------------------------------------------

class TestValidateAcceptanceCommandDrift(_SyntheticRegistry):
    """P1-4: a literal (non tc-*) acceptance_auto item must appear in commands."""

    def test_literal_acceptance_missing_from_commands_is_error(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["acceptance_auto"] = ["cmake --build --preset dev-x64"]
        milestones["m0"]["tasks"][0]["commands"] = []
        self.write_registry(index, milestones)
        errors, _warnings = validate_plans.validate()
        self.assertTrue(
            any("not found verbatim in commands" in e for e in errors), errors)

    def test_literal_acceptance_present_in_commands_is_clean(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["acceptance_auto"] = ["cmake --build --preset dev-x64"]
        milestones["m0"]["tasks"][0]["commands"] = ["cmake --build --preset dev-x64"]
        self.write_registry(index, milestones)
        errors, _warnings = validate_plans.validate()
        self.assertEqual(errors, [])

    def test_tc_star_acceptance_is_exempt_from_the_drift_check(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["acceptance_auto"] = ["tc-1"]
        milestones["m0"]["tasks"][0]["commands"] = ["ctest --preset dev-x64 -R tc-1"]
        self.write_registry(index, milestones)
        errors, _warnings = validate_plans.validate()
        self.assertEqual(errors, [])


class TestValidateLiveInvariant(unittest.TestCase):
    def test_zero_semantic_errors(self):
        errors, _warnings = validate_plans.validate()
        self.assertEqual(errors, [], "validate errors:\n" + "\n".join(errors))


class TestNextTaskLiveInvariant(unittest.TestCase):
    def test_pick_result_if_any_is_ready_with_all_deps_done(self):
        mid, task = next_task.pick()
        if task is None:
            return  # no eligible task is itself a valid terminal state
        self.assertEqual(task["status"], "ready")
        for dep in task.get("depends_on", []):
            _dmid, dtask, _ = repo.find_task(dep)
            self.assertIsNotNone(dtask, f"depends_on target '{dep}' not found")
            self.assertEqual(dtask["status"], "done")


# ---------------------------------------------------------------------------
# build_brief slicing + operating-rule merge (synthetic)
# ---------------------------------------------------------------------------

class TestBriefSlicing(_SyntheticRegistry):
    def test_fragment_sliced_and_large_whole_file_collapses_to_heading_index(self):
        index = _sample_index()
        milestones = _sample_milestones()
        (repo.ROOT / "doc-with-headings.md").write_text(
            "# Title\n\n## Section A\n\nbody A\n\n## Section B\n\nbody B\n",
            encoding="utf-8")
        (repo.ROOT / "big-doc.md").write_text(
            "\n".join(f"## H{i}\n\ntext {i}" for i in range(200)), encoding="utf-8")
        milestones["m0"]["tasks"][0]["doc_refs"] = [
            "doc-with-headings.md#section-a", "big-doc.md"]
        self.write_registry(index, milestones)
        brief = build_brief.build("m0-1")
        self.assertIn("section-a", brief)
        self.assertIn("body A", brief)
        self.assertNotIn("body B", brief)  # only the referenced fragment, not the whole file
        self.assertIn("heading index", brief)
        self.assertNotIn("text 199", brief)  # full content never inlined

    def test_authoritative_rules_merged_and_deduped_with_queue_rules(self):
        index = _sample_index()
        milestones = _sample_milestones()
        (repo.ROOT / "extra-rule.md").write_text("# Extra Rule\n\nDo the thing.\n", encoding="utf-8")
        # queue 3 maps to .rules/build-dependencies.md, which does not exist
        # under this synthetic root, so only the authoritative_rules entry
        # should surface — duplicated on purpose to assert dedup.
        milestones["m0"]["tasks"][0]["authoritative_rules"] = ["extra-rule.md", "extra-rule.md"]
        self.write_registry(index, milestones)
        brief = build_brief.build("m0-1")
        self.assertEqual(brief.count("extra-rule.md"), 1)
        self.assertIn("Do the thing.", brief)


def _parse_queue_table(md_text):
    """Return {queue_number: [doc paths]} from the .rules/agent-workflow.md
    queue table's '우선 참조 문서' column."""
    out = {}
    for line in md_text.splitlines():
        m = re.match(r"\|\s*\*\*(\d+)\*\*\s*\|[^|]*\|([^|]*)\|", line)
        if not m:
            continue
        out[int(m.group(1))] = re.findall(r"`([^`]+)`", m.group(2))
    return out


class TestQueueRulesSyncWithAgentWorkflowDoc(unittest.TestCase):
    """P2-5: QUEUE_RULES must mirror the table's AGENTS.md/.rules/*.md paths
    (the table's _workspace/*.md entries are intentionally excluded — those
    reach the brief via sliced doc_refs, not inlined whole)."""

    def test_queue_rules_matches_table_non_workspace_paths(self):
        text = (repo.ROOT / ".rules" / "agent-workflow.md").read_text(encoding="utf-8")
        table = _parse_queue_table(text)
        self.assertTrue(table, "failed to parse the queue table")
        for qnum, paths in table.items():
            expected = [p for p in paths if not p.startswith("_workspace/")]
            actual = build_brief.QUEUE_RULES.get(qnum, [])
            self.assertEqual(actual, expected, f"queue {qnum} rule set drifted from the table")


# ---------------------------------------------------------------------------
# run_acceptance: buildable gate + exit code + pwsh execution (P0-1, P2-7)
# ---------------------------------------------------------------------------

class TestBuildableGate(_SyntheticRegistry):
    def test_no_cmakelists_is_not_buildable(self):
        ok, reason = run_acceptance.buildable([])
        self.assertFalse(ok)
        self.assertIn("no CMakeLists.txt", reason)

    def test_configure_command_unlocks_the_bootstrap_chicken_and_egg(self):
        (repo.ROOT / "CMakeLists.txt").write_text("# stub\n", encoding="utf-8")
        ok, _reason = run_acceptance.buildable(["cmake --preset dev-x64"])
        self.assertTrue(ok)

    def test_build_or_ctest_only_without_configure_stays_blocked(self):
        (repo.ROOT / "CMakeLists.txt").write_text("# stub\n", encoding="utf-8")
        ok, reason = run_acceptance.buildable(
            ["cmake --build --preset dev-x64", "ctest --preset dev-x64"])
        self.assertFalse(ok)
        self.assertIn("not configured", reason)


class TestRunAcceptanceExitCode(_SyntheticRegistry):
    def test_main_returns_1_when_auto_pass_is_false(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["commands"] = ["exit 1"]
        self.write_registry(index, milestones)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run_acceptance.main(["m0-1"])
        self.assertEqual(rc, 1)

    def test_main_returns_0_on_dry_run_regardless_of_commands(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["commands"] = ["exit 1"]
        self.write_registry(index, milestones)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run_acceptance.main(["m0-1", "--dry-run"])
        self.assertEqual(rc, 0)

    def test_main_returns_0_when_auto_pass_is_true(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["commands"] = ["exit 0"]
        self.write_registry(index, milestones)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run_acceptance.main(["m0-1"])
        self.assertEqual(rc, 0)


class TestRunAcceptancePwshExecution(unittest.TestCase):
    class _FakeResult:
        def __init__(self, returncode=0):
            self.returncode = returncode
            self.stdout = ""
            self.stderr = ""

    def setUp(self):
        self._orig_run = run_acceptance.subprocess.run
        self._orig_pwsh = run_acceptance._pwsh_path

    def tearDown(self):
        run_acceptance.subprocess.run = self._orig_run
        run_acceptance._pwsh_path = self._orig_pwsh

    def test_uses_pwsh_when_available(self):
        calls = []
        run_acceptance.subprocess.run = lambda args, **kw: calls.append(args) or self._FakeResult()
        run_acceptance._pwsh_path = lambda: "pwsh"
        _r, warn = run_acceptance._run_command("echo hi")
        self.assertIsNone(warn)
        self.assertEqual(calls[0][0], "pwsh")
        self.assertIn("-NoProfile", calls[0])
        self.assertIn("echo hi", calls[0])

    def test_falls_back_to_shell_when_pwsh_missing(self):
        calls = []

        def fake_run(cmd, shell=False, **kw):
            calls.append((cmd, shell))
            return self._FakeResult()

        run_acceptance.subprocess.run = fake_run
        run_acceptance._pwsh_path = lambda: None
        _r, warn = run_acceptance._run_command("echo hi")
        self.assertIsNotNone(warn)
        self.assertEqual(calls[0], ("echo hi", True))


# ---------------------------------------------------------------------------
# update_status: dry-run handoff, Notes carry-over (P0-2), done warning (P2-6)
# ---------------------------------------------------------------------------

class TestUpdateStatusDryRun(_SyntheticRegistry):
    def test_dry_run_emits_handoff_without_writing(self):
        index = _sample_index()
        milestones = _sample_milestones()
        self.write_registry(index, milestones)
        state_path = repo.PLANS / "session-state.md"
        self.assertFalse(state_path.exists())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = update_status.apply("m0-1", "in_progress", dry_run=True)
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("DRY RUN", out)
        self.assertIn("Next recommended task", out)
        self.assertFalse(state_path.exists(), "dry-run must not write session-state.md")


class TestSessionStateNotesCarryOver(_SyntheticRegistry):
    def test_existing_notes_section_is_preserved(self):
        index = _sample_index()
        milestones = _sample_milestones()
        self.write_registry(index, milestones)
        (repo.PLANS / "session-state.md").write_text(
            "# Session State\n\n## Notes for next session\n\n- keep-me marker\n",
            encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            update_status.apply("m0-1", "in_progress", dry_run=True)
        self.assertIn("keep-me marker", buf.getvalue())

    def test_missing_notes_section_gets_a_placeholder(self):
        index = _sample_index()
        milestones = _sample_milestones()
        self.write_registry(index, milestones)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            update_status.apply("m0-1", "in_progress", dry_run=True)
        self.assertIn("Notes for next session", buf.getvalue())


class TestUpdateStatusDoneWarning(_SyntheticRegistry):
    def test_warns_on_done_transition_when_commands_present(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["commands"] = ["echo hi"]
        self.write_registry(index, milestones)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            update_status.apply("m0-1", "done", dry_run=True)
        self.assertIn("WARNING", buf.getvalue())

    def test_no_warning_when_task_has_no_commands(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["commands"] = []
        self.write_registry(index, milestones)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            update_status.apply("m0-1", "done", dry_run=True)
        self.assertNotIn("WARNING", buf.getvalue())

    def test_no_warning_for_non_done_transitions(self):
        index = _sample_index()
        milestones = _sample_milestones()
        milestones["m0"]["tasks"][0]["commands"] = ["echo hi"]
        self.write_registry(index, milestones)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            update_status.apply("m0-1", "in_progress", dry_run=True)
        self.assertNotIn("WARNING", buf.getvalue())


class TestAtomicWrite(unittest.TestCase):
    def test_roundtrip(self):
        d = tempfile.mkdtemp()
        p = pathlib.Path(d) / "x.json"
        repo.dump_json_atomic(p, {"a": 1, "b": [1, 2]})
        self.assertEqual(repo.load_json(p), {"a": 1, "b": [1, 2]})


if __name__ == "__main__":
    unittest.main()
