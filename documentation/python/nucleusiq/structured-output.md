# Structured output

Parse agent responses into typed schemas using Pydantic, dataclass, or TypedDict. Works with both OpenAI and Gemini providers.

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

- **OpenAI** — Uses `response_format` with JSON schema enforcement
- **Gemini** — Uses `response_mime_type: "application/json"` with `response_json_schema`

Both providers produce the same typed result at the framework level.

## See also

- [Agents](agents.md) — Agent configuration
- [Gemini provider](guides/gemini-provider.md) — Gemini structured output details
- [Quickstart](quickstart.md) — Basic usage
