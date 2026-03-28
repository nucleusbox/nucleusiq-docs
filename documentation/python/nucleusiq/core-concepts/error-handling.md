# Error handling

NucleusIQ provides a framework-level error taxonomy so you can write provider-agnostic error handling code. Whether you use OpenAI, Gemini, or any future provider, the same exception types are raised.

## Error hierarchy

All LLM-related errors inherit from `LLMError`, which inherits from `NucleusIQError`:

```
NucleusIQError
└── LLMError
    ├── AuthenticationError      # Invalid API key (401)
    ├── PermissionDeniedError    # Insufficient permissions (403)
    ├── RateLimitError           # Too many requests (429)
    ├── InvalidRequestError      # Malformed request (400)
    ├── ModelNotFoundError       # Model doesn't exist (404)
    ├── ContentFilterError       # Content blocked by safety filter
    ├── ProviderServerError      # Provider server error (5xx)
    ├── ProviderConnectionError  # Network/connection failure
    └── ProviderError            # Other provider-specific errors
```

## Error attributes

Every `LLMError` carries context about what went wrong:

| Attribute | Type | Description |
|-----------|------|-------------|
| `provider` | `str` | Which provider raised it (`"openai"`, `"gemini"`) |
| `status_code` | `int | None` | HTTP status code if applicable |
| `original_error` | `BaseException | None` | The original SDK exception |
| `message` | `str` | Human-readable error description |

## Usage

### Catch specific errors

```python
from nucleusiq.llms.errors import (
    AuthenticationError,
    RateLimitError,
    ProviderServerError,
    LLMError,
)

try:
    result = await agent.execute({"id": "e1", "objective": "Hello"})
except AuthenticationError as e:
    print(f"Bad API key for {e.provider}")
except RateLimitError as e:
    print(f"Rate limited (status {e.status_code}), implement backoff")
except ProviderServerError:
    print("Provider is having issues, retry later")
except LLMError as e:
    print(f"Unexpected LLM error from {e.provider}: {e}")
```

### Catch all LLM errors

```python
from nucleusiq.llms.errors import LLMError

try:
    result = await agent.execute(task)
except LLMError as e:
    log.error(f"provider={e.provider} status={e.status_code} error={e}")
    # Access the original SDK exception if needed
    if e.original_error:
        log.debug(f"Original: {type(e.original_error).__name__}")
```

### Provider-agnostic handling

The same error handling code works regardless of which LLM provider you use:

```python
# This works with OpenAI, Gemini, or any future provider
from nucleusiq.llms.errors import RateLimitError

try:
    result = await agent.execute({"id": "e2", "objective": "Analyze this data"})
except RateLimitError as e:
    # e.provider tells you which one hit the limit
    print(f"{e.provider} rate limit hit")
```

## Built-in retry

Both OpenAI and Gemini providers include automatic retry with exponential backoff for transient errors:

| Error type | Behavior |
|-----------|----------|
| Rate limits (429) | Retry up to 3 times with exponential backoff |
| Server errors (5xx) | Retry up to 3 times with exponential backoff |
| Connection errors | Retry up to 3 times with exponential backoff |
| Auth errors (401/403) | Fail immediately (no retry) |
| Bad requests (400) | Fail immediately (no retry) |
| Model not found (404) | Fail immediately (no retry) |

If retries are exhausted, the corresponding framework exception is raised.

## Imports

```python
# All errors available from the llms.errors module
from nucleusiq.llms.errors import (
    NucleusIQError,
    LLMError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
    InvalidRequestError,
    ModelNotFoundError,
    ContentFilterError,
    ProviderServerError,
    ProviderConnectionError,
    ProviderError,
)

# Also available from the top-level llms package
from nucleusiq.llms import LLMError, RateLimitError
```

## See also

- [Gemini provider](../guides/gemini-provider.md) — Gemini-specific error mapping
- [OpenAI provider](../guides/openai-provider.md) — OpenAI-specific error mapping
- [Providers](../providers.md) — Provider architecture
