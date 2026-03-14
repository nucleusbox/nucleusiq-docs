# Example: Autonomous Workflow

```python
agent = Agent(
    ...,
    config=AgentConfig(execution_mode=ExecutionMode.AUTONOMOUS, max_retries=2),
)

result = await agent.execute(Task(id="a1", objective="Analyze risk factors and propose mitigations"))
```

See `src/nucleusiq/examples/agents/autonomous_mode_example.py`.
