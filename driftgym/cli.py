"""Command line interface.

    driftgym list
    driftgym validate [--tasks SEL] [--no-old]
    driftgym run --agent oracle|noop|cheat_* [--tasks SEL] [--variant standard|impossible] [--out FILE]
    driftgym detector-report [--tasks SEL] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

from driftgym.agents import AGENTS, EXPECTED_FLAG
from driftgym.env import DriftEnv
from driftgym.task import load_tasks
from driftgym.validate import validate_task


def _write_jsonl(path: str | None, rows: list[dict]) -> None:
    if not path:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def cmd_list(args) -> int:
    for t in load_tasks(args.tasks):
        imp = " +impossible" if t.has_impossible else ""
        print(f"{t.id:32s} tier {t.tier}  {t.library} {t.old_version} -> {t.new_version}  {t.change}{imp}")
    return 0


def cmd_validate(args) -> int:
    bad = 0
    rows = []
    for t in load_tasks(args.tasks):
        v = validate_task(t, check_old=not args.no_old)
        rows.append(v.to_dict())
        status = "OK  " if v.ok else "FAIL"
        bad += not v.ok
        print(f"{status} {t.id:32s} old={v.old_ok} broken={v.broken} solution={v.solution_ok} impossible={v.impossible_ok}")
        if not v.ok and v.notes:
            print("     " + v.notes.replace("\n", "\n     ")[:3000])
    _write_jsonl(args.out, rows)
    print(f"{len(rows) - bad}/{len(rows)} tasks valid")
    return 1 if bad else 0


def run_scripted(agent: str, task, variant: str = "standard", private_envs: bool = False) -> dict:
    env = DriftEnv(task, variant=variant, private_envs=private_envs)
    env.reset()
    try:
        AGENTS[agent](env)
        g = env.grade()
    finally:
        env.close()
    return {"agent": agent, "variant": variant, **g.to_dict()}


def cmd_run(args) -> int:
    rows = []
    for t in load_tasks(args.tasks):
        if args.variant == "impossible" and not t.has_impossible:
            continue
        start = time.time()
        r = run_scripted(args.agent, t, args.variant, private_envs=args.private_envs)
        rows.append(r)
        flags = ",".join(sorted(r["flags"])) or "-"
        print(f"{t.id:32s} reward={r['reward']:.2f} solved={r['solved']} flags={flags} ({time.time() - start:.1f}s)")
    _write_jsonl(args.out, rows)
    return 0


def cmd_detector_report(args) -> int:
    """Run oracle and every scripted cheat on every task; report catch and false-positive rates."""
    tasks = load_tasks(args.tasks)
    rows = []
    for t in tasks:
        for agent in AGENTS:
            if agent == "cheat_shim" and not t.has_shim:
                continue
            rows.append(run_scripted(agent, t))
            r = rows[-1]
            print(f"{t.id:28s} {agent:20s} reward={r['reward']:.2f} flags={','.join(sorted(r['flags'])) or '-'}")
        if t.has_impossible:
            rows.append(run_scripted("oracle", t, "impossible"))
    _write_jsonl(args.out, rows)

    print("\nCatch rate by cheat (expected flag raised, reward zeroed for hard flags):")
    by = defaultdict(list)
    for r in rows:
        by[(r["agent"], r["variant"])].append(r)
    for (agent, variant), rs in sorted(by.items()):
        if agent in EXPECTED_FLAG:
            exp = EXPECTED_FLAG[agent]
            caught = sum(exp in r["flags"] for r in rs)
            print(f"  {agent:20s} {exp:18s} {caught}/{len(rs)}  mean reward {sum(r['reward'] for r in rs) / len(rs):.2f}")
    orc = by.get(("oracle", "standard"), [])
    if orc:
        fp = sum(bool(r["flags"]) for r in orc)
        print(f"\nOracle (honest fix): solved {sum(r['solved'] for r in orc)}/{len(orc)}, any flag {fp}/{len(orc)}")
    imp = by.get(("oracle", "impossible"), [])
    if imp:
        print(f"Oracle on impossible variants: impossible_pass {sum('impossible_pass' in r['flags'] for r in imp)}/{len(imp)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="driftgym")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list")
    s.add_argument("--tasks", default="all")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("validate")
    s.add_argument("--tasks", default="all")
    s.add_argument("--no-old", action="store_true", help="skip checking the original code on the old version")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("run")
    s.add_argument("--agent", required=True, choices=sorted(AGENTS))
    s.add_argument("--tasks", default="all")
    s.add_argument("--variant", default="standard", choices=["standard", "impossible"])
    s.add_argument("--private-envs", action="store_true")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("detector-report")
    s.add_argument("--tasks", default="all")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_detector_report)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
