# Production Path

## Recommended sequence

1. Start with `ExecutionMode.STANDARD`
2. Add file tools and plugin guardrails
3. Add memory strategy
4. Add usage dashboards (`agent.last_usage.summary()`)
5. Evaluate AUTONOMOUS for complex workflows

## Typical production config

```python
agent = Agent(
    ...,
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD, llm_call_timeout=90),
    tools=[...],
    memory=..., 
    plugins=[ModelCallLimitPlugin(max_calls=20), ToolRetryPlugin(max_retries=2)],
)
```
