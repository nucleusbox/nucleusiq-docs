# Anthropic (Claude) provider

!!! success "🟢 Stable — `nucleusiq-anthropic` 0.2.0 (Phase B feature-complete)"

    **`nucleusiq-anthropic` 0.2.0** ships as **`Development Status :: 5 - Production/Stable`** (first stable line; semver applies from here). It connects **Claude** to NucleusIQ through the **Messages API** and the official **`anthropic`** Python SDK (**`AsyncAnthropic` / `Anthropic`**), with full Phase B feature parity.

    - **Requires** **`nucleusiq>=0.7.12`** and **`anthropic>=0.40,<1`**.
    - **151 unit tests + 6 live integration tests, 95.91% coverage** (gate ≥ 95%).
    - All Phase B features are covered by both unit tests and live API tests.

Use this guide as the canonical reference for **capabilities, environment, parameters, and operational notes**. Copy-paste workflows live in the [Anthropic quickstart](../examples/anthropic-quickstart.md). Conceptual deep-dives on **native server tools**, **prompt caching**, and **extended thinking** live on their own pages.

## What's in 0.2.0 (Phase B)

| Capability | Status |
|------------|--------|
| Messages API (`POST /v1/messages`) — `BaseAnthropic.call` / `call_stream` → `StreamEvent` | ✅ |
| `@tool` / local function tools | ✅ |
| Streaming (tokens, `THINKING` events, `tool_call_start` / `tool_call_end`, `COMPLETE` with metadata) | ✅ |
| Structured output (**JSON Schema** → Messages `output_config.format`) — tools + format gracefully fall back to function-style tools with a warning | ✅ |
| Sampling — `temperature`, `max_output_tokens`, `top_p` (auto-elided when temperature is set on incompatible SKUs) | ✅ via framework `LLMParams` |
| Errors / retries — SDK exceptions mapped to `nucleusiq.llms.errors`, `Retry-After` + capped backoff via shared `retry_policy` | ✅ |
| **`AnthropicTool` native server tools** — `web_search()`, `web_fetch()`, `code_execution()` with dated wire types + auto beta headers | ✅ **New in 0.2.0** |
| **Prompt caching** — `cache_system=True` / `cache_tools=True` emit `cache_control: ephemeral` blocks on the wire | ✅ **New in 0.2.0** |
| **Extended thinking** — `thinking="low"|"medium"|"high"|"max"` or full dict | ✅ **New in 0.2.0** |
| **`strict_tools=True`** + **`disable_parallel_tool_use=True`** | ✅ **New in 0.2.0** |
| **Server-tool observability** — `AnthropicLLMResponse.server_tool_calls` populated from `server_tool_use` + per-tool `*_tool_result` blocks; surfaced as `ToolCallRecord(executed_by="provider")` by the core agent loop | ✅ **New in 0.2.0** |
| **`LLMCallRecord` enrichment** — `provider="anthropic"`, `request_id`, `organization_id`, `stop_reason`, `cache_read_input_tokens`, `cache_creation_input_tokens` | ✅ **New in 0.2.0** |
| Multimodal image messages (HTTP / data URLs) | ✅ via translation layer |

### Not in 0.2.0 (deferred)

- **Anthropic Phase C** — Memory tool / `computer_use` / `bash` — planned for **`nucleusiq-anthropic 0.3.x`**.
- **Bedrock / Vertex / Foundry** backends — direct Anthropic API only for the stable line.

## Prerequisites

1. **[Anthropic Console](https://console.anthropic.com/)** API key (**`ANTHROPIC_API_KEY`**).
2. A **model id** your organization can call. Phase B features (native tools, prompt caching, extended thinking) require **Claude Sonnet 4 / Opus 4 / 3.7-Sonnet** or newer.

!!! tip "Pick a Phase-B-capable model"

    The Phase B examples and live integration tests default to **`claude-sonnet-4-5-20250929`** because it supports every Phase B feature (`web_search`, `code_execution`, `cache_*`, `thinking`).

    If you see **`404 model_not_found`**, discover the model ids available on your key with `examples/agents/09_anthropic_list_models.py` and override via `ANTHROPIC_PHASE_B_MODEL=<id>`.

## Installation

```bash
pip install nucleusiq nucleusiq-anthropic
```

Pin the stable line for reproducible builds:

```bash
pip install "nucleusiq>=0.7.12" "nucleusiq-anthropic>=0.2.0,<0.3"
```

## Environment

| Variable | Purpose |
|----------|---------|
| **`ANTHROPIC_API_KEY`** | Required for live calls unless you pass **`api_key="..."`** to **`BaseAnthropic`**. |
| **`ANTHROPIC_MODEL`** | Optional default model id for examples. |
| **`ANTHROPIC_PHASE_B_MODEL`** | Optional model id used by the Phase B examples / integration tests (default `claude-sonnet-4-5-20250929`). |

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export ANTHROPIC_PHASE_B_MODEL=claude-sonnet-4-5-20250929   # or your accessible Phase B model
```

## Quick start (DIRECT)

Use **`BaseAnthropic(..., async_mode=True)`**, **`AgentConfig`** with **`LLMParams`** for sampling, and **`await agent.initialize()`** before **`execute()`** (matches **[`01_anthropic_direct.py`](https://github.com/nucleusbox/NucleusIQ/blob/main/src/providers/llms/anthropic/examples/agents/01_anthropic_direct.py)**).

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.llms.llm_params import LLMParams
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_anthropic import BaseAnthropic


async def main() -> None:
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
    llm = BaseAnthropic(model_name=model, async_mode=True)

    agent = Agent(
        name="anthropic-direct",
        prompt=ZeroShotPrompt().configure(
            system="You are a concise assistant. Reply in one or two short sentences.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.DIRECT,
            llm_params=LLMParams(temperature=0.3, max_output_tokens=256),
        ),
    )

    await agent.initialize()
    result = await agent.execute(
        Task(id="anthropic-direct-1", objective="What is the capital of France?"),
    )
    print(result.output)


asyncio.run(main())
```

## Phase B at a glance

=== "Native server tools"

    Server tools run **inside Anthropic's infrastructure** — you don't execute them, you just declare them.

    ```python
    from nucleusiq_anthropic import AnthropicTool, BaseAnthropic

    llm = BaseAnthropic(model_name="claude-sonnet-4-5-20250929", async_mode=True)

    result = await llm.call(
        model="claude-sonnet-4-5-20250929",
        messages=[{"role": "user", "content": "Use code_execution to compute Fib(12)."}],
        tools=[AnthropicTool.code_execution()],
        max_output_tokens=512,
    )
    print(result.choices[0].message.content)
    for stc in result.server_tool_calls:
        print(stc.name, stc.id, stc.result)
    ```

    → Full reference on the [Native server tools](native-server-tools.md) page.

=== "Prompt caching"

    Reuse expensive system prompts across calls — Anthropic serves cached prefixes at a fraction of the cost.

    ```python
    from nucleusiq_anthropic import AnthropicLLMParams, BaseAnthropic

    llm = BaseAnthropic(
        model_name="claude-sonnet-4-5-20250929",
        async_mode=True,
        llm_params=AnthropicLLMParams(cache_system=True, cache_tools=True),
    )
    ```

    → Full reference on the [Prompt caching](prompt-caching.md) page.

=== "Extended thinking"

    Give Claude a token budget to reason internally before responding.

    ```python
    from nucleusiq_anthropic import AnthropicLLMParams, BaseAnthropic

    llm = BaseAnthropic(
        model_name="claude-sonnet-4-5-20250929",
        async_mode=True,
        llm_params=AnthropicLLMParams(thinking="medium"),  # 8 000 token budget
    )
    # NOTE: max_output_tokens MUST exceed thinking.budget_tokens
    # and temperature MUST be 1.0 when thinking is enabled.
    ```

    → Full reference on the [Extended thinking](extended-thinking.md) page.

=== "Server-tool observability"

    The framework emits `ToolCallRecord(executed_by="provider")` for every server-side tool call **automatically** — no configuration required.

    ```python
    result = await agent.execute(task)
    for tc in result.tool_calls:
        print(tc.tool_name, tc.executed_by)
    # → web_search       provider
    # → code_execution   provider
    # → my_local_fn      local
    ```

    → Full reference on the [Observability guide](../observability/index.md).

## Provider-specific parameters

Pass **Claude-only** knobs on **`BaseAnthropic`** via **`AnthropicLLMParams`** (not on **`AgentConfig`**):

```python
from nucleusiq_anthropic import AnthropicLLMParams, BaseAnthropic

llm = BaseAnthropic(
    model_name="claude-sonnet-4-5-20250929",
    async_mode=True,
    llm_params=AnthropicLLMParams(
        top_k=40,
        anthropic_beta="user-beta-flag-if-needed",
        extra_headers={"X-Custom": "value"},

        # Phase B
        thinking="medium",                # "low"|"medium"|"high"|"max" or dict
        cache_system=True,                # cache_control on system prompt
        cache_tools=True,                 # cache_control on last tool def
        strict_tools=True,                # strict JSON schema on custom tools
        disable_parallel_tool_use=True,   # one tool call per turn
    ),
)
```

Keep **temperature / max tokens** on **`AgentConfig(llm_params=LLMParams(...))`**.

!!! warning "Extended thinking constraints"

    When `thinking` is enabled Anthropic enforces:

    - `temperature` **must** be `1.0` (not 0.0).
    - `max_output_tokens` **must** be **strictly greater than** `thinking.budget_tokens` (budgets: low=2000, medium=8000, high=32000, max=64000).

    A `400 invalid_request_error` will mention `max_tokens must be greater than thinking.budget_tokens` if you violate this.

## Structured output

When your Claude model supports **native structured outputs**, set **`response_format=`** on **`Agent`** (Pydantic model, dataclass, `TypedDict`, or schema dict). The adapter maps this to Messages `output_config.format` and parses JSON into your type.

!!! warning "Tools + structured output"

    If the agent also has **tools**, structured output is **dropped** for that call path with a warning — align with [Structured output](../structured-output.md) and test without tools first.

Streaming (`call_stream`) does **not** apply `response_format`; you'll see a warning if it's set.

## Public API

```python
from nucleusiq_anthropic import (
    AnthropicLLMParams,         # extended Phase B knobs (thinking, cache_*, strict_tools)
    AnthropicTool,              # factory for native server tools
    BaseAnthropic,              # the LLM wrapper
    NATIVE_TOOL_TYPES,          # frozenset {"web_search","web_fetch","code_execution"}
    NATIVE_TOOL_WIRE_TYPES,     # dated wire identifiers
    NATIVE_TOOL_BETA_HEADERS,   # required anthropic-beta tokens
    ServerToolCall,             # Pydantic model for server-executed tools
    ThinkingEffort,             # Literal["low","medium","high","max"]
    to_anthropic_tool_definition,
)
```

## Runnable examples

Clone **[NucleusIQ](https://github.com/nucleusbox/NucleusIQ)** and run from `src/providers/llms/anthropic`:

```bash
uv sync --group full   # or pip install -e . from that directory + core

# Phase A (always-works baseline)
uv run python examples/agents/01_anthropic_direct.py
uv run python examples/agents/03_anthropic_standard_tools.py
uv run python examples/agents/05_anthropic_stream.py
uv run python examples/agents/09_anthropic_list_models.py

# Phase B (require ANTHROPIC_PHASE_B_MODEL = Sonnet 4.5 / Opus 4 etc.)
uv run python examples/agents/10_anthropic_native_tools.py
uv run python examples/agents/11_anthropic_prompt_caching.py
uv run python examples/agents/12_anthropic_extended_thinking.py
```

## Live integration tests

```bash
cd src/providers/llms/anthropic
uv run pytest tests/integration -m integration -q
# 6 tests: web_search, code_execution, prompt caching,
# extended thinking (low + medium), disable_parallel_tool_use
```

Live tests skip cleanly if your `ANTHROPIC_API_KEY` lacks access to the configured Phase B model.

## See also

- [Native server tools](native-server-tools.md) — `web_search`, `web_fetch`, `code_execution`
- [Prompt caching](prompt-caching.md) — `cache_system`, `cache_tools`, cost wins
- [Extended thinking](extended-thinking.md) — `thinking` budgets and constraints
- [Observability](../observability/index.md) — `executed_by`, `cache_read_input_tokens`, `stop_reason`
- [Anthropic quickstart](../examples/anthropic-quickstart.md) — copy-paste flows
- [Structured output](../structured-output.md) — resolver + `get_provider_from_llm`
- [Error handling](../core-concepts/error-handling.md) — shared exception families + retries
