# Models

NucleusIQ uses a **provider-agnostic** `BaseLLM` interface. Swap providers without changing the rest of your agent code.

## Supported providers

| Provider | Package | Install |
|----------|---------|---------|
| OpenAI | `nucleusiq-openai` | `pip install nucleusiq-openai` |
| Google Gemini | `nucleusiq-gemini` | `pip install nucleusiq-gemini` |
| Groq | `nucleusiq-groq` | `pip install nucleusiq-groq` |
| Ollama | `nucleusiq-ollama` | `pip install nucleusiq-ollama` |
| Mock (testing) | Built-in | `from nucleusiq.core.llms.mock_llm import MockLLM` |

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

=== "Mock (testing)"

    ```python
    from nucleusiq.core.llms.mock_llm import MockLLM

    llm = MockLLM()  # No API key needed
    ```

## Available models

### OpenAI

| Model | Use case |
|-------|----------|
| `gpt-4o` | High capability, multimodal |
| `gpt-4o-mini` | Fast, cost-effective |
| `gpt-4.1` | Latest GPT-4 series |
| `gpt-4.1-mini` | Balanced performance/cost |
| `gpt-4.1-nano` | Ultra-fast, lowest cost |
| `o3` | Reasoning model |
| `o3-mini` | Reasoning, cost-effective |
| `o4-mini` | Latest reasoning model |

### Gemini

| Model | Context | Thinking |
|-------|---------|----------|
| `gemini-2.5-pro` | 1M tokens | Yes |
| `gemini-2.5-flash` | 1M tokens | Yes |
| `gemini-2.0-flash` | 1M tokens | No |
| `gemini-1.5-pro` | 2M tokens | No |
| `gemini-1.5-flash` | 1M tokens | No |

### Groq

Groq rotates **Llama**, **Mixtral**, **Qwen**, **GPT-OSS**, and other checkpoints frequently — see [Groq models](https://console.groq.com/docs/models). Typical starter IDs:

| Model id | Typical use |
|----------|-------------|
| `llama-3.3-70b-versatile` | Chat + local tools |
| `openai/gpt-oss-20b` | Structured output demos (`json_schema`) |

Beta package **`nucleusiq-groq` 0.1.0b1** requires **`nucleusiq>=0.7.9`** and ships against the official **`groq`** Python SDK (`>=1.2,<2`).

### Ollama

Model ids are **whatever your Ollama server exposes** (`ollama list`). Typical local tags:

| Model id | Typical use |
|----------|-------------|
| `llama3.2` | General chat + tools (examples default) |
| `mistral`, `qwen2.5`, … | Swap names per your catalog |

Alpha package **`nucleusiq-ollama` 0.1.0a1** requires **`nucleusiq>=0.7.10`** and uses the official **`ollama`** SDK (`>=0.5,<1`). See [Ollama provider guide](guides/ollama-provider.md).

## Parameter control

### AgentConfig (recommended)

Set LLM parameters at the agent level:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig
from nucleusiq.prompts.zero_shot import ZeroShotPrompt

config = AgentConfig(
    llm_max_output_tokens=1024,
    verbose=True,
)
agent = Agent(
    name="configured-agent",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=llm,  # e.g. BaseOpenAI / BaseGemini / BaseGroq / BaseOllama from the sections above
    config=config,
)
```

### Provider-specific params

Use provider-specific parameter classes for advanced settings:

=== "OpenAI"

    ```python
    from nucleusiq_openai import OpenAILLMParams

    config = AgentConfig(
        llm_params=OpenAILLMParams(temperature=0.2, reasoning_effort="high"),
    )
    ```

=== "Gemini"

    ```python
    from nucleusiq_gemini import GeminiLLMParams, GeminiThinkingConfig

    config = AgentConfig(
        llm_params=GeminiLLMParams(
            temperature=0.5,
            thinking_config=GeminiThinkingConfig(thinking_budget=2048),
        ),
    )
    ```

=== "Groq"

    ```python
    from nucleusiq_groq import GroqLLMParams

    config = AgentConfig(
        llm_params=GroqLLMParams(
            temperature=0.5,
            parallel_tool_calls=True,
        ),
    )
    ```

=== "Ollama"

    ```python
    from nucleusiq_ollama import OllamaLLMParams

    config = AgentConfig(
        llm_params=OllamaLLMParams(
            temperature=0.5,
            think="high",
            keep_alive="10m",
        ),
    )
    ```

### Per-task overrides

Override parameters for a single execution:

=== "OpenAI"

    ```python
    from nucleusiq_openai import OpenAILLMParams

    result = await agent.execute(
        task,
        llm_params=OpenAILLMParams(temperature=0.0),
    )
    ```

=== "Gemini"

    ```python
    from nucleusiq_gemini import GeminiLLMParams

    result = await agent.execute(
        task,
        llm_params=GeminiLLMParams(temperature=0.0),
    )
    ```

=== "Groq"

    ```python
    from nucleusiq_groq import GroqLLMParams

    result = await agent.execute(
        task,
        llm_params=GroqLLMParams(temperature=0.0, max_output_tokens=512),
    )
    ```

=== "Ollama"

    ```python
    from nucleusiq_ollama import OllamaLLMParams

    result = await agent.execute(
        task,
        llm_params=OllamaLLMParams(temperature=0.0, max_output_tokens=512),
    )
    ```

## See also

- [Providers](providers.md) — Provider architecture and portability
- [OpenAI provider guide](guides/openai-provider.md) — OpenAI-specific features
- [Gemini provider guide](guides/gemini-provider.md) — Gemini-specific features
- [Groq provider guide](guides/groq-provider.md) — Groq Chat Completions (beta), **`strict_model_capabilities`**, rate limits
- [Ollama provider guide](guides/ollama-provider.md) — Ollama alpha, **`think`**, structured output cautions
- [Install](install.md) — Setup instructions
