# Prompt caching (Anthropic)

!!! abstract "What this page covers"

    **Prompt caching** lets Anthropic keep a prefix of your prompt (system message, tool definitions) in cache for ~5 minutes and serve it on subsequent calls at a fraction of the normal token cost — typically **~10% of the normal input rate** for cache reads.

    NucleusIQ exposes this through two simple knobs on `AnthropicLLMParams` — `cache_system=True` and `cache_tools=True` — and surfaces the cache effect on every `LLMCallRecord` via `cache_read_input_tokens` / `cache_creation_input_tokens`.

## When to use it

Prompt caching pays off whenever the **same prefix** is sent **multiple times** within a 5-minute window:

- 🔁 **Agents with long system prompts** that run multiple tasks in a session.
- 🧰 **Tool-heavy agents** with large tool catalogs (think MCP-style adapters).
- 📚 **Document-grounded agents** that prepend the same source corpus / schema to every call.

!!! info "Floor: ~1024 tokens"

    Anthropic only caches prefixes of **≥ 1024 prompt tokens**. Anything shorter is served from the normal path without billing benefit.

## How to enable it

```python
from nucleusiq_anthropic import AnthropicLLMParams, BaseAnthropic

llm = BaseAnthropic(
    model_name="claude-sonnet-4-5-20250929",
    async_mode=True,
    llm_params=AnthropicLLMParams(
        cache_system=True,   # add cache_control to the system prompt
        cache_tools=True,    # add cache_control to the LAST tool definition
    ),
)
```

Under the hood, NucleusIQ:

- Promotes a plain-string system prompt into a block list and attaches `cache_control: {"type": "ephemeral"}`.
- Adds `cache_control: {"type": "ephemeral"}` to the **last** tool definition when `cache_tools=True` (Anthropic caches everything up to the marked block).
- Strips the private `_cache_system` / `_cache_tools` keys before reaching the SDK's `messages.create`.

## Reading the cache effect

With `enable_tracing=True`, every `LLMCallRecord` exposes the cache split:

```python
for rec in result.llm_calls:
    print(
        f"round={rec.round}  prompt={rec.prompt_tokens:>5} "
        f"cache_read={rec.cache_read_input_tokens:>5} "
        f"cache_create={rec.cache_creation_input_tokens:>5} "
        f"stop_reason={rec.stop_reason}"
    )
```

Typical pattern across two calls with `cache_system=True`:

| Call | `prompt_tokens` | `cache_creation_input_tokens` | `cache_read_input_tokens` |
| --- | --- | --- | --- |
| 1 (cache miss / create) | 1 851 | 1 830 | 0 |
| 2 (cache hit) | 1 851 | 0 | 1 830 |

→ on call 2, ~99% of the prompt is billed at the cache-read rate.

!!! example "Live demo"

    `examples/agents/11_anthropic_prompt_caching.py` in the monorepo runs exactly this pattern with a 9 780-character system prompt and prints the per-call cache token split. Verified live against `claude-sonnet-4-5-20250929` during the v0.7.12 release.

## Live integration test

```python
@pytest.mark.asyncio
async def test_live_prompt_caching_reads_cache_on_second_call() -> None:
    llm = BaseAnthropic(
        model_name="claude-sonnet-4-5-20250929",
        async_mode=True,
        llm_params=AnthropicLLMParams(cache_system=True),
    )
    r1 = await llm.call(..., messages=[...long system + q1...])
    r2 = await llm.call(..., messages=[...long system + q2...])
    assert (
        r1.usage.cache_creation_input_tokens
        + r2.usage.cache_creation_input_tokens
        + r1.usage.cache_read_input_tokens
        + r2.usage.cache_read_input_tokens
    ) > 0
```

Lives at `src/providers/llms/anthropic/tests/integration/test_anthropic_phase_b_live.py::test_live_prompt_caching_reads_cache_on_second_call`.

## Caveats

!!! warning "Cache TTL is short"

    Anthropic's cache TTL is **~5 minutes** from the last access. Cache hits across longer-lived sessions need a heartbeat / keep-warm strategy.

!!! warning "Cache key includes everything before the breakpoint"

    Changing **any** token in the system prompt or any tool definition before the `cache_control` marker invalidates the cache. Sort your tool catalog deterministically before passing it to the agent so that re-ordering doesn't bust the cache.

## See also

- [Anthropic provider guide](anthropic-provider.md) — full surface for Claude
- [Native server tools](native-server-tools.md) — pairs well with caching (large tool catalogs)
- [Observability](../observability/index.md) — `cache_read_input_tokens`, `cache_creation_input_tokens`
- [Anthropic docs — Prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
