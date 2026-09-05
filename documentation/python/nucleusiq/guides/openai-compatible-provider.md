# OpenAI-compatible provider

The **`nucleusiq-openai-compatible`** package runs NucleusIQ agents against **any server that speaks the OpenAI Chat Completions protocol**. Your GPU, your model, your key.

Use it for **vLLM**, **SGLang**, **TGI**, **llama.cpp**, **LM Studio**, **NVIDIA NIM**, Ollama's `/v1` shim, and OpenAI-compatible clouds (OpenRouter, Together, Fireworks, DeepInfra, Databricks, LiteLLM, **Azure OpenAI v1**).

!!! success "🟢 New in v0.7.13 — `nucleusiq-openai-compatible` 0.1.0 Stable"

    Requires **`nucleusiq>=0.7.13`**. **675 tests, 99.40% coverage.**

    This is a **separate package** from [`nucleusiq-openai`](openai-provider.md). The cloud OpenAI adapter owns Responses API, hosted tools, and tiktoken. This package owns self-hosted and third-party Chat Completions servers. It does **not** depend on `nucleusiq-openai`.

!!! warning "Not the Azure SDK"

    Azure is supported only on the **v1 Chat Completions URL** (`https://{resource}.openai.azure.com/openai/v1`) with `HeaderAuth("api-key", ...)`. Classic deployment URLs (`/openai/deployments/{name}/...?api-version=...`) and the `AzureOpenAI` client are **not** used. See [Azure OpenAI v1](#azure-openai-v1).

## Why a separate package

Pointing `BaseOpenAI(base_url=...)` at a self-hosted server looks tempting and produces tokens, but NucleusIQ's context engine reads provider metadata. The cloud adapter then:

- requires `OPENAI_API_KEY` (a local vLLM with no `--api-key` needs a fake key)
- assumes a **128K** window for unknown models (Gemma at `--max-model-len 32768` never compact)
- counts tokens with **tiktoken** (wrong family for Llama / Qwen / Gemma)
- routes native tools to the **Responses API** (self-hosted servers have no `/v1/responses`)
- guesses capabilities from the **model name string**

This package declares capabilities. Nothing is inferred from `my-finetune-v3`.

## Installation

```bash
pip install "nucleusiq>=0.7.13" nucleusiq-openai-compatible
```

Optional: exact token counts with a Hugging Face tokenizer (tiktoken is not used):

```bash
pip install "nucleusiq-openai-compatible[tokenizer]"
```

## Quick start

```python
import asyncio

from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai_compatible import OpenAICompatibleLLM


async def main() -> None:
    llm = OpenAICompatibleLLM(
        base_url="http://gpu-node-1:8000/v1",
        model="gemma-4-27b-it",       # your --served-model-name
        api_key="token-abc123",       # omit entirely if the server has no key
        context_window=32_768,        # must match --max-model-len
        engine="vllm",
    )

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a concise data analyst.",
        ),
        llm=llm,
        config=AgentConfig(execution_mode=ExecutionMode.DIRECT),
    )
    await agent.initialize()
    result = await agent.execute(
        Task(id="q1", objective="What is 17% of 4,830?"),
    )
    print(result.output)


asyncio.run(main())
```

`BaseOpenAICompatible` is an alias for `OpenAICompatibleLLM`.

### Environment variables

| Variable | Purpose |
|----------|---------|
| **`OPENAI_COMPATIBLE_BASE_URL`** | Server root. `/v1` is appended if missing. |
| **`OPENAI_COMPATIBLE_MODEL`** | Served model / deployment name. |
| **`OPENAI_COMPATIBLE_API_KEY`** | Optional. Omit for an unauthenticated server. |

Pass `context_window` if you know it. Without it the provider probes `/v1/models` for `max_model_len`, then falls back to **8192** with a warning. Over-reporting the window is the dangerous direction: compaction never fires and the server rejects the request.

## One instance, one model

An `OpenAICompatibleLLM` describes **exactly one model on exactly one endpoint**. Passing a different `model=` to `call()` raises.

NucleusIQ reads `BaseLLM.get_context_window()` once, with no model argument, to size the whole context budget. A per-call model switch would size that budget for the wrong window.

Serving several models from one node? Build several instances.

## Check the server before an agent run

`validate()` is explicit and never called from the constructor (a constructor must not do I/O):

```python
report = await llm.validate()
print(report.render())
```

The report checks reachability, auth, whether `model` appears in `/v1/models`, and the claimed context window. A typo becomes a list of served names instead of a mid-run `404`.

## Engine presets

Pass `engine=` so tools, JSON schema, parallel tool calls, streamed usage, and reasoning defaults match the server. Override any flag if your build differs.

| Engine | Tools | JSON schema | Notes |
|--------|-------|-------------|-------|
| `vllm` | yes | yes | Do not send `response_format` together with `tools` + `tool_choice="auto"` — vLLM then returns JSON and **no** tool calls. This package routes that case through the policy layer. |
| `sglang` | yes | yes | Tool calling needs `--tool-call-parser`. |
| `tgi` | yes | **no** (varies by version) | Verify before relying on schema enforcement. |
| `llamacpp` | yes | no | Grammar / tool-parser depend on the build. |
| `lmstudio` | yes | yes | Desktop; unauthenticated by default. |
| `ollama` | yes | **no** | The `/v1` shim accepts `json_schema` and ignores it. Schema is prompt-injected. For Ollama's **native** `format`, use [`nucleusiq-ollama`](ollama-provider.md). |
| `nim` | yes | yes | NVIDIA NIM. Bearer `NVIDIA_API_KEY` when hosted. |
| `azure` | yes | yes | v1 URL only. `model=` is the **deployment name**. |
| `litellm` | yes | yes | Follows the routed backend. |
| `openrouter` / `together` / `fireworks` / `deepinfra` / `databricks` | yes | yes | Cloud shims; capabilities vary per model. |
| `generic` | conservative | no | Default when you do not know the engine. |

```python
llm = OpenAICompatibleLLM(
    base_url="http://127.0.0.1:11434/v1",
    model="llama3.2",
    engine="ollama",
    supports_json_schema=False,   # already the ollama preset
)
```

## Auth (bring your own key)

| Strategy | Sends | Use for |
|----------|-------|---------|
| `NoAuth()` *(default)* | nothing | local vLLM / SGLang / llama.cpp / LM Studio without `--api-key` |
| `BearerAuth(v)` or `api_key=v` | `Authorization: Bearer v` | vLLM `--api-key`, most clouds |
| `HeaderAuth(name, v)` | `name: v` | Azure `api-key`, gateways `X-API-Key` |

`api_key=` and `auth=` together are rejected as ambiguous.

Credentials may be a literal, an env-var name, or a **callable**. A callable is resolved **once per request** and shared between headers and the SDK key, so a token-minting hook is not billed twice.

```python
import os

from nucleusiq_openai_compatible import HeaderAuth, OpenAICompatibleLLM

llm = OpenAICompatibleLLM(
    base_url="https://my-resource.openai.azure.com/openai/v1",
    model="my-deployment",
    engine="azure",
    auth=HeaderAuth("api-key", os.environ["AZURE_OPENAI_API_KEY"]),
)
```

Secrets never appear in `repr()`, logs, or mapped exception messages.

mTLS, SigV4, or a corporate proxy: pass a configured `httpx.AsyncClient` as `http_client=`.

## Azure OpenAI v1

```python
import os

from nucleusiq_openai_compatible import HeaderAuth, OpenAICompatibleLLM

llm = OpenAICompatibleLLM(
    base_url="https://my-resource.openai.azure.com/openai/v1",
    model="gpt4o-prod",   # deployment name
    engine="azure",
    auth=HeaderAuth("api-key", os.environ["AZURE_OPENAI_API_KEY"]),
    # Preview features only:
    # default_query={"api-version": "preview"},
)
```

A Microsoft Entra bearer token can go in as `api_key=` (Bearer). This is **not** the `AzureOpenAI` SDK class.

## Standard mode + tools

Same `@tool` / `BaseTool` surface as every other provider:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai_compatible import OpenAICompatibleLLM


@tool
def add(a: int, b: int) -> str:
    """Add two integers."""
    return str(a + b)


llm = OpenAICompatibleLLM(
    base_url="http://gpu-node-1:8000/v1",
    model="gemma-4-27b-it",
    context_window=32_768,
    engine="vllm",
)

agent = Agent(
    name="compat-tools",
    prompt=ZeroShotPrompt().configure(
        system="Use tools when arithmetic is needed.",
    ),
    llm=llm,
    tools=[add],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

## Structured output

Core still hands the schema to the adapter (`OutputMode.AUTO` → NATIVE). **This** adapter decides whether the server can enforce it.

- Engines with `supports_json_schema=True` send `response_format`.
- Engines that cannot (Ollama `/v1`, `generic`) use `json_object` plus a prompt-injected schema (`PromptPolicy`).
- Combined `tools` + `response_format` on vLLM is rewritten so tool calls are not suppressed.

```python
from pydantic import BaseModel

from nucleusiq_openai_compatible import OpenAICompatibleLLM


class MovieReview(BaseModel):
    title: str
    rating: float
    summary: str


llm = OpenAICompatibleLLM(
    base_url="http://gpu-node-1:8000/v1",
    model="gemma-4-27b-it",
    engine="vllm",
    context_window=32_768,
)

review = await llm.call(
    messages=[{"role": "user", "content": "Review Inception"}],
    response_format=MovieReview,
)
print(review.title, review.rating)
```

Policies: `DropPolicy`, `ErrorPolicy`, `PromptPolicy`.

## Which package should I use?

| Situation | Package |
|-----------|---------|
| OpenAI cloud (Responses API, hosted tools, tiktoken) | [`nucleusiq-openai`](openai-provider.md) |
| Groq official SDK | [`nucleusiq-groq`](groq-provider.md) |
| Ollama **native** API (`/api/chat`, `format`, vision) | [`nucleusiq-ollama`](ollama-provider.md) |
| Your vLLM / SGLang / TGI / llama.cpp / LM Studio | **this package** |
| OpenAI-compatible cloud with no first-party adapter | **this package** |
| Azure OpenAI **v1** Chat Completions | **this package** |

## Not in 0.1.0

`/v1/embeddings`, vision content parts, and engine auto-detection from `/v1/models` are planned for `0.2.x`.

## See also

- [OpenAI-compatible quickstart](../examples/openai-compatible-quickstart.md)
- [OpenAI cloud provider](openai-provider.md)
- [Ollama native provider](ollama-provider.md)
- Monorepo examples: [`src/providers/inference/openai_compatible/examples`](https://github.com/nucleusbox/NucleusIQ/tree/main/src/providers/inference/openai_compatible/examples)
