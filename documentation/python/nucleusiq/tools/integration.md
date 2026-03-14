# Tool Integration Patterns

## Pattern 1: Local function + file tools

```python
agent = Agent(
    ...,
    tools=[
        BaseTool.from_function(add, description="Add numbers"),
        FileReadTool(workspace_root="./workspace"),
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

## Pattern 3: MCP + guardrails

```python
agent = Agent(
    ...,
    tools=[OpenAITool.mcp(server_label="dmcp", server_description="...", server_url="https://.../sse")],
    plugins=[ModelCallLimitPlugin(max_calls=10)],
)
```
