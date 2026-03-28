# Example: Streaming

Real-time token-by-token output from agent execution.

## Basic streaming

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq_openai import BaseOpenAI

async def main():
    agent = Agent(
        name="writer",
        llm=BaseOpenAI(model_name="gpt-4o-mini"),
        model="gpt-4o-mini",
        instructions="You are a creative writer.",
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    async for event in agent.execute_stream({"id": "s1", "objective": "Write a haiku about the ocean"}):
        if event.type.value == "token":
            print(event.token, end="", flush=True)
        elif event.type.value == "complete":
            print("\n\n--- Done ---")

asyncio.run(main())
```

## Streaming with tool visibility

```python
async for event in agent.execute_stream({"id": "s2", "objective": "Find and summarize the config file"}):
    match event.type.value:
        case "token":
            print(event.token, end="", flush=True)
        case "tool_call_start":
            print(f"\n[Calling tool: {event.tool_name}]")
        case "tool_call_end":
            print(f"[Tool result: {event.tool_result[:100]}...]")
        case "thinking":
            pass  # Gemini 2.5 thinking tokens (event.message)
        case "complete":
            print("\n--- Done ---")
        case "error":
            print(f"\nError: {event.message}")
```

## Gemini with thinking tokens

Gemini 2.5+ models emit thinking tokens during reasoning. These appear as `THINKING` events:

```python
from nucleusiq_gemini import BaseGemini, GeminiLLMParams, GeminiThinkingConfig

agent = Agent(
    name="reasoner",
    llm=BaseGemini(model_name="gemini-2.5-flash"),
    model="gemini-2.5-flash",
    instructions="Think step by step.",
    config=AgentConfig(
        llm_params=GeminiLLMParams(
            thinking_config=GeminiThinkingConfig(thinking_budget=2048),
        ),
    ),
)

async for event in agent.execute_stream({"id": "s3", "objective": "Solve: if x^2 + 3x - 10 = 0, what is x?"}):
    if event.type.value == "thinking":
        print(f"[thinking] {event.message}", end="")
    elif event.type.value == "token":
        print(event.token, end="", flush=True)
    elif event.type.value == "complete":
        print("\n--- Done ---")
```

## Collecting full response

```python
chunks = []
async for event in agent.execute_stream({"id": "s4", "objective": "Explain quantum computing"}):
    if event.type.value == "token" and event.token:
        chunks.append(event.token)
        print(event.token, end="", flush=True)
    elif event.type.value == "complete":
        print("\n--- Done ---")

full_text = "".join(chunks)
```

## See also

- [Streaming reference](../streaming.md) — Event types and all modes
- [Gemini provider](../guides/gemini-provider.md) — Gemini-specific streaming features
