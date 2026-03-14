# Core Concept: Tools, Memory, Plugins

These three components shape runtime behavior.

## Tools

Allow the agent to act on external systems (files/APIs/etc).

## Memory

Controls conversation state retention strategy.

## Plugins

Inject policy, guardrails, retry, limits, and validation via lifecycle hooks.

## Combined example

```python
agent = Agent(
    ...,
    tools=[...],
    memory=MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW, window_size=10),
    plugins=[ModelCallLimitPlugin(max_calls=20), ToolRetryPlugin(max_retries=2)],
)
```
