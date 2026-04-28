# Execution modes

NucleusIQ uses the **Gearbox Strategy** — three execution modes that scale from simple chat to autonomous reasoning. All modes work identically with any LLM provider (OpenAI, Gemini).

## Comparison

| Capability | Direct | Standard | Autonomous |
|------------|--------|----------|------------|
| Memory | Yes | Yes | Yes |
| Plugins | Yes | Yes | Yes |
| Tools | Yes (default **25** / run) | Yes (default **80** / run) | Yes (default **300** / run) |
| Tool loop | Yes | Yes | Yes |
| Streaming | Yes | Yes | Yes |
| Structured output | Yes | Yes | Yes |
| Context management | Yes | Yes | Yes |
| Synthesis pass | No | **Yes** | **Yes** |
| Task decomposition | No | No | **Yes** |
| Critic (verification) | No | No | **Yes** |
| Refiner (correction) | No | No | **Yes** |
| Validation pipeline | No | No | **Yes** |

Default **tool-call budgets** (and the maximum number of **user-registered** tools on the agent, excluding framework recall tools) are **25 / 80 / 300** for Direct / Standard / Autonomous. Override any time with `AgentConfig(max_tool_calls=N)` or read the resolved value via `config.get_effective_max_tool_calls()`.

## Direct

Fast, single LLM call. Best for Q&A, classification, and simple lookups.

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="classifier",
        prompt=ZeroShotPrompt().configure(
            system="Classify the user's message as: positive, negative, or neutral. Respond with only the label.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        config=AgentConfig(execution_mode=ExecutionMode.DIRECT),
    )
    result = await agent.execute({"id": "d1", "objective": "I love this product, it's amazing!"})
    print(result.output)  # "positive"

asyncio.run(main())
```

Use Direct when latency matters and the task doesn't need tools or iteration.

## Standard (default)

Tool-enabled, linear execution. The agent calls tools iteratively until it has enough information to answer.

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def get_stock_price(symbol: str) -> str:
    """Get current stock price for a ticker symbol."""
    prices = {"AAPL": "$195.50", "GOOGL": "$175.20", "MSFT": "$420.30"}
    return prices.get(symbol.upper(), f"Unknown: {symbol}")

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

async def main():
    agent = Agent(
        name="finance-bot",
        prompt=ZeroShotPrompt().configure(
            system="You are a financial assistant. Use tools to look up stock prices and do calculations.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[get_stock_price, calculate],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({
        "id": "s1",
        "objective": "What is the total value of 100 shares of AAPL and 50 shares of GOOGL?",
    })
    print(result.output)
    print(f"Duration: {result.duration_ms}ms")

asyncio.run(main())
```

Use Standard for most production workflows: data lookup, calculations, file operations, API calls.

### Synthesis pass

*New in v0.7.6*

After multiple rounds of tool calls, Standard mode makes one final LLM call **without tools** and with an explicit instruction to write the full deliverable. This breaks the "mode inertia" pattern where the model stays in tool-calling behaviour and returns a terse summary instead of full output.

How it works:

1. Agent enters tool loop — calls tools, receives results, decides next action
2. When the LLM stops calling tools, the framework detects the loop has ended
3. If `enable_synthesis=True` (default), one final LLM call is made **without tools**
4. The final call includes an explicit instruction to produce the complete deliverable
5. The LLM writes the full response without being distracted by tool availability

```python
config = AgentConfig(
    execution_mode=ExecutionMode.STANDARD,
    enable_synthesis=True,  # Default: True
)
```

Set `enable_synthesis=False` only if your agent's task is simple enough that synthesis adds unnecessary latency.

## Autonomous

Planning, multi-step execution with Critic/Refiner verification. The agent decomposes complex tasks, executes subtasks, and verifies its own output.

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def analyze_risk(factor: str) -> str:
    """Analyze a specific risk factor."""
    risks = {
        "market": "HIGH — 30% revenue impact in downturn",
        "supply_chain": "MEDIUM — 2-3 month disruption tolerance",
        "regulatory": "LOW — compliant with current frameworks",
    }
    return risks.get(factor, f"No data for: {factor}")

async def main():
    agent = Agent(
        name="risk-analyst",
        prompt=ZeroShotPrompt().configure(
            system=(
                "You are a risk analyst. Break down complex assessments into subtasks. "
                "Analyze each risk factor using tools, then provide a comprehensive report "
                "with severity ratings and mitigation recommendations."
            ),
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[analyze_risk],
        config=AgentConfig(
            execution_mode=ExecutionMode.AUTONOMOUS,
            require_quality_check=True,
            max_iterations=5,
            max_tool_calls=50,
        ),
    )
    result = await agent.execute({
        "id": "a1",
        "objective": "Assess market, supply chain, and regulatory risks for Q4.",
    })
    print(result.output)

    # Autonomous detail (when tracing is enabled)
    if result.autonomous:
        print(f"Sub-tasks: {result.autonomous.sub_task_names}")

asyncio.run(main())
```

Use Autonomous for complex, high-stakes tasks where correctness matters more than speed.

### What happens under the hood

1. **Decomposition** — The agent breaks the task into subtasks
2. **Execution** — Each subtask runs in its own Standard-mode loop with tools
3. **Critic** — An independent verification pass checks if the output is correct
4. **Refiner** — If the Critic finds gaps, the Refiner corrects them
5. **Synthesis** — A final LLM call (without tools) produces the complete deliverable (v0.7.6)
6. **Return** — The verified, complete result is returned

### Sub-agent telemetry rollup

*New in v0.7.6*

In Autonomous mode, sub-agent LLM calls, tool calls, and context telemetry are merged into the parent agent's `AgentResult`. This gives you a complete view of the entire execution tree in one place.

## Context management across modes

*New in v0.7.6*

All three modes support context window management via `ContextConfig`. Add it to prevent context overflow in tool-heavy agents:

```python
from nucleusiq.agents.context import ContextConfig, ContextStrategy

config = AgentConfig(
    execution_mode=ExecutionMode.STANDARD,
    context=ContextConfig(
        optimal_budget=50_000,
        strategy=ContextStrategy.PROGRESSIVE,
    ),
)
```

See [Context management](context-management.md) for details.

## Choosing a mode

| Scenario | Recommended mode | Why |
|----------|-----------------|-----|
| Simple Q&A, classification | DIRECT | Fastest, single LLM call |
| Tool-enabled data workflows | STANDARD | Iterative tool use, synthesis pass |
| Complex analysis with verification | AUTONOMOUS | Decomposition + Critic/Refiner |
| Chat applications | STANDARD | Good balance of capability and speed |
| Code generation with validation | AUTONOMOUS | Critic verifies correctness |
| Latency-sensitive endpoints | DIRECT | Minimal overhead |
| Research tasks with many sources | STANDARD + context mgmt | Handles large context |

## See also

- [Agents](agents.md) — Agent configuration and lifecycle
- [Context management](context-management.md) — Context window management
- [Tools](tools.md) — Built-in tools, `@tool` decorator, and provider native tools
- [Strategy guide](guides/strategy.md) — Detailed mode selection guidance
- [Examples: Autonomous workflow](examples/autonomous-workflow.md) — Complete autonomous example
