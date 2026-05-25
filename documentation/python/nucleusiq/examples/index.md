# Examples

Detailed practical examples for common NucleusIQ workflows.

*Updated for v0.7.10+: mandatory `prompt=` and current pins; **Anthropic Claude** (**alpha**) examples live under [Anthropic quickstart](anthropic-quickstart.md). See [migration notes](../learn/migration-notes.md) if upgrading.*

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

- [Gemini quickstart](gemini-quickstart.md) — Google Gemini with all three execution modes
- [Anthropic quickstart](anthropic-quickstart.md) — Claude DIRECT / STANDARD / AUTONOMOUS (**`nucleusiq-anthropic` 0.1.0a1**, **`nucleusiq>=0.7.10`** — **alpha**)
- [Groq quickstart](groq-quickstart.md) — Groq DIRECT / STANDARD / AUTONOMOUS (**`nucleusiq-groq` 0.1.0b1**, **`nucleusiq>=0.7.9`**)
- [Ollama quickstart](ollama-quickstart.md) — Local Ollama DIRECT / STANDARD (**`nucleusiq-ollama` 0.1.0a1**, **`nucleusiq>=0.7.10`** — **alpha**)
- [Anthropic provider guide](../guides/anthropic-provider.md) — Alpha announcement, Messages API scope, structured-output caveats, runnable **`src/providers/llms/anthropic/examples`**
- [Groq provider guide](../guides/groq-provider.md) — Beta scope, **429** / **`Retry-After`**, **`strict_model_capabilities`**, repo scripts
- [Ollama provider guide](../guides/ollama-provider.md) — Alpha scope, **`think`**, structured-output + tools caveat, repo matrix

## Tool adapter examples

- [MCP quickstart](mcp-quickstart.md) — Universal **Model Context Protocol** adapter across **every** provider (**`nucleusiq-mcp` 0.1.0b1**, **`nucleusiq>=0.7.11`** — **beta**): single stdio server, HTTP + Bearer auth, multi-server, filter/rename, graceful degradation, source tracing, plugin guardrails
- [MCP integration guide](../guides/mcp-integration.md) — Beta announcement, transports (stdio + Streamable HTTP + SSE), auth strategies (Bearer / OAuth 2.1 / Env / Custom), filtering, `ping()`, comparison vs OpenAI server-side MCP

!!! tip "Which page for Anthropic (Claude)?"

    Start with **[Anthropic quickstart](anthropic-quickstart.md)**; use **[Anthropic provider](../guides/anthropic-provider.md)** for install pins, env vars, limitations, and CI-tested examples.

!!! tip "Which page for Ollama?"

    Start with **[Ollama quickstart](ollama-quickstart.md)**; use **[Ollama provider](../guides/ollama-provider.md)** for the full capability matrix and env reference.

!!! tip "Which Groq page?"

    Start with **[Groq quickstart](groq-quickstart.md)** for copy-paste snippets; use **[Groq provider](../guides/groq-provider.md)** for deeper operational guidance.

!!! tip "Which page for MCP?"

    Start with **[MCP quickstart](mcp-quickstart.md)** for copy-paste recipes (stdio + HTTP, multi-server, tracing); use **[MCP integration guide](../guides/mcp-integration.md)** for the full beta scope, OAuth, decorator filters, and graceful degradation.

## Repository examples

Full runnable scripts are available in the GitHub repository:

- [Core examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/nucleusiq/examples)
- [OpenAI examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/openai/examples)
- [Gemini examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/gemini/examples)
- [Anthropic examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/anthropic/examples) — DIRECT through AUTONOMOUS, streaming, native structured demo (**alpha**)
- [Groq examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/groq/examples) — Direct through Autonomous + structured output
- [Ollama examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/ollama/examples) — Smoke, Direct, streaming live, capabilities matrix (**alpha**)
- [MCP examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/tools/mcp/examples) — Eight runnable examples: stdio, HTTP + auth, multi-server, OAuth, error handling, health check, decorator filters, full agent with LLM (**beta**)
- [Notebooks](https://github.com/nucleusbox/NucleusIQ/tree/main/notebooks) — Jupyter notebooks: context management showcase, **`mcp_tools_showcase.ipynb`** (Windows-friendly Streamable HTTP demo), and more
