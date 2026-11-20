"""Model agents: run a language model through a DriftGym episode.

The model gets the task prompt and the environment's tools (list_files,
read_file, write_file, ...). Each turn it asks for one or more tool calls; the
harness runs them with ``env.step`` and sends the results back. The episode
ends when the model calls ``submit``, the environment's step limit is reached
(``DriftEnv.max_steps``), the token budget runs out, the model replies without
calling a tool, the model refuses, or its reply is cut off (output limit or
context window). The workspace is then graded, and
``run_episode`` returns one record with everything: the model's messages, the
tool calls and their results, token counts, wall time, why it stopped, and the
grade.

Two providers:

- ``anthropic``: Claude through the official Anthropic SDK (Messages API with
  tool use). Every request turns on prompt caching, so a long episode pays the
  full input price only for each turn's new messages.
- ``openai``: any model behind an OpenAI-compatible Chat Completions API with
  function calling. ``OPENAI_BASE_URL`` points it at OpenRouter, vLLM or
  another server.

API keys are read by the SDKs from environment variables only
(``ANTHROPIC_API_KEY``, ``OPENAI_API_KEY``). Model names always come from the
caller; nothing here names a model. Both SDKs retry rate limits (429), server
errors (5xx) and dropped connections with exponential backoff. If a request
still fails, the episode ends with stop reason ``error`` and the message is
recorded; the episode is never silently retried as a whole.

Server-side model fallbacks are deliberately not used: a fallback would hand
part of an episode to another model, and the result would no longer belong to
the model being measured. A refusal simply ends the episode.

Token counts are kept as four numbers, so cost can be worked out with any
price list: ``input`` (uncached input), ``cache_read``, ``cache_write`` and
``output``.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from driftgym.env import DriftEnv

SYSTEM_PROMPT = (
    "You are a software engineer working in a Python repository through the tools provided. "
    "Use them to inspect and change files and to run the tests. "
    "When you are finished, call the submit tool."
)
MAX_RETRIES = 8  # per request, with the SDK's exponential backoff
USAGE_KEYS = ("input", "cache_read", "cache_write", "output")


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict | None  # None when the model's arguments could not be parsed
    error: str = ""


@dataclass
class Turn:
    """One model response, in the same shape for every provider."""

    calls: list[ToolCall]
    # "tool_use", "end_turn", "max_tokens", "refusal", "context_window", or the provider's own value.
    stop: str
    usage: dict[str, int] = field(default_factory=dict)


def _jsonable(x):
    """SDK response objects, and lists or dicts of them, as plain JSON-ready data."""
    if hasattr(x, "to_dict"):
        return x.to_dict(mode="json")
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    return x


class AnthropicProvider:
    """Claude through the Anthropic Messages API, one request per turn."""

    name = "anthropic"

    def __init__(self, model: str, *, max_tokens: int = 16000, effort: str | None = None, client=None):
        import anthropic

        self.model, self.max_tokens, self.effort = model, max_tokens, effort
        self.client = client or anthropic.Anthropic(max_retries=MAX_RETRIES)
        self.errors = (anthropic.APIError,)
        self.messages: list = []

    def settings(self) -> dict:
        return {"max_tokens": self.max_tokens, "effort": self.effort}

    def start(self, system: str, prompt: str, tools: list[dict]) -> None:
        self.system, self.tools = system, tools  # tools are already in Anthropic's format
        self.messages = [{"role": "user", "content": prompt}]

    def send(self) -> Turn:
        kwargs = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system,
            tools=self.tools,
            messages=self.messages,
            # Cache everything up to the newest message; the next request reads it back cheaply.
            cache_control={"type": "ephemeral"},
        )
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}
        r = self.client.messages.create(**kwargs)
        # Keep the whole content, thinking blocks included: they must go back unchanged.
        self.messages.append({"role": "assistant", "content": r.content})
        u = r.usage
        usage = {
            "input": u.input_tokens,
            "cache_read": u.cache_read_input_tokens or 0,
            "cache_write": u.cache_creation_input_tokens or 0,
            "output": u.output_tokens,
        }
        calls = [ToolCall(b.id, b.name, b.input) for b in r.content if b.type == "tool_use"]
        stop = "context_window" if r.stop_reason == "model_context_window_exceeded" else r.stop_reason
        return Turn(calls, stop, usage)

    def add_results(self, results: list[tuple[ToolCall, str, bool]]) -> None:
        # Every result of one turn goes back in a single user message.
        blocks = []
        for call, output, is_error in results:
            block = {"type": "tool_result", "tool_use_id": call.id, "content": output}
            if is_error:
                block["is_error"] = True
            blocks.append(block)
        self.messages.append({"role": "user", "content": blocks})

    def transcript(self) -> list:
        return _jsonable(self.messages)


class OpenAIProvider:
    """Any model behind an OpenAI-compatible Chat Completions API with function calling."""

    name = "openai"
    STOPS = {"tool_calls": "tool_use", "stop": "end_turn", "length": "max_tokens", "content_filter": "refusal"}

    def __init__(self, model: str, *, client=None):
        import openai

        self.model = model
        self.client = client or openai.OpenAI(max_retries=MAX_RETRIES)  # reads OPENAI_BASE_URL and OPENAI_API_KEY
        self.errors = (openai.APIError,)
        self.messages: list = []

    def settings(self) -> dict:
        return {}

    def start(self, system: str, prompt: str, tools: list[dict]) -> None:
        self.tools = [
            {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]}}
            for t in tools
        ]
        self.messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

    def send(self) -> Turn:
        r = self.client.chat.completions.create(model=self.model, messages=self.messages, tools=self.tools)
        choice = r.choices[0]
        msg = choice.message
        calls, sent = [], []
        for tc in msg.tool_calls or []:
            fn = getattr(tc, "function", None)
            if fn is None:
                calls.append(ToolCall(tc.id, "", None, f"unsupported tool call type {tc.type!r}"))
                continue
            sent.append({"id": tc.id, "type": "function", "function": {"name": fn.name, "arguments": fn.arguments}})
            try:
                args = json.loads(fn.arguments or "{}")
                error = "" if isinstance(args, dict) else "arguments must be a JSON object"
            except json.JSONDecodeError as e:
                args, error = None, f"arguments are not valid JSON ({e})"
            calls.append(ToolCall(tc.id, fn.name, args if not error else None, error))
        assistant = {"role": "assistant", "content": msg.content}
        if sent:
            assistant["tool_calls"] = sent
        self.messages.append(assistant)
        # prompt_tokens includes cached tokens; some servers report no usage at all.
        u = r.usage
        details = getattr(u, "prompt_tokens_details", None) if u else None
        cached = (getattr(details, "cached_tokens", None) or 0) if details else 0
        usage = {
            "input": (u.prompt_tokens - cached) if u else 0,
            "cache_read": cached,
            "cache_write": 0,
            "output": u.completion_tokens if u else 0,
        }
        return Turn(calls, self.STOPS.get(choice.finish_reason, choice.finish_reason), usage)

    def add_results(self, results: list[tuple[ToolCall, str, bool]]) -> None:
        for call, output, _ in results:
            self.messages.append({"role": "tool", "tool_call_id": call.id, "content": output})

    def transcript(self) -> list:
        return _jsonable(self.messages)


PROVIDERS = {"anthropic": AnthropicProvider, "openai": OpenAIProvider}


def run_episode(env: DriftEnv, provider, *, max_total_tokens: int | None = None, sample: int = 0) -> dict:
    """Run one episode of ``env`` with ``provider``, grade it, and return its record.

    ``max_total_tokens`` caps all four token counts added together; the check
    runs before each request, so the last request can take it a little over.
    """
    prompt = env.reset()
    usage = dict.fromkeys(USAGE_KEYS, 0)
    model_calls = 0
    stop = error = None
    start = time.time()
    try:
        try:
            provider.start(SYSTEM_PROMPT, prompt, env.tool_specs())
            while stop is None:
                if max_total_tokens is not None and sum(usage.values()) >= max_total_tokens:
                    stop = "token_budget"
                    break
                turn = provider.send()
                model_calls += 1
                for k in USAGE_KEYS:
                    usage[k] += turn.usage.get(k, 0)
                if turn.stop in ("refusal", "max_tokens", "context_window"):
                    stop = turn.stop
                elif not turn.calls:
                    stop = "no_tool_call"
                else:
                    results = []
                    for call in turn.calls:
                        if call.args is None:
                            results.append((call, f"Error: {call.error}", True))
                            continue
                        obs, done = env.step(call.name, call.args)
                        results.append((call, obs, obs.startswith("Error:")))
                        if done:
                            break
                    if env.done:
                        stop = "submit" if env.steps[-1].tool == "submit" else "max_steps"
                    else:
                        provider.add_results(results)
        except provider.errors as e:  # raised only after the SDK's own retries
            stop, error = "error", f"{type(e).__name__}: {e}"
        seconds = round(time.time() - start, 2)
        grade = env.grade()
    finally:
        env.close()
    return {
        "provider": provider.name,
        "model": provider.model,
        "settings": provider.settings(),
        "task_id": env.task.id,
        "condition": env.condition,
        "variant": env.variant,
        "sample": sample,
        "stop_reason": stop,
        "error": error,
        "model_calls": model_calls,
        "tool_steps": len(env.steps),
        "usage": usage,
        "seconds": seconds,
        "system": SYSTEM_PROMPT,
        "messages": provider.transcript(),
        "steps": env.transcript(),
        "grade": grade.to_dict(),
    }
