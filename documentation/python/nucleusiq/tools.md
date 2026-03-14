# Tools

Tools let the agent interact with external systems—files, APIs, databases—by calling functions you define.

## Built-in file tools

NucleusIQ includes 5 file tools, sandboxed to a `workspace_root` directory:

| Tool | Description |
|------|-------------|
| `FileReadTool` | Read file content with optional line ranges |
| `FileWriteTool` | Write or append text files (with backup-on-overwrite) |
| `FileSearchTool` | Text/regex search across files |
| `DirectoryListTool` | List directory with glob filtering |
| `FileExtractTool` | Structured extraction (CSV, JSON, YAML, etc.) |

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
agent = Agent(..., tools=tools)
```

## v0.5.0 tool improvements

- `FileReadTool` defaults to `encoding="auto"` and can detect text encoding via `chardet` (with UTF-8 fallback).
- `DirectoryListTool(max_entries=...)` protects context windows by truncating very large trees.
- `FileSearchTool` supports extension controls: `include_extensions`, `exclude_extensions`, and `binary_extensions`.
- `FileExtractTool` supports query-focused extraction via `columns` (CSV/TSV) and `key_path` (JSON/YAML/TOML).
- `FileWriteTool` supports safe writes/appends with optional backup-on-overwrite.

## Common built-in workflows

### 1) Search -> read targeted lines

```python
from nucleusiq.agents.task import Task

task = Task(
    id="find-config",
    objective=(
        "Find all API timeout settings in this repo and summarize the values. "
        "Use file_search first, then file_read for exact ranges."
    ),
)
result = await agent.execute(task)
```

### 2) Extract tabular subset

```python
# Example tool call intent (performed by the agent in STANDARD/AUTONOMOUS mode):
# file_extract(path="sales.csv", columns="region,revenue")
# file_extract(path="config.yaml", key_path="database.host")
```

### 3) Safe write with backup

```python
# Example tool call intent:
# file_write(path="reports/summary.txt", content="...", mode="write")
# Existing file is backed up as .bak when backup=True
```

## Custom tools

Implement `BaseTool` or use OpenAI-compatible function tools:

```python
from nucleusiq.tools import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(name="get_weather", description="Get weather for a city")

    async def initialize(self) -> None:
        return

    async def execute(self, city: str) -> str:
        return f"Weather in {city}: sunny"

    def get_spec(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        }
```

## OpenAI native tools

The OpenAI provider supports native tools: `code_interpreter`, `file_search`, `web_search`, `image_generation`, `mcp`, `computer_use`. See the [OpenAI provider guide](guides/openai-provider.md).

## See also

- [File handling guide](guides/file-handling.md) — Attachment vs Tool vs Both
- [Attachments](attachments.md) — File-as-context for prompts
