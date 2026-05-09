# Groq quickstart example

Use **[Groq](https://groq.com/)** Chat Completions through **`nucleusiq-groq`** across all three execution modes.

**Requirements:** **`nucleusiq>=0.7.9`**, **`nucleusiq-groq` 0.1.0b1** (public beta). Use **`BaseGroq(..., async_mode=True)`** and call **`await agent.initialize()`** before **`execute()`** so startup matches the [monorepo scripts](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/groq/examples/agents).

*Prompt refactor (v0.7.6+): `prompt` is mandatory — always pass **`ZeroShotPrompt().configure(...)`**.*

## Setup

```bash
pip install "nucleusiq>=0.7.9" "nucleusiq-groq>=0.1.0b1"
export GROQ_API_KEY="gsk_..."
# Optional defaults used by monorepo examples:
# export GROQ_MODEL=llama-3.3-70b-versatile
```

## Gear 1: DIRECT mode

Fast path — single LLM hop for straightforward questions:

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_groq import BaseGroq, GroqLLMParams


async def main():
    llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)
    agent = Agent(
        name="groq-direct",
        prompt=ZeroShotPrompt().configure(
            system="Give concise, accurate answers.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.DIRECT,
            llm_params=GroqLLMParams(temperature=0.3, max_output_tokens=256),
        ),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(id="gq1", objective="What is the speed of light in vacuum?"),
    )
    print(result.output)


asyncio.run(main())
```

## Gear 2: STANDARD mode with tools

Linear tool loop — good for lookups and arithmetic:

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_groq import BaseGroq, GroqLLMParams


@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price for a ticker symbol."""
    prices = {"AAPL": "$195.50", "GOOGL": "$175.20", "MSFT": "$420.30"}
    return prices.get(symbol.upper(), f"Unknown symbol: {symbol}")


@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))


async def main():
    llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)
    agent = Agent(
        name="groq-analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a financial analyst. Use tools when you need data or math.",
        ),
        llm=llm,
        tools=[get_stock_price, calculate],
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            llm_params=GroqLLMParams(
                temperature=0.4,
                max_output_tokens=512,
                parallel_tool_calls=True,
            ),
        ),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(
            id="gq2",
            objective=(
                "What is the total value of 100 shares of AAPL and 50 shares of GOOGL?"
            ),
        ),
    )
    print(result.output)


asyncio.run(main())
```

!!! tip "`parallel_tool_calls`"

    With **`parallel_tool_calls=True`**, unknown models log a **warning** by default. Set **`GroqLLMParams(strict_model_capabilities=True)`** to **fail fast** before the HTTP call if the model is outside the built-in allowlist — see [Groq provider guide](../guides/groq-provider.md) (**Model capabilities** section).

## Gear 3: AUTONOMOUS mode

Planning plus Critic / Refiner — higher tool budget and verification:

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_groq import BaseGroq, GroqLLMParams


@tool
def search_knowledge(query: str) -> str:
    """Search the knowledge base for information."""
    return f"Knowledge base result for '{query}': [relevant data here]"


async def main():
    llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)
    agent = Agent(
        name="groq-researcher",
        prompt=ZeroShotPrompt().configure(
            system="You are a thorough researcher. Break down complex questions.",
        ),
        llm=llm,
        tools=[search_knowledge],
        config=AgentConfig(
            execution_mode=ExecutionMode.AUTONOMOUS,
            require_quality_check=True,
            max_iterations=5,
            llm_params=GroqLLMParams(temperature=0.5, max_output_tokens=1024),
        ),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(
            id="gq3",
            objective=(
                "Compare the economic impact of AI adoption in healthcare vs manufacturing."
            ),
        ),
    )
    print(result.output)


asyncio.run(main())
```

## Structured output (optional)

When your Groq model supports **`json_schema`** ([Groq structured outputs](https://console.groq.com/docs/structured-outputs)), pass **`response_format=YourModel`** on **`Agent`**. Many teams use **`openai/gpt-oss-20b`** for demos — verify against Groq’s current matrix.

See [Structured output](../structured-output.md) and **[Groq provider guide](../guides/groq-provider.md)** (structured-output section).

## Runnable scripts in the repo

Clone **[NucleusIQ](https://github.com/nucleusbox/NucleusIQ)** and run from **`src/providers/inference/groq`**:

```bash
uv sync
uv run python examples/agents/01_groq_direct.py
uv run python examples/agents/03_groq_standard_tools.py
uv run python examples/agents/05_groq_structured_output.py
```

Integration smoke tests (live API) use **`pytest -m integration`** with **`GROQ_API_KEY`** — see the provider **`README`**.

## See also

- [Groq provider guide](../guides/groq-provider.md) — Beta scope, 429 / **`Retry-After`** retries, capabilities, limitations
- [Installation](../install.md) — Package matrix and environment variables
- [Gemini quickstart](gemini-quickstart.md) — Same three gears on Google Gemini
- [Basic agent example](basic-agent.md) — OpenAI-focused patterns with context management
