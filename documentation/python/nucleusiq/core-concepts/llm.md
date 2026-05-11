# Core Concept: LLM and Providers

NucleusIQ core is provider-agnostic. Provider packages implement concrete model APIs against the `BaseLLM` interface.

## Base + provider pattern

```
nucleusiq (core)
├── BaseLLM          # Abstract interface
├── LLMParams        # Common parameters
└── MockLLM          # Built-in for testing

nucleusiq-openai     # Provider package
├── BaseOpenAI       # Implements BaseLLM
└── OpenAILLMParams  # Extends LLMParams

nucleusiq-gemini     # Provider package
├── BaseGemini       # Implements BaseLLM
└── GeminiLLMParams  # Extends LLMParams

nucleusiq-groq       # Provider package (public beta)
├── BaseGroq         # Implements BaseLLM (Groq Chat Completions)
└── GroqLLMParams    # Extends LLMParams

nucleusiq-ollama     # Provider package (alpha)
├── BaseOllama       # Implements BaseLLM (Ollama /api/chat)
└── OllamaLLMParams  # Extends LLMParams
```

## Usage

=== "OpenAI"

    ```python
    from nucleusiq_openai import BaseOpenAI
    llm = BaseOpenAI(model_name="gpt-4o-mini")
    ```

=== "Gemini"

    ```python
    from nucleusiq_gemini import BaseGemini
    llm = BaseGemini(model_name="gemini-2.5-flash")
    ```

=== "Groq"

    ```python
    from nucleusiq_groq import BaseGroq

    llm = BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True)
    ```

=== "Ollama"

    ```python
    from nucleusiq_ollama import BaseOllama

    llm = BaseOllama(model_name="llama3.2", async_mode=True)
    ```

## Parameter control

Three levels of control — use what you need:

| Level | Who | How |
|-------|-----|-----|
| **Agent defaults** | Most users | `AgentConfig(llm_max_output_tokens=1024)` |
| **Provider params** | Power users | `AgentConfig(llm_params=OpenAILLMParams(reasoning_effort="high"))` |
| **Per-task override** | Advanced | `agent.execute(task, llm_params=OpenAILLMParams(temperature=0))` |

=== "OpenAI"

    ```python
    from nucleusiq.agents.config import AgentConfig
    from nucleusiq_openai import OpenAILLMParams

    config = AgentConfig(
        llm_params=OpenAILLMParams(temperature=0.2, reasoning_effort="medium"),
    )
    ```

=== "Gemini"

    ```python
    from nucleusiq.agents.config import AgentConfig
    from nucleusiq_gemini import GeminiLLMParams, GeminiThinkingConfig

    config = AgentConfig(
        llm_params=GeminiLLMParams(
            temperature=0.2,
            thinking_config=GeminiThinkingConfig(thinking_budget=2048),
        ),
    )
    ```

=== "Groq"

    ```python
    from nucleusiq.agents.config import AgentConfig
    from nucleusiq_groq import GroqLLMParams

    config = AgentConfig(
        llm_params=GroqLLMParams(
            temperature=0.2,
            parallel_tool_calls=True,
        ),
    )
    ```

=== "Ollama"

    ```python
    from nucleusiq.agents.config import AgentConfig
    from nucleusiq_ollama import OllamaLLMParams

    config = AgentConfig(
        llm_params=OllamaLLMParams(
            temperature=0.2,
            think="low",
            keep_alive="5m",
        ),
    )
    ```

## Universal parameters

These parameters work across all providers:

| Parameter | Description |
|-----------|-------------|
| `temperature` | Sampling temperature (0.0–2.0) |
| `max_output_tokens` | Maximum tokens in the response |
| `top_p` | Nucleus sampling threshold |

Provider-specific parameters (for example **`reasoning_effort`** for OpenAI, **`thinking_config`** for Gemini, **`parallel_tool_calls`** for Groq, **`think`** / **`keep_alive`** for Ollama) are defined in the provider's **`LLMParams`** subclass.

## Error contract

All providers raise the same [framework-level exceptions](error-handling.md):

```python
from nucleusiq.llms.errors import RateLimitError, AuthenticationError

try:
    result = await agent.execute({"id": "l1", "objective": "Hello"})
except RateLimitError:
    # Works with any provider
    pass
```

## See also

- [Providers](../providers.md) — Full provider architecture
- [Ollama provider guide](../guides/ollama-provider.md) — Ollama alpha (**`nucleusiq>=0.7.10`**)
- [Groq provider guide](../guides/groq-provider.md) — Groq Chat Completions (beta), **`retry_policy`** alignment (**v0.7.9+**)
- [Models](../models.md) — Available models per provider
- [Error handling](error-handling.md) — Framework error taxonomy
