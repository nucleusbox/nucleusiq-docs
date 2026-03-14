# Execution modes

NucleusIQ uses the **Gearbox Strategy**—three execution modes that scale from simple chat to autonomous reasoning.

## Comparison

| Capability | Direct | Standard | Autonomous |
|------------|--------|----------|------------|
| Memory | Yes | Yes | Yes |
| Plugins | Yes | Yes | Yes |
| Tools | Yes (max 5) | Yes (max 30) | Yes (max 100) |
| Tool loop | Yes | Yes | Yes |
| Task decomposition | No | No | Yes |
| Critic (verification) | No | No | Yes |
| Refiner (correction) | No | No | Yes |
| Validation pipeline | No | No | Yes |

Tool limits are configurable via `AgentConfig(max_tool_calls=N)`.

## Direct

Fast, single LLM call. Best for Q&A and simple lookups.

```python
agent = Agent(..., config=AgentConfig(execution_mode=ExecutionMode.DIRECT))
```

## Standard

Tool-enabled, linear execution. Default for most workflows.

```python
agent = Agent(..., config=AgentConfig(execution_mode=ExecutionMode.STANDARD))
# or omit — STANDARD is the default
```

## Autonomous

Planning, multi-step execution with Critic/Refiner verification. For complex, high-stakes tasks.

```python
agent = Agent(..., config=AgentConfig(execution_mode=ExecutionMode.AUTONOMOUS))
```

## See also

- [Agents](agents.md) — Agent configuration
- [Tools](tools.md) — Built-in and custom tools
