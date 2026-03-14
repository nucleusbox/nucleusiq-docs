# Built-in plugins

NucleusIQ includes 10 built-in plugins for common use cases.

## Plugin list

| Plugin | Purpose |
|--------|---------|
| `ModelCallLimitPlugin` | Limit total LLM calls per execution |
| `ToolCallLimitPlugin` | Limit tool calls per execution |
| `ToolRetryPlugin` | Retry failed tool calls |
| `ModelFallbackPlugin` | Fallback to a cheaper model on failure |
| `PIIGuardPlugin` | Detect and redact PII in inputs/outputs |
| `HumanApprovalPlugin` | Pause for human approval before tool execution |
| `ToolGuardPlugin` | Allow/block specific tools by policy |
| `AttachmentGuardPlugin` | Validate attachments (type, size, count) |
| `ContextWindowPlugin` | Enforce context window limits |
| `ResultValidatorPlugin` | Validate agent output against a schema |

## Example

```python
from nucleusiq.plugins.builtin import (
    ToolRetryPlugin,
    PIIGuardPlugin,
)

agent = Agent(
    ...,
    plugins=[
        ToolRetryPlugin(max_retries=2),
        PIIGuardPlugin(redact_patterns=["email", "phone"]),
    ],
)
```

## See also

- [Plugins overview](overview.md) — Hook points and APIs
