# Get Started

Start here to install NucleusIQ and run your first agent.

## Recommended order

1. [Introduction](../overview.md)
2. [Installation](../install.md)
3. [Quickstart](../quickstart.md)
4. [Core concepts](../core-concepts/index.md)
5. [Guides](../guides/index.md)
6. [Examples](../examples/index.md)

## Quick links

- [Introduction](../overview.md)
- [Installation](../install.md)
- [Quickstart](../quickstart.md)

Then continue with:

- [Execution modes](../execution-modes.md)
- [Examples](../examples/index.md)

## Inference backends

Same **`Agent`** code works across packages — pick an install tab in [Installation](../install.md), then:

- [OpenAI-compatible provider](../guides/openai-compatible-provider.md) · [OpenAI-compatible quickstart](../examples/openai-compatible-quickstart.md) — self-hosted / BYOM Chat Completions (**`nucleusiq-openai-compatible` 0.1.0**, **`nucleusiq>=0.7.13`**)
- [Anthropic provider](../guides/anthropic-provider.md) · [Anthropic quickstart](../examples/anthropic-quickstart.md) — Claude Messages API (**`nucleusiq-anthropic` 0.2.1**, **`nucleusiq>=0.7.12`**)
- [Groq provider](../guides/groq-provider.md) · [Groq quickstart](../examples/groq-quickstart.md) — Groq cloud (**`nucleusiq-groq` 0.1.1**)
- [Ollama provider](../guides/ollama-provider.md) · [Ollama quickstart](../examples/ollama-quickstart.md) — native `/api/chat` (**`nucleusiq-ollama` 0.2.1**, **`nucleusiq>=0.7.12`**)

## Tool adapters

- [MCP integration guide](../guides/mcp-integration.md) · [MCP quickstart](../examples/mcp-quickstart.md) — Universal **Model Context Protocol** adapter (**`nucleusiq-mcp` 0.1.1**, **`nucleusiq>=0.7.12`**, **`mcp>=1.28.1`**); works with **every** provider. Plug GitHub, Slack, Postgres, Stripe, or any custom MCP server into an agent in one line.
