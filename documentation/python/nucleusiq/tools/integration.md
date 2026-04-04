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

## Pattern 4: Gemini native + custom tool mixing

*New in v0.7.5*

Combine Gemini's native tools with your custom tools in a single agent. NucleusIQ's proxy pattern handles the Gemini API restriction transparently:

```python
from nucleusiq_gemini import BaseGemini
from nucleusiq_gemini.tools.gemini_tool import GeminiTool
from nucleusiq.tools.decorators import tool

@tool
def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units (km/miles, celsius/fahrenheit, kg/pounds)."""
    conversions = {
        ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
        ("km", "miles"): lambda v: v * 0.621371,
    }
    result = conversions.get((from_unit, to_unit), lambda v: v)(value)
    return f"{value} {from_unit} = {result:.2f} {to_unit}"

agent = Agent(
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[
        GeminiTool.google_search(),   # Native — searches the web
        GeminiTool.code_execution(),  # Native — runs Python code
        unit_converter,               # Custom — your business logic
    ],
    config=AgentConfig(execution_mode="standard", enable_tracing=True),
    ...
)
```

!!! note

    On Gemini 2.5 models, mixing native and custom tools would normally produce a `400 INVALID_ARGUMENT` error. NucleusIQ handles this automatically — see the [Gemini provider guide](../guides/gemini-provider.md#mixing-native-and-custom-tools) for details.

## Pattern 5: Mixed tools with guardrails

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

## Pattern 6: MCP integration (OpenAI)

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
