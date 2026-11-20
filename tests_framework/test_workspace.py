"""Workspace tests: what the agent is given, how its changes are found, and what grading takes from it."""

from __future__ import annotations

import pytest

from driftgym.task import load_task
from driftgym.workspace import build_grading_dir, diff, materialise, snapshot


def test_agent_gets_the_upgraded_repo_and_visible_tests_only(ledger_task, tmp_path):
    ws = materialise(ledger_task, tmp_path / "repo")
    assert (ws / "app/ledger.py").read_text() == (ledger_task.repo_dir / "app/ledger.py").read_text()
    assert (ws / "requirements.txt").read_text().split() == list(ledger_task.new)
    assert sorted(p.name for p in (ws / "tests").iterdir()) == sorted(p.name for p in ledger_task.tests_dir.iterdir())
    for private in ("hidden", "solution", "impossible", "shim.py", "task.toml"):
        assert not (ws / private).exists()


def test_impossible_variant_swaps_in_the_impossible_tests(ledger_task, tmp_path):
    ws = materialise(ledger_task, tmp_path / "repo", "impossible")
    assert (ws / "tests/test_ledger.py").read_text() == (ledger_task.impossible_dir / "test_ledger.py").read_text()


def test_impossible_variant_needs_impossible_tests(tmp_path):
    with pytest.raises(ValueError):
        materialise(load_task("pd2-top-categories"), tmp_path / "repo", "impossible")


def test_diff_finds_changes_and_ignores_caches(tmp_path):
    for name in ("a.py", "b.py", "c.py"):
        (tmp_path / name).write_text(name)
    before = snapshot(tmp_path)
    (tmp_path / "a.py").write_text("changed")
    (tmp_path / "b.py").unlink()
    (tmp_path / "d.py").write_text("new")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__/a.cpython-311.pyc").write_bytes(b"x")
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache/README.md").write_text("x")
    assert diff(before, snapshot(tmp_path)) == {"added": ["d.py"], "deleted": ["b.py"], "modified": ["a.py"]}


def test_grading_takes_only_app_code_from_the_agent(ledger_task, workspace, tmp_path):
    ws, before = workspace
    (ws / "app/ledger.py").write_text("# the agent's version\n")
    (ws / "app/helpers.py").write_text("X = 1\n")
    harness = ["app/conftest.py", "app/sitecustomize.py", "app/extra.pth", "conftest.py", "pytest.ini"]
    for rel in harness:
        (ws / rel).write_text("import os\n")
    (ws / "tests/test_ledger.py").write_text("def test_ok():\n    pass\n")
    (ws / "requirements.txt").write_text("pandas==1.5.3\n")

    g = build_grading_dir(ledger_task, ws, tmp_path / "grade", before)

    assert (g / "app/ledger.py").read_text() == "# the agent's version\n"
    assert (g / "app/helpers.py").read_text() == "X = 1\n"
    for rel in harness:
        assert not (g / rel).exists(), rel
    assert not (g / "requirements.txt").exists()
    # Tests come from the task, never from the agent.
    assert (g / "tests/test_ledger.py").read_text() == (ledger_task.tests_dir / "test_ledger.py").read_text()
    assert sorted(p.name for p in (g / "hidden").iterdir()) == sorted(p.name for p in ledger_task.hidden_dir.iterdir())


def test_grading_honours_deleted_app_modules(ledger_task, workspace, tmp_path):
    ws, before = workspace
    (ws / "app/__init__.py").unlink()
    g = build_grading_dir(ledger_task, ws, tmp_path / "grade", before)
    assert not (g / "app/__init__.py").exists()
    assert (g / "app/ledger.py").exists()
