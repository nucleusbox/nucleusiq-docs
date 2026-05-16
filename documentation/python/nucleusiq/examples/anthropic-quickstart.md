# Anthropic (Claude) quickstart

Use **[Anthropic](https://www.anthropic.com/) Claude** through **`nucleusiq-anthropic`** (**Messages API**, official **`anthropic`** SDK) across NucleusIQ execution modes.

!!! danger "Alpha"

    **`nucleusiq-anthropic` 0.1.0a1** — **pre-release**. Requires **`nucleusiq>=0.7.10`**, **`anthropic>=0.40,<1`**. Pin **`==0.1.0a1`** when you need reproducible builds.

**Pattern:** **`BaseAnthropic(..., async_mode=True)`**, **`await agent.initialize()`**, mandatory **`prompt=`**. Sampling via **`LLMParams`** on **`AgentConfig`**; **`AnthropicLLMParams`** on **`BaseAnthropic`** for **`top_k`** / beta headers — see **[Anthropic provider](../guides/anthropic-provider.md)**.

## Setup

```bash
pip install "nucleusiq>=0.7.10" "nucleusiq-anthropic>=0.1.0a1"
export ANTHROPIC_API_KEY="sk-ant-..."
# Optional — examples default to a widely documented id; override if your org differs:
# export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

If **`404` model not found**, list models your key can access — **`examples/agents/09_anthropic_list_models.py`** in the **[monorepo](https://github.com/nucleusbox/NucleusIQ)** — then export **`ANTHROPIC_MODEL`** to a printed **`id`**.

## Gear 1: DIRECT mode

Single hop — great for Q&A without tools:

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.llms.llm_params import LLMParams
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_anthropic import BaseAnthropic


async def main():
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    llm = BaseAnthropic(model_name=model, async_mode=True)
    agent = Agent(
        name="anthropic-direct",
        prompt=ZeroShotPrompt().configure(
            system="Give concise, accurate answers.",
        ),
        llm=llm,
        config=AgentConfig(
            execution_mode=ExecutionMode.DIRECT,
            llm_params=LLMParams(temperature=0.3, max_output_tokens=256),
        ),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(id="claude-1", objective="What is the speed of light in vacuum?"),
    )
    print(result.output)


asyncio.run(main())
```

## Gear 2: STANDARD mode with tools

Linear tool loop — **`@tool`** decorators work like other providers:

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.llms.llm_params import LLMParams
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_anthropic import BaseAnthropic


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
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    llm = BaseAnthropic(model_name=model, async_mode=True)
    agent = Agent(
        name="anthropic-analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a financial analyst. Use tools when you need data or math.",
        ),
        llm=llm,
        tools=[get_stock_price, calculate],
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            llm_params=LLMParams(temperature=0.4, max_output_tokens=512),
        ),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(
            id="claude-2",
            objective=(
                "What is the total value of 100 shares of AAPL and 50 shares of GOOGL?"
            ),
        ),
    )
    print(result.output)


asyncio.run(main())
```

## Gear 3: AUTONOMOUS mode

Planning plus Critic / Refiner — higher tool budget:

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.llms.llm_params import LLMParams
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_anthropic import BaseAnthropic


@tool
def search_knowledge(query: str) -> str:
    """Search the knowledge base for information."""
    return f"Knowledge base result for '{query}': [relevant data here]"


async def main():
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    llm = BaseAnthropic(model_name=model, async_mode=True)
    agent = Agent(
        name="anthropic-researcher",
        prompt=ZeroShotPrompt().configure(
            system="You are a thorough researcher. Break down complex questions.",
        ),
        llm=llm,
        tools=[search_knowledge],
        config=AgentConfig(
            execution_mode=ExecutionMode.AUTONOMOUS,
            require_quality_check=True,
            max_iterations=5,
            llm_params=LLMParams(temperature=0.5, max_output_tokens=1024),
        ),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(
            id="claude-3",
            objective=(
                "Compare the economic impact of AI adoption in healthcare vs manufacturing."
            ),
        ),
    )
    print(result.output)


asyncio.run(main())
```

## Structured output (optional)

When your Messages API model supports **native JSON Schema outputs**, pass **`response_format=`** on **`Agent`**. With **tools** enabled, structured output is **skipped** with a **warning** — test structured-only paths first.

See [Structured output](../structured-output.md) and **`examples/output_parsers/anthropic_native_structured_example.py`** in the repo.

## Runnable scripts in the repo

From **`src/providers/llms/anthropic`**:

```bash
uv sync --group full
uv run python examples/agents/01_anthropic_direct.py
uv run python examples/agents/03_anthropic_standard_tools.py
uv run python examples/agents/05_anthropic_stream.py
```

## See also

- [Anthropic provider guide](../guides/anthropic-provider.md) — Alpha scope, env, structured-output caveats, retries
- [Installation](../install.md) — Package matrix
- [Groq quickstart](groq-quickstart.md) — Same three gears on Groq (**beta**)
- [Basic agent](basic-agent.md) — OpenAI/Gemini-focused patterns + context management
