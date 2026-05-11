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

=== "Gemini"

    ```bash
    pip install nucleusiq nucleusiq-gemini
    ```

=== "Groq"

    ```bash
    pip install nucleusiq nucleusiq-groq
    ```

    Public beta — pin if needed: `pip install "nucleusiq-groq==0.1.0b1"`

=== "Ollama"

    ```bash
    pip install nucleusiq nucleusiq-ollama
    ```

    **Alpha** — pin if needed: `pip install "nucleusiq>=0.7.10" "nucleusiq-ollama==0.1.0a1"`

=== "Both (OpenAI + Gemini)"

    ```bash
    pip install nucleusiq nucleusiq-openai nucleusiq-gemini
    ```

=== "All four providers"

    ```bash
    pip install nucleusiq nucleusiq-openai nucleusiq-gemini nucleusiq-groq nucleusiq-ollama
    ```

=== "OpenAI + Gemini + Groq only"

    ```bash
    pip install nucleusiq nucleusiq-openai nucleusiq-gemini nucleusiq-groq
    ```

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

for pkg in ("nucleusiq", "nucleusiq-openai", "nucleusiq-gemini"):
    print(f"{pkg}: {version(pkg)}")

try:
    print(f"nucleusiq-groq: {version('nucleusiq-groq')}")
except PackageNotFoundError:
    print("nucleusiq-groq: (not installed)")

try:
    print(f"nucleusiq-ollama: {version('nucleusiq-ollama')}")
except PackageNotFoundError:
    print("nucleusiq-ollama: (not installed)")
```

## Environment variables

=== "OpenAI"

    ```bash
    export OPENAI_API_KEY=sk-...
    ```

=== "Gemini"

    ```bash
    export GEMINI_API_KEY=your-gemini-api-key
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

Or create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=gsk_...
# OLLAMA_HOST=
# OLLAMA_API_KEY=
```

NucleusIQ automatically loads `.env` files from the project root.

## Package architecture

NucleusIQ is a monorepo with independently installable packages:

| Package | Version | Description | Depends on |
|---------|---------|-------------|-----------|
| `nucleusiq` | **0.7.10** | Core framework; optional **`nucleusiq[http]`**; structured-output resolver recognizes **Ollama** / Groq LLMs (**v0.7.10**) | — |
| `nucleusiq-openai` | **0.6.4** | OpenAI provider | `nucleusiq>=0.7.9` |
| `nucleusiq-gemini` | **0.2.6** | Google Gemini provider | `nucleusiq>=0.7.9` |
| `nucleusiq-groq` | **0.1.0b1** (beta) | Groq Chat Completions (`groq` SDK) | `nucleusiq>=0.7.9`, `groq>=1.2,<2` |
| `nucleusiq-ollama` | **0.1.0a1** (alpha) | Ollama `/api/chat` (`ollama` SDK) | `nucleusiq>=0.7.10`, `ollama>=0.5,<1` |

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

# Groq provider (beta — Chat Completions)
cd ../../inference/groq
uv venv && uv sync --all-groups

# Ollama provider (alpha)
cd ../ollama
uv venv && uv sync --all-groups
```

See [CONTRIBUTING.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CONTRIBUTING.md) for full details.

---

Now that you have NucleusIQ installed, follow the [Quickstart](quickstart.md) to build your first agent.
