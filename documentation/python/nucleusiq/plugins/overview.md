# Plugins overview

Plugins intercept agent execution at 6 hook points to add logging, retries, guards, and more.

## Hook points

| Hook | When |
|------|------|
| `before_agent` | Before agent execution starts |
| `after_agent` | After agent execution completes |
| `before_model` | Before each LLM call |
| `after_model` | After each LLM call |
| `wrap_model_call` | Wrap LLM calls (retry, fallback) |
| `wrap_tool_call` | Wrap tool calls (retry, guard) |

## Two APIs

**Class-based** — Subclass `BasePlugin` for multi-hook plugins:

```python
from nucleusiq.plugins import BasePlugin

class LogPlugin(BasePlugin):
    async def before_model(self, context, request):
        print(f"LLM call to {request.model}")
```

**Decorator-based** — Use `@before_model` etc. for simple hooks:

```python
from nucleusiq.plugins import before_model

@before_model
def log(request):
    print(f"Call #{request.call_count}")
```

## Adding plugins

```python
agent = Agent(..., plugins=[LogPlugin(), log])
```

## See also

- [Built-in plugins](built-in.md) — 10 ready-to-use plugins
