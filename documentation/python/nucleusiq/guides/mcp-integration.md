# MCP integration (Model Context Protocol)

!!! success "Beta release — `nucleusiq-mcp` 0.1.0b1"

    **`nucleusiq-mcp` 0.1.0b1** is now available as a **PyPI beta** (**`Development Status :: 4 - Beta`**). It is a **universal Model Context Protocol** adapter built on the **official `mcp` SDK** that turns any MCP server (GitHub, Slack, Postgres, Stripe, your own) into native NucleusIQ tools.

    - **Requires** **`nucleusiq>=0.7.11`** and **`mcp>=1.27,<2`**.
    - **API is stable** for the 0.1.x line — feature-additive changes only; breaking changes will go through a `0.2.0` major.

NucleusIQ has **two complementary MCP integration paths**. This page covers both and tells you when to use which.

| Path | Package | Where MCP runs | Best for |
|------|---------|----------------|----------|
| **Universal adapter (recommended)** | **`nucleusiq-mcp`** | NucleusIQ process opens the connection (stdio / Streamable HTTP / SSE) and exposes each MCP tool as a **`BaseTool`** to the agent | **Any LLM provider** — OpenAI, Anthropic, Gemini, Groq, Ollama, mock. Works with all execution modes, plugins, and tracing. |
| **OpenAI server-side MCP** | **`nucleusiq-openai`** | OpenAI's Responses API routes calls to the MCP server itself; NucleusIQ just declares the `mcp` tool | Quick PoC when you're already on **OpenAI** and want the model to drive a remote MCP server **without your process handling the connection**. |

If you have a choice, use the **universal adapter** — it works with every provider, gives you full observability (`source="mcp://..."` on every tool call), and supports stdio / HTTP / SSE transports plus OAuth 2.1, Bearer, env-var, and custom auth.

---

## What is MCP?

[Model Context Protocol](https://modelcontextprotocol.io/) is an **open standard** for connecting LLM applications to external systems (databases, SaaS APIs, file systems, dev tools). An MCP server exposes **tools**, **resources**, and **prompts** over JSON-RPC; an MCP client (your agent) discovers and calls them. Anthropic published the spec in late 2024; OpenAI, Google, Microsoft, and the community have since published servers and clients.

NucleusIQ's universal adapter turns each MCP **tool** into a `BaseTool`, so your agent calls it the same way it calls **`@tool`** functions or built-in `FileReadTool` — no provider-specific glue.

---

## Universal adapter (`nucleusiq-mcp`)

### What ships in 0.1.0b1

| Capability | Supported |
|------------|-----------|
| **Transports** | `stdio` (subprocess), `Streamable HTTP` (preferred for HTTP servers), `SSE` (legacy HTTP), auto-detected from URL/command |
| **Auth** | **`BearerAuth`**, **`OAuthAuth`** (OAuth 2.1 + PKCE via MCP SDK's `OAuthClientProvider`), **`EnvAuth`** (forwards env vars to a subprocess), **`CustomHeadersAuth`**; auto-wired from `MCPTool(..., auth="xoxb-...")` shorthand |
| **`MCPTool`** factory | Public entry point; expands into **N** `BaseTool` instances during **`Agent.initialize()`** via the core `ExpandableTool` protocol |
| **`MCPBoundTool`** | Per-tool adapter; carries `source="mcp://server=<name> (path=A)"` for tracing |
| **`MCPSession`** | Thin wrapper around `mcp.ClientSession` — connect / list_tools / call_tool with retry + error mapping |
| **`MCPSchemaAdapter`** | Converts MCP `inputSchema` → NucleusIQ `BaseTool` spec, supports `$ref` / `$defs` inlining |
| **Decorator filters** | `@mcp_tool_filter` to include / exclude / rename MCP tools per server |
| **Graceful degradation** | `on_connect_failure="raise"` (default) or `"skip"` — agent boots even if a server is unreachable |
| **Health check + ping** | `health_check=True` (default) does a `list_tools` RPC after connect; **`MCPTool.ping()`** for runtime probes |
| **Observability** | Every MCP tool call produces a `ToolCallRecord` with `source="mcp://server=<name> ..."`; works with `enable_tracing=True` |
| **Errors** | `MCPConnectionError`, `MCPAuthError`, `MCPProtocolError`, `MCPTimeoutError`, `MCPToolError` — typed, structured |
| **Tests** | 235 unit (98.68% coverage) + 13 live integration tests against `@modelcontextprotocol/server-everything` (stdio + HTTP + SSE) |

### What's not (yet) in scope

- **MCP resources & prompts** — only **tools** are wired in 0.1.0b1. We treat MCP "prompts" as message lists; reach for NucleusIQ's own prompt framework (`PromptFactory`, `PromptTechnique`) for templating, few-shot, RAG, etc.
- **Server hosting** — `nucleusiq-mcp` is a **client/adapter only**. To author an MCP server, use the [official MCP SDK directly](https://github.com/modelcontextprotocol/python-sdk).
- **Sampling / progress callbacks** — planned for 0.2.x once usage patterns settle.

### Prerequisites

1. **Python** **`>=3.10`** with `nucleusiq>=0.7.11`.
2. **Node.js + `npx`** if you're connecting to **stdio** servers that ship as `@modelcontextprotocol/...` npm packages (most reference servers do).
3. The MCP server itself (a local command, a URL, or a token).

### Installation

```bash
# Through the core extras (recommended — keeps your pyproject tidy)
pip install "nucleusiq[mcp]" nucleusiq-anthropic     # or any provider

# Or pin the adapter directly
pip install "nucleusiq>=0.7.11" "nucleusiq-mcp==0.1.0b1"
```

### Quick start

The simplest case — connect to the GitHub MCP server via stdio and let Claude call it:

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
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")

    agent = Agent(
        name="github-researcher",
        prompt=ZeroShotPrompt().configure(
            system="You are a research assistant. Use the MCP tools when you need data from GitHub.",
        ),
        llm=BaseAnthropic(model_name=model, async_mode=True),
        tools=[
            # Transport auto-detected from the command (stdio); env vars are forwarded
            MCPTool(
                "npx -y @modelcontextprotocol/server-github",
                auth=os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"],
            ),
        ],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD, enable_tracing=True),
    )

    await agent.initialize()                  # Connects to the MCP server + discovers tools
    result = await agent.execute(
        Task(id="mcp-1", objective="Summarise the last 5 open issues in nucleusbox/NucleusIQ."),
    )
    print(result.output)

    # Tool calls now include their MCP origin
    for tc in result.tool_calls:
        print(tc.name, "<-", tc.source)        # e.g. "list_issues  <-  mcp://server=github (path=A)"


asyncio.run(main())
```

That's the whole integration. **`Agent.initialize()`** is where the connection happens; **`Agent.cleanup()`** (called automatically at the end of `execute()`) closes it.

### Transports

`MCPTool` auto-detects the transport from its first argument:

| Input shape | Transport | Example |
|-------------|-----------|---------|
| A shell command starting with an executable | `stdio` (subprocess) | `MCPTool("npx -y @modelcontextprotocol/server-github")` |
| `https://.../mcp` (or `/messages`) — newest spec | `Streamable HTTP` | `MCPTool("https://mcp.example.com/mcp", auth="...")` |
| `https://.../sse` — legacy spec | `SSE` | `MCPTool("https://mcp.example.com/sse", auth="...")` |

You can force it explicitly:

```python
from nucleusiq_mcp import MCPServerConfig, MCPTool, MCPTransport

MCPTool(MCPServerConfig(
    name="db",
    transport=MCPTransport.STDIO,
    command="python",
    args=["-m", "my_mcp_server"],
    env={"DATABASE_URL": "postgres://..."},
))
```

### Authentication

The string passed to `auth=` is interpreted heuristically; for production code prefer a typed strategy:

=== "Bearer / API key"

    ```python
    from nucleusiq_mcp import BearerAuth, MCPTool

    MCPTool(
        "https://mcp.slack.com/mcp",
        auth=BearerAuth(token="xoxb-..."),
    )
    ```

=== "Environment variable forwarded to stdio"

    ```python
    from nucleusiq_mcp import EnvAuth, MCPTool

    MCPTool(
        "npx -y @modelcontextprotocol/server-github",
        auth=EnvAuth(env={"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."}),
    )
    ```

=== "OAuth 2.1 (PKCE)"

    ```python
    from mcp.client.auth import OAuthClientProvider
    from nucleusiq_mcp import MCPTool, OAuthAuth

    MCPTool(
        "https://mcp.atlassian.com/mcp",
        auth=OAuthAuth(provider=OAuthClientProvider(
            server_url="https://mcp.atlassian.com",
            client_metadata=...,         # Per MCP SDK docs
            storage=...,                 # Where to persist tokens
        )),
    )
    ```

=== "Custom HTTP headers"

    ```python
    from nucleusiq_mcp import CustomHeadersAuth, MCPTool

    MCPTool(
        "https://mcp.example.com/mcp",
        auth=CustomHeadersAuth(headers={"X-Org-Id": "org_42", "X-Api-Key": "..."}),
    )
    ```

### Filtering and renaming MCP tools

A server may expose 30 tools and you only want 3 — or you want to rename a poorly-named one. Use **decorator-style filters** or the `include_tools` / `exclude_tools` / `rename` kwargs:

```python
from nucleusiq_mcp import MCPTool, mcp_tool_filter


@mcp_tool_filter(
    include={"get-sum", "get-issue"},                    # keep only these
    rename={"get-sum": "add", "get-issue": "github_issue"},
)
def my_filter(tool_name: str) -> bool:
    return True


agent = Agent(
    ...,
    tools=[
        MCPTool(
            "https://mcp.example.com/mcp",
            auth="...",
            include_tools=["get-sum", "get-issue"],
            rename={"get-sum": "add"},
        ),
        # Or attach a filter decorator directly:
        MCPTool("npx -y @modelcontextprotocol/server-everything", filter=my_filter),
    ],
)
```

### Graceful degradation

If a server is unreachable at boot, you can either fail fast (default) or skip it:

```python
MCPTool(
    "https://flaky.example.com/mcp",
    auth="...",
    on_connect_failure="skip",  # logs warning, agent keeps booting without these tools
)
```

This catches transport errors, OAuth failures, and even `asyncio.CancelledError` from `anyio` task groups (a known HTTP-transport edge case) — your agent still initializes cleanly.

### Health checks and runtime ping

By default, after the transport opens, `nucleusiq-mcp` does a `list_tools` RPC to confirm the JSON-RPC channel is alive (`health_check=True`). For long-running agents you can also probe at runtime:

```python
mcp = MCPTool("https://mcp.example.com/mcp", auth="...")
agent = Agent(..., tools=[mcp])
await agent.initialize()

# Later — never raises, returns False if the server has gone away
if not await mcp.ping():
    logger.warning("MCP server is down — disabling related tools")
```

### Multi-server

A single agent can talk to many MCP servers — each one expands into its own set of `MCPBoundTool` instances:

```python
agent = Agent(
    name="ops",
    llm=llm,
    tools=[
        MCPTool("npx -y @modelcontextprotocol/server-github", auth=os.environ["GITHUB_TOKEN"]),
        MCPTool("https://mcp.slack.com/mcp", auth=os.environ["SLACK_TOKEN"]),
        MCPTool("https://mcp.linear.app/mcp", auth=os.environ["LINEAR_TOKEN"]),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.AUTONOMOUS, enable_tracing=True),
)
```

`Agent.initialize()` opens all connections in **parallel** (`asyncio.gather(return_exceptions=True)`) and cleans every adapter up — even if one peer fails or the process is cancelled.

### Observability — `mcp://` source attribution

Every tool call routed through `nucleusiq-mcp` carries its origin in **`ToolCallRecord.source`**:

```python
result = await agent.execute(task)
for tc in result.tool_calls:
    print(f"{tc.name:20}  source={tc.source}")
# get_repo            source=mcp://server=github (path=A)
# search_messages     source=mcp://server=slack (path=A)
```

This is the **same field** used by all other tool adapters (built-in file tools leave it `None`, native OpenAI/Gemini tools may set their own). You can filter telemetry on it, alert on per-server error rates, and prove to security review exactly which third-party servers your agent touched on a given run.

### Imports

```python
from nucleusiq_mcp import (
    # Public entry point
    MCPTool,
    # Auth strategies
    MCPAuth, BearerAuth, EnvAuth, OAuthAuth, CustomHeadersAuth,
    # Configuration
    MCPServerConfig, MCPTransport, infer_transport,
    # Lower-level (advanced)
    MCPSession, MCPBoundTool, MCPSchemaAdapter,
    # Decorator filters
    MCPToolset, mcp_tool_filter,
    # Exceptions
    MCPError, MCPConnectionError, MCPAuthError,
    MCPTimeoutError, MCPProtocolError, MCPToolError,
)
```

### Runnable examples

Eight examples ship with the package — clone **[NucleusIQ](https://github.com/nucleusbox/NucleusIQ)** and run from **`src/providers/tools/mcp`**:

```bash
uv sync --group dev
uv run python examples/01_basic_stdio.py
uv run python examples/02_http_with_auth.py
uv run python examples/03_multi_server.py
uv run python examples/04_oauth_flow.py
uv run python examples/05_error_handling.py
uv run python examples/06_health_check.py
uv run python examples/07_decorator_filters.py
uv run python examples/08_full_agent_with_llm.py     # End-to-end Claude + MCP
```

Each is self-contained and includes setup notes. See **[examples/README.md](https://github.com/nucleusbox/NucleusIQ/blob/main/src/providers/tools/mcp/examples/README.md)** for the full parity table.

---

## Legacy path: OpenAI server-side MCP

If you're already on OpenAI and just want to point GPT at a remote MCP server without your process holding the connection, you can use the **`OpenAITool.mcp(...)`** factory. This routes the call through OpenAI's Responses API.

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

### When to use which

| You want… | Use |
|-----------|-----|
| Same MCP servers across OpenAI, Anthropic, Gemini, Groq, Ollama | **`nucleusiq-mcp`** (universal) |
| Observability (`source=mcp://...`) and a single `BaseTool` surface | **`nucleusiq-mcp`** |
| OAuth 2.1 / Bearer / env / custom auth | **`nucleusiq-mcp`** |
| Graceful degradation (`on_connect_failure="skip"`) | **`nucleusiq-mcp`** |
| **stdio** / local-process MCP servers | **`nucleusiq-mcp`** (OpenAI server-side cannot reach local processes) |
| Just declare a public MCP URL and let OpenAI handle the connection | **`OpenAITool.mcp(...)`** |
| Provider-native approval flow inside OpenAI's Responses API | **`OpenAITool.mcp(...)`** |

---

## Plugin guardrails

MCP tools are normal `BaseTool` instances, so every NucleusIQ plugin applies — **`ToolGuardPlugin`**, **`ToolCallLimitPlugin`**, **`ToolRetryPlugin`**, **`HumanApprovalPlugin`**, etc.:

```python
from nucleusiq.plugins.builtin import HumanApprovalPlugin, ToolGuardPlugin

agent = Agent(
    ...,
    tools=[MCPTool("https://mcp.stripe.com/mcp", auth="...")],
    plugins=[
        ToolGuardPlugin(allowed_tools=["search_customer", "list_invoices"]),     # whitelist
        HumanApprovalPlugin(require_approval_for=["refund_charge"]),             # gate destructive calls
    ],
)
```

---

## See also

- **[MCP quickstart](../examples/mcp-quickstart.md)** — Copy-paste patterns: single-server, multi-server, decorator filters, graceful degradation, tracing.
- **[Tool integration patterns](../tools/integration.md)** — How MCP coexists with `@tool`, built-in file tools, and provider-native tools.
- **[Tools overview](../tools.md)** — All four ways to add tools (decorator, BaseTool, provider-native, MCP).
- **[Providers](../providers.md)** — Portability table (MCP works with all of them).
- **[Anthropic provider](anthropic-provider.md)** — Used as the LLM in the examples on this page.
- **[Error handling](../core-concepts/error-handling.md)** — Where `MCPError` sits in the framework taxonomy.
- **[MCP design doc](https://github.com/nucleusbox/NucleusIQ/blob/main/docs/design/MCP_INTEGRATION_DESIGN.md)** — Full architecture, rationale, and Phase 1/2/3 status.
- **[Model Context Protocol spec](https://modelcontextprotocol.io/)** — The upstream open standard.
