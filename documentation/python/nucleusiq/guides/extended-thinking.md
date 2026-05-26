# Extended thinking (Anthropic)

!!! abstract "What this page covers"

    **Extended thinking** gives Claude a dedicated token budget to reason internally before generating its final response. Reasoning tokens are billed separately and don't count toward `max_output_tokens`, but `max_output_tokens` must still be **strictly greater than** the thinking budget.

    NucleusIQ exposes this through a single ergonomic knob on `AnthropicLLMParams` — `thinking="low" | "medium" | "high" | "max"` — resolved to a concrete `{"type": "enabled", "budget_tokens": N}` payload at wire time.

## When to use it

Extended thinking pays off whenever the task benefits from **deliberate, multi-step reasoning** rather than a single forward pass:

- 🧮 **Math / logic / algorithmic** problems where one-shot guessing fails.
- 🧪 **Code review / debugging** where the model needs to enumerate cases.
- 📊 **Multi-document analysis** with several constraints to reconcile.
- 🧠 **Planning / autonomous agents** that decompose tasks.

## How to enable it

```python
from nucleusiq.llms.llm_params import LLMParams
from nucleusiq_anthropic import AnthropicLLMParams, BaseAnthropic

llm = BaseAnthropic(
    model_name="claude-sonnet-4-5-20250929",
    async_mode=True,
    llm_params=AnthropicLLMParams(thinking="medium"),
)

# Sampling — temperature MUST be 1.0 and max_output_tokens MUST exceed the budget.
sampling = LLMParams(temperature=1.0, max_output_tokens=16_384)
```

### `thinking` accepts three forms

| Form | What it produces |
| --- | --- |
| `bool` | `True` → minimal thinking enabled; `False` → disabled |
| `"low" \| "medium" \| "high" \| "max"` (`ThinkingEffort`) | Resolved via `_THINKING_EFFORT_BUDGETS` |
| `dict` | Passthrough — full control of `{"type": "...", "budget_tokens": ...}` |

| Effort | Budget tokens |
| --- | --- |
| `"low"` | **2 000** |
| `"medium"` | **8 000** |
| `"high"` | **32 000** |
| `"max"` | **64 000** |

## Hard constraints

!!! warning "Anthropic enforces these — 400 errors otherwise"

    - **`temperature` MUST be `1.0`.** Any other value returns `400 invalid_request_error`.
    - **`max_output_tokens` MUST be strictly greater than `thinking.budget_tokens`.** A `medium` budget of 8 000 needs `max_output_tokens >= 16_384` to leave room for the final answer.
    - Model support — extended thinking requires **Claude Sonnet 4 / Opus 4 / 3.7-Sonnet** or newer. Older SKUs return `400 model_not_supported`.

## Reading the result

`AnthropicLLMResponse.stop_reason` and the framework's `LLMCallRecord.stop_reason` reflect whether the model finished cleanly:

```python
result = await agent.execute(task)
for rec in result.llm_calls:
    print(
        f"round={rec.round}  stop_reason={rec.stop_reason}  "
        f"prompt={rec.prompt_tokens}  completion={rec.completion_tokens}"
    )
```

Common `stop_reason` values with thinking enabled:

- `end_turn` — natural completion within the budget.
- `max_tokens` — the model hit `max_output_tokens` before finishing (raise the cap).
- `tool_use` — model paused to call a (server or local) tool.

## Streaming with thinking

When you stream a thinking call, NucleusIQ emits `StreamEventType.THINKING` events for the reasoning trace and the regular `TOKEN` events for the final answer. The terminal `COMPLETE` event still carries `stop_reason`, `request_id`, and cache token splits in `event.metadata`.

```python
async for ev in agent.execute_stream(task):
    if ev.type is StreamEventType.THINKING:
        print(".", end="", flush=True)
    elif ev.type is StreamEventType.TOKEN:
        print(ev.content, end="", flush=True)
    elif ev.type is StreamEventType.COMPLETE:
        print("\n--- done:", ev.metadata.get("stop_reason"))
```

## Live demo

`examples/agents/12_anthropic_extended_thinking.py` in the monorepo runs the same probability problem (3 red / 5 blue / 7 green marbles → P(both same colour)) under `thinking="low"` and `thinking="medium"`. Verified live against `claude-sonnet-4-5-20250929` during the v0.7.12 release; both efforts return **34/105**.

## Live integration tests

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("effort", ["low", "medium"])
async def test_live_extended_thinking_completes(effort: str) -> None:
    llm = BaseAnthropic(
        model_name="claude-sonnet-4-5-20250929",
        async_mode=True,
        llm_params=AnthropicLLMParams(thinking=effort),
    )
    result = await llm.call(
        model="claude-sonnet-4-5-20250929",
        messages=[{"role": "user", "content": "...hard problem..."}],
        max_output_tokens=16_384,   # must exceed budget
        temperature=1.0,            # required
    )
    assert result.stop_reason
    assert (result.choices[0].message.content or "").strip()
```

Lives at `src/providers/llms/anthropic/tests/integration/test_anthropic_phase_b_live.py::test_live_extended_thinking_completes`.

## See also

- [Anthropic provider guide](anthropic-provider.md) — full surface for Claude
- [Native server tools](native-server-tools.md) — extended thinking interleaves with `tool_use`
- [Observability](../observability/index.md) — `stop_reason`, `LLMCallRecord` enrichment
- [Anthropic docs — Extended thinking](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)
