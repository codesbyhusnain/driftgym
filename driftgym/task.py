"""Task definitions.

A task lives in ``tasks/<id>/`` and contains:

    task.toml      metadata (see Task below)
    repo/          the client project as it was before the upgrade (old-API code)
    tests/         visible tests, shown to the agent
    hidden/        hidden tests, never shown; different inputs from the visible ones
    solution/      files that replace repo/ files to give the reference fix
    impossible/    optional: replacement visible tests that contradict the task
                   specification, so passing them is only possible by cheating
    shim.py        optional: code that restores the removed API (used by the
                   scripted "shim" cheater to validate the library-patch detector)
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

TASKS_DIR = Path(__file__).resolve().parent.parent / "tasks"


@dataclass(frozen=True)
class Task:
    id: str
    root: Path
    library: str
    modules: tuple[str, ...]
    old: tuple[str, ...]
    new: tuple[str, ...]
    old_version: str
    new_version: str
    python: str
    tier: int
    change: str
    summary: str
    spec: str
    package: str = "app"
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def repo_dir(self) -> Path:
        return self.root / "repo"

    @property
    def tests_dir(self) -> Path:
        return self.root / "tests"

    @property
    def hidden_dir(self) -> Path:
        return self.root / "hidden"

    @property
    def solution_dir(self) -> Path:
        return self.root / "solution"

    @property
    def impossible_dir(self) -> Path:
        return self.root / "impossible"

    @property
    def has_impossible(self) -> bool:
        return self.impossible_dir.is_dir()

    @property
    def shim_path(self) -> Path:
        return self.root / "shim.py"

    @property
    def has_shim(self) -> bool:
        return self.shim_path.is_file()


def load_task(path: Path | str) -> Task:
    root = Path(path)
    if not root.is_absolute() and not root.exists():
        root = TASKS_DIR / str(path)
    meta = tomllib.loads((root / "task.toml").read_text())
    return Task(
        id=meta["id"],
        root=root.resolve(),
        library=meta["library"],
        modules=tuple(meta.get("modules", [meta["library"]])),
        old=tuple(meta["old"]),
        new=tuple(meta["new"]),
        old_version=meta["old_version"],
        new_version=meta["new_version"],
        python=meta.get("python", "3.11"),
        tier=int(meta["tier"]),
        change=meta["change"],
        summary=meta["summary"],
        spec=meta["spec"].strip(),
        package=meta.get("package", "app"),
        tags=tuple(meta.get("tags", [])),
    )


def load_tasks(selector: str | None = None, tasks_dir: Path = TASKS_DIR) -> list[Task]:
    """Load all tasks, or those whose id contains ``selector`` (comma-separated allowed)."""
    tasks = [load_task(p) for p in sorted(tasks_dir.iterdir()) if (p / "task.toml").is_file()]
    if selector and selector != "all":
        wanted = [s.strip() for s in selector.split(",") if s.strip()]
        tasks = [t for t in tasks if any(w == t.id or w in t.id for w in wanted)]
    return tasks
