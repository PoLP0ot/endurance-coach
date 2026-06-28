"""LLM converse loop tests — tool-calling with a scripted fake client (B3).

No network: a fake OpenAI client returns scripted responses so we can assert the
loop runs tools, appends results, answers, and clamps turns.
"""
from __future__ import annotations

from types import SimpleNamespace

from app.services.coach_tools import TOOL_SPECS
from app.services.llm import LLMProvider, Task


def _resp(content=None, tool_calls=None):
    msg = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def _tool_call(call_id: str, name: str, arguments: str = "{}"):
    return SimpleNamespace(
        id=call_id, function=SimpleNamespace(name=name, arguments=arguments)
    )


class _FakeClient:
    """Mimics ``client.chat.completions.create`` returning scripted responses."""

    def __init__(self, scripted: list) -> None:
        self._scripted = scripted
        self.calls: list[dict] = []

    @property
    def chat(self):
        return self

    @property
    def completions(self):
        return self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._scripted.pop(0)


def _provider(fake: _FakeClient) -> LLMProvider:
    prov = LLMProvider(api_key="test-key")
    prov._client = lambda: fake  # type: ignore[method-assign]
    return prov


def test_converse_runs_tool_then_answers():
    fake = _FakeClient(
        [
            _resp(tool_calls=[_tool_call("c1", "get_goal_progress")]),
            _resp(content="You're tracking well toward your goal."),
        ]
    )
    prov = _provider(fake)
    ran: list[str] = []

    def runner(name, args):
        ran.append(name)
        return {"goal": {"on_track_band": "on_track"}}

    out = prov.converse(Task.CHAT, {"x": 1}, "How am I doing?", TOOL_SPECS, runner)
    assert out == "You're tracking well toward your goal."
    assert ran == ["get_goal_progress"]
    assert len(fake.calls) == 2
    # The tool result was appended as a 'tool' role message before the 2nd call.
    assert any(m["role"] == "tool" for m in fake.calls[1]["messages"])


def test_converse_answers_immediately_without_tools():
    fake = _FakeClient([_resp(content="Quick answer.")])
    out = _provider(fake).converse(Task.CHAT, {}, "hi", TOOL_SPECS, lambda n, a: {})
    assert out == "Quick answer."
    assert len(fake.calls) == 1


def test_converse_clamps_turns_and_forces_answer():
    tc = _tool_call("c1", "get_goal_progress")
    fake = _FakeClient(
        [_resp(tool_calls=[tc]), _resp(tool_calls=[tc]), _resp(content="Final.")]
    )
    out = _provider(fake).converse(
        Task.CHAT, {}, "hi", TOOL_SPECS, lambda n, a: {"ok": 1}, max_turns=2
    )
    assert out == "Final."
    assert len(fake.calls) == 3  # 2 tool rounds + 1 forced final (no tools)
    assert "tools" not in fake.calls[-1]
