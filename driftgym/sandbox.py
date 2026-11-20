"""Run untrusted commands inside the operating system's sandbox.

Whenever tests run, the agent's code runs too: during the episode
(``run_tests`` and ``run_command``) and during grading. Without a sandbox that
code has all of the user's rights. It could copy the reference solution or the
hidden tests out of ``tasks/``, change the files grading relies on (``tasks/``,
the cached venvs, the driftgym code itself), read the user's files, read other
programs' command lines and environment variables (which can hold API keys),
or use the network.

``wrap`` runs a command under macOS's built-in sandbox (``sandbox-exec``) with
a profile that denies everything and then allows only:

- reading system files (``/usr``, ``/bin``, ``/System``, ``/dev``, ``/etc``),
  plus the paths the caller lists as readable or writable;
- writing the paths the caller lists as writable;
- starting other programs, which inherit the same limits;
- reading a short list of system settings that Python needs (CPU count,
  OS version and the like).

Everything else is denied: the network, the rest of the disk, information
about other processes, and system services (so the code cannot ask another
app, such as Finder, to act for it). The time zone database is not readable,
so local time is UTC inside the sandbox. Code can still check whether a path
exists anywhere (programs need that to start), but it cannot list folders or
read files outside the allowed paths.

Only macOS is supported for now. On other systems ``wrap`` raises instead of
running agent code unprotected.
"""

from __future__ import annotations

import sys
from pathlib import Path

SANDBOX_EXEC = Path("/usr/bin/sandbox-exec")
SYSTEM_READ = ("/usr", "/bin", "/System", "/dev", "/private/etc")

# System settings (sysctl) that may be read. Others, such as kern.proc.all,
# would list every process on the machine.
SYSCTLS = """
    (sysctl-name-prefix "hw.") (sysctl-name-prefix "machdep.cpu.") (sysctl-name-prefix "kern.os")
    (sysctl-name "kern.version") (sysctl-name "kern.hostname") (sysctl-name "kern.argmax")
    (sysctl-name "kern.maxfilesperproc") (sysctl-name "kern.usrstack64") (sysctl-name "vm.pagesize")
    (sysctl-name "sysctl.proc_translated")
"""


class SandboxUnavailable(RuntimeError):
    pass


def _subpaths(paths) -> str:
    out = []
    for p in paths:
        s = str(Path(p).resolve())  # the sandbox matches real paths, e.g. /private/var rather than /var
        if '"' in s or "\\" in s:
            raise ValueError(f"cannot put this path in a sandbox profile: {s!r}")
        out.append(f'(subpath "{s}")')
    return " ".join(out)


def profile(read: list[Path], write: list[Path]) -> str:
    """The sandbox rules, in Apple's profile language. Later rules override earlier ones."""
    return "\n".join([
        "(version 1)",
        "(deny default)",
        # Start child processes; they stay in this sandbox.
        "(allow process-fork process-exec)",
        # Signals only to processes in this sandbox, and no information about any process but itself:
        # another process's arguments and environment variables can hold secrets such as API keys.
        # ("(target others)" is not enough: it still lets the code read its parent's.)
        "(allow signal (target same-sandbox))",
        "(deny process-info*)",
        "(allow process-info* (target self))",
        f"(allow sysctl-read {SYSCTLS})",
        # Look up file attributes anywhere (needed to start programs and resolve paths),
        # and load code from files that are readable.
        "(allow file-read-metadata)",
        "(allow file-map-executable)",
        # Reading the root folder itself is needed for any program to start.
        f'(allow file-read* (literal "/") {_subpaths([*SYSTEM_READ, *read, *write])})',
        f'(allow file-write* (literal "/dev/null") {_subpaths(write)})',
    ])


def wrap(args: list[str], *, read: list[Path], write: list[Path]) -> list[str]:
    """Return a command that runs ``args`` in the sandbox."""
    if sys.platform != "darwin" or not SANDBOX_EXEC.exists():
        raise SandboxUnavailable(
            "DriftGym runs agent code only inside a sandbox, and the sandbox currently supports macOS only "
            f"(this is {sys.platform})."
        )
    return [str(SANDBOX_EXEC), "-p", profile(read, write), *args]
