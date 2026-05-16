# Anthropic (Claude) provider

!!! danger "Alpha announcement"

    **`nucleusiq-anthropic` 0.1.0a1** is now available as a **PyPI pre-release** (**`Development Status :: 3 - Alpha`**). It wires **[Anthropic](https://www.anthropic.com/) Claude** through NucleusIQ using the **Messages API** and the official **`anthropic`** Python SDK (**`AsyncAnthropic` / `Anthropic`**).

    - **Requires** **`nucleusiq>=0.7.10`** and **`anthropic>=0.40,<1`**.
    - **Treat as experimental:** APIs and defaults may change before a stable track. **Pin versions** for anything important.

Use this guide for **capabilities, limits, environment variables, and operational notes**. Copy-paste workflows live in the **[Anthropic quickstart](../examples/anthropic-quickstart.md)**.

## Why Claude + NucleusIQ

Claude’s **Messages API** uses **`tool_use` / `tool_result`** blocks and different streaming events than OpenAI Chat Completions. **`BaseAnthropic`** adapts that surface to NucleusIQ’s **`BaseLLM`** so your **`Agent`**, execution modes, **`@tool`** tools, streaming, and structured-output wiring stay **familiar** — without maintaining a brittle “pretend it’s OpenAI” shim.

## What’s in this alpha

| Capability | Supported |
|------------|-----------|
| Messages API (`POST /v1/messages`) | Yes |
| **`BaseAnthropic.call` / `call_stream`** → **`StreamEvent`** | Yes |
| **`@tool`** / local function tools | Yes |
| Structured output (**JSON Schema** → Messages **`output_config.format`**) | Yes — model / API must support it; combining **`response_format`** with **tools** drops structured output with a **warning** (same pattern as Groq / Ollama); **`call_stream`** ignores **`response_format`** with a **warning** |
| **`AnthropicLLMParams`** | **`top_k`**, **`anthropic_beta`**, **`extra_headers`** (merged on the client) |
| Sampling (**`temperature`**, **`max_output_tokens`**, …) | Use framework **`LLMParams`** on **`AgentConfig.llm_params`** (merged into each call). The adapter omits **`top_p`** when **`temperature`** is set where needed to avoid **400** mutual-exclusion errors on newer Claude SKUs. |
| Errors / retries | SDK exceptions mapped to **`nucleusiq.llms.errors`**; **`Retry-After`** + exponential backoff via shared **`retry_policy`** (**v0.7.9+** core) |
| Multimodal images (HTTP / data URLs in messages) | Wired in the translation layer (see monorepo provider README for caveats) |

### Not in this alpha yet

- **Native / server-side Claude tools** (web search, code execution, etc.) — **`NATIVE_TOOL_TYPES`** is **empty**; no **`AnthropicTool`** factory yet. Use **`@tool`** for Phase A.
- Full **observability** enrichment on **`LLMCallRecord`** (request ids, org headers, …) — planned polish.
- **Bedrock / Vertex / Foundry** backends — direct Anthropic API only for v1 scope.

## Prerequisites

1. **[Anthropic Console](https://console.anthropic.com/)** API key (**`ANTHROPIC_API_KEY`**).
2. A **model id** your organization can call. Defaults in examples often use **`claude-3-5-sonnet-20241022`**; if you see **`404` / model not found**, discover ids with the repo script **`09_anthropic_list_models.py`** and set **`ANTHROPIC_MODEL`**.

## Installation

```bash
pip install nucleusiq nucleusiq-anthropic
```

Pin the alpha for reproducible builds:

```bash
pip install "nucleusiq>=0.7.10" "nucleusiq-anthropic==0.1.0a1"
```

## Environment

| Variable | Purpose |
|----------|---------|
| **`ANTHROPIC_API_KEY`** | Required for live calls unless you pass **`api_key="..."`** to **`BaseAnthropic`**. |
| **`ANTHROPIC_MODEL`** | Optional default model id for examples (**`claude-3-5-sonnet-20241022`** if unset). |

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# export ANTHROPIC_MODEL=claude-sonnet-4-20250514   # example — use IDs valid for your key
```

## Quick start (Direct)

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
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
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

## Provider-specific parameters

Pass **Claude-only** knobs on **`BaseAnthropic`** via **`AnthropicLLMParams`** (not on **`AgentConfig`**):

```python
from nucleusiq_anthropic import AnthropicLLMParams, BaseAnthropic

llm = BaseAnthropic(
    model_name="claude-3-5-sonnet-20241022",
    async_mode=True,
    llm_params=AnthropicLLMParams(
        top_k=40,
        anthropic_beta="your-beta-flag-if-needed",
        extra_headers={"X-Custom": "value"},
    ),
)
```

Keep **temperature / max tokens** on **`AgentConfig(llm_params=LLMParams(...))`** as in the quick start.

## Structured output

When your Claude model supports **native structured outputs**, set **`response_format=`** on **`Agent`** (Pydantic model, dataclass, **`TypedDict`**, or schema dict). The adapter maps this to Messages **`output_config.format`** and parses JSON into your type.

!!! warning "Tools + structured output"

    If the agent also has **tools**, structured output is **dropped** for that call path with a **warning** — align with **[Structured output](../structured-output.md)** and test without tools first.

Streaming (**`call_stream`**) does **not** apply **`response_format`**; you’ll see a **warning** if it’s set.

See **`examples/output_parsers/anthropic_native_structured_example.py`** in the monorepo for an **Agent + native JSON schema** demo.

## Imports

```python
from nucleusiq_anthropic import (
    AnthropicLLMParams,
    BaseAnthropic,
    NATIVE_TOOL_TYPES,
    to_anthropic_tool_definition,
)
```

**`NATIVE_TOOL_TYPES`** is **empty** in alpha — prefer **`@tool`** and **`to_anthropic_tool_definition`** for debugging schemas (**`08_anthropic_tool_schema.py`** is offline-only).

## Runnable examples

Clone **[NucleusIQ](https://github.com/nucleusbox/NucleusIQ)** and run from **`src/providers/llms/anthropic`**:

```bash
uv sync --group full   # or pip install -e . from that directory + core
uv run python examples/agents/01_anthropic_direct.py
uv run python examples/agents/03_anthropic_standard_tools.py
uv run python examples/agents/05_anthropic_stream.py
uv run python examples/agents/09_anthropic_list_models.py  # discover model IDs
```

Full parity table: **[examples/README.md](https://github.com/nucleusbox/NucleusIQ/blob/main/src/providers/llms/anthropic/examples/README.md)**.

## See also

- [Anthropic quickstart](../examples/anthropic-quickstart.md) — Three gears + optional structured output pointers
- [Structured output](../structured-output.md) — Resolver + **`get_provider_from_llm`** (**`anthropic`**)
- [Installation](../install.md) — Package matrix
- [Providers](../providers.md) — Portability overview
- [Error handling](../core-concepts/error-handling.md) — Shared exception families + retries
