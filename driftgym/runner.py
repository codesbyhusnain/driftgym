"""Run pytest inside a venv, in the sandbox, and collect per-test outcomes."""

from __future__ import annotations

import secrets
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from driftgym import sandbox
from driftgym.envs import python_bin, python_home

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
    # True if the canary test was reported as failing; False if it was reported any other way,
    # or was missing while other tests passed; None if there was no canary or nothing to judge.
    canary_ok: bool | None = None

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
    canary: bool = False,
) -> TestRun:
    """Run pytest on ``paths`` (relative to ``cwd``).

    ``hardened`` is used for grading: conftest files, ini files and the cache
    are ignored so nothing in the directory can change how tests run.
    The non-hardened mode is what the agent gets: a normal pytest run that
    honours whatever is in its workspace, as a real CI job would.

    ``canary`` is also for grading. The agent's code runs inside the pytest
    process, so it could rewrite the results file or flip test outcomes. To
    catch that, a test with a random name that always fails is put in the
    first of ``paths`` (a directory) for this run only. If the results do not
    show it failing, ``canary_ok`` is False and the results cannot be trusted.
    A run that stops before the canary executes (e.g. broken app code makes
    collection fail) only counts as tampering if it still reports passes.

    Every run is sandboxed (see ``driftgym.sandbox``). Tests can read the venv,
    its Python and ``cwd``, and write only a private temporary folder, which is
    also their HOME and TMPDIR. In the non-hardened mode they may also write
    ``cwd`` (the agent's own workspace); grading runs cannot change it.
    """
    with tempfile.TemporaryDirectory(prefix="driftgym-junit-") as tmp:
        junit = Path(tmp) / "junit.xml"
        args = [str(python_bin(venv)), "-m", "pytest", "-q", "-rN", f"--junitxml={junit}"]
        if hardened:
            ini = Path(tmp) / "pytest.ini"
            ini.write_text("[pytest]\n")
            # --confcutdir stops pytest looking at folders above cwd, which the sandbox hides. It must be the
            # real path (e.g. /private/var, not /var), because that is the path pytest sees as its cwd.
            root = str(cwd.resolve())
            args += ["-c", str(ini), "--rootdir", root, "--confcutdir", root, "--noconftest", "-p", "no:cacheprovider"]
        args += paths
        writable = [Path(tmp)] if hardened else [Path(tmp), cwd]
        args = sandbox.wrap(args, read=[venv, python_home(venv), cwd], write=writable)
        env = {
            "PATH": f"{venv / 'bin'}:/usr/bin:/bin",
            "HOME": tmp,
            "TMPDIR": tmp,
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": str(cwd),
            "LC_ALL": "C.UTF-8",
        }
        if extra_env:
            env.update(extra_env)
        canary_name = None
        if canary:
            canary_name = f"test_{secrets.token_hex(8)}"
            canary_file = cwd / paths[0] / f"{canary_name}.py"
            canary_file.write_text(f"def {canary_name}():\n    assert False\n")
        try:
            proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or "") if isinstance(e.stdout, str) else ""
            return TestRun(output=out + "\n[driftgym] test run timed out", returncode=-1, timed_out=True)
        finally:
            if canary_name:
                canary_file.unlink(missing_ok=True)
        run = TestRun(output=(proc.stdout + proc.stderr), returncode=proc.returncode)
        if junit.exists():
            _parse_junit(junit, run, canary_name)
        elif proc.returncode != 0:
            run.errors.append("<collection>")
        return run


def _parse_junit(path: Path, run: TestRun, canary: str | None = None) -> None:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        run.errors.append("<junit-parse>")
        return
    canary_seen: list[bool] = []  # one entry per report of the canary: was it a failure?
    for case in root.iter("testcase"):
        name = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("failure") is not None:
            bucket = run.failed
        elif case.find("error") is not None:
            bucket = run.errors
        elif case.find("skipped") is not None:
            bucket = run.skipped
        else:
            bucket = run.passed
        if canary and case.get("name") == canary:
            # The canary is a check on the results, not one of the task's tests: keep it out of the counts.
            canary_seen.append(bucket is run.failed)
            continue
        bucket.append(name)
    if canary and canary_seen:
        run.canary_ok = canary_seen == [True]
    elif canary and run.passed:
        run.canary_ok = False  # passes reported, but the canary is missing
    # Canary missing and nothing passed: the run stopped early, and nothing was gained.
    # Collection errors are reported as <error> on a testcase or as suite-level errors.
    for suite in root.iter("testsuite"):
        if int(suite.get("errors", "0")) and not run.errors and not run.failed and not run.passed:
            run.errors.append("<collection>")
