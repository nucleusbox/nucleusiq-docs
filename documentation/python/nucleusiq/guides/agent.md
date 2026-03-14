# Agent Guide

## Agent anatomy

```python
agent = Agent(
    name="analyst",          # identity
    role="Data analyst",     # system framing
    objective="Analyze data",# long-lived purpose
    llm=...,                  # model backend
    config=...,               # execution strategy and limits
    tools=[...],              # optional tool set
    memory=...,               # optional conversation memory
    plugins=[...],            # optional policy/guardrails
)
```

## Lifecycle pattern

```python
from nucleusiq.agents.task import Task

await agent.initialize()
result = await agent.execute(Task(id="t1", objective="..."))
```

## Streaming pattern

```python
async for event in agent.execute_stream(Task(id="s1", objective="...")):
    ...
```

Use `execute_stream()` in UIs where progressive output matters.
