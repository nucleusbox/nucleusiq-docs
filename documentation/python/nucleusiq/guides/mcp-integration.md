# MCP Integration (OpenAI)

NucleusIQ supports MCP (Model Context Protocol) via OpenAI native tools when using `nucleusiq-openai`.

## When to use

Use MCP when you want the model to call external capability servers through OpenAI Responses API tool routing.

## Example

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI, OpenAITool

mcp_tool = OpenAITool.mcp(
    server_label="dmcp",
    server_description="D&D helper server",
    server_url="https://dmcp-server.deno.dev/sse",
    require_approval="never",
)

agent = Agent(
    name="mcp-agent",
    prompt=ZeroShotPrompt().configure(
        system="You are an assistant. Use MCP tools when needed to answer user questions.",
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[mcp_tool],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

result = await agent.execute({"id": "mcp-1", "objective": "Roll a d20 for initiative"})
print(result.output)
```

## Notes

- MCP support here is provider-specific (OpenAI native tool path).
- Native tool execution is server-side in the provider flow.
- Combine with plugin guardrails if you need approval/policy controls.

## See also

- [OpenAI provider](openai-provider.md) — Full OpenAI integration guide
- [Tools](../tools.md) — All tool types (custom, built-in, provider native)
