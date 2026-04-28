# File tools deep dive

All file tools are sandboxed to a `workspace_root` directory. Path traversal (`../`), symlink escape, and absolute path injection are blocked.

## FileReadTool

Read file content with optional line ranges and encoding auto-detection:

```python
from nucleusiq.tools.builtin import FileReadTool

reader = FileReadTool(
    workspace_root="./workspace",
    max_lines=500,          # truncate large files
    max_file_size=10_000_000,  # 10 MB limit
)
```

Features:
- `encoding="auto"` detects encoding via `chardet` (with UTF-8 fallback)
- Binary file detection (null byte check)
- Optional `start_line` / `end_line` for targeted reads

## FileWriteTool

Write or append text files with optional backup:

```python
from nucleusiq.tools.builtin import FileWriteTool

writer = FileWriteTool(
    workspace_root="./workspace",
    backup=True,        # creates .bak before overwrite
    max_write_size=5_000_000,  # 5 MB limit
)
```

Supports `mode="write"` (overwrite) and `mode="append"`.

## FileSearchTool

Text or regex search across files:

```python
from nucleusiq.tools.builtin import FileSearchTool

searcher = FileSearchTool(
    workspace_root="./workspace",
    include_extensions=[".py", ".md"],     # whitelist mode
    exclude_extensions=[".pyc", ".lock"],   # additions to skip
    max_results=50,
)
```

## DirectoryListTool

List directory contents with glob filtering:

```python
from nucleusiq.tools.builtin import DirectoryListTool

lister = DirectoryListTool(
    workspace_root="./workspace",
    max_entries=200,  # truncate large directories
)
```

## FileExtractTool

Structured extraction from tabular and config files:

```python
from nucleusiq.tools.builtin import FileExtractTool

extractor = FileExtractTool(workspace_root="./workspace")
```

Supported formats: CSV, TSV, JSON, JSONL/NDJSON, YAML, XML, TOML.

Query-focused extraction:
- `columns="region,revenue"` — filter CSV/TSV columns
- `key_path="database.host"` — navigate JSON/YAML/TOML with dot notation and array indices

## Common agent workflows

### Search then read

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="search-then-read",
    prompt=ZeroShotPrompt().configure(
        system="Search for relevant files first, then read specific sections.",
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[
        FileSearchTool(workspace_root="./project"),
        FileReadTool(workspace_root="./project"),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "file-tools-1", "objective": "Find all API timeout settings in this codebase"})
```

### Extract and analyze

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import FileExtractTool
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="extract-analyze",
    prompt=ZeroShotPrompt().configure(
        system="Extract data from files and provide analysis.",
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[FileExtractTool(workspace_root="./data")],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "file-tools-2", "objective": "What are the top 5 regions by revenue in sales.csv?"})
```

## See also

- [Tools overview](../tools.md) — All tool types
- [File handling guide](../guides/file-handling.md) — Attachment vs Tool decision guide
