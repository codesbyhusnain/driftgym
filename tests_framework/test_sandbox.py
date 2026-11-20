"""Sandbox tests: code run by the tests cannot get out of the paths it is given.

Each probe below is a test that runs inside a sandboxed pytest run and checks
that one kind of access is refused. The probes only make sense on macOS, the
one system the sandbox supports; elsewhere the sandbox must refuse to run.
"""

from __future__ import annotations

import sys

import pytest
from conftest import write_files

from driftgym import sandbox
from driftgym.runner import run_pytest

macos_only = pytest.mark.skipif(sys.platform != "darwin", reason="the sandbox supports macOS only")

PROBES = '''
import ctypes
import ctypes.util
import os
import socket
import subprocess

import pytest

SECRET = {secret!r}
VENV_BIN = {venv_bin!r}


def test_cannot_read_files_outside():
    with pytest.raises(PermissionError):
        open(SECRET).read()


def test_cannot_list_folders_outside():
    with pytest.raises(PermissionError):
        os.listdir(os.path.dirname(SECRET))


def test_child_processes_are_sandboxed_too():
    assert subprocess.run(["/bin/cat", SECRET], capture_output=True).returncode != 0


def test_cannot_write_the_run_folder():
    with pytest.raises(PermissionError):
        open("written.txt", "w")


def test_cannot_write_the_venv():
    with pytest.raises(PermissionError):
        open(os.path.join(VENV_BIN, "written.txt"), "w")


def test_home_and_tmpdir_are_a_private_writable_folder():
    assert os.environ["HOME"] == os.environ["TMPDIR"]
    with open(os.path.join(os.environ["TMPDIR"], "ok.txt"), "w") as f:
        f.write("ok")


def test_no_network():
    with pytest.raises(PermissionError):
        socket.create_connection(("1.1.1.1", 443), timeout=5)


def test_cannot_read_another_process_arguments_or_environment():
    libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
    mib = (ctypes.c_int * 3)(1, 49, os.getppid())  # CTL_KERN, KERN_PROCARGS2, the process that started pytest
    buf = ctypes.create_string_buffer(1 << 16)
    size = ctypes.c_size_t(1 << 16)
    assert libc.sysctl(mib, 3, buf, ctypes.byref(size), None, 0) == -1
'''


def test_refuses_to_run_where_there_is_no_sandbox(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    with pytest.raises(sandbox.SandboxUnavailable):
        sandbox.wrap(["true"], read=[], write=[])


@macos_only
def test_code_under_test_stays_inside(bare_venv, tmp_path):
    secret = tmp_path / "outside" / "secret.txt"
    secret.parent.mkdir()
    secret.write_text("hidden test or API key")
    run = tmp_path / "run"
    write_files(run, {"tests/test_probes.py": PROBES.format(secret=str(secret), venv_bin=str(bare_venv / "bin"))})
    r = run_pytest(bare_venv, run, ["tests"])
    assert r.total == 8
    assert r.all_passed, r.output


@macos_only
def test_agent_run_may_write_its_workspace(bare_venv, tmp_path):
    write_files(tmp_path, {"tests/test_write.py": "def test_write():\n    open('written.txt', 'w').write('ok')\n"})
    assert run_pytest(bare_venv, tmp_path, ["tests"], hardened=False).all_passed
    assert (tmp_path / "written.txt").read_text() == "ok"
