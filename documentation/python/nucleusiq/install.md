# Install NucleusIQ

## Core package

```bash
pip install nucleusiq
# Requires Python 3.10+
```

```bash
uv add nucleusiq
```

## LLM providers

NucleusIQ providers live in independent packages. Install the ones you need:

=== "OpenAI"

    ```bash
    pip install nucleusiq nucleusiq-openai
    ```

=== "OpenAI-compatible (self-hosted / BYOM)"

    ```bash
    pip install "nucleusiq>=0.7.13" nucleusiq-openai-compatible
    ```

    Use this for **vLLM**, **SGLang**, **TGI**, **llama.cpp**, **LM Studio**, **NVIDIA NIM**, Ollama `/v1`, OpenRouter, Together, and **Azure OpenAI v1**. See the [OpenAI-compatible provider guide](guides/openai-compatible-provider.md).

=== "Gemini"

    ```bash
    pip install nucleusiq nucleusiq-gemini
    ```

=== "Anthropic (Claude)"

    ```bash
    pip install nucleusiq nucleusiq-anthropic
    ```

    Stable — pin if needed: `pip install "nucleusiq>=0.7.12" "nucleusiq-anthropic>=0.2.1,<0.3"`

=== "Groq"

    ```bash
    pip install nucleusiq nucleusiq-groq
    ```

    Stable — pin if needed: `pip install "nucleusiq>=0.7.12" "nucleusiq-groq>=0.1.1,<0.2"`

=== "Ollama"

    ```bash
    pip install nucleusiq nucleusiq-ollama
    ```

    Stable native Ollama API — pin if needed: `pip install "nucleusiq>=0.7.12" "nucleusiq-ollama>=0.2.1,<0.3"`. For Ollama's OpenAI `/v1` shim, use `nucleusiq-openai-compatible` instead.

=== "Both (OpenAI + Gemini)"

    ```bash
    pip install nucleusiq nucleusiq-openai nucleusiq-gemini
    ```

=== "All major LLM providers"

    ```bash
    pip install nucleusiq nucleusiq-openai nucleusiq-openai-compatible nucleusiq-gemini nucleusiq-anthropic nucleusiq-groq nucleusiq-ollama
    ```

=== "OpenAI + Gemini + Groq only"

    ```bash
    pip install nucleusiq nucleusiq-openai nucleusiq-gemini nucleusiq-groq
    ```

## Tool adapters

=== "MCP (Model Context Protocol)"

    ```bash
    # Recommended — through the core extras
    pip install "nucleusiq[mcp]" nucleusiq-anthropic     # or any provider

    # Or pin the adapter directly
    pip install "nucleusiq>=0.7.12" "nucleusiq-mcp>=0.1.1,<0.2"
    ```

    **Stable** — universal MCP adapter built on the official **`mcp`** SDK. Works with **every** provider (OpenAI, Anthropic, Gemini, Groq, Ollama, OpenAI-compatible). Supports **stdio + Streamable HTTP + SSE** transports and Bearer / OAuth 2.1 / Env / custom-header auth. Requires **`nucleusiq>=0.7.12`** and **`mcp>=1.28.1,<2`**. See the [MCP integration guide](guides/mcp-integration.md).

    **Node.js + `npx` 18+** are required if you connect to **stdio** servers shipped as `@modelcontextprotocol/server-...` npm packages.

=== "Legacy (OpenAI server-side MCP)"

    ```bash
    pip install nucleusiq nucleusiq-openai
    ```

    Uses **`OpenAITool.mcp(...)`** from `nucleusiq-openai`. The MCP server is reached by **OpenAI's Responses API**, not your process. OpenAI provider only — for cross-provider use, prefer **`nucleusiq-mcp`** above. See **[MCP integration guide → When to use which](guides/mcp-integration.md#when-to-use-which)**.

### Optional dependencies

```bash
# Auto Chain-of-Thought clustering (scikit-learn ~50MB)
pip install "nucleusiq[clustering]"
```

**v0.7.10+ — HTTP stack for notebooks / legacy apps** (not imported by core):

```bash
pip install "nucleusiq[http]"
```

The clustering extra is only needed if you use the `AutoChainOfThoughtPrompt` technique. The core framework works without it.

## Verify installation

```python
from importlib.metadata import PackageNotFoundError, version

for pkg in ("nucleusiq", "nucleusiq-openai", "nucleusiq-openai-compatible", "nucleusiq-gemini"):
    print(f"{pkg}: {version(pkg)}")

try:
    print(f"nucleusiq-anthropic: {version('nucleusiq-anthropic')}")
except PackageNotFoundError:
    print("nucleusiq-anthropic: (not installed)")

try:
    print(f"nucleusiq-groq: {version('nucleusiq-groq')}")
except PackageNotFoundError:
    print("nucleusiq-groq: (not installed)")

try:
    print(f"nucleusiq-ollama: {version('nucleusiq-ollama')}")
except PackageNotFoundError:
    print("nucleusiq-ollama: (not installed)")

try:
    print(f"nucleusiq-mcp: {version('nucleusiq-mcp')}")
except PackageNotFoundError:
    print("nucleusiq-mcp: (not installed)")
```

## Environment variables

=== "OpenAI"

    ```bash
    export OPENAI_API_KEY=sk-...
    ```

=== "OpenAI-compatible"

    ```bash
    export OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:8000/v1
    export OPENAI_COMPATIBLE_MODEL=gemma-4-27b-it
    # export OPENAI_COMPATIBLE_API_KEY=...   # omit if the server has no key
    ```

=== "Gemini"

    ```bash
    export GEMINI_API_KEY=your-gemini-api-key
    ```

=== "Anthropic"

    ```bash
    export ANTHROPIC_API_KEY=sk-ant-...
    # export ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
    ```

=== "Groq"

    ```bash
    export GROQ_API_KEY=gsk_...
    # Optional defaults used by repo examples:
    # export GROQ_MODEL=llama-3.3-70b-versatile
    # export GROQ_MODEL_STRUCTURED=openai/gpt-oss-20b
    ```

=== "Ollama"

    ```bash
    # Optional — default is local SDK default (often http://127.0.0.1:11434)
    # export OLLAMA_HOST=http://127.0.0.1:11434
    # export OLLAMA_API_KEY=...   # hosted / Bearer endpoints only
    # export OLLAMA_MODEL=llama3.2
    ```

=== "MCP (server-specific)"

    ```bash
    # MCP servers each have their own env requirements. Common ones:
    export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...   # @modelcontextprotocol/server-github
    export SLACK_BOT_TOKEN=xoxb-...                # mcp.slack.com
    # OAuth servers — handled by the OAuthAuth strategy at runtime; no env required.
    ```

    See the **[MCP integration guide](guides/mcp-integration.md)** for the four auth strategies (`BearerAuth`, `OAuthAuth`, `EnvAuth`, `CustomHeadersAuth`).

Or create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=your-gemini-api-key
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
# OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:8000/v1
# OPENAI_COMPATIBLE_MODEL=gemma-4-27b-it
# OPENAI_COMPATIBLE_API_KEY=
# OLLAMA_HOST=
# OLLAMA_API_KEY=
```

NucleusIQ automatically loads `.env` files from the project root.

## Package architecture

NucleusIQ is a monorepo with independently installable packages:

| Package | Version | Description | Depends on |
|---------|---------|-------------|-----------|
| `nucleusiq` | **0.7.13** | Core framework; declared `BaseLLM.PROVIDER_NAME`; optional **`nucleusiq[http]`**, **`nucleusiq[mcp]`** | — |
| `nucleusiq-openai-compatible` | **0.1.0** | Self-hosted / BYOM Chat Completions (vLLM, SGLang, llama.cpp, LM Studio, Azure OpenAI v1, …) | `nucleusiq>=0.7.13` |
| `nucleusiq-openai` | **0.7.1** | OpenAI cloud (Chat Completions + Responses API) | `nucleusiq>=0.7.12` |
| `nucleusiq-gemini` | **0.3.1** | Google Gemini provider | `nucleusiq>=0.7.12` |
| `nucleusiq-anthropic` | **0.2.1** | Claude Messages API (`anthropic` SDK) | `nucleusiq>=0.7.12`, `anthropic>=0.40,<1` |
| `nucleusiq-groq` | **0.1.1** | Groq Chat Completions (`groq` SDK) | `nucleusiq>=0.7.12`, `groq>=1.2,<2` |
| `nucleusiq-ollama` | **0.2.1** | Ollama native `/api/chat` (`ollama` SDK) | `nucleusiq>=0.7.12`, `ollama>=0.5,<1` |
| `nucleusiq-mcp` | **0.1.1** | Universal Model Context Protocol adapter (official `mcp` SDK); stdio + Streamable HTTP + SSE; OAuth/Bearer/Env auth | `nucleusiq>=0.7.12`, `mcp>=1.28.1,<2` |

Install the core first, then add providers as needed.

## Developers (contributing)

Clone the repo and install in editable mode:

```bash
git clone https://github.com/nucleusbox/NucleusIQ.git
cd NucleusIQ

# Core package
cd src/nucleusiq
uv venv && uv sync --all-groups

# OpenAI provider
cd ../providers/llms/openai
uv venv && uv sync --all-groups

# Gemini provider
cd ../gemini
uv venv && uv sync --all-groups

# Anthropic provider (Claude Messages API)
cd ../anthropic
uv venv && uv sync --all-groups

# Groq provider
cd ../../inference/groq
uv venv && uv sync --all-groups

# Ollama provider (native API)
cd ../ollama
uv venv && uv sync --all-groups

# OpenAI-compatible provider (self-hosted / BYOM)
cd ../openai_compatible
uv venv && uv sync --all-groups

# MCP tool adapter
cd ../../tools/mcp
uv venv && uv sync --all-groups
```

See [CONTRIBUTING.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CONTRIBUTING.md) for full details.

---

Now that you have NucleusIQ installed, follow the [Quickstart](quickstart.md) to build your first agent.
