# Example: File Workflow

```python
agent = Agent(
    ...,
    tools=[
        DirectoryListTool(workspace_root="./workspace"),
        FileSearchTool(workspace_root="./workspace"),
        FileReadTool(workspace_root="./workspace"),
        FileExtractTool(workspace_root="./workspace"),
    ],
)

task = Task(id="file-1", objective="Find all revenue lines and summarize trends")
result = await agent.execute(task)
```

See `src/nucleusiq/examples/agents/file_tools_example.py`.
