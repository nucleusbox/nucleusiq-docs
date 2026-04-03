# Migration notes

## From simpler chat wrappers

If you are migrating from direct API calls or thin wrappers:

1. Move from `prompt → response` to `Agent + execute()`
2. Introduce tools gradually using the `@tool` decorator in STANDARD mode
3. Add memory with `MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW)`
4. Use `agent.last_usage` and `CostTracker` to monitor costs — prevents billing surprises
5. Add plugins for guardrails: `ModelCallLimitPlugin`, `ToolGuardPlugin`

## From heavier workflow systems (LangChain, etc.)

If you are migrating from a heavier framework:

1. Start with one Agent + STANDARD mode — NucleusIQ's single-agent model covers most cases
2. Replace chain/graph abstractions with execution modes (Direct → Standard → Autonomous)
3. Add plugins for policy and retries instead of custom middleware
4. Introduce AUTONOMOUS mode only where Critic/Refiner verification loops are genuinely needed
5. Use provider portability to switch LLMs without rewriting agent logic

## From v0.6.0 to v0.7.x

Key changes in v0.7.x:

| Change | Migration |
|--------|----------|
| `agent.execute()` returns `AgentResult` not raw string | Use `result.output` for text, `str(result)` for string, `result.status` for outcome |
| New exception hierarchy | Replace `except ValueError` with `except ToolValidationError`, `except AgentExecutionError`, etc. |
| `from nucleusiq.agents.components.pricing import CostTracker` moved | Use `from nucleusiq.agents.usage import CostTracker` |
| `from nucleusiq.agents.components.usage_tracker import UsageTracker` moved | Use `from nucleusiq.agents.usage import UsageTracker` |
| `AgentConfig.enable_tracing` new field | Set `enable_tracing=True` to populate `AgentResult.tool_calls`, `.llm_calls`, `.warnings` |
| All errors now have structured attributes | `ToolError` carries `tool_name`, `AgentError` carries `mode`, etc. |

## From v0.5.0 to v0.6.0

Key changes in v0.6.0:

| Change | Migration |
|--------|----------|
| `max_tokens` → `max_output_tokens` | Update `AgentConfig` and `LLMParams` usages |
| `nucleusiq-openai` now requires `nucleusiq>=0.6.0` | Upgrade core first: `pip install --upgrade nucleusiq` |
| New error types in `nucleusiq.llms.errors` | Replace bare `except Exception` with specific error catches |
| `@tool` decorator available | Optional — existing `BaseTool` subclasses still work |
| `CostTracker` available | Optional add-on for cost monitoring |

## See also

- [Changelog](../../../reference/changelog.md) — Full release history
- [Production path](production-path.md) — Production readiness checklist
