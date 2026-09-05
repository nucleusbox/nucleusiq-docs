# Structured output

Parse agent responses into typed schemas using Pydantic, dataclass, or TypedDict. Works with **OpenAI**, **Gemini**, **Anthropic**, **Groq**, **Ollama** (native `format`), and **OpenAI-compatible** servers (vLLM, SGLang, …).

**`OutputMode.AUTO` always resolves to NATIVE** — "hand the schema to the adapter". The adapter decides whether the server can enforce JSON schema. Combining **`response_format`** with **tools** drops native structured output with a **warning** on several backends — test tool-free paths first. Guides: [OpenAI-compatible provider](guides/openai-compatible-provider.md), [Anthropic provider](guides/anthropic-provider.md), [Groq provider](guides/groq-provider.md), [Ollama provider](guides/ollama-provider.md).

## Pydantic model (recommended)

```python
from pydantic import BaseModel
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

class Summary(BaseModel):
    title: str
    bullets: list[str]
    confidence: float

agent = Agent(
    name="structured-output",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    response_format=Summary,
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "structured-output-1", "objective": "Summarize the key points of quantum computing"})
# result is a Summary instance
print(result.title, result.bullets)
```

## Dataclass

```python
from dataclasses import dataclass
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

@dataclass
class Contact:
    name: str
    email: str
    role: str

agent = Agent(
    name="structured-dataclass",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    response_format=Contact,
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "structured-output-2", "objective": "Extract contact info from: John Doe, john@example.com, CTO"})
```

## Direct LLM call with structured output

You can also get structured output directly from the LLM without an agent:

=== "OpenAI"

    ```python
    from nucleusiq_openai import BaseOpenAI
    from pydantic import BaseModel

    class MovieReview(BaseModel):
        title: str
        rating: float
        summary: str

    llm = BaseOpenAI(model_name="gpt-4o-mini")
    result = await llm.call(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Review the movie Inception"}],
        response_format=MovieReview,
        max_output_tokens=512,
    )
    ```

=== "Gemini"

    ```python
    from nucleusiq_gemini import BaseGemini
    from pydantic import BaseModel

    class MovieReview(BaseModel):
        title: str
        rating: float
        summary: str

    llm = BaseGemini(model_name="gemini-2.5-flash")
    result = await llm.call(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Review the movie Inception"}],
        response_format=MovieReview,
        max_output_tokens=512,
    )
    ```

=== "OpenAI-compatible"

    ```python
    from nucleusiq_openai_compatible import OpenAICompatibleLLM
    from pydantic import BaseModel

    class MovieReview(BaseModel):
        title: str
        rating: float
        summary: str

    llm = OpenAICompatibleLLM(
        base_url="http://127.0.0.1:8000/v1",
        model="gemma-4-27b-it",
        context_window=32_768,
        engine="vllm",
    )
    result = await llm.call(
        messages=[{"role": "user", "content": "Review the movie Inception"}],
        response_format=MovieReview,
    )
    ```

## Supported formats

| Format | How it works |
|--------|-------------|
| **Pydantic `BaseModel`** | JSON schema enforced by the provider, parsed into model instance |
| **`@dataclass`** | Converted to JSON schema, parsed back into dataclass |
| **`TypedDict`** | For simple key-value structures |

## Provider implementation

- **OpenAI** — Uses `response_format` with JSON schema enforcement.
- **OpenAI-compatible** — Engine preset decides. vLLM / SGLang send `response_format`. Ollama `/v1` and `generic` inject the schema into the prompt (`PromptPolicy`). Combined `tools` + schema on vLLM is rewritten so tool calls are not suppressed. See [OpenAI-compatible provider](guides/openai-compatible-provider.md).
- **Gemini** — Uses `response_mime_type: "application/json"` with `response_json_schema`.
- **Anthropic** — Messages **`output_config.format`** with JSON Schema when the model/API supports native structured outputs; **`response_format`** is skipped when **tools** are present (**warning**); streaming ignores **`response_format`** (**warning**). See [Anthropic provider](guides/anthropic-provider.md).
- **Groq** — Chat Completions **`json_schema`** when the checkpoint supports it. Same tools + structured-output interaction caveats as other backends — see [Groq provider](guides/groq-provider.md).
- **Ollama** — Native **`format`** when the server/model supports it (**`nucleusiq-ollama`**). For the `/v1` shim, use **`nucleusiq-openai-compatible`** instead. See [Ollama provider](guides/ollama-provider.md).

All wired providers aim for the same typed **`Agent`** result at the framework layer when native mode succeeds.

## See also

- [Agents](agents.md) — Agent configuration
- [OpenAI-compatible provider](guides/openai-compatible-provider.md) — Engine presets and degradation policies
- [Anthropic provider](guides/anthropic-provider.md) — Claude Messages API structured outputs
- [Groq provider](guides/groq-provider.md) — Groq structured outputs
- [Ollama provider](guides/ollama-provider.md) — Ollama structured **`format`**
- [Gemini provider](guides/gemini-provider.md) — Gemini structured output details
- [Quickstart](quickstart.md) — Basic usage
