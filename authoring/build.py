"""Materialise every authored task into tasks/.

    python authoring/build.py            # all groups
    python authoring/build.py pandas2    # one group
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import write  # noqa: E402

GROUPS = ["pandas2", "pandas3", "numpy2", "sqlalchemy2", "pydantic2", "misc"]


def main(argv: list[str]) -> None:
    groups = argv or GROUPS
    n = 0
    for g in groups:
        try:
            mod = importlib.import_module(g)
        except ModuleNotFoundError:
            print(f"skip {g} (not written yet)")
            continue
        for t in mod.TASKS:
            write(t)
            n += 1
        print(f"{g}: {len(mod.TASKS)} tasks")
    print(f"wrote {n} tasks")


if __name__ == "__main__":
    main(sys.argv[1:])
