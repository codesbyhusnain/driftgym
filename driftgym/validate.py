"""Check that every task is well formed.

For each task:
  old_ok        original code passes visible + hidden tests on the old version
                (skipped if the old version cannot be installed on this Python)
  broken        original code fails the visible tests on the new version
  solution_ok   reference fix passes visible + hidden tests on the new version
  impossible    reference fix fails the impossible tests (they contradict the spec)
"""

from __future__ import annotations

import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from driftgym.envs import EnvBuildError, ensure_env
from driftgym.runner import run_pytest
from driftgym.task import Task
from driftgym.workspace import copy_tree


@dataclass
class Validation:
    task_id: str
    old_ok: bool | None
    broken: bool
    solution_ok: bool
    impossible_ok: bool | None
    notes: str = ""

    @property
    def ok(self) -> bool:
        return (self.old_ok is not False) and self.broken and self.solution_ok and (self.impossible_ok is not False)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ok"] = self.ok
        return d


def _tree(task: Task, dest: Path, with_solution: bool, tests_from: Path | None = None) -> Path:
    copy_tree(task.repo_dir, dest)
    if with_solution:
        copy_tree(task.solution_dir, dest)
    copy_tree(tests_from or task.tests_dir, dest / "tests")
    copy_tree(task.hidden_dir, dest / "hidden")
    return dest


def validate_task(task: Task, check_old: bool = True) -> Validation:
    notes = []
    with tempfile.TemporaryDirectory(prefix=f"driftgym-validate-{task.id}-") as tmp:
        tmp = Path(tmp)
        new_env = ensure_env(task.python, task.new)

        old_ok: bool | None = None
        if check_old:
            try:
                old_env = ensure_env(task.python, task.old)
                d = _tree(task, tmp / "old", with_solution=False)
                r = run_pytest(old_env, d, ["tests", "hidden"])
                old_ok = r.all_passed
                if not old_ok:
                    notes.append(f"old: {len(r.failed)} failed, {len(r.errors)} errors\n{r.output[-1500:]}")
            except EnvBuildError as e:
                notes.append(f"old env unavailable: {str(e)[:200]}")

        d = _tree(task, tmp / "broken", with_solution=False)
        r = run_pytest(new_env, d, ["tests"])
        broken = not r.all_passed
        if not broken:
            notes.append("original code already passes on the new version")

        d = _tree(task, tmp / "solution", with_solution=True)
        r = run_pytest(new_env, d, ["tests", "hidden"])
        solution_ok = r.all_passed
        if not solution_ok:
            notes.append(f"solution: {len(r.failed)} failed, {len(r.errors)} errors\n{r.output[-1500:]}")

        impossible_ok: bool | None = None
        if task.has_impossible:
            d = _tree(task, tmp / "impossible", with_solution=True)
            copy_tree(task.impossible_dir, d / "tests")
            r = run_pytest(new_env, d, ["tests"])
            impossible_ok = not r.all_passed
            if not impossible_ok:
                notes.append("reference fix passes the impossible tests, so they are not impossible")

    return Validation(task.id, old_ok, broken, solution_ok, impossible_ok, "\n".join(notes))
