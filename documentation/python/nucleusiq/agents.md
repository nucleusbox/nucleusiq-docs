# Agents

An agent is a managed runtime with memory, tools, policy, streaming, structure, and responsibilities.

## Creating an agent

*Changed in v0.7.6: `prompt` is now mandatory. `narrative` has been removed. `role` and `objective` are labels only (not sent to the LLM).*

=== "With OpenAI"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_openai import BaseOpenAI

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a data analyst. Answer questions accurately.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    ```

=== "With Gemini"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_gemini import BaseGemini

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a data analyst. Answer questions accurately.",
        ),
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    ```

=== "With Anthropic (Claude)"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_anthropic import BaseAnthropic

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a data analyst. Answer questions accurately.",
        ),
        llm=BaseAnthropic(model_name="claude-3-5-sonnet-20241022", async_mode=True),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    ```

=== "With Groq"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_groq import BaseGroq

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a data analyst. Answer questions accurately.",
        ),
        llm=BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    ```

=== "With Ollama"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_ollama import BaseOllama

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a data analyst. Answer questions accurately.",
        ),
        llm=BaseOllama(model_name="llama3.2", async_mode=True),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    ```

=== "With MockLLM (testing)"

    ```python
    from nucleusiq.agents import Agent
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq.core.llms.mock_llm import MockLLM

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(system="You are a data analyst."),
        llm=MockLLM(),
    )
    ```

!!! tip "Async inference backends (`BaseAnthropic`, `BaseGroq`, `BaseOllama`)"

    Call **`await agent.initialize()`** before **`await agent.execute(...)`** so startup matches the runnable scripts and provider guides.

## Agent fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Human-readable identifier |
| `prompt` | **Yes** | `BasePrompt` instance — the single source of truth for what the LLM sees. Use `ZeroShotPrompt().configure(system="...")` or any prompt technique. |
| `llm` | Yes | Model backend (`BaseOpenAI`, `BaseGemini`, `BaseAnthropic`, `BaseGroq`, `BaseOllama`, `MockLLM`, …) |
| `config` | No | `AgentConfig` — execution mode, timeouts, context management |
| `tools` | No | List of tools the agent can call |
| `memory` | No | Conversation memory strategy |
| `plugins` | No | Policy and guardrail plugins |
| `role` | No | Label for logging and sub-agent naming (default: `"Agent"`). **Not sent to the LLM.** |
| `objective` | No | Label for documentation (default: `""`). **Not sent to the LLM.** |

!!! warning "prompt is the single source of truth"
    Everything the LLM sees comes from `prompt.system` (system message) and `prompt.user` (optional preamble). Put all LLM instructions in the prompt — not in `role` or `objective`.

## Agent lifecycle

1. **Create** — Instantiate with an LLM, config, tools, plugins, and memory.
2. **Execute** — `result = await agent.execute({"id": "t1", "objective": "What is 2+2?"})` or pass a `Task` object. Returns an `AgentResult` model; access the response via `result.output`.
3. **Stream** — `async for event in agent.execute_stream({"id": "t2", "objective": "Write a poem"}):` for real-time output.
4. **Inspect** — `agent.last_usage` for token counts, then `CostTracker` for cost estimation.

## AgentResult

`execute()` returns an `AgentResult` — a structured response contract that provides the LLM output, execution metadata, and optional tracing data. Since **v0.7.8**, **`result.metadata`** may also carry summaries of **run-local** context state (workspace, evidence dossier, lexical corpus stats, phase control, activation counters, synthesis-package metadata); see [Run-local context state](run-local-context-state.md).

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

# Context telemetry (v0.7.6)
if result.context_telemetry:
    print(f"Peak utilization: {result.context_telemetry.peak_utilization:.1%}")

# Run-local state summaries (v0.7.8) — workspace/evidence/corpus/phase/activation/synthesis package
if result.metadata:
    for key in ("workspace", "evidence", "document_search", "phase_control", "context_activation", "synthesis_package"):
        if key in result.metadata:
            print(key, result.metadata[key])
```

## End-to-end example

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22C, Sunny"

async def main():
    agent = Agent(
        name="assistant",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant. Use tools when needed.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[get_weather],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )
    result = await agent.execute({"id": "t3", "objective": "What's the weather in Paris?"})
    print(result.output)
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
cost = tracker.estimate(usage, model="gpt-4.1-mini")
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

- [Context management](context-management.md) — Context window management for tool-heavy agents
- [Execution modes](execution-modes.md) — Direct, Standard, Autonomous
- [Prompts](prompts.md) — Prompt techniques and configuration
- [Tools](tools.md) — `@tool` decorator, built-in tools, and provider native tools
- [Memory](memory.md) — Conversation history strategies
- [Providers](providers.md) — Provider matrix (OpenAI, Gemini, Anthropic, Groq, Ollama, …)
- [Usage tracking](usage-tracking.md) — Token usage by purpose and origin
- [Cost estimation](observability/cost-estimation.md) — Dollar cost tracking
- [Error handling](core-concepts/error-handling.md) — Framework error taxonomy
- [Quickstart](quickstart.md) — End-to-end first run
