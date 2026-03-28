# Providers

NucleusIQ uses provider packages so your agent code stays stable while model backends change. Write your agent once, swap providers with one line.

## Core idea

- `nucleusiq` contains agent orchestration, tools, memory, plugins, prompts, and streaming.
- Provider packages implement concrete LLM backends against the `BaseLLM` interface.
- Your agent code never imports provider internals — just the LLM class.

## Current providers

| Package | Category | Status | Install |
|---------|----------|--------|---------|
| `nucleusiq-openai` | LLM provider | **Active** — Chat Completions + Responses API | `pip install nucleusiq-openai` |
| `nucleusiq-gemini` | LLM provider | **Active** — Google GenAI SDK (GA) | `pip install nucleusiq-gemini` |

## Planned providers

| Package | Category | Target |
|---------|----------|--------|
| `nucleusiq-anthropic` | LLM provider | v0.7.0 |
| `nucleusiq-ollama` | Inference provider | v0.7.0 |
| `nucleusiq-groq` | Inference provider | Backlog |
| `nucleusiq-chroma` | DB provider | Backlog |
| `nucleusiq-pinecone` | DB provider | Backlog |

## Provider portability

The same agent code works with any provider:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode

# Choose your provider — one line change
from nucleusiq_openai import BaseOpenAI
llm = BaseOpenAI(model_name="gpt-4o")

# Or switch to Gemini
from nucleusiq_gemini import BaseGemini
llm = BaseGemini(model_name="gemini-2.5-flash")

# Same agent, same tools, same plugins
agent = Agent(
    name="assistant",
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

Common parameters (`temperature`, `max_output_tokens`, `top_p`) are defined in the base `LLMParams` and work across all providers.

## Provider-native tools

Each provider can expose server-side tools:

| Provider | Native tools |
|----------|-------------|
| OpenAI | `code_interpreter`, `file_search`, `web_search`, `image_generation`, `mcp`, `computer_use` |
| Gemini | `google_search`, `code_execution`, `url_context`, `google_maps` |

Native tools are accessed via provider-specific factories (`OpenAITool`, `GeminiTool`) and can be mixed with framework-level tools in the same agent.

## Error handling

All providers map SDK errors to NucleusIQ's [framework-level error taxonomy](core-concepts/error-handling.md). You catch `RateLimitError`, `AuthenticationError`, etc. regardless of which provider raised it.

## Compatibility

- The core package is versioned independently from provider packages.
- Provider packages declare their minimum `nucleusiq` version (e.g., `nucleusiq>=0.6.0`).
- Always keep provider versions compatible with your installed `nucleusiq` version.

## See also

- [Gemini provider guide](guides/gemini-provider.md) — Full Gemini integration details
- [OpenAI provider guide](guides/openai-provider.md) — Full OpenAI integration details
- [Models](models.md) — Provider-agnostic model usage
- [Install](install.md) — Setup instructions
