# Gemini provider

The NucleusIQ Gemini provider (`nucleusiq-gemini`) integrates Google's Gemini models using the official `google-genai` SDK (GA).

## Installation

```bash
pip install nucleusiq nucleusiq-gemini
```

Set your API key:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

Or in a `.env` file at your project root:

```
GEMINI_API_KEY=your-gemini-api-key
```

## Quick start

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq_gemini import BaseGemini, GeminiLLMParams

async def main():
    llm = BaseGemini(model_name="gemini-2.5-flash")
    agent = Agent(
        name="assistant",
        llm=llm,
        model="gemini-2.5-flash",
        instructions="You are a helpful assistant.",
        config=AgentConfig(
            execution_mode=ExecutionMode.STANDARD,
            llm_params=GeminiLLMParams(temperature=0.7, max_output_tokens=1024),
        ),
    )
    result = await agent.execute({"id": "gemini-guide-1", "objective": "What is the capital of France?"})
    print(result.content)

asyncio.run(main())
```

## Supported models

| Model | Context window | Max output | Thinking support |
|-------|---------------|------------|-----------------|
| `gemini-2.5-pro` | 1M tokens | 65,536 | Yes |
| `gemini-2.5-flash` | 1M tokens | 65,536 | Yes |
| `gemini-2.0-flash` | 1M tokens | 8,192 | No |
| `gemini-1.5-pro` | 2M tokens | 8,192 | No |
| `gemini-1.5-flash` | 1M tokens | 8,192 | No |

## Gemini-specific parameters

Use `GeminiLLMParams` for parameters beyond the common set:

```python
from nucleusiq_gemini import GeminiLLMParams, GeminiThinkingConfig, GeminiSafetySettings

params = GeminiLLMParams(
    temperature=0.7,
    max_output_tokens=2048,
    top_k=40,
    top_p=0.95,

    # Thinking mode (Gemini 2.5+ models)
    thinking_config=GeminiThinkingConfig(thinking_budget=2048),

    # Safety settings
    safety_settings=[
        GeminiSafetySettings(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_ONLY_HIGH",
        )
    ],
)

config = AgentConfig(llm_params=params)
agent = Agent(llm=llm, config=config, ...)
```

## Native server-side tools

Gemini provides built-in tools that execute on Google's servers. These tools are free to use with the API (standard model pricing applies).

```python
from nucleusiq_gemini import GeminiTool

# Google Search — ground responses with real-time web results
search = GeminiTool.google_search()

# Code Execution — run Python in a secure sandbox
code = GeminiTool.code_execution()

# URL Context — fetch and understand web pages
url_ctx = GeminiTool.url_context()

# Google Maps — location-aware grounding
maps = GeminiTool.google_maps()
```

Use them like any other tool:

```python
agent = Agent(
    llm=llm,
    config=config,
    tools=[GeminiTool.google_search(), GeminiTool.code_execution()],
    ...
)
```

Or call directly on the LLM:

```python
result = await llm.call(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "What are the latest AI news?"}],
    tools=[GeminiTool.google_search()],
    max_output_tokens=1024,
)
```

## Gearbox strategy (3 modes)

All three execution modes work identically with Gemini:

=== "Gear 1: DIRECT"

    Single LLM call. Best for Q&A, classification, summarization.

    ```python
    config = AgentConfig(execution_mode=ExecutionMode.DIRECT)
    agent = Agent(llm=BaseGemini(model_name="gemini-2.5-flash"), config=config, ...)
    result = await agent.execute({"id": "gemini-guide-2", "objective": "What is quantum computing?"})
    ```

=== "Gear 2: STANDARD"

    Iterative tool calling (up to 30 calls). Best for tasks needing external data.

    ```python
    from nucleusiq.tools.decorators import tool

    @tool
    def get_weather(city: str) -> str:
        """Get weather for a city."""
        return "22°C, Sunny"

    config = AgentConfig(execution_mode=ExecutionMode.STANDARD)
    agent = Agent(llm=llm, config=config, tools=[get_weather], ...)
    result = await agent.execute({"id": "gemini-guide-3", "objective": "What's the weather in Tokyo?"})
    ```

=== "Gear 3: AUTONOMOUS"

    Task decomposition, Critic verification, Refiner loop.

    ```python
    config = AgentConfig(
        execution_mode=ExecutionMode.AUTONOMOUS,
        require_quality_check=True,
        max_iterations=5,
    )
    agent = Agent(llm=llm, config=config, tools=[...], ...)
    result = await agent.execute({"id": "gemini-guide-4", "objective": "Compare Python and Rust for AI applications."})
    ```

## Structured output

Pass a Pydantic model to get typed responses:

```python
from pydantic import BaseModel

class MovieReview(BaseModel):
    title: str
    rating: float
    summary: str

result = await llm.call(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "Review the movie Inception"}],
    response_format=MovieReview,
    max_output_tokens=512,
)
print(result.title, result.rating)
```

## Streaming

```python
async for event in agent.execute_stream({"id": "s1", "objective": "Write a poem about the ocean"}):
    if event.type.value == "token":
        print(event.token, end="", flush=True)
    elif event.type.value == "thinking":
        print(f"[thinking] {event.message}", end="")
    elif event.type.value == "complete":
        print(f"\nTokens: {event.metadata.get('usage', {})}")
```

## Multimodal attachments

Gemini natively supports images, PDFs, and files:

```python
from nucleusiq.agents.task import Task
from nucleusiq.core.attachments.models import Attachment, AttachmentType

task = Task(
    id="analyze",
    objective="Describe this image",
    attachments=[
        Attachment(type=AttachmentType.IMAGE_URL, content="https://example.com/photo.jpg"),
    ],
)
result = await agent.execute(task)
```

Supported attachment types: `IMAGE_URL`, `IMAGE_BASE64`, `PDF`, `FILE_BYTES`, `FILE_BASE64`, `TEXT`.

## Error handling

The provider maps all Gemini SDK errors to NucleusIQ's framework-level exceptions:

```python
from nucleusiq.llms.errors import RateLimitError, AuthenticationError, LLMError

try:
    result = await agent.execute({"id": "gemini-guide-5", "objective": "Hello"})
except RateLimitError as e:
    print(f"Rate limited: retry after backoff (status {e.status_code})")
except AuthenticationError:
    print("Check your GEMINI_API_KEY")
except LLMError as e:
    print(f"LLM error from {e.provider}: {e}")
```

Built-in retry with exponential backoff handles transient errors automatically (rate limits, server errors, connection issues). Auth and validation errors fail fast.

## Provider portability

Switch between providers with zero agent code changes:

```python
# Gemini
from nucleusiq_gemini import BaseGemini
llm = BaseGemini(model_name="gemini-2.5-flash")

# OpenAI (same agent code)
from nucleusiq_openai import BaseOpenAI
llm = BaseOpenAI(model_name="gpt-4o")

# Same agent works with either
agent = Agent(llm=llm, config=config, tools=tools, plugins=plugins, ...)
```

Tools, plugins, memory, and streaming all work identically across providers.

## See also

- [OpenAI provider guide](openai-provider.md) — OpenAI-specific features
- [Providers](../providers.md) — Provider architecture
- [Models](../models.md) — Provider-agnostic model usage
- [Cost estimation](../observability/cost-estimation.md) — Track dollar costs
- [Error handling](../core-concepts/error-handling.md) — Framework error taxonomy
