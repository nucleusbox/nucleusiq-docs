# Providers

NucleusIQ uses provider packages so your agent code stays stable while model backends change. Write your agent once, swap providers with one line.

## Core idea

- `nucleusiq` contains agent orchestration, tools, memory, plugins, prompts, and streaming.
- Provider packages implement concrete LLM backends against the `BaseLLM` interface.
- Your agent code never imports provider internals — just the LLM class.

## Current providers

| Package | Category | Status | Install |
|---------|----------|--------|---------|
| `nucleusiq-openai` | LLM provider | 🟢 **Stable** — Chat Completions + Responses API | `pip install nucleusiq-openai` |
| `nucleusiq-openai-compatible` | Inference provider | 🟢 **Stable** — any Chat Completions server (vLLM, SGLang, llama.cpp, LM Studio, Azure OpenAI **v1**, …); **`nucleusiq>=0.7.13`** | `pip install nucleusiq-openai-compatible` |
| `nucleusiq-gemini` | LLM provider | 🟢 **Stable** — Google GenAI SDK (GA) | `pip install nucleusiq-gemini` |
| `nucleusiq-anthropic` | LLM provider | 🟢 **Stable** — Claude Messages API (`anthropic` SDK); **`nucleusiq>=0.7.12`** | `pip install nucleusiq-anthropic` |
| `nucleusiq-groq` | Inference provider | 🟢 **Stable** — Groq Chat Completions (`groq` SDK); **`nucleusiq>=0.7.12`** | `pip install nucleusiq-groq` |
| `nucleusiq-ollama` | Inference provider | 🟢 **Stable** — Ollama **native `/api/chat`** (`ollama` SDK); **`nucleusiq>=0.7.12`** | `pip install nucleusiq-ollama` |

## Tool adapters

NucleusIQ also ships **tool adapters** — provider-agnostic packages that expose external systems as `BaseTool` instances. They work with **every** LLM provider listed above.

| Package | Category | Status | Install |
|---------|----------|--------|---------|
| `nucleusiq-mcp` | Tool adapter | 🟢 **Stable** — Universal **[Model Context Protocol](https://modelcontextprotocol.io/)** client built on the official `mcp` SDK; stdio + Streamable HTTP + SSE; Bearer / OAuth 2.1 / Env / custom auth; **`nucleusiq>=0.7.12`**, **`mcp>=1.28.1`** | `pip install "nucleusiq[mcp]"` |

See the **[MCP integration guide](guides/mcp-integration.md)** for the full universal-adapter walkthrough and the comparison to **OpenAI's server-side MCP** path.

## Planned providers

| Package | Category | Target |
|---------|----------|--------|
| `nucleusiq-chroma` | DB provider | Backlog |
| `nucleusiq-pinecone` | DB provider | Backlog |

## Provider portability

The same agent code works with any provider:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt

# Choose your provider — swap the LLM line
from nucleusiq_openai import BaseOpenAI

llm = BaseOpenAI(model_name="gpt-4o")

# Or Gemini
# from nucleusiq_gemini import BaseGemini
# llm = BaseGemini(model_name="gemini-2.5-flash")

# Or a self-hosted / OpenAI-compatible server (vLLM, SGLang, llama.cpp, …)
# from nucleusiq_openai_compatible import OpenAICompatibleLLM
# llm = OpenAICompatibleLLM(
#     base_url="http://gpu-node-1:8000/v1",
#     model="gemma-4-27b-it",
#     context_window=32_768,
#     engine="vllm",
# )

# Or Anthropic Claude — Messages API (async_mode=True)
# from nucleusiq_anthropic import BaseAnthropic
# llm = BaseAnthropic(model_name="claude-3-5-sonnet-20241022", async_mode=True)

# Or Groq (use async_mode=True with the official SDK path)
# from nucleusiq_groq import BaseGroq
# llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)

# Or Ollama — native /api/chat (async_mode=True)
# from nucleusiq_ollama import BaseOllama
# llm = BaseOllama(model_name="llama3.2", async_mode=True)

agent = Agent(
    name="assistant",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=llm,
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    tools=my_tools,
    plugins=my_plugins,
)
result = await agent.execute({"id": "providers-doc-1", "objective": "Analyze this data"})
```

Tools, plugins, memory strategies, streaming, structured output, and all execution modes work identically across providers.

## Provider-specific parameters

Each provider has its own `LLMParams` subclass for provider-specific settings:

=== "OpenAI"

    ```python
    from nucleusiq_openai import OpenAILLMParams

    config = AgentConfig(
        llm_params=OpenAILLMParams(
            temperature=0.7,
            max_output_tokens=1024,
            reasoning_effort="high",  # OpenAI-specific
        ),
    )
    ```

=== "Gemini"

    ```python
    from nucleusiq_gemini import GeminiLLMParams, GeminiThinkingConfig

    config = AgentConfig(
        llm_params=GeminiLLMParams(
            temperature=0.7,
            max_output_tokens=1024,
            thinking_config=GeminiThinkingConfig(thinking_budget=2048),  # Gemini-specific
        ),
    )
    ```

=== "Anthropic"

    ```python
    from nucleusiq.agents.config import AgentConfig
    from nucleusiq.llms.llm_params import LLMParams
    from nucleusiq_anthropic import AnthropicLLMParams, BaseAnthropic

    llm = BaseAnthropic(
        model_name="claude-3-5-sonnet-20241022",
        async_mode=True,
        llm_params=AnthropicLLMParams(top_k=40),
    )
    config = AgentConfig(
        llm_params=LLMParams(temperature=0.7, max_output_tokens=1024),
    )
    ```

    **`AnthropicLLMParams`** lives on **`BaseAnthropic`** (**`top_k`**, **`anthropic_beta`**, **`extra_headers`**). Sampling uses framework **`LLMParams`** on **`AgentConfig`** — see [Anthropic provider](guides/anthropic-provider.md).

=== "Groq"

    ```python
    from nucleusiq_groq import GroqLLMParams

    config = AgentConfig(
        llm_params=GroqLLMParams(
            temperature=0.7,
            max_output_tokens=1024,
            parallel_tool_calls=True,
        ),
    )
    ```

=== "Ollama"

    ```python
    from nucleusiq_ollama import OllamaLLMParams

    config = AgentConfig(
        llm_params=OllamaLLMParams(
            temperature=0.7,
            max_output_tokens=1024,
            think="medium",
            keep_alive="5m",
        ),
    )
    ```

=== "OpenAI-compatible"

    ```python
    from nucleusiq_openai_compatible import OpenAICompatibleLLMParams

    config = AgentConfig(
        llm_params=OpenAICompatibleLLMParams(
            temperature=0.7,
            max_output_tokens=1024,
        ),
    )
    ```

Common parameters (`temperature`, `max_output_tokens`, `top_p`) are defined in the base `LLMParams` and work across all providers.

## Provider-native tools

Each provider can expose server-side tools:

| Provider | Native tools |
|----------|-------------|
| OpenAI | `code_interpreter`, `file_search`, `web_search`, `image_generation`, `mcp` (server-side), `computer_use` |
| Gemini | `google_search`, `code_execution`, `url_context`, `google_maps` |
| Anthropic | `AnthropicTool.web_search()` / `web_fetch()` / `code_execution()` plus framework `@tool` ([Anthropic provider](guides/anthropic-provider.md)) |
| Groq | Framework `@tool` / local function tools — Groq hosted tools are not wired yet ([Groq provider](guides/groq-provider.md)) |
| Ollama | Framework `@tool` via native `/api/chat` — no separate native-tool factory ([Ollama provider](guides/ollama-provider.md)) |
| OpenAI-compatible | Framework `@tool` over Chat Completions `tools` — no hosted-tool factory ([OpenAI-compatible provider](guides/openai-compatible-provider.md)) |

Native tools are accessed via provider-specific factories (`OpenAITool`, `GeminiTool`) and can be mixed with framework-level tools in the same agent.

### Cross-provider tools via `nucleusiq-mcp`

When you need a tool to work across **every** provider, use the **MCP tool adapter** — it exposes any [Model Context Protocol](https://modelcontextprotocol.io/) server (GitHub, Slack, Postgres, Stripe, your own) as one or more `BaseTool` instances. Same agent code, same plugins, same tracing — no provider-specific tool factory.

```python
from nucleusiq_mcp import MCPTool

agent = Agent(
    ...,
    llm=BaseAnthropic(model_name="claude-haiku-4-5", async_mode=True),  # or any provider
    tools=[MCPTool("npx -y @modelcontextprotocol/server-github", auth=os.environ["GITHUB_TOKEN"])],
)
await agent.initialize()
```

See the **[MCP integration guide](guides/mcp-integration.md)** for full coverage.

## Error handling

All providers map SDK errors to NucleusIQ's [framework-level error taxonomy](core-concepts/error-handling.md). You catch `RateLimitError`, `AuthenticationError`, etc. regardless of which provider raised it.

## Compatibility

- The core package is versioned independently from provider packages.
- Provider packages declare their minimum **`nucleusiq`** version. **`nucleusiq-openai-compatible`** requires **`>=0.7.13`**. The other first-party providers floor on **`>=0.7.12`**.
- Always keep provider versions compatible with your installed `nucleusiq` version.

## See also

- [OpenAI-compatible provider](guides/openai-compatible-provider.md) — Self-hosted / BYOM Chat Completions
- [MCP integration guide](guides/mcp-integration.md) — Universal Model Context Protocol adapter, works with every provider
- [Anthropic provider guide](guides/anthropic-provider.md) — Claude Messages API, Phase B native tools
- [Ollama provider guide](guides/ollama-provider.md) — Native `/api/chat`, vision, **`think`**
- [Groq provider guide](guides/groq-provider.md) — Groq Chat Completions, rate limits
- [Gemini provider guide](guides/gemini-provider.md) — Full Gemini integration details
- [OpenAI provider guide](guides/openai-provider.md) — OpenAI cloud, Responses API, hosted tools
- [Models](models.md) — Provider-agnostic model usage
- [Install](install.md) — Setup instructions
