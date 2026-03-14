# Example: Usage Tracking

```python
result = await agent.execute(Task(id="u1", objective="Summarize this file"))
usage = agent.last_usage

print(usage.display())
print(usage.summary())
```

See `src/nucleusiq/examples/agents/v050_features_example.py` and `src/providers/llms/openai/examples/agents/usage_tracking_example.py`.
