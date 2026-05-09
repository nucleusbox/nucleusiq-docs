# Examples

Detailed practical examples for common NucleusIQ workflows.

*Updated for v0.7.9+: curated examples use the mandatory `prompt=` API and current provider pins. See [migration notes](../learn/migration-notes.md) if upgrading from older releases.*

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
- [Groq quickstart](groq-quickstart.md) — Groq DIRECT / STANDARD / AUTONOMOUS (**`nucleusiq-groq` 0.1.0b1**, **`nucleusiq>=0.7.9`**)
- [Groq provider guide](../guides/groq-provider.md) — Beta scope, **429** / **`Retry-After`**, **`strict_model_capabilities`**, repo scripts

!!! tip "Which Groq page?"

    Start with **[Groq quickstart](groq-quickstart.md)** for copy-paste snippets; use **[Groq provider](../guides/groq-provider.md)** for deeper operational guidance.

## Repository examples

Full runnable scripts are available in the GitHub repository:

- [Core examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/nucleusiq/examples)
- [OpenAI examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/openai/examples)
- [Gemini examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/llms/gemini/examples)
- [Groq examples](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/groq/examples) — Direct through Autonomous + structured output
- [Notebooks](https://github.com/nucleusbox/NucleusIQ/tree/main/notebooks) — Jupyter notebooks for context management showcase and more
