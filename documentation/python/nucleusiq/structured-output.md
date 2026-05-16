# Structured output

Parse agent responses into typed schemas using Pydantic, dataclass, or TypedDict. Works with **OpenAI**, **Gemini**, **Anthropic** (**`nucleusiq-anthropic` 0.1.0a1**, **`nucleusiq>=0.7.10`**) when Claude exposes native **JSON Schema** structured outputs via Messages **`output_config.format`**, **Groq** (`nucleusiq-groq` **0.1.0b1**, **`nucleusiq>=0.7.9`**) when the Groq model supports **`json_schema`**, and **Ollama** via **`nucleusiq-ollama` 0.1.0a1** (**alpha**) when your Ollama model / server supports structured **`format`**. Combining **`response_format`** with **tools** drops native structured output with a **warning** on several backends — test tool-free paths first. Guides: [Anthropic provider](guides/anthropic-provider.md), [Groq provider](guides/groq-provider.md), [Ollama provider](guides/ollama-provider.md).

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

## Supported formats

| Format | How it works |
|--------|-------------|
| **Pydantic `BaseModel`** | JSON schema enforced by the provider, parsed into model instance |
| **`@dataclass`** | Converted to JSON schema, parsed back into dataclass |
| **`TypedDict`** | For simple key-value structures |

## Provider implementation

- **OpenAI** — Uses `response_format` with JSON schema enforcement.
- **Gemini** — Uses `response_mime_type: "application/json"` with `response_json_schema`.
- **Anthropic** — Messages **`output_config.format`** with JSON Schema when the model/API supports native structured outputs (**`nucleusiq-anthropic`**, **alpha**); **`response_format`** is skipped when **tools** are present (**warning**); streaming ignores **`response_format`** (**warning**). See [Anthropic provider](guides/anthropic-provider.md).
- **Groq** — Chat Completions **`json_schema`** when the checkpoint supports it (**`nucleusiq-groq`** beta). Same tools + structured-output interaction caveats as other backends — see [Groq provider](guides/groq-provider.md).
- **Ollama** — Native **`format`** when the server/model supports it (**`nucleusiq-ollama`**, **alpha**). See [Ollama provider](guides/ollama-provider.md).

All wired providers aim for the same typed **`Agent`** result at the framework layer when native mode succeeds.

## See also

- [Agents](agents.md) — Agent configuration
- [Anthropic provider](guides/anthropic-provider.md) — Claude Messages API structured outputs (**alpha**)
- [Groq provider](guides/groq-provider.md) — Groq structured outputs (beta)
- [Ollama provider](guides/ollama-provider.md) — Ollama structured **`format`** (**alpha**)
- [Gemini provider](guides/gemini-provider.md) — Gemini structured output details
- [Quickstart](quickstart.md) — Basic usage
