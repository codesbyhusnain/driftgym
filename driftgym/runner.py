"""Run pytest inside a venv and collect per-test outcomes."""

from __future__ import annotations

import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from driftgym.envs import python_bin

DEFAULT_TIMEOUT = 180


@dataclass
class TestRun:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    output: str = ""
    returncode: int = 0
    timed_out: bool = False

    @property
    def total(self) -> int:
        return len(self.passed) + len(self.failed) + len(self.errors) + len(self.skipped)

    @property
    def all_passed(self) -> bool:
        return self.total > 0 and not self.failed and not self.errors and not self.skipped

    @property
    def pass_fraction(self) -> float:
        return len(self.passed) / self.total if self.total else 0.0

    def to_dict(self) -> dict:
        return {
            "passed": len(self.passed),
            "failed": len(self.failed),
            "errors": len(self.errors),
            "skipped": len(self.skipped),
            "timed_out": self.timed_out,
        }


def run_pytest(
    venv: Path,
    cwd: Path,
    paths: list[str],
    *,
    hardened: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
    extra_env: dict[str, str] | None = None,
) -> TestRun:
    """Run pytest on ``paths`` (relative to ``cwd``).

    ``hardened`` is used for grading: conftest files, ini files and the cache
    are ignored so nothing in the directory can change how tests run.
    The non-hardened mode is what the agent gets: a normal pytest run that
    honours whatever is in its workspace, as a real CI job would.
    """
    with tempfile.TemporaryDirectory(prefix="driftgym-junit-") as tmp:
        junit = Path(tmp) / "junit.xml"
        args = [str(python_bin(venv)), "-m", "pytest", "-q", "-rN", f"--junitxml={junit}"]
        if hardened:
            ini = Path(tmp) / "pytest.ini"
            ini.write_text("[pytest]\n")
            args += ["-c", str(ini), "--rootdir", str(cwd), "--noconftest", "-p", "no:cacheprovider"]
        args += paths
        env = {
            "PATH": f"{venv / 'bin'}:/usr/bin:/bin",
            "HOME": os.environ.get("HOME", "/tmp"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": str(cwd),
            "LC_ALL": "C.UTF-8",
        }
        if extra_env:
            env.update(extra_env)
        try:
            proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or "") if isinstance(e.stdout, str) else ""
            return TestRun(output=out + "\n[driftgym] test run timed out", returncode=-1, timed_out=True)
        run = TestRun(output=(proc.stdout + proc.stderr), returncode=proc.returncode)
        if junit.exists():
            _parse_junit(junit, run)
        elif proc.returncode != 0:
            run.errors.append("<collection>")
        return run


def _parse_junit(path: Path, run: TestRun) -> None:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        run.errors.append("<junit-parse>")
        return
    for case in root.iter("testcase"):
        name = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("failure") is not None:
            run.failed.append(name)
        elif case.find("error") is not None:
            run.errors.append(name)
        elif case.find("skipped") is not None:
            run.skipped.append(name)
        else:
            run.passed.append(name)
    # Collection errors are reported as <error> on a testcase or as suite-level errors.
    for suite in root.iter("testsuite"):
        if int(suite.get("errors", "0")) and not run.errors and not run.failed and not run.passed:
            run.errors.append("<collection>")
