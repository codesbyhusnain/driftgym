# CLAUDE.md

Read SPEC.md first. It is the source of truth for scope, design decisions and the order of remaining work.

## Commands
- Install: `pip install -e '.[all]'` (needs `uv` on PATH: `pip install uv`)
- Build tasks from authoring files: `python authoring/build.py [group]`
- Validate tasks: `driftgym validate [--tasks prefix]`
- Detector check: `driftgym detector-report --out results/detector.jsonl --md results/detector.md`
- Wrong-fix check for tier-2 tasks: `python authoring/wrong_fixes.py` (writes `results/wrong_fixes.jsonl`)
- Task table: `driftgym list --md results/tasks.md`
- Model run (paid; pilot first): `driftgym eval --provider anthropic --model ID --out results/runs/ID.jsonl --max-usd N --price-in P --price-out P --price-cache-read P --price-cache-write P`
- Results report: `driftgym report results/runs/*.jsonl` (needs `pip install -e '.[report]'`)
- Run one scripted agent: `driftgym run --agent oracle --tasks pd2`
- Framework tests: `pip install -e '.[test]'`, then `pytest`

## Rules
- Verify every breaking change by running the old and new library versions before writing a task. Never author from memory.
- Never weaken or delete a test to make validation pass.
- Keep the clean-room grading design in SPEC.md §3 intact.
- API keys come from environment variables only. Never write them to files that are tracked by git, and never print them.
- No made-up numbers in docs: every figure must come from a file in `results/`.
- Explain every module in plain English in its docstring. The owner reviews all code and must be able to explain it unaided.
- Run a small pilot before any paid model run, and respect `--max-usd`.
