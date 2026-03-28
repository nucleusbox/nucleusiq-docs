# Tool integration patterns

## Pattern 1: @tool decorator + file tools

The most common pattern — custom logic via decorators, file access via built-ins:

```python
from nucleusiq.tools.decorators import tool
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool

@tool
def summarize(text: str) -> str:
    """Summarize the given text."""
    return text[:200] + "..."

agent = Agent(
    ...,
    tools=[
        summarize,
        FileReadTool(workspace_root="./workspace"),
        FileSearchTool(workspace_root="./workspace"),
    ],
)
```

## Pattern 2: OpenAI native tools

```python
from nucleusiq_openai import OpenAITool

agent = Agent(
    ...,
    tools=[
        OpenAITool.web_search(),
        OpenAITool.code_interpreter(),
    ],
)
```

## Pattern 3: Gemini native tools

```python
from nucleusiq_gemini import GeminiTool

agent = Agent(
    ...,
    tools=[
        GeminiTool.google_search(),
        GeminiTool.code_execution(),
        GeminiTool.url_context(),
        GeminiTool.google_maps(),
    ],
)
```

## Pattern 4: Mixed tools with guardrails

Combine custom tools, native tools, and plugins for production safety:

```python
from nucleusiq.plugins.builtin import ModelCallLimitPlugin, ToolGuardPlugin

agent = Agent(
    ...,
    tools=[
        calculate,                                    # @tool decorator
        FileReadTool(workspace_root="./workspace"),    # Built-in
        GeminiTool.google_search(),                    # Native
    ],
    plugins=[
        ModelCallLimitPlugin(max_calls=10),
        ToolGuardPlugin(allowed_tools=["calculate", "file_read", "google_search"]),
    ],
)
```

## Pattern 5: MCP integration (OpenAI)

```python
from nucleusiq_openai import OpenAITool

agent = Agent(
    ...,
    tools=[
        OpenAITool.mcp(
            server_label="my-mcp",
            server_description="Custom MCP server",
            server_url="https://my-server.example.com/sse",
        ),
    ],
    plugins=[ModelCallLimitPlugin(max_calls=10)],
)
```

## See also

- [Tools overview](../tools.md) — All tool types
- [`@tool` decorator](tool-decorator.md) — Create tools from functions
- [MCP integration guide](../guides/mcp-integration.md) — Full MCP setup
