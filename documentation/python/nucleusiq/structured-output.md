# Structured output

Parse agent responses into typed schemas using Pydantic, dataclass, or TypedDict.

## Usage

```python
from nucleusiq.agents import Agent
from pydantic import BaseModel

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent(..., response_format=Summary)
result = await agent.execute(task)
```

## Dataclass example

```python
from dataclasses import dataclass

@dataclass
class Contact:
    name: str
    email: str

agent = Agent(..., response_format=Contact)
result = await agent.execute(task)
```

## Supported formats

- **Pydantic** — `BaseModel` subclasses
- **Dataclass** — `@dataclass`
- **TypedDict** — For simple structures

## See also

- [Agents](agents.md) — Agent configuration
- [Quickstart](quickstart.md) — Basic usage
