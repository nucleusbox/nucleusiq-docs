# Ollama provider

Run **[Ollama](https://ollama.com/)** models (local daemon or a reachable HTTP API) through NucleusIQ using the official **`ollama`** Python SDK — **no LangChain**.

!!! danger "Alpha release"

    **`nucleusiq-ollama` 0.1.0a1** is a **PyPI pre-release** (**`Development Status :: 3 - Alpha`**). APIs and behavior may change. Requires **`nucleusiq>=0.7.10`** (structured-output resolver wiring). Treat as **experimental** for production.

## What you get (Phase A)

| Capability | Supported |
|------------|-----------|
| Chat (`/api/chat`) | Yes |
| Streaming (`StreamEvent`, tokens + metadata) | Yes |
| **`@tool`** / function tools | Yes |
| Structured output (`format` / JSON schema) | Yes — combining **`response_format`** with **tools** drops format with a **warning** (same caution pattern as Groq) |
| **`think`** (reasoning / **`THINKING`** stream events) | Yes |
| Vision / embeddings | **Not wired** in **`BaseOllama`** yet |

## Prerequisites

1. **Ollama** installed and a model pulled, e.g. `ollama pull llama3.2` (names depend on your catalog).
2. Daemon reachable at **`OLLAMA_HOST`** or the SDK default (`http://127.0.0.1:11434` when unset).

## Installation

```bash
pip install nucleusiq nucleusiq-ollama
```

Pin the alpha explicitly when reproducibility matters:

```bash
pip install "nucleusiq>=0.7.10" "nucleusiq-ollama==0.1.0a1"
```

Dependency: **`ollama>=0.5.0,<1.0`**.

## Environment

| Variable | Purpose |
|----------|---------|
| **`OLLAMA_HOST`** | Passed as **`host=`** to the **`ollama`** **`AsyncClient`** / **`Client`** (omit for local default). |
| **`OLLAMA_API_KEY`** | Optional **Bearer** token for hosted / authenticated endpoints. |
| **`OLLAMA_MODEL`** | Optional default model id (examples often use **`llama3.2`**). |

```bash
# export OLLAMA_HOST=http://127.0.0.1:11434
# export OLLAMA_API_KEY=...   # only if your endpoint requires it
export OLLAMA_MODEL=llama3.2
```

## Quick start (Direct)

Use **`BaseOllama`** with **`async_mode=True`**. Call **`await agent.initialize()`** before **`execute()`** (matches monorepo examples).

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_ollama import BaseOllama, OllamaLLMParams


async def main() -> None:
    llm = BaseOllama(model_name="llama3.2", async_mode=True)

    agent = Agent(
        name="ollama-demo",
        prompt=ZeroShotPrompt().configure(
            system="You are a concise assistant.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.DIRECT,
            llm_params=OllamaLLMParams(temperature=0.3, max_output_tokens=256),
        ),
    )

    await agent.initialize()

    result = await agent.execute(
        Task(id="ollama-1", objective="What is the capital of France?"),
    )
    print(result.output)


asyncio.run(main())
```

## Tools (Standard / Autonomous)

Ollama accepts OpenAI-style **function** tools via **`to_ollama_function_tool`**. From the agent’s perspective this is the same **`@tool`** workflow as other providers.

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_ollama import BaseOllama, OllamaLLMParams


@tool
def add(a: int, b: int) -> str:
    """Add two integers."""
    return str(a + b)


llm = BaseOllama(model_name="llama3.2", async_mode=True)
agent = Agent(
    name="ollama-tools",
    prompt=ZeroShotPrompt().configure(system="Use tools for arithmetic."),
    llm=llm,
    tools=[add],
    config=AgentConfig(
        execution_mode=ExecutionMode.STANDARD,
        llm_params=OllamaLLMParams(temperature=0.4, max_output_tokens=512),
    ),
)
```

There are **no Ollama “native server tools”** wired like Gemini **`GoogleTool`** — local **`@tool`** only in this alpha.

## OllamaLLMParams

Extends **`LLMParams`** with **`extra="forbid"`**.

| Field | Meaning |
|-------|---------|
| **`think`** | `bool` or **`"low"`** / **`"medium"`** / **`"high"`** — maps to Ollama **`think`**; streams **`THINKING`** events when enabled. |
| **`keep_alive`** | Ollama model keep-alive duration (`float`, `str`, or `None`). |

Framework fields such as **`temperature`**, **`max_output_tokens`** (→ Ollama **`num_predict`**), **`top_p`**, penalties, **`stop`**, **`seed`** are merged into Ollama **`options`** — see the design doc.

```python
from nucleusiq.agents.config import AgentConfig
from nucleusiq_ollama import OllamaLLMParams

config = AgentConfig(
    llm_params=OllamaLLMParams(
        temperature=0.2,
        max_output_tokens=512,
        think="medium",
        keep_alive="5m",
    ),
)
```

## Structured output

With **`nucleusiq>=0.7.10`**, the core **`structured_output` resolver** recognizes **`BaseOllama`** so **`Agent(..., response_format=MyModel)`** uses the correct provider payload. Model and schema support still depend on **your Ollama model** and server version — validate on your stack.

!!! warning "Tools + schema"

    If the agent has **tools**, structured **`format`** is **dropped** for safety (logged). Prefer a tools-only pass or a separate **`execute`** without tools when you need strict JSON.

## Streaming

Use **`agent.execute_stream(...)`** like other providers; the adapter emits **`StreamEvent`** tokens (and **`THINKING`** when **`think`** is enabled).

## Runnable examples (monorepo)

From **`src/providers/inference/ollama`** after **`uv sync`**:

```bash
uv run python examples/agents/00_ollama_smoke.py
uv run python examples/agents/01_ollama_direct.py
uv run python examples/agents/02_ollama_stream_live.py
uv run python examples/agents/03_ollama_capabilities_matrix.py
```

**[`03_ollama_capabilities_matrix.py`](https://github.com/nucleusbox/NucleusIQ/blob/main/src/providers/inference/ollama/examples/agents/03_ollama_capabilities_matrix.py)** — chat, stream, structured output, and thinking × **DIRECT / STANDARD / AUTONOMOUS** (filter with **`--only`**).

Package README: [`src/providers/inference/ollama/README.md`](https://github.com/nucleusbox/NucleusIQ/blob/main/src/providers/inference/ollama/README.md).

## See also

- [Ollama quickstart](../examples/ollama-quickstart.md) — Copy-paste gears  
- [Providers](../providers.md) — Portability  
- [Models](../models.md) — Parameter tabs  
- [Installation](../install.md) — **`nucleusiq[http]`** optional extra (**v0.7.10**)  
- [Structured output](../structured-output.md) — Framework patterns  
