# Groq provider

The **`nucleusiq-groq`** package adds **[Groq](https://groq.com/)** inference to NucleusIQ using Groq’s **OpenAI-compatible Chat Completions** API and Groq’s official **[`groq`](https://github.com/groq/groq-python)** Python SDK (`AsyncGroq` / `Groq`).

**Status:** **0.1.0b1** (public **beta** on PyPI, Trove `Development Status :: 4 - Beta`). Requires **`nucleusiq>=0.7.9`**.

!!! warning "Phase A scope"

    This release focuses on **Chat Completions**, **local function tools**, **streaming**, **structured output** (where the model supports `json_schema`), and **retries** (including **429** / **`Retry-After`** on chat *and* stream **open**). **Not wired yet:** Groq **Responses API**, **built-in/hosted tools** (constants exist for future work), **remote MCP** — see the design tracker below.

## Installation

```bash
pip install nucleusiq nucleusiq-groq
```

Pin the beta explicitly if you need reproducible builds:

```bash
pip install "nucleusiq>=0.7.9" "nucleusiq-groq==0.1.0b1"
```

## API keys and defaults

| Variable | Purpose |
|----------|---------|
| **`GROQ_API_KEY`** | Required for live calls. |
| **`GROQ_MODEL`** | Optional default model for chat/tools (examples often use `llama-3.3-70b-versatile`). |
| **`GROQ_MODEL_STRUCTURED`** | Optional model for **`json_schema`** structured output (many Llama checkpoints differ; examples default to `openai/gpt-oss-20b` — verify against [Groq structured outputs](https://console.groq.com/docs/structured-outputs)). |

```bash
export GROQ_API_KEY=gsk_...
```

## Rate limiting (HTTP 429)

**v0.7.9** introduces **`nucleusiq.llms.retry_policy`** in core — shared parsing of **`Retry-After`** (seconds or HTTP-date), merged with capped exponential backoff, and a ceiling (**`DEFAULT_RATE_LIMIT_MAX_SLEEP_SECONDS`**). **`nucleusiq-groq`** uses this policy for normal chat **and** for **streaming** session setup (**stream open**), matching non-stream behavior. OpenAI and Gemini providers were aligned on the same **429** handling in their respective **`0.6.4`** / **`0.2.6`** releases.

## Quick start (Direct mode)

Use **`BaseGroq`** like other providers. Call **`await agent.initialize()`** before **`execute()`** (recommended for full resolver/setup parity with the examples in the monorepo).

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_groq import BaseGroq, GroqLLMParams


async def main() -> None:
    llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)

    agent = Agent(
        name="groq-demo",
        prompt=ZeroShotPrompt().configure(
            system="You are a concise assistant.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.DIRECT,
            llm_params=GroqLLMParams(temperature=0.3, max_output_tokens=256),
        ),
    )

    await agent.initialize()

    result = await agent.execute(
        Task(id="groq-1", objective="What is the capital of France?"),
    )
    print(result.output)


asyncio.run(main())
```

## Standard mode + local tools

Groq is wired for **OpenAI-style local tools** (`@tool` / function declarations). All three **execution modes** (Direct, Standard, Autonomous) behave like OpenAI/Gemini from the agent’s perspective.

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_groq import BaseGroq, GroqLLMParams


@tool
def add(a: int, b: int) -> str:
    """Add two integers."""
    return str(a + b)


llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)
agent = Agent(
    name="groq-tools",
    prompt=ZeroShotPrompt().configure(
        system="Use tools when arithmetic is needed.",
    ),
    llm=llm,
    tools=[add],
    config=AgentConfig(
        execution_mode=ExecutionMode.STANDARD,
        llm_params=GroqLLMParams(temperature=0.4, max_output_tokens=512),
    ),
)
```

## GroqLLMParams

Typed provider params extend core **`LLMParams`** with **`extra="forbid"`**. Supported fields include the usual merged knobs (e.g. **`temperature`**, **`max_output_tokens`**) plus Groq-oriented options such as:

| Field | Meaning |
|-------|---------|
| **`parallel_tool_calls`** | Whether the model may emit multiple tool calls in one turn (`bool \| None`). |
| **`strict_model_capabilities`** | If **`True`**, reject **`parallel_tool_calls=True`** when the model id is **not** in the built-in allowlist ( **`InvalidRequestError`** before HTTP); default **`False`** logs a **warning** only. Never sent on the wire (excluded in **`to_call_kwargs()`**). |
| **`user`** | Optional end-user id string for abuse monitoring (OpenAI-compatible). |

Unsupported Chat Completions parameters for Groq (e.g. **`logit_bias`**, **`messages[].name`**) are stripped at the wire layer — see the design doc.

```python
from nucleusiq.agents.config import AgentConfig
from nucleusiq_groq import GroqLLMParams

config = AgentConfig(
    llm_params=GroqLLMParams(
        temperature=0.2,
        max_output_tokens=1024,
        parallel_tool_calls=True,
    ),
)
```

## Model capabilities (`parallel_tool_calls`)

Groq’s matrix changes over time; **`nucleusiq_groq.capabilities`** keeps a conservative **`PARALLEL_TOOL_CALLS_DOCUMENTED_MODELS`** allowlist and **`check_parallel_tool_calls_capability(...)`** used when **`parallel_tool_calls`** is enabled:

- **Default:** unknown models → **`logging`** warning (request still sent).
- **`GroqLLMParams(strict_model_capabilities=True)`** → **`InvalidRequestError`** if the model is unknown — fail fast for strict pipelines.

Advanced imports:

```python
from nucleusiq_groq.capabilities import (
    PARALLEL_TOOL_CALLS_DOCUMENTED_MODELS,
    check_parallel_tool_calls_capability,
)
```

## Structured output

Pass a **Pydantic** model to **`Agent(..., response_format=MyModel)`** when the chosen Groq model supports **`json_schema`**. Pick a model listed under Groq’s [structured outputs](https://console.groq.com/docs/structured-outputs) docs; fallback/env override via **`GROQ_MODEL_STRUCTURED`**.

```python
from pydantic import BaseModel, Field

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_groq import BaseGroq, GroqLLMParams


class Answer(BaseModel):
    city: str = Field(description="City name")
    population_millions: float = Field(description="Approximate population in millions")


agent = Agent(
    name="groq-structured",
    prompt=ZeroShotPrompt().configure(
        system="Reply only as JSON matching the schema.",
    ),
    llm=BaseGroq(model_name="openai/gpt-oss-20b", async_mode=True),
    config=AgentConfig(
        execution_mode=ExecutionMode.DIRECT,
        llm_params=GroqLLMParams(temperature=0.1, max_output_tokens=512),
    ),
    response_format=Answer,
)
```

## Streaming

Streaming follows the same **`agent.execute_stream(...)`** pattern as other providers — Groq deltas are merged in the provider adapter. **Opening** the stream shares the same **429** / **`Retry-After`** policy as non-stream chat (**v0.7.9+**).

## Models

Groq hosts many **Llama**, **Mixtral**, **Qwen**, **GPT-OSS**, and other checkpoints; names and capabilities change frequently. Use the **Groq console** as source of truth:

- [Models](https://console.groq.com/docs/models)
- [OpenAI compatibility notes](https://console.groq.com/docs/openai) (unsupported fields, temperature quirks)

Common defaults in our examples:

| Model id | Typical use |
|----------|-------------|
| `llama-3.3-70b-versatile` | General chat and tools |
| `openai/gpt-oss-20b` | Structured output demos (`json_schema`) |

## Runnable examples (monorepo)

Full scripts (Direct → Autonomous, structured output) live in the NucleusIQ repository:

**Path:** [`src/providers/inference/groq/examples/`](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/groq/examples)

| Script | Mode | Notes |
|--------|------|--------|
| `01_groq_direct.py` | DIRECT | Plain completion |
| `02_groq_direct_with_tool.py` | DIRECT | Single-hop tool |
| `03_groq_standard_tools.py` | STANDARD | Multi-step tool loop |
| `04_groq_autonomous.py` | AUTONOMOUS | Critic / Refiner path |
| `05_groq_structured_output.py` | DIRECT | Pydantic `response_format` |
| `06_groq_builtin_tools_status.py` | — | Built-in tools status (Phase B placeholder) |

From the provider directory after **`uv sync`**:

```bash
cd src/providers/inference/groq
uv run python examples/agents/01_groq_direct.py
```

## Design & roadmap

Maintainer-facing tracker (Phase A vs B, HTTP caveats, CI): [`docs/design/GROQ_PROVIDER.md`](https://github.com/nucleusbox/NucleusIQ/blob/main/docs/design/GROQ_PROVIDER.md) in the main repo.

Package README (install + dev): [`src/providers/inference/groq/README.md`](https://github.com/nucleusbox/NucleusIQ/blob/main/src/providers/inference/groq/README.md).

## See also

- [Groq quickstart](../examples/groq-quickstart.md) — Three execution modes with copy-paste examples  
- [Providers](../providers.md) — Porting agents across backends  
- [Models](../models.md) — Provider matrix and parameter tabs  
- [Installation](../install.md) — Env vars and verify installs  
- [Structured output](../structured-output.md) — Framework-wide patterns  
- [Execution modes](../execution-modes.md) — Gearbox behavior  
