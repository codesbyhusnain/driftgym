"""Shared fixtures for the framework tests.

These tests check DriftGym itself (detectors, workspaces, the test runner, the
sandbox and grading), not the tasks. Run them with ``pytest`` from the repo
root. Tests that run pytest inside a venv use venvs from DriftGym's cache,
which uv builds the first time they are needed.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from driftgym.envs import ensure_env
from driftgym.task import Task, load_task
from driftgym.workspace import materialise, snapshot


@pytest.fixture
def ledger_task() -> Task:
    return load_task("pd2-ledger-append")


@pytest.fixture
def workspace(tmp_path: Path, ledger_task: Task) -> tuple[Path, dict[str, str]]:
    """A fresh agent workspace for the ledger task, and its snapshot before any change."""
    ws = materialise(ledger_task, tmp_path / "repo")
    return ws, snapshot(ws)


@pytest.fixture(scope="session")
def bare_venv() -> Path:
    """A cached venv with only pytest installed, for runner tests that need no library."""
    return ensure_env("3.11", ())


def write_files(root: Path, files: dict[str, str]) -> None:
    """Write each {relative path: source} under root, removing the source's common indent."""
    for rel, src in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(src).lstrip("\n"))
