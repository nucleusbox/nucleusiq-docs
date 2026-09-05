# Examples

Detailed practical examples for common NucleusIQ workflows.

*Updated for v0.7.13: mandatory `prompt=` and current pins. New **[OpenAI-compatible quickstart](openai-compatible-quickstart.md)** for self-hosted / BYOM. See [migration notes](../learn/migration-notes.md) if upgrading.*

## Getting started

- [Basic agent](basic-agent.md) — Your first agent with tools (OpenAI, Gemini, context management)
- [Streaming](streaming.md) — Real-time token-by-token output

## Workflows

- [File workflow](file-workflow.md) — Search, read, and extract from files
- [Autonomous workflow](autonomous-workflow.md) — Multi-step task with Critic/Refiner verification

## Observability

- [Usage tracking](usage-tracking.md) — Token usage by purpose and origin
- [Cost estimation](cost-estimation.md) — Dollar cost tracking after execution

## Provider examples

- [OpenAI-compatible quickstart](openai-compatible-quickstart.md) — Self-hosted vLLM / SGLang / llama.cpp / LM Studio / Azure OpenAI **v1** (**`nucleusiq-openai-compatible` 0.1.0**, **`nucleusiq>=0.7.13`**)
- [Gemini quickstart](gemini-quickstart.md) — Google Gemini with all three execution modes
- [Anthropic quickstart](anthropic-quickstart.md) — Claude DIRECT / STANDARD / AUTONOMOUS (**`nucleusiq-anthropic` 0.2.1**, **`nucleusiq>=0.7.12`**)
- [Groq quickstart](groq-quickstart.md) — Groq DIRECT / STANDARD / AUTONOMOUS (**`nucleusiq-groq` 0.1.1**, **`nucleusiq>=0.7.12`**)
- [Ollama quickstart](ollama-quickstart.md) — Native Ollama DIRECT / STANDARD (**`nucleusiq-ollama` 0.2.1**, **`nucleusiq>=0.7.12`**)
- [OpenAI-compatible provider](../guides/openai-compatible-provider.md) — Engines, auth, `validate()`, structured-output policy
- [Anthropic provider guide](../guides/anthropic-provider.md) — Phase B native tools, prompt caching, extended thinking
- [Groq provider guide](../guides/groq-provider.md) — **429** / **`Retry-After`**, **`strict_model_capabilities`**, repo scripts
- [Ollama provider guide](../guides/ollama-provider.md) — Native `/api/chat`, **`think`**, vision, structured-output + tools caveat

## Tool adapter examples

- [MCP quickstart](mcp-quickstart.md) — Universal **Model Context Protocol** adapter across **every** provider (**`nucleusiq-mcp` 0.1.1**, **`nucleusiq>=0.7.12`**): stdio, HTTP + Bearer, multi-server, filter/rename, graceful degradation, source tracing, plugin guardrails
- [MCP integration guide](../guides/mcp-integration.md) — Transports, auth strategies, filtering, `ping()`, comparison vs OpenAI server-side MCP

!!! tip "Which page for self-hosted / BYOM?"

    Start with **[OpenAI-compatible quickstart](openai-compatible-quickstart.md)**; use **[OpenAI-compatible provider](../guides/openai-compatible-provider.md)** for engines, auth, `validate()`, and Azure OpenAI v1 limits.

!!! tip "Which page for Anthropic (Claude)?"

    Start with **[Anthropic quickstart](anthropic-quickstart.md)**; use **[Anthropic provider](../guides/anthropic-provider.md)** for install pins, env vars, limitations, and CI-tested examples.

!!! tip "Which page for Ollama?"

    Start with **[Ollama quickstart](ollama-quickstart.md)**; use **[Ollama provider](../guides/ollama-provider.md)** for the full capability matrix and env reference.

!!! tip "Which Groq page?"

    Start with **[Groq quickstart](groq-quickstart.md)** for copy-paste snippets; use **[Groq provider](../guides/groq-provider.md)** for deeper operational guidance.

!!! tip "Which page for MCP?"

    Start with **[MCP quickstart](mcp-quickstart.md)** for copy-paste recipes (stdio + HTTP, multi-server, tracing); use **[MCP integration guide](../guides/mcp-integration.md)** for transports, OAuth, decorator filters, and graceful degradation.

## Repository examples

Full runnable scripts are available in the GitHub repository:

- [Core examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/nucleusiq/examples)
- [OpenAI examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/openai/examples)
- [OpenAI-compatible examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/openai_compatible/examples)
- [Gemini examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/gemini/examples)
- [Anthropic examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/anthropic/examples) — DIRECT through AUTONOMOUS, streaming, native structured demo
- [Groq examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/groq/examples) — Direct through Autonomous + structured output
- [Ollama examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/ollama/examples) — Smoke, Direct, streaming live, capabilities matrix
- [MCP examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/tools/mcp/examples) — Eight runnable examples: stdio, HTTP + auth, multi-server, OAuth, error handling, health check, decorator filters, full agent with LLM
- [Notebooks](https://github.com/nucleusbox/NucleusIQ/tree/main/notebooks) — Jupyter notebooks: context management showcase, **`mcp_tools_showcase.ipynb`** (Windows-friendly Streamable HTTP demo), and more
