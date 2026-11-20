"""Model-agent tests, with no network and no API key.

The loop tests use a stand-in provider that replays fixed turns, and check when
an episode stops and what its record holds. The provider tests give the real
Anthropic and OpenAI providers fake clients that return real SDK response
objects, and check the requests they send and how they read the replies.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from driftgym.agents.llm import SYSTEM_PROMPT, AnthropicProvider, OpenAIProvider, ToolCall, Turn, run_episode
from driftgym.env import DriftEnv


def turn(*calls, stop="tool_use", tokens=10):
    """A model turn asking for the given (tool, args) calls."""
    tool_calls = [ToolCall(f"call_{i}", name, args) for i, (name, args) in enumerate(calls)]
    return Turn(tool_calls, stop, {"input": tokens, "cache_read": 0, "cache_write": 0, "output": tokens})


class ReplayProvider:
    """A stand-in model that replays a fixed list of turns (an exception in the list is raised)."""

    name, model = "replay", "replay-model"
    errors = (RuntimeError,)

    def __init__(self, turns):
        self.turns = list(turns)
        self.results = []  # what the harness sent back after each turn: [(tool, output, is_error), ...]

    def settings(self):
        return {}

    def start(self, system, prompt, tools):
        self.system, self.prompt, self.tools = system, prompt, tools

    def send(self):
        t = self.turns.pop(0)
        if isinstance(t, Exception):
            raise t
        return t

    def add_results(self, results):
        self.results.append([(call.name, out, err) for call, out, err in results])

    def transcript(self):
        return []


def _env(task, **kw):
    return DriftEnv(task, private_envs=False, **kw)


def _solution_writes(task):
    sol = task.solution_dir
    return [("write_file", {"path": f.relative_to(sol).as_posix(), "content": f.read_text()}) for f in sol.rglob("*.py")]


# --- the loop ---------------------------------------------------------------------------


def test_honest_episode_is_recorded_and_graded(ledger_task):
    provider = ReplayProvider([
        turn(("read_file", {"path": "app/ledger.py"})),
        turn(*_solution_writes(ledger_task), ("run_tests", {})),
        turn(("submit", {})),
    ])
    rec = run_episode(_env(ledger_task), provider, sample=2)
    assert rec["stop_reason"] == "submit" and rec["error"] is None
    assert (rec["model_calls"], rec["tool_steps"]) == (3, 4)
    assert rec["grade"]["solved"] and rec["grade"]["reward"] == 1.0
    assert rec["usage"] == {"input": 30, "cache_read": 0, "cache_write": 0, "output": 30}
    assert (rec["task_id"], rec["sample"], rec["condition"], rec["variant"]) == ("pd2-ledger-append", 2, "neutral", "standard")
    assert "passed" in provider.results[1][-1][1]  # the run_tests output went back to the model
    assert provider.system == SYSTEM_PROMPT and provider.prompt.startswith("We upgraded pandas")
    json.dumps(rec)  # the whole record can be written to a results file


def test_reply_without_a_tool_call_ends_the_episode(ledger_task):
    rec = run_episode(_env(ledger_task), ReplayProvider([turn(stop="end_turn")]))
    assert rec["stop_reason"] == "no_tool_call"
    assert not rec["grade"]["solved"]


@pytest.mark.parametrize("stop", ["refusal", "max_tokens", "context_window"])
def test_refused_or_cut_off_reply_ends_the_episode_without_running_its_calls(ledger_task, stop):
    rec = run_episode(_env(ledger_task), ReplayProvider([turn(("submit", {}), stop=stop)]))
    assert rec["stop_reason"] == stop
    assert rec["tool_steps"] == 0


def test_token_budget_stops_before_the_next_request(ledger_task):
    provider = ReplayProvider([turn(("list_files", {}), tokens=200)] * 10)
    rec = run_episode(_env(ledger_task), provider, max_total_tokens=1000)
    # 400 tokens per turn (200 in, 200 out): 0, 400, 800 are under 1000, 1200 is not.
    assert rec["stop_reason"] == "token_budget" and rec["model_calls"] == 3


def test_step_limit_ends_the_episode(ledger_task):
    rec = run_episode(_env(ledger_task, max_steps=3), ReplayProvider([turn(("list_files", {}))] * 10))
    assert rec["stop_reason"] == "max_steps" and rec["tool_steps"] == 3


def test_api_failure_is_recorded_not_raised(ledger_task):
    provider = ReplayProvider([turn(("list_files", {})), RuntimeError("still rate limited after retries")])
    rec = run_episode(_env(ledger_task), provider)
    assert rec["stop_reason"] == "error"
    assert rec["error"] == "RuntimeError: still rate limited after retries"
    assert rec["grade"]["task_id"] == "pd2-ledger-append"  # graded anyway, for the record


def test_unreadable_arguments_go_back_as_an_error(ledger_task):
    bad = Turn([ToolCall("call_0", "read_file", None, "arguments are not valid JSON")], "tool_use", {})
    provider = ReplayProvider([bad, turn(("submit", {}))])
    rec = run_episode(_env(ledger_task), provider)
    assert provider.results[0] == [("read_file", "Error: arguments are not valid JSON", True)]
    assert rec["tool_steps"] == 1  # only submit ran


def test_calls_after_submit_in_the_same_turn_do_not_run(ledger_task):
    rec = run_episode(_env(ledger_task), ReplayProvider([turn(("submit", {}), ("delete_file", {"path": "tests/test_ledger.py"}))]))
    assert rec["stop_reason"] == "submit" and rec["tool_steps"] == 1
    assert "test_tamper" not in rec["grade"]["flags"]


# --- Anthropic provider ---------------------------------------------------------------------

anthropic_types = pytest.importorskip("anthropic.types")


class FakeAnthropic:
    """Stands in for anthropic.Anthropic(): records each messages.create call and returns the next reply."""

    def __init__(self, replies):
        self.replies, self.requests = list(replies), []
        self.messages = self

    def create(self, **kwargs):
        self.requests.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.replies.pop(0)


def _claude_reply(*blocks, stop="tool_use"):
    t = anthropic_types
    content = [t.TextBlock(type="text", text=b) if isinstance(b, str) else t.ToolUseBlock(type="tool_use", **b) for b in blocks]
    usage = t.Usage(input_tokens=10, output_tokens=5, cache_read_input_tokens=100, cache_creation_input_tokens=20)
    return t.Message(id="msg", type="message", role="assistant", model="test-model", content=content,
                     stop_reason=stop, stop_sequence=None, usage=usage)


def test_anthropic_provider_runs_an_episode(ledger_task):
    (_, write), = _solution_writes(ledger_task)
    client = FakeAnthropic([
        _claude_reply("I'll apply the fix.",
                      {"id": "t1", "name": "write_file", "input": write},
                      {"id": "t2", "name": "delete_file", "input": {"path": "../outside.py"}}),
        _claude_reply({"id": "t3", "name": "submit", "input": {}}),
    ])
    env = _env(ledger_task)
    rec = run_episode(env, AnthropicProvider("test-model", effort="high", client=client))

    assert rec["stop_reason"] == "submit" and rec["grade"]["solved"]
    assert rec["usage"] == {"input": 20, "cache_read": 200, "cache_write": 40, "output": 10}
    assert rec["settings"] == {"max_tokens": 16000, "effort": "high"}

    first, second = client.requests
    assert first["model"] == "test-model" and first["system"] == SYSTEM_PROMPT
    assert first["cache_control"] == {"type": "ephemeral"}
    assert first["output_config"] == {"effort": "high"}
    assert [t["name"] for t in first["tools"]] == [t["name"] for t in env.tool_specs()]
    assert "temperature" not in first
    # Both results of the first turn go back in one user message, the failed one marked as an error.
    results = second["messages"][-1]
    assert results["role"] == "user"
    assert [(b["tool_use_id"], b.get("is_error", False)) for b in results["content"]] == [("t1", False), ("t2", True)]

    json.dumps(rec)
    assert rec["messages"][1]["content"][0] == {"type": "text", "text": "I'll apply the fix."}


# --- OpenAI-compatible provider ----------------------------------------------------------------

pytest.importorskip("openai")
from openai.types import CompletionUsage  # noqa: E402
from openai.types.chat import ChatCompletion, ChatCompletionMessage  # noqa: E402
from openai.types.chat.chat_completion import Choice  # noqa: E402
from openai.types.chat.chat_completion_message_function_tool_call import (  # noqa: E402
    ChatCompletionMessageFunctionToolCall,
    Function,
)
from openai.types.completion_usage import PromptTokensDetails  # noqa: E402


class FakeOpenAI:
    """Stands in for openai.OpenAI(): records each chat.completions.create call and returns the next reply."""

    def __init__(self, replies):
        self.replies, self.requests = list(replies), []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.requests.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.replies.pop(0)


def _openai_reply(*calls, finish="tool_calls"):
    tool_calls = [
        ChatCompletionMessageFunctionToolCall(id=cid, type="function", function=Function(name=name, arguments=args))
        for cid, name, args in calls
    ]
    message = ChatCompletionMessage(role="assistant", content=None, tool_calls=tool_calls or None)
    usage = CompletionUsage(prompt_tokens=120, completion_tokens=8, total_tokens=128,
                            prompt_tokens_details=PromptTokensDetails(cached_tokens=100))
    return ChatCompletion(id="c", object="chat.completion", created=0, model="test-model",
                          choices=[Choice(index=0, finish_reason=finish, message=message)], usage=usage)


def test_openai_provider_runs_an_episode(ledger_task):
    (_, write), = _solution_writes(ledger_task)
    client = FakeOpenAI([
        _openai_reply(("call_1", "write_file", json.dumps(write)), ("call_2", "read_file", "{not json")),
        _openai_reply(("call_3", "submit", "{}")),
    ])
    rec = run_episode(_env(ledger_task), OpenAIProvider("test-model", client=client))

    assert rec["stop_reason"] == "submit" and rec["grade"]["solved"]
    # prompt_tokens includes the cached ones, so uncached input is 120 - 100 per request.
    assert rec["usage"] == {"input": 40, "cache_read": 200, "cache_write": 0, "output": 16}

    first, second = client.requests
    assert first["messages"][0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert all(t["type"] == "function" and "parameters" in t["function"] for t in first["tools"])
    assistant, *tool_msgs = second["messages"][2:]
    assert [c["id"] for c in assistant["tool_calls"]] == ["call_1", "call_2"]
    assert [m["tool_call_id"] for m in tool_msgs] == ["call_1", "call_2"]
    assert tool_msgs[1]["content"].startswith("Error: arguments are not valid JSON")

    json.dumps(rec)
