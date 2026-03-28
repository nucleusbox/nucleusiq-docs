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

=== "Both"

    ```bash
    pip install nucleusiq nucleusiq-openai nucleusiq-gemini
    ```

### Optional dependencies

```bash
# Clustering support (for some memory strategies)
pip install "nucleusiq[clustering]"
```

## Verify installation

```python
from importlib.metadata import version

print(version("nucleusiq"))        # e.g., 0.6.0
print(version("nucleusiq-openai")) # e.g., 0.5.0
print(version("nucleusiq-gemini")) # e.g., 0.1.0
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

Or create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=your-gemini-api-key
```

NucleusIQ automatically loads `.env` files from the project root.

## Package architecture

NucleusIQ is a monorepo with independently installable packages:

| Package | Version | Description | Depends on |
|---------|---------|-------------|-----------|
| `nucleusiq` | 0.6.0 | Core framework (agents, tools, memory, plugins) | — |
| `nucleusiq-openai` | 0.5.0 | OpenAI provider | `nucleusiq>=0.6.0` |
| `nucleusiq-gemini` | 0.1.0 | Google Gemini provider | `nucleusiq>=0.6.0` |

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
```

See [CONTRIBUTING.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CONTRIBUTING.md) for full details.

---

Now that you have NucleusIQ installed, follow the [Quickstart](quickstart.md) to build your first agent.
