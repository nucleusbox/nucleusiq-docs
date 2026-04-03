# Agents

An agent is a managed runtime with memory, tools, policy, streaming, structure, and responsibilities.

## Creating an agent

=== "With OpenAI"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq_openai import BaseOpenAI

    agent = Agent(
        name="analyst",
        llm=BaseOpenAI(model_name="gpt-4o-mini"),
        model="gpt-4o-mini",
        instructions="You are a data analyst. Answer questions accurately.",
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    ```

=== "With Gemini"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq_gemini import BaseGemini

    agent = Agent(
        name="analyst",
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        model="gemini-2.5-flash",
        instructions="You are a data analyst. Answer questions accurately.",
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    ```

=== "With MockLLM (testing)"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.core.llms.mock_llm import MockLLM

    agent = Agent(
        name="analyst",
        llm=MockLLM(),
        instructions="You are a data analyst.",
    )
    ```

## Agent lifecycle

1. **Create** — Instantiate with an LLM, config, tools, plugins, and memory.
2. **Execute** — `result = await agent.execute({"id": "t1", "objective": "What is 2+2?"})` or pass a `Task` object. Returns an `AgentResult` model (v0.7.2+); access the response via `result.output`.
3. **Stream** — `async for event in agent.execute_stream({"id": "t2", "objective": "Write a poem"}):` for real-time output.
4. **Inspect** — `agent.last_usage` for token counts, then `CostTracker` for cost estimation.

## AgentResult

`execute()` returns an `AgentResult` — a structured response contract that provides the LLM output, execution metadata, and optional tracing data.

```python
result = await agent.execute(task)

# Output text
print(result.output)       # The LLM's response text
print(str(result))         # Same — str() returns output

# Status
print(result.status)       # ResultStatus.SUCCESS, ERROR, or HALTED
print(result.is_error)     # True if execution failed
print(result.error)        # Error message if failed

# Identity
print(result.agent_name)   # Agent name
print(result.mode)         # Execution mode used
print(result.model)        # LLM model used
print(result.duration_ms)  # Execution time in milliseconds

# Observability (requires enable_tracing=True)
print(result.tool_calls)   # Traced tool calls (empty tuple if tracing disabled)
print(result.llm_calls)    # Traced LLM calls
print(result.warnings)     # Any warnings during execution
```

## End-to-end example

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.tools.decorators import tool
from nucleusiq_gemini import BaseGemini

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22°C, Sunny"

async def main():
    agent = Agent(
        name="assistant",
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        model="gemini-2.5-flash",
        instructions="You are a helpful assistant. Use tools when needed.",
        tools=[get_weather],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({"id": "t3", "objective": "What's the weather in Paris?"})
    print(result.output)

    # Token usage
    print(agent.last_usage.display())

asyncio.run(main())
```

## Usage tracking and cost estimation

After execution, inspect token usage and estimate costs:

```python
result = await agent.execute({"id": "t4", "objective": "Analyze this data"})

# Token usage
usage = agent.last_usage
print(usage.display())

# Cost estimation
from nucleusiq.agents.usage import CostTracker
tracker = CostTracker()
cost = tracker.estimate(usage, model="gemini-2.5-flash")
print(f"Estimated cost: ${cost.total_cost:.6f}")
```

`usage.by_origin` separates user tokens (initial MAIN call) from framework overhead (planning, tool loops, critic, refiner).

## Error handling

All providers raise the same framework-level exceptions:

```python
from nucleusiq.errors import NucleusIQError
from nucleusiq.llms.errors import RateLimitError, AuthenticationError, LLMError
from nucleusiq.tools.errors import ToolExecutionError
from nucleusiq.agents.errors import AgentExecutionError

try:
    result = await agent.execute({"id": "t5", "objective": "Hello"})
except RateLimitError:
    print("Rate limited — implement backoff")
except AuthenticationError:
    print("Check your API key")
except ToolExecutionError as e:
    print(f"Tool failed: {e}")
except AgentExecutionError as e:
    print(f"Agent execution failed: {e}")
except LLMError as e:
    print(f"LLM error from {e.provider}: {e}")
except NucleusIQError as e:
    print(f"Framework error: {e}")
```

## See also

- [Execution modes](execution-modes.md) — Direct, Standard, Autonomous
- [Tools](tools.md) — `@tool` decorator, built-in tools, and provider native tools
- [Memory](memory.md) — Conversation history strategies
- [Providers](providers.md) — OpenAI, Gemini, and provider portability
- [Usage tracking](usage-tracking.md) — Token usage by purpose and origin
- [Cost estimation](observability/cost-estimation.md) — Dollar cost tracking
- [Error handling](core-concepts/error-handling.md) — Framework error taxonomy
- [Quickstart](quickstart.md) — End-to-end first run
