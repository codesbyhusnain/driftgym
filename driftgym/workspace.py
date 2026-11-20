"""Build agent workspaces and grading directories, and snapshot file trees."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from driftgym.task import Task

IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".venv"}
# Files that can change how pytest or the interpreter behaves. Never carried into grading.
HARNESS_FILES = {
    "conftest.py",
    "pytest.ini",
    "tox.ini",
    "setup.cfg",
    "pyproject.toml",
    "sitecustomize.py",
    "usercustomize.py",
}


def _ignored(rel: Path) -> bool:
    return any(p in IGNORED_PARTS for p in rel.parts) or rel.suffix == ".pyc"


def copy_tree(src: Path, dst: Path) -> None:
    for f in sorted(src.rglob("*")):
        rel = f.relative_to(src)
        if _ignored(rel) or f.is_dir():
            continue
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)


def requirements_text(task: Task) -> str:
    return "\n".join(task.new) + "\n"


def materialise(task: Task, dest: Path, variant: str = "standard") -> Path:
    """Create the workspace the agent sees: the client repo after the upgrade."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    copy_tree(task.repo_dir, dest)
    (dest / "requirements.txt").write_text(requirements_text(task))
    copy_tree(task.tests_dir, dest / "tests")
    if variant == "impossible":
        if not task.has_impossible:
            raise ValueError(f"task {task.id} has no impossible variant")
        copy_tree(task.impossible_dir, dest / "tests")
    return dest


def snapshot(root: Path) -> dict[str, str]:
    snap: dict[str, str] = {}
    for f in sorted(root.rglob("*")):
        rel = f.relative_to(root)
        if f.is_dir() or _ignored(rel):
            continue
        try:
            snap[rel.as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
        except OSError:
            continue
    return snap


def diff(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    return {
        "added": sorted(set(after) - set(before)),
        "deleted": sorted(set(before) - set(after)),
        "modified": sorted(p for p in set(before) & set(after) if before[p] != after[p]),
    }


def build_grading_dir(task: Task, workspace: Path, dest: Path, before: dict[str, str]) -> Path:
    """Pristine repo + the agent's application code + pristine visible and hidden tests.

    Only files inside the application package are taken from the agent. Harness
    files (conftest.py, sitecustomize.py, ini files) and .pth files are dropped,
    tests come from the task definition, and requirements are ignored because
    grading runs in a clean environment built from the task's pins.
    """
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    copy_tree(task.repo_dir, dest)
    pkg = workspace / task.package
    after = snapshot(workspace)
    # Honour deletions of application modules.
    for rel in set(before) - set(after):
        if rel.startswith(f"{task.package}/"):
            (dest / rel).unlink(missing_ok=True)
    if pkg.is_dir():
        for f in sorted(pkg.rglob("*")):
            rel = f.relative_to(workspace)
            if f.is_dir() or _ignored(rel):
                continue
            if f.name in HARNESS_FILES or f.suffix == ".pth":
                continue
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)
    copy_tree(task.tests_dir, dest / "tests")
    copy_tree(task.hidden_dir, dest / "hidden")
    return dest
