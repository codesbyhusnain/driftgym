"""Eval runner: run one model on many episodes and save every finished one.

An eval run is every combination of task, prompt condition (``neutral``,
``pressure``), variant (``standard``, ``impossible``; tasks without an
impossible variant skip it) and sample number. Each combination is one
episode of ``run_episode`` (``driftgym.agents.llm``). Episodes run in
parallel threads (``concurrency``, default 4). Each finished episode is added
to the output file as one JSON line as soon as it ends.

Resuming. A run that stops for any reason (spending cap, API error, Ctrl-C,
crash) keeps every episode it already saved. Running the same command again
skips each (task, condition, variant, sample) already in the file and runs
only the missing ones. A file holds one model: resuming it with another model
or provider is refused, so results never get mixed.

Cost and the spending cap. The caller gives the price of each of the four
token counts the harness records (uncached input, cache read, cache write,
output) in USD per million tokens; nothing here knows any model's price. The
cap (``max_usd``) covers the whole output file, so episodes already saved
count toward it. Before every model request the runner checks the running
total, and once it reaches the cap no new request is sent. Requests already
sent still finish, so the total can pass the cap by at most one request per
thread.

Episodes that do not finish are not saved, so a later run starts them again:

- cut short by the cap or by Ctrl-C (stop reason ``budget``);
- ended by an API error that the SDK's own retries did not clear. The first
  such error also stops the whole run, since it usually means something is
  wrong for every episode (a bad model name, a key without credit, an outage).
  The error is printed.

Their tokens count toward this run's total, but a later run does not know
about them.

Environments. Episodes have no shell tool, so the agent cannot change its
virtualenv (the sandbox lets its tests write only the workspace). Episodes
therefore share DriftGym's cached venvs instead of building one each. They
are built before any thread starts, so two threads never build the same one.
"""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from driftgym.agents.llm import USAGE_KEYS, run_episode
from driftgym.env import CONDITIONS, DriftEnv
from driftgym.envs import ensure_env

VARIANTS = ("standard", "impossible")


def cost(usage: dict, prices: dict[str, float]) -> float:
    """USD for one set of token counts; ``prices`` is USD per million tokens for each of USAGE_KEYS."""
    return sum(usage.get(k, 0) * prices[k] for k in USAGE_KEYS) / 1_000_000


class Budget:
    """The spending cap of one run, shared by all of its threads."""

    def __init__(self, prices: dict[str, float], max_usd: float, spent: float = 0.0):
        self.prices, self.max_usd, self.spent = prices, max_usd, spent
        self.stopped = False  # set on an API error, Ctrl-C or a crash: no new requests either
        self._lock = threading.Lock()

    def add(self, usage: dict) -> None:
        with self._lock:
            self.spent += cost(usage, self.prices)

    @property
    def exhausted(self) -> bool:
        return self.stopped or self.spent >= self.max_usd


def plan(tasks, conditions, variants, samples: int) -> list[tuple]:
    """Every (task, condition, variant, sample) of a run; tasks without an impossible variant skip it."""
    return [
        (t, c, v, s)
        for t in tasks
        for c in conditions
        for v in variants
        for s in range(samples)
        if v == "standard" or t.has_impossible
    ]


def run_eval(
    tasks,
    make_provider,
    out: str | Path,
    *,
    conditions,
    variants,
    samples: int,
    prices: dict[str, float],
    max_usd: float,
    concurrency: int = 4,
    max_steps: int = 40,
    log=print,
) -> dict:
    """Run every planned episode that is not already in ``out``, and return the counts.

    ``make_provider()`` returns a new provider for one episode; the providers
    should share one SDK client.
    """
    for c in conditions:
        if c not in CONDITIONS:
            raise ValueError(f"unknown condition {c!r}; choose from {sorted(CONDITIONS)}")
    for v in variants:
        if v not in VARIANTS:
            raise ValueError(f"unknown variant {v!r}; choose from {list(VARIANTS)}")
    out = Path(out)
    first = make_provider()
    saved = [json.loads(line) for line in out.read_text().splitlines() if line.strip()] if out.exists() else []
    for rec in saved:
        if (rec["provider"], rec["model"]) != (first.name, first.model):
            raise ValueError(
                f"{out} holds results for {rec['provider']} {rec['model']}; "
                f"use another output file for {first.name} {first.model}"
            )
    done = {(r["task_id"], r["condition"], r["variant"], r["sample"]) for r in saved}
    todo = [(t, c, v, s) for t, c, v, s in plan(tasks, conditions, variants, samples) if (t.id, c, v, s) not in done]
    budget = Budget(prices, max_usd, spent=sum(cost(r["usage"], prices) for r in saved))
    log(f"{len(todo)} episodes to run, {len(saved)} already in {out}. "
        f"Spent so far (estimate): ${budget.spent:.2f} of ${max_usd:.2f}")
    if not todo:
        return {"planned": 0, "saved": 0, "cut": 0, "failed": 0, "not_started": 0, "spent_usd": round(budget.spent, 4)}

    for t in {t.id: t for t, *_ in todo}.values():
        ensure_env(t.python, t.new)
    out.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    counts = {"saved": 0, "cut": 0, "failed": 0, "not_started": 0}
    saved_costs = []

    def episode(task, condition, variant, sample):
        if budget.exhausted:
            with lock:
                counts["not_started"] += 1
            return
        env = DriftEnv(task, variant=variant, condition=condition, private_envs=False, max_steps=max_steps)
        rec = run_episode(env, make_provider(), sample=sample, budget=budget)
        name = f"{task.id:28s} {condition:8s} {variant:10s} #{sample}"
        with lock:
            if rec["stop_reason"] == "budget":
                counts["cut"] += 1
                return
            if rec["stop_reason"] == "error":
                counts["failed"] += 1
                budget.stopped = True
                log(f"{name} API error, stopping the run: {rec['error']}")
                return
            with out.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            counts["saved"] += 1
            saved_costs.append(cost(rec["usage"], prices))
            g = rec["grade"]
            log(f"{name} {rec['stop_reason']:13s} solved={g['solved']} "
                f"flags={','.join(sorted(g['flags'])) or '-'} ${saved_costs[-1]:.3f}")

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(episode, *job) for job in todo]
        try:
            for f in as_completed(futures):
                f.result()
        except BaseException:
            # Ctrl-C or a crash: send no new requests, start no new episodes, and let the
            # running ones end at their next request (they are not saved).
            budget.stopped = True
            for f in futures:
                f.cancel()
            log("Stopping: episodes still running end at their next model request and are not saved.")
            raise

    log(f"\nSaved {counts['saved']}, cut short by the cap {counts['cut']}, failed {counts['failed']}, "
        f"not started {counts['not_started']}. Spent (estimate, whole file): ${budget.spent:.2f} of ${max_usd:.2f}")
    if saved_costs:
        log(f"Mean cost per saved episode in this run: ${sum(saved_costs) / len(saved_costs):.3f}")
    if counts["saved"] < len(todo):
        log("Not every episode finished. Run the same command again to run the rest.")
    return {"planned": len(todo), **counts, "spent_usd": round(budget.spent, 4)}
