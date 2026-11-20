"""CLI tests: results files are replaced on every run, so reruns never double-count."""

from __future__ import annotations

from driftgym.cli import _write_jsonl


def test_rerun_replaces_the_results_file(tmp_path):
    out = tmp_path / "results" / "r.jsonl"
    _write_jsonl(str(out), [{"run": 1}, {"run": 1}])
    _write_jsonl(str(out), [{"run": 2}])
    assert out.read_text().splitlines() == ['{"run": 2}']
