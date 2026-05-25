# MCP quickstart

Connect any **[Model Context Protocol](https://modelcontextprotocol.io/)** server (GitHub, Slack, Postgres, Stripe, your own) to a NucleusIQ agent — across **any LLM provider** — using **`nucleusiq-mcp`**.

!!! success "Beta"

    **`nucleusiq-mcp` 0.1.0b1** — public **beta**. Requires **`nucleusiq>=0.7.11`** and **`mcp>=1.27,<2`**. API is stable for the 0.1.x line.

**Pattern:** create one or more **`MCPTool`** instances → pass them in `tools=[...]` → call **`await agent.initialize()`** to open the connections and discover tools → run **`agent.execute(...)`** as usual.

For the **why** and the **scope** (transports, auth strategies, decorator filters, graceful degradation, ping, source tracing), see the **[MCP integration guide](../guides/mcp-integration.md)**.

## Setup

```bash
pip install "nucleusiq>=0.7.11" "nucleusiq-mcp==0.1.0b1" nucleusiq-anthropic
# Or via the core extras
# pip install "nucleusiq[mcp]" nucleusiq-anthropic

export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_..."   # for the stdio example
```

Many reference MCP servers are distributed as `@modelcontextprotocol/server-...` npm packages and run over **stdio** via `npx`. Make sure **Node.js 18+** with **`npx`** is on `PATH` if you use those.

---

## Pattern 1: single stdio server (GitHub)

The simplest case. The MCP server runs as a subprocess; env vars are forwarded.

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_anthropic import BaseAnthropic
from nucleusiq_mcp import MCPTool


async def main() -> None:
    agent = Agent(
        name="github-researcher",
        prompt=ZeroShotPrompt().configure(
            system="You are a research assistant. Use the MCP tools when you need GitHub data.",
        ),
        llm=BaseAnthropic(
            model_name=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
            async_mode=True,
        ),
        tools=[
            MCPTool(
                "npx -y @modelcontextprotocol/server-github",
                auth=os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"],
            ),
        ],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD, enable_tracing=True),
    )

    await agent.initialize()
    result = await agent.execute(
        Task(id="mcp-1", objective="Summarise the last 5 open issues in nucleusbox/NucleusIQ."),
    )
    print(result.output)


asyncio.run(main())
```

---

## Pattern 2: HTTP server with Bearer auth (Slack)

Same code, different transport — `MCPTool` auto-detects **Streamable HTTP** from the URL.

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_anthropic import BaseAnthropic
from nucleusiq_mcp import BearerAuth, MCPTool


async def main() -> None:
    agent = Agent(
        name="slack-bot",
        prompt=ZeroShotPrompt().configure(
            system="You read team Slack messages and summarise threads on request.",
        ),
        llm=BaseAnthropic(model_name="claude-haiku-4-5", async_mode=True),
        tools=[
            MCPTool(
                "https://mcp.slack.com/mcp",
                auth=BearerAuth(token=os.environ["SLACK_BOT_TOKEN"]),
            ),
        ],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD, enable_tracing=True),
    )

    await agent.initialize()
    result = await agent.execute(
        Task(id="slack-1", objective='Summarise the last 24h of #engineering.'),
    )
    print(result.output)


asyncio.run(main())
```

For OAuth 2.1 (PKCE) and Env / Custom-header strategies see the **[guide](../guides/mcp-integration.md#authentication)**.

---

## Pattern 3: multi-server agent

A single agent can talk to several MCP servers — they're opened in **parallel** during `initialize()`. Different LLM providers work the same way.

```python
import asyncio
import os

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI       # swap to any provider
from nucleusiq_mcp import MCPTool


async def main() -> None:
    agent = Agent(
        name="ops",
        prompt=ZeroShotPrompt().configure(
            system="You are an operations agent. Use the tools to answer questions across systems.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[
            MCPTool("npx -y @modelcontextprotocol/server-github", auth=os.environ["GITHUB_TOKEN"]),
            MCPTool("https://mcp.slack.com/mcp", auth=os.environ["SLACK_TOKEN"]),
            MCPTool("https://mcp.linear.app/mcp", auth=os.environ["LINEAR_TOKEN"]),
        ],
        config=AgentConfig(execution_mode=ExecutionMode.AUTONOMOUS, enable_tracing=True),
    )

    await agent.initialize()
    result = await agent.execute(
        Task(id="ops-1", objective=(
            "For each P0 Linear issue created in the last week, find the linked PR "
            "in nucleusbox/NucleusIQ and post a status update to #engineering."
        )),
    )
    print(result.output)


asyncio.run(main())
```

---

## Pattern 4: filter & rename tools

Most MCP servers expose more tools than you want to expose to your LLM. Trim and rename them:

```python
from nucleusiq_mcp import MCPTool

agent = Agent(
    ...,
    tools=[
        MCPTool(
            "npx -y @modelcontextprotocol/server-everything",
            include_tools=["get-sum", "get-issue"],          # whitelist
            rename={"get-sum": "add"},                       # nicer name for the LLM
        ),
    ],
)
```

For full programmatic control use the **`@mcp_tool_filter`** decorator — see the [guide](../guides/mcp-integration.md#filtering-and-renaming-mcp-tools).

---

## Pattern 5: graceful degradation

Boot the agent even if one server is unreachable:

```python
from nucleusiq_mcp import MCPTool

agent = Agent(
    ...,
    tools=[
        MCPTool("https://reliable.example.com/mcp", auth="..."),
        MCPTool(
            "https://flaky.example.com/mcp",
            auth="...",
            on_connect_failure="skip",   # warn + continue instead of raising
        ),
    ],
)
await agent.initialize()
```

For runtime probes use **`MCPTool.ping()`** — it returns `bool` and never raises:

```python
mcp = MCPTool("https://mcp.example.com/mcp", auth="...")
agent = Agent(..., tools=[mcp])
await agent.initialize()

if not await mcp.ping():
    logger.warning("MCP server is down — skipping related work")
```

---

## Pattern 6: trace the `mcp://` origin of every tool call

When you set **`enable_tracing=True`**, every tool call in **`AgentResult.tool_calls`** carries a `source` attribute identifying the MCP server it came from:

```python
result = await agent.execute(task)

for tc in result.tool_calls:
    print(f"{tc.name:24}  source={tc.source}")
# list_issues               source=mcp://server=github (path=A)
# search_messages           source=mcp://server=slack (path=A)
# linear_get_issue          source=mcp://server=linear (path=A)
```

That same field flows through `ExecutionTracer` records, so per-server error rates and latencies are queryable from your telemetry sink.

---

## Pattern 7: plugin guardrails on MCP tools

MCP tools are normal **`BaseTool`** instances — every plugin applies:

```python
from nucleusiq.plugins.builtin import HumanApprovalPlugin, ToolGuardPlugin
from nucleusiq_mcp import MCPTool

agent = Agent(
    ...,
    tools=[MCPTool("https://mcp.stripe.com/mcp", auth=os.environ["STRIPE_KEY"])],
    plugins=[
        ToolGuardPlugin(allowed_tools=["search_customer", "list_invoices"]),
        HumanApprovalPlugin(require_approval_for=["refund_charge"]),
    ],
)
```

---

## Optional: OpenAI server-side MCP

If you're on OpenAI and want OpenAI's Responses API to hold the MCP connection itself (no `initialize()` step in your process), use the legacy `OpenAITool.mcp(...)` factory:

```python
from nucleusiq_openai import BaseOpenAI, OpenAITool

mcp_tool = OpenAITool.mcp(
    server_label="dmcp",
    server_description="D&D helper server",
    server_url="https://dmcp-server.deno.dev/sse",
    require_approval="never",
)

agent = Agent(
    name="mcp-agent",
    prompt=ZeroShotPrompt().configure(system="You are an assistant. Use MCP tools when needed."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[mcp_tool],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

See the **[guide → When to use which](../guides/mcp-integration.md#when-to-use-which)** for the trade-offs.

---

## Runnable scripts in the repo

From **`src/providers/tools/mcp`**:

```bash
uv sync --group dev
uv run python examples/01_basic_stdio.py
uv run python examples/02_http_with_auth.py
uv run python examples/03_multi_server.py
uv run python examples/04_oauth_flow.py
uv run python examples/05_error_handling.py
uv run python examples/06_health_check.py
uv run python examples/07_decorator_filters.py
uv run python examples/08_full_agent_with_llm.py
```

Notebook demo: **[notebooks/agents/mcp_tools_showcase.ipynb](https://github.com/nucleusbox/NucleusIQ/blob/main/notebooks/agents/mcp_tools_showcase.ipynb)** — runs the reference server in Streamable HTTP mode (Windows-friendly) and walks through transport detection, tool calls, tracing, and graceful degradation.

## See also

- **[MCP integration guide](../guides/mcp-integration.md)** — Full scope, auth, transports, filtering, OAuth, observability, comparison vs OpenAI server-side MCP.
- **[Providers](../providers.md)** — MCP works with **every** provider (OpenAI, Anthropic, Gemini, Groq, Ollama, Mock).
- **[Tools overview](../tools.md)** — All four ways to add tools.
- **[Anthropic quickstart](anthropic-quickstart.md)** — The LLM used in most examples on this page.
- **[Installation](../install.md)** — Package matrix, `nucleusiq[mcp]` extras, env vars.
