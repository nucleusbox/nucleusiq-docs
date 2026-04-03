# Production path

How to take NucleusIQ agents from prototype to production.

## 1. Start with STANDARD mode

Most production agents use `ExecutionMode.STANDARD` — it provides tool calling without the overhead of autonomous planning.

```python
from nucleusiq.agents.config import AgentConfig, ExecutionMode

config = AgentConfig(
    execution_mode=ExecutionMode.STANDARD,
    llm_call_timeout=90,
)
```

## 2. Add guardrail plugins

```python
from nucleusiq.plugins.builtin import (
    ModelCallLimitPlugin,
    ToolRetryPlugin,
    ToolGuardPlugin,
    PIIGuardPlugin,
)

agent = Agent(
    ...,
    plugins=[
        ModelCallLimitPlugin(max_calls=20),
        ToolRetryPlugin(max_retries=2),
        ToolGuardPlugin(allowed_tools=["file_read", "file_search", "calculate"]),
        PIIGuardPlugin(redact_patterns=["email", "phone"]),
    ],
)
```

## 3. Choose a memory strategy

- `SLIDING_WINDOW` for most applications
- `TOKEN_BUDGET` when you need hard cost limits
- `SUMMARY_WINDOW` for long-running assistants

## 4. Add observability

```python
# After execution
usage = agent.last_usage
print(usage.display())  # Human-readable token summary

# Cost estimation
from nucleusiq.agents.usage import CostTracker
tracker = CostTracker()
cost = tracker.estimate(usage, model="gpt-4o")
print(f"Cost: ${cost.total_cost:.6f}")

# Log for dashboards
log_payload = usage.summary()  # dict for JSON serialization
```

## 5. Handle errors

```python
from nucleusiq.llms.errors import RateLimitError, AuthenticationError, LLMError

try:
    result = await agent.execute(task)
except RateLimitError:
    # Implement backoff or queue the request
    pass
except AuthenticationError:
    # Alert ops team
    pass
except LLMError as e:
    logger.error(f"LLM error: provider={e.provider} status={e.status_code}")
```

## 6. Evaluate AUTONOMOUS for complex tasks

Only use Autonomous mode when you need:
- Task decomposition into subtasks
- Independent verification (Critic)
- Targeted correction (Refiner)
- Validation pipeline

## 7. Plan for provider portability

Write agent code against the framework interface, not provider-specific APIs. This lets you:
- Switch providers without code changes
- A/B test models (e.g., GPT-4o vs Gemini 2.5 Pro)
- Fall back when a provider has issues

## Checklist

- [ ] Execution mode chosen (STANDARD for most, AUTONOMOUS for complex)
- [ ] Tool guard plugin limiting which tools the agent can use
- [ ] Model call limit plugin preventing runaway loops
- [ ] Memory strategy selected
- [ ] Usage tracking and cost monitoring in place
- [ ] Error handling for rate limits, auth failures, and server errors
- [ ] PII guard if handling sensitive data
