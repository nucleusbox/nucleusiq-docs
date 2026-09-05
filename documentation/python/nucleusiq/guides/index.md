# Guides

Implementation-focused guides for common production patterns.

## Core guides

- [Strategy](strategy.md) — Gearbox strategy and mode selection
- [Agent guide](agent.md) — Agent lifecycle and configuration
- [Agent config guide](agent-config.md) — `AgentConfig` deep dive
- [MCP integration](mcp-integration.md) — **Model Context Protocol** universal adapter — **🟢 `nucleusiq-mcp` 0.1.1 Stable**, `nucleusiq>=0.7.12`, `mcp>=1.28.1` + legacy OpenAI server-side path
- [File handling](file-handling.md) — Attachment vs Tool vs Both

## Provider guides

| Provider | Package | Version | Status |
|----------|---------|---------|--------|
| [OpenAI](openai-provider.md) | `nucleusiq-openai` | **0.7.1** | 🟢 Stable — Chat Completions, Responses API, native tools, usage-accounting fix |
| [OpenAI-compatible](openai-compatible-provider.md) | `nucleusiq-openai-compatible` | **0.1.0** | 🟢 **New, Stable** — vLLM / SGLang / llama.cpp / LM Studio / Azure OpenAI **v1** / any Chat Completions server. Requires **`nucleusiq>=0.7.13`** |
| [Gemini](gemini-provider.md) | `nucleusiq-gemini` | **0.3.1** | 🟢 Stable — google_search / code_execution server-tool observability, thinking, multimodal |
| [Anthropic](anthropic-provider.md) | `nucleusiq-anthropic` | **0.2.1** | 🟢 Stable — **Phase B feature-complete** (native tools, prompt caching, extended thinking) |
| [Groq](groq-provider.md) | `nucleusiq-groq` | **0.1.1** | 🟢 Stable — Chat Completions, local tools, streaming, server-tool emission stub |
| [Ollama](ollama-provider.md) | `nucleusiq-ollama` | **0.2.1** | 🟢 Stable — native `/api/chat`, streaming, tools, structured output, **vision** |

`nucleusiq-openai-compatible` requires `nucleusiq>=0.7.13`. Every other first-party provider floors on `nucleusiq>=0.7.12`.

## Cross-cutting concepts (new in v0.7.12)

!!! tip "Pair with the Anthropic provider guide"

    These three pages explain features that are exposed through `nucleusiq-anthropic 0.2.0` but the **observability** they surface (`executed_by="provider"`, `cache_*_tokens`, `stop_reason`, `request_id`) applies uniformly across **every** provider in v0.7.12.

- [Native server tools](native-server-tools.md) — `web_search` / `code_execution` / `google_search` / `file_search` — local vs provider execution.
- [Prompt caching](prompt-caching.md) — Anthropic `cache_system` / `cache_tools` and reading `cache_read_input_tokens`.
- [Extended thinking](extended-thinking.md) — Claude `thinking="low"|"medium"|"high"|"max"` and its hard constraints.
