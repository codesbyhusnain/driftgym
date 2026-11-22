"""Eval-runner tests, with no network and no API key.

A stand-in model plays every episode from a short fixed script (for example:
list the files, then submit), and each of its requests is billed as one
million uncached input tokens, which costs $1 at the test prices. The tests
check what gets saved, that a rerun resumes the file, that the spending cap
stops new requests, that an API error stops the run, and that the CLI passes
its arguments through.
"""

from __future__ import annotations

import json

import pytest

from driftgym.agents import llm
from driftgym.agents.llm import ToolCall, Turn
from driftgym.cli import main
from driftgym.eval import cost, plan, run_eval
from driftgym.task import load_tasks

PRICES = {"input": 1.0, "cache_read": 0.0, "cache_write": 0.0, "output": 0.0}  # USD per million tokens
DOLLAR = {"input": 1_000_000}  # usage of one request: $1 at PRICES


class ScriptedProvider:
    """A stand-in model that plays one episode from a list of tool names (an exception in it is raised)."""

    name = "fake"
    errors = (RuntimeError,)

    def __init__(self, model="fake-model", client=None, script=("submit",)):
        self.model, self.client, self.script = model, client, list(script)

    def settings(self):
        return {}

    def start(self, system, prompt, tools):
        pass

    def send(self):
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return Turn([ToolCall("c", step, {})], "tool_use", dict(DOLLAR))

    def add_results(self, results):
        pass

    def transcript(self):
        return []


def _run(out, *, script=("submit",), samples=1, max_usd=100.0, concurrency=1, model="fake-model", **kw):
    lines = []
    r = run_eval(
        load_tasks("pd2-ledger-append"),
        lambda: ScriptedProvider(model, script=script),
        out,
        conditions=["neutral"],
        variants=["standard"],
        samples=samples,
        prices=PRICES,
        max_usd=max_usd,
        concurrency=concurrency,
        log=lines.append,
        **kw,
    )
    return r, lines


def _rows(out):
    return [json.loads(line) for line in out.read_text().splitlines()] if out.exists() else []


def test_cost_uses_the_price_of_each_token_count():
    prices = {"input": 3.0, "cache_read": 0.3, "cache_write": 3.75, "output": 15.0}
    usage = {"input": 2_000_000, "cache_read": 10_000_000, "cache_write": 1_000_000, "output": 100_000}
    assert cost(usage, prices) == pytest.approx(6.0 + 3.0 + 3.75 + 1.5)


def test_plan_skips_the_impossible_variant_of_tasks_without_one():
    tasks = load_tasks("pd2")
    jobs = plan(tasks, ["neutral", "pressure"], ["standard", "impossible"], 2)
    with_impossible = sum(t.has_impossible for t in tasks)
    assert len(jobs) == len(tasks) * 2 * 2 + with_impossible * 2 * 2
    assert all(t.has_impossible for t, _, v, _ in jobs if v == "impossible")


def test_episodes_are_saved_and_a_rerun_runs_only_the_missing_ones(tmp_path):
    out = tmp_path / "runs" / "fake.jsonl"
    r, _ = _run(out, samples=2, concurrency=2)
    assert (r["planned"], r["saved"]) == (2, 2)
    assert sorted(row["sample"] for row in _rows(out)) == [0, 1]

    r, lines = _run(out, samples=3)
    assert (r["planned"], r["saved"]) == (1, 1)
    assert "1 episodes to run, 2 already in" in lines[0]
    rows = _rows(out)
    assert sorted(row["sample"] for row in rows) == [0, 1, 2]
    assert r["spent_usd"] == 3.0  # the two saved earlier count toward the cap
    assert all(row["model"] == "fake-model" and row["grade"]["task_id"] == "pd2-ledger-append" for row in rows)


def test_spending_cap_stops_new_requests_and_cut_episodes_are_not_saved(tmp_path):
    out = tmp_path / "fake.jsonl"
    # Each episode makes 3 requests at $1. The first ends at $3; the second sends one request
    # ($4, the cap), is cut before its next one and is not saved; the third never starts.
    r, lines = _run(out, script=("list_files", "list_files", "submit"), samples=3, max_usd=4.0)
    assert (r["saved"], r["cut"], r["not_started"], r["spent_usd"]) == (1, 1, 1, 4.0)
    assert [row["sample"] for row in _rows(out)] == [0]
    assert "Run the same command again" in lines[-1]


def test_api_error_stops_the_run_and_is_not_saved(tmp_path):
    out = tmp_path / "fake.jsonl"
    r, lines = _run(out, script=(RuntimeError("model not found"),), samples=2)
    assert (r["saved"], r["failed"], r["not_started"]) == (0, 1, 1)
    assert not out.exists()
    assert any("API error, stopping the run: RuntimeError: model not found" in line for line in lines)


def test_a_results_file_holds_one_model(tmp_path):
    out = tmp_path / "fake.jsonl"
    _run(out)
    with pytest.raises(ValueError, match="holds results for fake fake-model"):
        _run(out, model="other-model")


def test_unknown_condition_is_refused_before_anything_runs(tmp_path):
    with pytest.raises(ValueError, match="unknown condition"):
        run_eval(load_tasks("pd2-ledger-append"), ScriptedProvider, tmp_path / "x.jsonl", conditions=["calm"],
                 variants=["standard"], samples=1, prices=PRICES, max_usd=1.0)


def test_cli_runs_an_eval(tmp_path, monkeypatch, capsys):
    monkeypatch.setitem(llm.PROVIDERS, "fake", ScriptedProvider)
    out = tmp_path / "fake.jsonl"
    code = main([
        "eval", "--provider", "fake", "--model", "fake-model", "--out", str(out), "--max-usd", "5",
        "--price-in", "1", "--price-out", "0", "--price-cache-read", "0", "--price-cache-write", "0",
        "--tasks", "pd2-ledger-append", "--conditions", "pressure", "--variants", "standard", "--samples", "1",
    ])
    assert code == 0
    (row,) = _rows(out)
    assert (row["condition"], row["stop_reason"]) == ("pressure", "submit")
    assert "Spent (estimate, whole file): $1.00 of $5.00" in capsys.readouterr().out
