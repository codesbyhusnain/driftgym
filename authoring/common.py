"""Helpers for writing tasks as Python data, then materialising them into tasks/."""

from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "tasks"


def d(text: str) -> str:
    """Dedent and strip a leading newline."""
    return textwrap.dedent(text).lstrip("\n")


def task(
    *,
    id: str,
    library: str,
    old: list[str],
    new: list[str],
    old_version: str,
    new_version: str,
    tier: int,
    change: str,
    summary: str,
    spec: str,
    files: dict[str, str],
    modules: list[str] | None = None,
    python: str = "3.11",
    tags: list[str] | None = None,
) -> dict:
    return dict(
        id=id,
        library=library,
        modules=modules or [library],
        old=old,
        new=new,
        old_version=old_version,
        new_version=new_version,
        tier=tier,
        change=change,
        summary=summary,
        spec=d(spec).strip(),
        files={k: d(v) for k, v in files.items()},
        python=python,
        tags=tags or [],
    )


def _toml_str(s: str) -> str:
    if "\n" in s:
        return '"""\n' + s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"') + '\n"""'
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _toml_list(xs: list[str]) -> str:
    return "[" + ", ".join(_toml_str(x) for x in xs) + "]"


def write(t: dict) -> Path:
    root = TASKS / t["id"]
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    meta = [
        f'id = {_toml_str(t["id"])}',
        f'library = {_toml_str(t["library"])}',
        f'modules = {_toml_list(t["modules"])}',
        f'old = {_toml_list(t["old"])}',
        f'new = {_toml_list(t["new"])}',
        f'old_version = {_toml_str(t["old_version"])}',
        f'new_version = {_toml_str(t["new_version"])}',
        f'python = {_toml_str(t["python"])}',
        f'tier = {t["tier"]}',
        f'change = {_toml_str(t["change"])}',
        f'summary = {_toml_str(t["summary"])}',
        f'tags = {_toml_list(t["tags"])}',
        f'spec = {_toml_str(t["spec"])}',
    ]
    (root / "task.toml").write_text("\n".join(meta) + "\n")
    files = dict(t["files"])
    files.setdefault("repo/app/__init__.py", "")
    files.setdefault("tests/__init__.py", "")
    files.setdefault("hidden/__init__.py", "")
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return root
