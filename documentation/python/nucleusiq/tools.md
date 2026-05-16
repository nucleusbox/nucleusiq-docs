# Tools

Tools let the agent interact with external systems — files, APIs, databases — by calling functions you define.

NucleusIQ provides three ways to create tools:

1. **`@tool` decorator** — create tools from plain functions (recommended for most cases)
2. **`BaseTool` subclass** — full control with custom initialization and execution
3. **Provider native tools** — server-side tools from OpenAI and Gemini (**Anthropic**, Groq, and **Ollama** route tool calls through **`@tool`** / function tools in Phase A — see [Tool integration patterns](tools/integration.md))

## @tool decorator (v0.6.0+)

The fastest way to create tools:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get current weather for a city.

    Args:
        city: City name to look up.
        unit: Temperature unit (celsius or fahrenheit).
    """
    return f"Weather in {city}: 22°{unit[0].upper()}"

agent = Agent(
    name="weather-tool",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[get_weather],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

The decorator auto-generates a JSON schema spec from type hints and docstring. Both sync and async functions are supported.

See the full [`@tool` decorator guide](tools/tool-decorator.md) for all forms, type mapping, Pydantic validation, and docstring parsing.

## Built-in file tools

NucleusIQ includes 5 file tools, sandboxed to a `workspace_root` directory:

| Tool | Description |
|------|-------------|
| `FileReadTool` | Read file content with optional line ranges, encoding auto-detection |
| `FileWriteTool` | Write or append text files with backup-on-overwrite |
| `FileSearchTool` | Text/regex search across files with extension filtering |
| `DirectoryListTool` | List directory with glob filtering and max entries |
| `FileExtractTool` | Structured extraction (CSV, JSON, YAML, XML, TOML, JSONL) |

```python
from nucleusiq.tools.builtin import (
    DirectoryListTool,
    FileExtractTool,
    FileReadTool,
    FileSearchTool,
    FileWriteTool,
)

tools = [
    FileReadTool(workspace_root="./data", max_lines=500),
    FileWriteTool(workspace_root="./data", backup=True),
    FileSearchTool(workspace_root="./data", include_extensions=[".py", ".md"]),
    DirectoryListTool(workspace_root="./data", max_entries=200),
    FileExtractTool(workspace_root="./data"),
]
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="file-tools",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=tools,
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Custom tools (BaseTool)

For tools that need custom initialization or complex logic, subclass `BaseTool`:

```python
from nucleusiq.tools import BaseTool

class DatabaseQueryTool(BaseTool):
    def __init__(self, connection_string: str):
        super().__init__(name="query_db", description="Query the database")
        self._conn_str = connection_string

    async def initialize(self) -> None:
        self._pool = await create_pool(self._conn_str)

    async def execute(self, sql: str) -> str:
        result = await self._pool.fetch(sql)
        return str(result)

    def get_spec(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL query to execute"},
                },
                "required": ["sql"],
            },
        }
```

## Provider native tools

### OpenAI native tools

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI, OpenAITool

agent = Agent(
    name="openai-native",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[
        OpenAITool.web_search(),         # Web search
        OpenAITool.code_interpreter(),   # Code execution
        OpenAITool.file_search(),        # File search
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

### Gemini native tools

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_gemini import BaseGemini, GeminiTool

agent = Agent(
    name="gemini-native",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    tools=[
        GeminiTool.google_search(),    # Google Search grounding
        GeminiTool.code_execution(),   # Python sandbox
        GeminiTool.url_context(),      # Fetch and understand web pages
        GeminiTool.google_maps(),      # Location-aware grounding
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Mixing tool types

All tool types can be mixed in a single agent:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq.tools.builtin import FileReadTool
from nucleusiq_gemini import BaseGemini, GeminiTool

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

llm = BaseGemini(model_name="gemini-2.5-flash")
agent = Agent(
    name="mixed-tool-types",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=llm,
    tools=[
        calculate,                                  # @tool decorator
        FileReadTool(workspace_root="./data"),       # Built-in file tool
        GeminiTool.google_search(),                  # Provider native tool
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## See also

- [`@tool` decorator guide](tools/tool-decorator.md) — Full decorator documentation
- [Built-in tools](tools/built-in.md) — File tool details
- [File handling guide](guides/file-handling.md) — Attachment vs Tool vs Both
- [Anthropic provider](guides/anthropic-provider.md) — Claude Messages API (**alpha**)
- [Tool integration patterns](tools/integration.md) — Advanced patterns (includes **Anthropic** alpha)
- [Ollama provider](guides/ollama-provider.md) — Capability matrix for local inference (**alpha**)
- [Attachments](attachments.md) — File-as-context for prompts
