# Example: File Workflow

Use built-in file tools for agent-driven file exploration, search, reading, and extraction.

## Search then read

The agent searches for relevant files, then reads specific sections:

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool, DirectoryListTool
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="code-reviewer",
        llm=BaseOpenAI(model_name="gpt-4o-mini"),
        model="gpt-4o-mini",
        instructions=(
            "You are a code reviewer. Use directory listing to understand the project structure, "
            "file search to find relevant code, and file read to examine specific sections."
        ),
        tools=[
            DirectoryListTool(workspace_root="./my-project", max_entries=200),
            FileSearchTool(workspace_root="./my-project", include_extensions=[".py", ".md"]),
            FileReadTool(workspace_root="./my-project", max_lines=500),
        ],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = await agent.execute(
        {
            "id": "f1",
            "objective": "Find all API timeout settings in this project and summarize the values.",
        }
    )
    print(result.output)

asyncio.run(main())
```

## Extract and analyze data

Use `FileExtractTool` for structured extraction from CSV, JSON, YAML, and other formats:

```python
from nucleusiq.tools.builtin import FileExtractTool

agent = Agent(
    name="data-analyst",
    llm=llm,
    model="gpt-4o-mini",
    instructions="Extract and analyze data from files. Use column filtering for CSV files.",
    tools=[
        FileExtractTool(workspace_root="./data"),
        FileReadTool(workspace_root="./data"),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

result = await agent.execute(
    {"id": "f2", "objective": "What are the top 5 regions by revenue in sales.csv?"}
)
```

## Write results

Use `FileWriteTool` to save analysis results:

```python
from nucleusiq.tools.builtin import FileWriteTool

agent = Agent(
    name="report-writer",
    llm=llm,
    model="gpt-4o-mini",
    instructions="Analyze data and write reports. Save results to the reports directory.",
    tools=[
        FileReadTool(workspace_root="./workspace"),
        FileExtractTool(workspace_root="./workspace"),
        FileWriteTool(workspace_root="./workspace", backup=True),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

result = await agent.execute(
    {
        "id": "f3",
        "objective": (
            "Read sales.csv, calculate total revenue by region, and write a summary to reports/revenue-summary.txt"
        ),
    }
)
```

## See also

- [File tools deep dive](../tools/file-tools.md) — Tool constructors and features
- [File handling guide](../guides/file-handling.md) — Attachment vs Tool decision guide
- [Tools overview](../tools.md) — All tool types
