# Example: Streaming

```python
from nucleusiq.agents import StreamEventType

async for event in agent.execute_stream(task):
    if event.type == StreamEventType.TOKEN and event.token:
        print(event.token, end="", flush=True)
    elif event.type == StreamEventType.COMPLETE:
        print("\n[complete]")
```

See `src/nucleusiq/examples/agents/streaming_example.py` for a full runnable script.
