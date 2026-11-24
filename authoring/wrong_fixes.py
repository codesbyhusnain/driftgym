"""Check that plausible wrong fixes fail the tests.

On a tier-2 task the obvious fix is wrong or the break is silent. Each entry
below takes the reference fix and undoes one part of it the way a hurried
migration might (for example dropping squared=False instead of switching to
root_mean_squared_error). The task's tests must catch every one: this script
runs the visible and hidden tests on the new library version and writes one
row per entry to results/wrong_fixes.jsonl.

    python authoring/wrong_fixes.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from driftgym.envs import ensure_env  # noqa: E402
from driftgym.runner import run_pytest  # noqa: E402
from driftgym.task import load_task  # noqa: E402
from driftgym.validate import _tree  # noqa: E402

# (task id, what the wrong fix does, solution file, text in the reference fix, replacement)
WRONG_FIXES = [
    ("pd2-stats-loader", "squeeze() without an axis (a one-row file becomes a scalar)", "app/stats.py",
     '.squeeze("columns")', ".squeeze()"),
    ("pd2-region-totals", "fix only the mean; the sum still joins text columns", "app/sales.py",
     'sales.groupby("region")[COLUMNS].sum()', 'sales.groupby("region").sum()'),
    ("pd3-cow-prices", "use .loc but drop the copy, so the caller's catalog changes", "app/pricing.py",
     "    result = catalog.copy()\n    for i, sku", "    result = catalog\n    for i, sku"),
    ("pd3-text-columns", "check is_object_dtype, which the new str dtype fails", "app/text.py",
     "from pandas.api.types import is_string_dtype", "from pandas.api.types import is_object_dtype as is_string_dtype"),
    ("pd3-groupby-apply", "apply with include_groups=False, which drops the team column", "app/teams.py",
     '    ranked = players.sort_values(["team", "points"], ascending=[True, False])\n'
     '    return ranked.groupby("team").head(n).reset_index(drop=True)',
     '    top = players.groupby("team").apply(lambda g: g.nlargest(n, "points"), include_groups=False)\n'
     "    return top.reset_index(drop=True)"),
    ("np2-pixel-promotion", "vectorise without widening the dtype (uint8 still wraps)", "app/pixels.py",
     "np.clip(pixels.astype(np.int32) + amount, 0, 255)", "np.clip(pixels + amount, 0, 255)"),
    ("np2-copy-false", "drop copy=False, so arrays are always copied", "app/matrix.py",
     "np.asarray(data, dtype=np.float64)", "np.array(data, dtype=np.float64)"),
    ("sqla2-autocommit", "commit the insert but not the update", "app/orders.py",
     "def close_order(engine, order_id):\n    with engine.begin()", "def close_order(engine, order_id):\n    with engine.connect()"),
    ("sqla2-rows-select", "use row._mapping for values but keep `field in row`", "app/customers.py",
     "if field in row._mapping", "if field in row"),
    ("pyd2-coercion", "round the quantity instead of dropping the fraction", "app/items.py",
     "return int(value)", "return round(value)"),
    ("pyd2-config-validators", "keep only from_attributes; the old strip and read-only settings are lost", "app/bookings.py",
     "ConfigDict(from_attributes=True, str_strip_whitespace=True, frozen=True)", "ConfigDict(from_attributes=True)"),
    ("nx3-adjacency", "swap in to_numpy_array but keep `*`, now element-wise", "app/graphs.py",
     "(matrix @ matrix)", "(matrix * matrix)"),
    ("skl19-encoder-metrics", "drop squared=False, which returns the MSE", "app/features.py",
     "from sklearn.metrics import root_mean_squared_error", "from sklearn.metrics import mean_squared_error as root_mean_squared_error"),
    ("mm4-schema-defaults", "map default= to load_default instead of dump_default", "app/schemas.py",
     'status = fields.String(dump_default="active")', 'status = fields.String(load_default="active")'),
    ("httpx-wsgi-params", "fix the client but keep params=, which now encodes spaces as +", "app/client.py",
     '    query_string = f"q={quote(str(query), safe=\'\')}&page={page}"\n'
     '    return str(client.build_request("GET", f"/search?{query_string}").url)',
     '    return str(client.build_request("GET", "/search", params={"q": query, "page": page}).url)'),
    ("flask3-catalog-multi", "move to a JSON provider but drop sort_keys = False", "app/encoding.py",
     "    sort_keys = False\n", ""),
]


def check(task_id: str, rel: str, old: str, new: str) -> dict:
    task = load_task(task_id)
    with tempfile.TemporaryDirectory(prefix=f"driftgym-wrongfix-{task_id}-") as tmp:
        tree = _tree(task, Path(tmp) / "t", with_solution=True)
        path = tree / rel
        source = path.read_text()
        if old not in source:
            raise SystemExit(f"{task_id}: the text to replace is not in {rel}")
        path.write_text(source.replace(old, new, 1))
        run = run_pytest(ensure_env(task.python, task.new), tree, ["tests", "hidden"])
    return {"passed": len(run.passed), "failed": len(run.failed) + len(run.errors), "caught": not run.all_passed}


def main() -> None:
    rows = []
    for task_id, what, rel, old, new in WRONG_FIXES:
        rows.append({"task_id": task_id, "wrong_fix": what, **check(task_id, rel, old, new)})
        r = rows[-1]
        print(f"{'caught ' if r['caught'] else 'MISSED '} {task_id:24s} {r['failed']} failing  {what}")
    out = ROOT / "results" / "wrong_fixes.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"{sum(r['caught'] for r in rows)}/{len(rows)} wrong fixes caught; wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
