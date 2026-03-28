# Execution modes

NucleusIQ uses the **Gearbox Strategy** — three execution modes that scale from simple chat to autonomous reasoning. All modes work identically with any LLM provider (OpenAI, Gemini).

## Comparison

| Capability | Direct | Standard | Autonomous |
|------------|--------|----------|------------|
| Memory | Yes | Yes | Yes |
| Plugins | Yes | Yes | Yes |
| Tools | Yes (max 5) | Yes (max 30) | Yes (max 100) |
| Tool loop | Yes | Yes | Yes |
| Streaming | Yes | Yes | Yes |
| Structured output | Yes | Yes | Yes |
| Task decomposition | No | No | Yes |
| Critic (verification) | No | No | Yes |
| Refiner (correction) | No | No | Yes |
| Validation pipeline | No | No | Yes |

Tool limits are configurable via `AgentConfig(max_tool_calls=N)`.

## Direct

Fast, single LLM call. Best for Q&A, classification, and simple lookups.

```python
from nucleusiq.agents.config import AgentConfig, ExecutionMode

config = AgentConfig(execution_mode=ExecutionMode.DIRECT)
agent = Agent(llm=llm, config=config, ...)
```

Use Direct when latency matters and the task doesn't need tools or iteration.

## Standard (default)

Tool-enabled, linear execution. The agent calls tools iteratively until it has enough information to answer.

```python
config = AgentConfig(execution_mode=ExecutionMode.STANDARD)
# or omit — STANDARD is the default
```

Use Standard for most production workflows: data lookup, calculations, file operations, API calls.

## Autonomous

Planning, multi-step execution with Critic/Refiner verification. The agent decomposes complex tasks, executes subtasks, and verifies its own output.

```python
config = AgentConfig(
    execution_mode=ExecutionMode.AUTONOMOUS,
    require_quality_check=True,
    max_iterations=5,
)
```

Use Autonomous for complex, high-stakes tasks where correctness matters more than speed.

## Choosing a mode

| Scenario | Recommended mode |
|----------|-----------------|
| Simple Q&A, classification | DIRECT |
| Tool-enabled data workflows | STANDARD |
| Complex analysis with verification | AUTONOMOUS |
| Chat applications | STANDARD |
| Code generation with validation | AUTONOMOUS |

## See also

- [Agents](agents.md) — Agent configuration
- [Tools](tools.md) — Built-in tools, `@tool` decorator, and provider native tools
- [Strategy guide](guides/strategy.md) — Detailed mode selection guidance
