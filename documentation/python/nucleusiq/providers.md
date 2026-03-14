# Providers

NucleusIQ uses provider packages so your agent/runtime code stays stable while model backends change.

## Core idea

- `nucleusiq` contains agent orchestration, tools, memory, plugins, prompts, and streaming.
- Provider packages implement concrete LLM/database/inference backends.

## Current status

| Package | Category | Status |
|---------|----------|--------|
| `nucleusiq-openai` | LLM provider | Active and documented |
| `nucleusiq-gemini` | LLM provider | Pre-alpha scaffold |
| `nucleusiq-groq` | Inference provider | Pre-alpha scaffold |
| `nucleusiq-ollama` | Inference provider | Pre-alpha scaffold |
| `nucleusiq-chroma` | DB provider | Pre-alpha scaffold |
| `nucleusiq-pinecone` | DB provider | Pre-alpha scaffold |

## Install

```bash
pip install nucleusiq nucleusiq-openai
```

## OpenAI quick usage

```python
from nucleusiq.agents import Agent
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="assistant",
    role="Helpful assistant",
    objective="Answer user questions",
    llm=BaseOpenAI(model_name="gpt-4o-mini"),
)
```

## Compatibility notes

- The core package is versioned independently from provider packages.
- Keep provider versions compatible with your core `nucleusiq` version.
- For OpenAI-specific parameters, use `OpenAILLMParams`.

## See also

- [Models](models.md) — Provider-agnostic model usage
- [OpenAI provider guide](guides/openai-provider.md) — OpenAI integration details
- [Install](install.md) — Setup instructions
