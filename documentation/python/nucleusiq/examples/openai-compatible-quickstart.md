# OpenAI-compatible quickstart

Run the same NucleusIQ `Agent` against **vLLM**, **SGLang**, **llama.cpp**, **LM Studio**, or any Chat Completions server.

**Requirements:** **`nucleusiq>=0.7.13`**, **`nucleusiq-openai-compatible` 0.1.0**. Full reference: [OpenAI-compatible provider](../guides/openai-compatible-provider.md).

*Always pass `prompt=ZeroShotPrompt().configure(...)`. Always execute a `Task` or a dict with `id` and `objective`. Read `result.output`.*

## Setup

```bash
pip install "nucleusiq>=0.7.13" nucleusiq-openai-compatible

export OPENAI_COMPATIBLE_BASE_URL="http://127.0.0.1:8000/v1"
export OPENAI_COMPATIBLE_MODEL="gemma-4-27b-it"
# export OPENAI_COMPATIBLE_API_KEY="..."   # only if the server requires one
```

A local vLLM process for these snippets:

```bash
vllm serve google/gemma-4-27b-it \
  --served-model-name gemma-4-27b-it \
  --max-model-len 32768
```

## Gear 1: DIRECT

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai_compatible import OpenAICompatibleLLM


async def main() -> None:
    llm = OpenAICompatibleLLM(
        base_url="http://127.0.0.1:8000/v1",
        model="gemma-4-27b-it",
        context_window=32_768,
        engine="vllm",
    )
    agent = Agent(
        name="compat-direct",
        prompt=ZeroShotPrompt().configure(
            system="Give concise, accurate answers.",
        ),
        llm=llm,
        config=AgentConfig(execution_mode=ExecutionMode.DIRECT),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(id="c1", objective="What is the capital of France?"),
    )
    print(result.output)


asyncio.run(main())
```

## Gear 2: STANDARD with tools

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai_compatible import OpenAICompatibleLLM


@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a ticker symbol."""
    prices = {"AAPL": "$195.50", "GOOGL": "$175.20"}
    return prices.get(symbol.upper(), f"Unknown symbol: {symbol}")


async def main() -> None:
    llm = OpenAICompatibleLLM(
        base_url="http://127.0.0.1:8000/v1",
        model="gemma-4-27b-it",
        context_window=32_768,
        engine="vllm",
    )
    agent = Agent(
        name="compat-tools",
        prompt=ZeroShotPrompt().configure(
            system="Use tools when you need market data.",
        ),
        llm=llm,
        tools=[get_stock_price],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(id="c2", objective="What is AAPL trading at?"),
    )
    print(result.output)


asyncio.run(main())
```

## Preflight check

```python
report = await llm.validate()
if not report.ok:
    print(report.render())
```

## Unauthenticated local server

Omit `api_key` entirely. Do not pass `"EMPTY"` or `"none"`:

```python
llm = OpenAICompatibleLLM(
    base_url="http://127.0.0.1:8080/v1",
    model="local-model",
    engine="llamacpp",
    context_window=8192,
)
```

## Azure OpenAI v1

```python
import os

from nucleusiq_openai_compatible import HeaderAuth, OpenAICompatibleLLM

llm = OpenAICompatibleLLM(
    base_url="https://my-resource.openai.azure.com/openai/v1",
    model="my-deployment",
    engine="azure",
    auth=HeaderAuth("api-key", os.environ["AZURE_OPENAI_API_KEY"]),
)
```

This is the v1 Chat Completions URL, not the Azure SDK and not `/openai/deployments/...`.

## Next

- [Provider guide](../guides/openai-compatible-provider.md) — engines, auth strategies, structured-output policy, Azure limits
- [OpenAI cloud](../guides/openai-provider.md) — Responses API and hosted tools
- [Ollama native](../guides/ollama-provider.md) — official Ollama SDK, not the `/v1` shim
