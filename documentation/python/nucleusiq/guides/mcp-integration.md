# MCP Integration (OpenAI)

NucleusIQ supports MCP via OpenAI native tools when using `nucleusiq-openai`.

## When to use

Use MCP when you want the model to call external capability servers through OpenAI Responses API tool routing.

## Example

```python
from nucleusiq.agents import Agent
from nucleusiq_openai import BaseOpenAI, OpenAITool

mcp_tool = OpenAITool.mcp(
    server_label="dmcp",
    server_description="D&D helper server",
    server_url="https://dmcp-server.deno.dev/sse",
    require_approval="never",
)

agent = Agent(
    name="mcp-agent",
    role="Assistant",
    objective="Use MCP tools when needed",
    llm=BaseOpenAI(model_name="gpt-4o-mini"),
    tools=[mcp_tool],
)
```

## Notes

- MCP support here is provider-specific (OpenAI native tool path).
- Native tool execution is server-side in the provider flow.
- Combine with plugin guardrails if you need approval/policy controls.
