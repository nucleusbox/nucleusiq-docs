# @tool decorator

The `@tool` decorator lets you create agent tools from plain Python functions — no subclassing required.

## Basic usage

```python
from nucleusiq.tools.decorators import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 22°C, Sunny"
```

This creates a fully compliant `BaseTool` instance with an auto-generated JSON schema spec from the function's type hints and docstring.

## Decorator forms

Three forms are supported:

```python
# Form 1: bare decorator (uses function name)
@tool
def my_tool(x: str) -> str:
    """Description."""
    return x

# Form 2: with name
@tool("custom_name")
def my_tool(x: str) -> str:
    """Description."""
    return x

# Form 3: with keyword arguments
@tool(name="custom_name", description="Custom description")
def my_tool(x: str) -> str:
    return x
```

## Idempotent tools (same args → same result)

*New in v0.7.7*

By default, every tool call is executed — even if the model repeats the same tool with identical arguments. For **pure, cacheable** helpers (static lists, deterministic transforms, read-only config), you can opt in to **deduplication**: the framework short-circuits a second call with the same `(tool_name, arguments)` and reuses the prior result.

```python
@tool(idempotent=True)
def list_report_sections() -> str:
    """Fixed table of contents for the annual report pipeline."""
    return "financials,md&a,risks,subsidiaries"
```

**Do not** set `idempotent=True` on tools that hit live APIs, databases, clocks, or anything that should change between calls. The default remains **`idempotent=False`** on both `@tool` and `BaseTool`.

`BaseTool` subclasses can pass `idempotent=True` in their constructor when applicable.

## Async functions

Both sync and async functions work:

```python
@tool
async def fetch_data(url: str) -> str:
    """Fetch data from a URL."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.text
```

## Type mapping

The decorator maps Python type hints to JSON Schema types:

| Python type | JSON Schema type |
|-------------|-----------------|
| `str` | `string` |
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `list` | `array` |
| `dict` | `object` |

## Optional parameters

Parameters with default values are marked as optional in the spec:

```python
@tool
def search(query: str, max_results: int = 10, include_metadata: bool = False) -> str:
    """Search for documents.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.
        include_metadata: Whether to include metadata in results.
    """
    return f"Found results for: {query}"
```

Generated spec:

```json
{
  "name": "search",
  "description": "Search for documents.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "The search query string."},
      "max_results": {"type": "integer", "description": "Maximum number of results to return."},
      "include_metadata": {"type": "boolean", "description": "Whether to include metadata in results."}
    },
    "required": ["query"]
  }
}
```

## Docstring parsing

Parameter descriptions are extracted from docstrings. Three styles are supported:

=== "Google style"

    ```python
    @tool
    def fn(city: str, unit: str = "celsius") -> str:
        """Get weather for a city.

        Args:
            city: The city name.
            unit: Temperature unit.
        """
    ```

=== "Sphinx style"

    ```python
    @tool
    def fn(city: str, unit: str = "celsius") -> str:
        """Get weather for a city.

        :param city: The city name.
        :param unit: Temperature unit.
        """
    ```

=== "First line only"

    ```python
    @tool
    def fn(city: str) -> str:
        """Get weather for a city."""
    ```

## Pydantic validation

For complex input validation, pass an `args_schema`:

```python
from pydantic import BaseModel, Field

class SearchArgs(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=100)

@tool(name="search", args_schema=SearchArgs)
def search(query: str, max_results: int = 10) -> str:
    """Search with validated inputs."""
    return f"Results for: {query}"
```

## Using with agents

Decorated tools work with any provider and any execution mode:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

@tool
async def lookup_stock(symbol: str) -> str:
    """Get stock price for a ticker symbol."""
    return f"{symbol}: $150.25"

agent = Agent(
    name="analyst",
    prompt=ZeroShotPrompt().configure(
        system="You are a helpful analyst. Use tools when needed.",
    ),
    llm=llm,
    tools=[calculate, lookup_stock],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "tool-decorator-1", "objective": "What is 15% of $2,400?"})
```

## Mixing tool types

You can mix `@tool` functions with `BaseTool` subclasses and provider native tools:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import FileReadTool
from nucleusiq_gemini import BaseGemini, GeminiTool

agent = Agent(
    name="mixed-tool-kinds",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[
        calculate,                                  # @tool decorator
        FileReadTool(workspace_root="./data"),       # BaseTool subclass
        GeminiTool.google_search(),                  # Provider native tool
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## BaseTool contract

The `@tool` decorator creates a `DecoratedTool` that fully implements the `BaseTool` interface:

- `name` — tool name (from decorator or function name)
- `description` — from decorator or docstring first line
- `get_spec()` — auto-generated JSON schema
- `execute(**kwargs)` — calls the wrapped function
- `initialize()` — no-op (no setup needed)

Existing `BaseTool` subclasses continue to work unchanged.

## See also

- [Tools overview](../tools.md) — Built-in tools and custom tool patterns
- [Tool integration patterns](integration.md) — Combining tools with agents
