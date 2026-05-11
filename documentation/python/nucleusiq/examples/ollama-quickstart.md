# Ollama quickstart

Use **local or hosted [Ollama](https://ollama.com/)** with NucleusIQ through **`nucleusiq-ollama`**.

!!! danger "Alpha"

    **`nucleusiq-ollama` 0.1.0a1** is **alpha** — pre-release APIs. Requires **`nucleusiq>=0.7.10`**. Always **`pip install "nucleusiq>=0.7.10" "nucleusiq-ollama>=0.1.0a1"`** (or pin **`==0.1.0a1`**). See **[Ollama provider](../guides/ollama-provider.md)** for limitations.

**Pattern:** **`BaseOllama(..., async_mode=True)`**, **`await agent.initialize()`**, mandatory **`prompt=`**.

## Setup

```bash
pip install "nucleusiq>=0.7.10" "nucleusiq-ollama>=0.1.0a1"
# Ensure Ollama is running and you have pulled a model, e.g.:
# ollama pull llama3.2
```

Optional **`.env`** (same idea as monorepo examples):

```env
# OLLAMA_HOST=http://127.0.0.1:11434
# OLLAMA_API_KEY=...   # if your endpoint requires Bearer auth
OLLAMA_MODEL=llama3.2
```

## Gear 1: DIRECT mode

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_ollama import BaseOllama, OllamaLLMParams


async def main():
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    llm = BaseOllama(model_name=model, async_mode=True)

    agent = Agent(
        name="ollama-direct",
        prompt=ZeroShotPrompt().configure(
            system="Give concise, accurate answers.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.DIRECT,
            llm_params=OllamaLLMParams(temperature=0.3, max_output_tokens=256),
        ),
    )

    await agent.initialize()

    result = await agent.execute(
        Task(id="o1", objective="What is the speed of light in vacuum?"),
    )
    print(result.output)


asyncio.run(main())
```

## Gear 2: STANDARD mode with tools

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_ollama import BaseOllama, OllamaLLMParams


@tool
def multiply(a: float, b: float) -> str:
    """Multiply two numbers."""
    return str(a * b)


async def main():
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    llm = BaseOllama(model_name=model, async_mode=True)

    agent = Agent(
        name="ollama-tools",
        prompt=ZeroShotPrompt().configure(
            system="Use tools when arithmetic is required.",
        ),
        llm=llm,
        tools=[multiply],
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            llm_params=OllamaLLMParams(temperature=0.4, max_output_tokens=512),
        ),
    )

    await agent.initialize()

    result = await agent.execute(
        Task(id="o2", objective="What is 12.5 times 4?"),
    )
    print(result.output)


asyncio.run(main())
```

## Streaming & capability matrix

- **Live tokens:** run **`examples/agents/02_ollama_stream_live.py`** in the repo — prints **`call_stream`** deltas.
- **Full matrix** (chat × stream × structured × thinking × DIRECT/STANDARD/AUTONOMOUS): **`03_ollama_capabilities_matrix.py`** with **`--only`** filters.

```bash
cd src/providers/inference/ollama
uv sync --group dev
uv run python examples/agents/03_ollama_capabilities_matrix.py --only structured
```

## See also

- [Ollama provider](../guides/ollama-provider.md) — Alpha scope, **`think`**, structured output cautions, env vars  
- [Installation](../install.md) — Package table + **`nucleusiq[http]`** (**v0.7.10**)  
- [Groq quickstart](groq-quickstart.md) — Cloud Llama-style inference for comparison  
