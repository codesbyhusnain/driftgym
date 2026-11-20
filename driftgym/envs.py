"""Cached Python virtual environments, built with uv.

Each distinct (python version, package pins) set gets one venv under the cache
directory. Grading always uses these pristine cached venvs, so anything an agent
does to its own environment cannot leak into grading.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

CACHE = Path(os.environ.get("DRIFTGYM_CACHE", Path.home() / ".cache" / "driftgym"))
TEST_DEPS = ("pytest==8.3.5",)


class EnvBuildError(RuntimeError):
    pass


def _uv() -> str:
    uv = shutil.which("uv")
    if not uv:
        raise EnvBuildError("uv is required (https://docs.astral.sh/uv/). Install it with: pip install uv")
    return uv


def env_key(python: str, pins: tuple[str, ...] | list[str]) -> str:
    payload = json.dumps({"python": python, "pins": sorted(pins), "test": list(TEST_DEPS)})
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def ensure_env(python: str, pins: tuple[str, ...] | list[str], dest: Path | None = None) -> Path:
    """Return the path of a venv with ``pins`` installed, creating it if needed.

    If ``dest`` is given a fresh, private venv is built there instead (used for
    shell-enabled episodes, where the agent may modify its own environment).
    """
    pins = tuple(pins)
    target = dest or (CACHE / "venvs" / env_key(python, pins))
    marker = target / ".driftgym-ok"
    if marker.exists():
        return target
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    uv = _uv()
    run = lambda args: subprocess.run(args, capture_output=True, text=True)
    r = run([uv, "venv", "--quiet", "--python", python, str(target)])
    if r.returncode != 0:
        raise EnvBuildError(f"uv venv failed for python {python}: {r.stderr.strip()}")
    # Private envs run untrusted code, so copy files rather than hardlinking into uv's cache.
    link = ["--link-mode", "copy"] if dest else []
    r = run([uv, "pip", "install", "--quiet", *link, "--python", str(target / "bin" / "python"), *pins, *TEST_DEPS])
    if r.returncode != 0:
        shutil.rmtree(target, ignore_errors=True)
        raise EnvBuildError(f"install failed for {pins}: {r.stderr.strip()[-2000:]}")
    marker.write_text(json.dumps({"python": python, "pins": list(pins)}))
    return target


def python_bin(venv: Path) -> Path:
    return venv / "bin" / "python"


def python_home(venv: Path) -> Path:
    """The Python installation the venv was built from (the venv's python is a link into it)."""
    return python_bin(venv).resolve().parents[1]
