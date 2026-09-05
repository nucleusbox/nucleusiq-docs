<div class="home-hero" markdown>

# NucleusIQ Documentation

Build AI agents as durable software systems, not one-off demos.

[Get Started](python/nucleusiq/get-started/index.md){ .md-button .md-button--primary }
[Core Concepts](python/nucleusiq/core-concepts/index.md){ .md-button }

</div>

---

## What We Are Building

NucleusIQ is an **open-source, agent-first Python framework** for teams that want to ship agents into real products.

The core idea is simple: agents should be engineered like serious software systems:

- maintainable by teams over time
- testable and observable in production
- provider-portable as the ecosystem changes
- structured for tools, memory, policy, and validation

An agent is not just one model call. It is a managed runtime with responsibilities.

---

## Why NucleusIQ Exists

Modern models can produce impressive demos quickly.  
The hard part is owning those systems for months and years.

NucleusIQ is designed to close that gap between:

- what AI can generate fast, and
- what engineering teams can safely maintain long term.

This means less fragile glue code, less accidental complexity, and clearer architecture as systems grow.

---

## Our Philosophy

NucleusIQ follows a practical philosophy for dependable agent engineering:

### 1) Agent-first thinking
Design around the full agent lifecycle (execution, tools, memory, policy), not isolated model calls.

### 2) Harness over hype
Reliability comes from good scaffolding: boundaries, artifacts, visibility, and feedback loops.

### 3) Progressive complexity
Start simple, add orchestration only when the task justifies it.

### 4) Open integration, closed coupling
Integrate broadly with providers and tools, but keep the core architecture stable and portable.

### 5) Reliability is a feature
Validation, structured output, policy controls, and observability are first-class parts of the framework.

---

## Build Path

Choose your path based on where you are today:

- **Start**: [Installation](python/nucleusiq/install.md) and [Quickstart](python/nucleusiq/quickstart.md)
- **Understand**: [Overview](python/nucleusiq/overview.md) and [Core Concepts](python/nucleusiq/core-concepts/index.md)
- **Scale**: [Execution Modes](python/nucleusiq/execution-modes.md), [Tools](python/nucleusiq/tools.md), [Memory](python/nucleusiq/memory.md), [Plugins](python/nucleusiq/plugins/overview.md)
- **Ship**: [Production Architecture](python/nucleusiq/core-concepts/production-architecture.md), [Structured Output](python/nucleusiq/structured-output.md), [Observability](python/nucleusiq/usage-tracking.md)

---

## What's new in v0.7.13 — self-hosted and bring-your-own-model ✨

!!! success "`nucleusiq-openai-compatible` 0.1.0 Stable — one adapter for every Chat Completions server"

    **v0.7.13** lets you point a NucleusIQ agent at **your GPU, your model, your key**. Install one extra package and the same `Agent` / tools / memory / plugins stack talks to vLLM, SGLang, TGI, llama.cpp, LM Studio, NVIDIA NIM, Ollama `/v1`, OpenRouter, Together, and **Azure OpenAI v1**.

    | Package | Version | Notes |
    |---------|---------|-------|
    | **`nucleusiq`** | **`0.7.13`** | Declared `BaseLLM.PROVIDER_NAME` — no more class-name guessing |
    | **`nucleusiq-openai-compatible`** | **`0.1.0`** | 🟢 **New, Stable.** Requires `nucleusiq>=0.7.13` |
    | **`nucleusiq-openai`** | **`0.7.1`** | Responses API usage: tokens and cost no longer report as zero |
    | **`nucleusiq-mcp`** | **`0.1.1`** | Security floor `mcp>=1.28.1` |
    | **`nucleusiq-gemini`** | **`0.3.1`** | `PROVIDER_NAME` + declared `pydantic` |
    | **`nucleusiq-anthropic`** | **`0.2.1`** | `PROVIDER_NAME` + declared deps |
    | **`nucleusiq-ollama`** | **`0.2.1`** | same |
    | **`nucleusiq-groq`** | **`0.1.1`** | same |

    Only the new provider floors on `nucleusiq>=0.7.13`. Existing OpenAI / Gemini / Anthropic / Groq / Ollama / MCP apps keep working on `>=0.7.12`. **4,382 tests** passing.

    [Release notes — v0.7.13](reference/release-notes/v0.7.13.md){ .md-button .md-button--primary } · [OpenAI-compatible guide](python/nucleusiq/guides/openai-compatible-provider.md){ .md-button } · [Quickstart](python/nucleusiq/examples/openai-compatible-quickstart.md){ .md-button }

```python
from nucleusiq_openai_compatible import OpenAICompatibleLLM

llm = OpenAICompatibleLLM(
    base_url="http://gpu-node-1:8000/v1",
    model="gemma-4-27b-it",
    context_window=32_768,
    engine="vllm",
)
```

Drop that `llm` into any existing `Agent`. Tools, modes, memory, and plugins do not change.

!!! warning "Azure OpenAI is v1 Chat Completions only"

    Use `engine="azure"`, `base_url="https://{resource}.openai.azure.com/openai/v1"`, and `auth=HeaderAuth("api-key", ...)`. Classic `/openai/deployments/{name}?api-version=` URLs and the `AzureOpenAI` SDK are **not** used.

## What was new in v0.7.12 — coordinated stable release

!!! success "Every alpha/beta provider promoted to Stable in one coordinated release"

    **v0.7.12** is the largest release since the project began — a single, coordinated promotion that takes every alpha/beta provider to its **first stable line** and ships the **cross-cutting native-tool observability** that powers it.

    | Package | Before | Now | Status |
    |---------|--------|-----|--------|
    | **`nucleusiq`** | `0.7.11` | **`0.7.12`** | 🟢 Core release |
    | **`nucleusiq-anthropic`** | `0.1.0a1` (alpha) | **`0.2.0`** | 🟢 **Stable** — Phase B feature-complete |
    | **`nucleusiq-ollama`** | `0.1.0a1` (alpha) | **`0.2.0`** | 🟢 **Stable** — + vision wire |
    | **`nucleusiq-groq`** | `0.1.0b1` (beta) | **`0.1.0`** | 🟢 **Stable** |
    | **`nucleusiq-mcp`** | `0.1.0b1` (beta) | **`0.1.0`** | 🟢 **Stable** |
    | **`nucleusiq-openai`** | `0.6.4` | **`0.7.0`** | 🟢 Stable (native-tool obs) |
    | **`nucleusiq-gemini`** | `0.2.6` | **`0.3.0`** | 🟢 Stable (native-tool obs) |

    All providers floor on `nucleusiq>=0.7.12`. **3,705+ tests passing across the monorepo** (incl. 6 live Anthropic Phase B tests against the real API). After this release the project returns to a bug-fix / single-provider cadence.

    [Release notes — v0.7.12](reference/release-notes/v0.7.12.md){ .md-button .md-button--primary } · [Changelog](reference/changelog.md){ .md-button }

!!! info "Anthropic 0.2.0 Stable — Phase B feature-complete 🚀"

    `nucleusiq-anthropic` graduates from alpha to **Production/Stable** with full Phase B support: **native server tools**, **prompt caching**, **extended thinking**, and **first-class server-tool observability**.

    - **`AnthropicTool` factory** — `web_search()`, `web_fetch()`, `code_execution()` with dated wire types and auto `anthropic-beta` headers.
    - **Prompt caching** — `cache_system=True` / `cache_tools=True` cuts repeated-prompt token cost dramatically.
    - **Extended thinking** — `thinking="low"|"medium"|"high"|"max"` resolved to a token budget at wire time.
    - **Server-tool observability** — `server_tool_use` + per-tool `*_tool_result` blocks (`code_execution_tool_result`, `web_search_tool_result`, …) surface as `ServerToolCall` + `ToolCallRecord(executed_by="provider")` automatically.
    - 3 runnable Phase B example scripts + 6 **live** integration tests against the real Anthropic API.
    - **151 unit tests, 95.91% coverage** (gate ≥ 95%).

    [Anthropic provider guide](python/nucleusiq/guides/anthropic-provider.md){ .md-button } · [Native server tools](python/nucleusiq/guides/native-server-tools.md){ .md-button } · [Prompt caching](python/nucleusiq/guides/prompt-caching.md){ .md-button } · [Extended thinking](python/nucleusiq/guides/extended-thinking.md){ .md-button }

!!! tip "Provider-agnostic native-tool observability in core"

    A new field on every traced tool call — `ToolCallRecord.executed_by: Literal["local","provider"]` — lets you split locally-run tools from provider-executed ones (Anthropic `web_search`, OpenAI `code_interpreter` / `file_search` / `web_search`, Gemini `google_search` / `code_execution`, Groq compound tools) **with one query**.

    `LLMCallRecord` also gained `provider`, `request_id`, `organization_id`, `stop_reason`, `cache_read_input_tokens`, `cache_creation_input_tokens`, and a generic `metadata` dict — populated by every provider in this release.

    [Observability guide](python/nucleusiq/observability/index.md){ .md-button .md-button--primary }

!!! example "Ollama 0.2.0 Stable — vision wire"

    `nucleusiq-ollama` graduates to Stable. The wire layer now splits OpenAI-style multimodal `content` lists into Ollama's `message.content` + `message.images` fields, with proper handling of `data:image/...;base64,...` URLs and warnings for HTTP image URLs.

    [Ollama provider guide](python/nucleusiq/guides/ollama-provider.md){ .md-button }

## What was new in v0.7.11

### MCP tool adapter (now Stable in v0.7.12)

!!! success "`nucleusiq-mcp` 0.1.0 — Stable (was beta in v0.7.11)"

    **Universal [Model Context Protocol](https://modelcontextprotocol.io/) adapter** — plug any MCP server (GitHub, Slack, Postgres, Stripe, your own) into a NucleusIQ agent in one line, across **any** LLM provider. Built on the **official `mcp` SDK**.

    - **Transports**: **`stdio`** + **Streamable HTTP** + **SSE** (auto-detected).
    - **Auth**: **`BearerAuth`**, **`OAuthAuth`** (OAuth 2.1 + PKCE), **`EnvAuth`**, **`CustomHeadersAuth`** — typed strategies + `auth="..."` shorthand.
    - **Resilience**: **`on_connect_failure="skip"`**, **`health_check=True`**, runtime **`MCPTool.ping()`**.
    - **Observability**: every tool call carries **`source="mcp://server=<name> ..."`** for tracing.
    - **Tests**: 235 unit (**98.68%** coverage) + 13 live integration tests across all three transports.

    [MCP integration guide](python/nucleusiq/guides/mcp-integration.md){ .md-button .md-button--primary } · [MCP quickstart](python/nucleusiq/examples/mcp-quickstart.md){ .md-button }

### v0.7.10 (latest tagged core)

!!! success "Core security extras + Ollama alpha"
    - **`nucleusiq` 0.7.10** — optional **`nucleusiq[http]`**; **`urllib3`** resolution hardening in locks; structured-output resolver recognizes **Ollama** / Groq LLMs for **`OutputSchema`** payloads.
    - **`nucleusiq-ollama` 0.1.0a1** (**alpha**) — local / remote **[Ollama](https://ollama.com/)** via official **`ollama`** SDK: **`BaseOllama`**, tools, streaming, structured **`format`**, **`think`** / **`keep_alive`**. Requires **`nucleusiq>=0.7.10`**.

    [Changelog](reference/changelog.md){ .md-button } · [Ollama provider](python/nucleusiq/guides/ollama-provider.md){ .md-button } · [Ollama quickstart](python/nucleusiq/examples/ollama-quickstart.md){ .md-button } · [Migration (0.7.9 → 0.7.10)](python/nucleusiq/learn/migration-notes.md#from-v079-to-v0710){ .md-button }

### v0.7.9

!!! success "LLM rate limits + Groq beta"
    - **`nucleusiq.llms.retry_policy`** — shared **429** handling: **`Retry-After`** parsing, capped backoff, ceiling (**120s** default single sleep cap).
    - **Providers:** **`nucleusiq-openai` 0.6.4**, **`nucleusiq-gemini` 0.2.6**, **`nucleusiq-groq` 0.1.0b1** (public **beta**) — dependency floor **`nucleusiq>=0.7.9`**.
    - **Groq** — stream **open** uses the same **429** policy as chat; **`strict_model_capabilities`** on **`GroqLLMParams`**; **`nucleusiq_groq.capabilities`** allowlist for **`parallel_tool_calls`** (warnings vs strict **`InvalidRequestError`**).

    [Changelog](reference/changelog.md){ .md-button } · [Groq provider](python/nucleusiq/guides/groq-provider.md){ .md-button } · [Groq quickstart](python/nucleusiq/examples/groq-quickstart.md){ .md-button } · [Migration (0.7.8 → 0.7.9)](python/nucleusiq/learn/migration-notes.md#from-v078-to-v079){ .md-button }

### v0.7.8

!!! info "Run-local context state + Groq alpha debut"
    - **Workspace / evidence / lexical corpus** — per-run in-memory analyst state with optional framework tools (budget-exempt).
    - **L4.5 activation**, **phase control**, **evidence gate**, **synthesis package**, autonomous fixes — see [Run-local context state](python/nucleusiq/run-local-context-state.md).
    - **Groq** landed first as **`nucleusiq-groq` 0.1.0a1** (since superseded by **0.1.0b1** + **`nucleusiq>=0.7.9`**).

    [Changelog](reference/changelog.md){ .md-button } · [Migration (0.7.7 → 0.7.8)](python/nucleusiq/learn/migration-notes.md#from-v077-to-v078){ .md-button }

### v0.7.7

!!! success "Context Management v2 + execution fixes"
    - **Stable V2 pipeline** — compaction, masking, recall/rehydration tuned for PDF-heavy agents (`squeeze_threshold=0.70` default).
    - **Optional `@tool(idempotent=True)`** — safe dedup for pure tools; default remains non-idempotent.
    - **`AgentResult` + tool caps** — clearer `status=error` and `ToolCallLimitError` when limits bite; **tools-free synthesis** when the tool cap is hit (synthesis on).
    - **Providers:** `nucleusiq-openai` **0.6.3**, `nucleusiq-gemini` **0.2.5** — aligned with core 0.7.7.

    [Changelog](reference/changelog.md){ .md-button } · [Migration (0.7.6 → 0.7.7)](python/nucleusiq/learn/migration-notes.md#from-v076-to-v077){ .md-button }

### v0.7.6

!!! success "Context Window Management"

    Automatic context management for tool-heavy agents — prevents context overflow and ensures the LLM always has room to respond.

    ```python
    from nucleusiq.agents.context import ContextConfig, ContextStrategy

    config = AgentConfig(
        context=ContextConfig(strategy=ContextStrategy.PROGRESSIVE),
    )
    ```

    [Context management guide](python/nucleusiq/context-management.md){ .md-button }

!!! warning "Breaking: Prompt System Refactor"

    `prompt` is now **mandatory** on `Agent`. The `narrative` field has been removed. `role` and `objective` are labels only — they are **not** sent to the LLM.

    ```python
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a data analyst. Provide detailed analysis.",
        ),
        llm=llm,
    )
    ```

    [Migration guide](python/nucleusiq/learn/migration-notes.md#from-v075-to-v076){ .md-button }

!!! info "Synthesis Pass + ObservabilityConfig"

    - **Synthesis pass** — after multi-round tool loops, the agent makes one final LLM call without tools to produce the full deliverable
    - **ObservabilityConfig** — unified config replacing `verbose` + `enable_tracing`
    - **Context telemetry** — peak utilization, compaction events, token savings in `AgentResult`

    [Observability docs](python/nucleusiq/observability/index.md){ .md-button }

### v0.7.5

- **Gemini native + custom tool mixing** — transparent proxy pattern, zero code changes
- **Full observability wiring** — PluginEvent, MemorySnapshot, AutonomousDetail in AgentResult

### v0.7.4

- **ExecutionTracer** — full LLM/tool call observability
- **Pyrefly static type checking** — 121 type errors fixed, CI-gated
- **Exhaustive error wiring** — typed exceptions everywhere

### v0.7.2-0.7.3

- **Unified exception hierarchy** — 10 error families
- **AgentResult response contract** — typed, immutable Pydantic model
- **Gemini tool-calling fixes** — `$ref`/`$defs` inlining

Current packages (all 🟢 Stable as of **v0.7.13** / 2026-09-05): `nucleusiq` **0.7.13**, `nucleusiq-openai-compatible` **0.1.0**, `nucleusiq-openai` **0.7.1**, `nucleusiq-gemini` **0.3.1**, `nucleusiq-anthropic` **0.2.1**, `nucleusiq-groq` **0.1.1**, `nucleusiq-ollama` **0.2.1**, `nucleusiq-mcp` **0.1.1**. The new OpenAI-compatible provider floors on `nucleusiq>=0.7.13`; the others stay on `>=0.7.12`.

See the [full changelog](reference/changelog.md).

---

## Quick links

- [Get Started](python/nucleusiq/get-started/index.md)
- [Guides](python/nucleusiq/guides/index.md)
- [Examples](python/nucleusiq/examples/index.md)
- [Reference](reference/index.md)
