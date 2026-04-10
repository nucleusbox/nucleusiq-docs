# Gemini quickstart example

This example demonstrates NucleusIQ with Google Gemini across all three execution modes.

*Updated for v0.7.6: `prompt` is now mandatory.*

## Setup

```bash
pip install nucleusiq nucleusiq-gemini
export GEMINI_API_KEY="your-api-key"
```

## Gear 1: DIRECT mode

Fast, single LLM call for simple questions:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_gemini import BaseGemini

async def main():
    llm = BaseGemini(model_name="gemini-2.5-flash")
    agent = Agent(
        name="quick-answerer",
        prompt=ZeroShotPrompt().configure(
            system="Give concise, accurate answers.",
        ),
        llm=llm,
        config=AgentConfig(execution_mode=ExecutionMode.DIRECT),
    )
    result = await agent.execute({"id": "g1", "objective": "What is the speed of light?"})
    print(result.output)

asyncio.run(main())
```

## Gear 2: STANDARD mode with tools

Tool-enabled loop for tasks requiring external data:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_gemini import BaseGemini

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
    llm = BaseGemini(model_name="gemini-2.5-flash")
    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a financial analyst. Use tools to look up data.",
        ),
        llm=llm,
        tools=[get_stock_price, calculate],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute(
        {
            "id": "g2",
            "objective": "What is the total value of 100 shares of AAPL and 50 shares of GOOGL?",
        }
    )
    print(result.output)

asyncio.run(main())
```

## Gear 3: AUTONOMOUS mode

Complex multi-step task with Critic verification:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_gemini import BaseGemini, GeminiLLMParams, GeminiThinkingConfig

@tool
def search_knowledge(query: str) -> str:
    """Search the knowledge base for information."""
    return f"Knowledge base result for '{query}': [relevant data here]"

async def main():
    llm = BaseGemini(model_name="gemini-2.5-flash")
    agent = Agent(
        name="researcher",
        prompt=ZeroShotPrompt().configure(
            system="You are a thorough researcher. Break down complex questions.",
        ),
        llm=llm,
        tools=[search_knowledge],
        config=AgentConfig(
            execution_mode=ExecutionMode.AUTONOMOUS,
            require_quality_check=True,
            max_iterations=5,
            llm_params=GeminiLLMParams(
                thinking_config=GeminiThinkingConfig(thinking_budget=2048),
            ),
        ),
    )
    result = await agent.execute(
        {
            "id": "g3",
            "objective": "Compare the economic impact of AI adoption in healthcare vs manufacturing.",
        }
    )
    print(result.output)

asyncio.run(main())
```

## With native Google Search

Use Gemini's server-side Google Search for real-time grounding:

```python
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_gemini import GeminiTool

agent = Agent(
    name="news-agent",
    prompt=ZeroShotPrompt().configure(
        system="Answer with the latest information from the web.",
    ),
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[GeminiTool.google_search()],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "g4", "objective": "What are the top AI news stories today?"})
```

## Mixing native + custom tools

*New in v0.7.5*

NucleusIQ handles the Gemini API restriction transparently — just pass all tools to a single agent:

```python
from nucleusiq.tools.decorators import tool
from nucleusiq_gemini import GeminiTool

@tool
def summarize(text: str) -> str:
    """Summarize the given text."""
    return f"Summary of: {text[:50]}..."

agent = Agent(
    name="hybrid-researcher",
    prompt=ZeroShotPrompt().configure(
        system="Search the web for information, then summarize findings.",
    ),
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[GeminiTool.google_search(), summarize],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

See [Gemini provider guide — Mixing native and custom tools](../guides/gemini-provider.md#mixing-native-and-custom-tools).

## See also

- [Gemini provider guide](../guides/gemini-provider.md) — Full Gemini documentation
- [Basic agent example](basic-agent.md) — OpenAI-based example
- [Context management](../context-management.md) — Context window management
