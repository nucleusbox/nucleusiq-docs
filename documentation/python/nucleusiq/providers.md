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
| `nucleusiq-anthropic` | LLM provider | **Alpha** — Claude Messages API (`anthropic` SDK); **`nucleusiq>=0.7.10`** | `pip install nucleusiq-anthropic` |
| `nucleusiq-groq` | Inference provider | **Beta** — Groq Chat Completions (`groq` SDK); **`nucleusiq>=0.7.9`** | `pip install nucleusiq-groq` |
| `nucleusiq-ollama` | Inference provider | **Alpha** — Ollama **`/api/chat`** (`ollama` SDK); **`nucleusiq>=0.7.10`** | `pip install nucleusiq-ollama` |

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

# Or Anthropic Claude — Messages API (alpha package; async_mode=True)
# from nucleusiq_anthropic import BaseAnthropic
# llm = BaseAnthropic(model_name="claude-3-5-sonnet-20241022", async_mode=True)

# Or Groq (use async_mode=True with the official SDK path)
# from nucleusiq_groq import BaseGroq
# llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)

# Or Ollama — local / hosted daemon (alpha package; async_mode=True)
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

Common parameters (`temperature`, `max_output_tokens`, `top_p`) are defined in the base `LLMParams` and work across all providers.

## Provider-native tools

Each provider can expose server-side tools:

| Provider | Native tools |
|----------|-------------|
| OpenAI | `code_interpreter`, `file_search`, `web_search`, `image_generation`, `mcp`, `computer_use` |
| Gemini | `google_search`, `code_execution`, `url_context`, `google_maps` |
| Anthropic | **Alpha:** framework **`@tool`** / local tools — Claude **server-side** tools (**`web_search`**, …) are **not** wired yet ([Anthropic provider](guides/anthropic-provider.md)) |
| Groq | **Phase A:** framework **`@tool`** / local function tools only — Groq built-in/hosted tools are **not** wired yet (see [Groq provider](guides/groq-provider.md)) |
| Ollama | **Alpha:** framework **`@tool`** / function tools via Ollama **`/api/chat`** — no separate “native tool” factory yet ([Ollama provider](guides/ollama-provider.md)) |

Native tools are accessed via provider-specific factories (`OpenAITool`, `GeminiTool`) and can be mixed with framework-level tools in the same agent.

## Error handling

All providers map SDK errors to NucleusIQ's [framework-level error taxonomy](core-concepts/error-handling.md). You catch `RateLimitError`, `AuthenticationError`, etc. regardless of which provider raised it.

## Compatibility

- The core package is versioned independently from provider packages.
- Provider packages declare their minimum **`nucleusiq`** version (for example **`nucleusiq>=0.7.9`** for OpenAI / Gemini / Groq wheels published with that floor; **`nucleusiq-ollama`** and **`nucleusiq-anthropic`** require **`>=0.7.10`**).
- Always keep provider versions compatible with your installed `nucleusiq` version.

## See also

- [Anthropic provider guide](guides/anthropic-provider.md) — Claude Messages API (**alpha**), structured outputs, examples
- [Ollama provider guide](guides/ollama-provider.md) — Ollama alpha scope, env, **`think`**, examples
- [Groq provider guide](guides/groq-provider.md) — Groq Chat Completions, beta scope, rate limits, examples
- [Gemini provider guide](guides/gemini-provider.md) — Full Gemini integration details
- [OpenAI provider guide](guides/openai-provider.md) — Full OpenAI integration details
- [Models](models.md) — Provider-agnostic model usage
- [Install](install.md) — Setup instructions
