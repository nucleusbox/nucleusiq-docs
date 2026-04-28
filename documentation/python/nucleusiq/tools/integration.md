# Tool integration patterns

Every pattern below uses the **mandatory** `prompt=` argument (see [migration notes](../learn/migration-notes.md)). Swap `BaseOpenAI` / `BaseGemini` and model names to match your provider.

## Pattern 1: @tool decorator + file tools

The most common pattern — custom logic via decorators, file access via built-ins:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool
from nucleusiq_openai import BaseOpenAI

@tool
def summarize(text: str) -> str:
    """Summarize the given text."""
    return text[:200] + "..."

agent = Agent(
    name="file-tools-demo",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[
        summarize,
        FileReadTool(workspace_root="./workspace"),
        FileSearchTool(workspace_root="./workspace"),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Pattern 2: OpenAI native tools

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI, OpenAITool

agent = Agent(
    name="openai-native-tools",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[
        OpenAITool.web_search(),
        OpenAITool.code_interpreter(),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Pattern 3: Gemini native tools

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_gemini import BaseGemini, GeminiTool

agent = Agent(
    name="gemini-native-tools",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[
        GeminiTool.google_search(),
        GeminiTool.code_execution(),
        GeminiTool.url_context(),
        GeminiTool.google_maps(),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Pattern 4: Gemini native + custom tool mixing

*New in v0.7.5*

Combine Gemini's native tools with your custom tools in a single agent. NucleusIQ's proxy pattern handles the Gemini API restriction transparently:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
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
    name="gemini-mixed-tools",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[
        GeminiTool.google_search(),   # Native — searches the web
        GeminiTool.code_execution(),  # Native — runs Python code
        unit_converter,               # Custom — your business logic
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD, enable_tracing=True),
)
```

!!! note

    On Gemini 2.5 models, mixing native and custom tools would normally produce a `400 INVALID_ARGUMENT` error. NucleusIQ handles this automatically — see the [Gemini provider guide](../guides/gemini-provider.md#mixing-native-and-custom-tools) for details.

## Pattern 5: Mixed tools with guardrails

Combine custom tools, native tools, and plugins for production safety:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq.tools.builtin import FileReadTool
from nucleusiq_gemini import BaseGemini, GeminiTool
from nucleusiq.plugins.builtin import ModelCallLimitPlugin, ToolGuardPlugin

@tool
def calculate(expression: str) -> str:
    """Evaluate a safe math expression (example only — validate in production)."""
    return str(eval(expression, {"__builtins__": {}}, {}))

agent = Agent(
    name="guarded-mix",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[
        calculate,
        FileReadTool(workspace_root="./workspace"),
        GeminiTool.google_search(),
    ],
    plugins=[
        ModelCallLimitPlugin(max_calls=10),
        ToolGuardPlugin(allowed_tools=["calculate", "file_read", "google_search"]),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Pattern 6: MCP integration (OpenAI)

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI, OpenAITool
from nucleusiq.plugins.builtin import ModelCallLimitPlugin

agent = Agent(
    name="mcp-agent",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[
        OpenAITool.mcp(
            server_label="my-mcp",
            server_description="Custom MCP server",
            server_url="https://my-server.example.com/sse",
        ),
    ],
    plugins=[ModelCallLimitPlugin(max_calls=10)],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## See also

- [Tools overview](../tools.md) — All tool types
- [`@tool` decorator](tool-decorator.md) — Create tools from functions
- [MCP integration guide](../guides/mcp-integration.md) — Full MCP setup
