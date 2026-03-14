# Install NucleusIQ

To install the NucleusIQ core package:

```bash
pip install nucleusiq
# Requires Python 3.10+
```

```bash
uv add nucleusiq
# Requires Python 3.10+
```

NucleusIQ providers (LLM backends) live in independent packages. Install the ones you need:

```bash
# OpenAI provider (most common)
pip install nucleusiq-openai

# Or with uv
uv add nucleusiq-openai
```

```bash
# Core + OpenAI in one command
pip install nucleusiq nucleusiq-openai
```

### Optional dependencies

```bash
# Clustering support (for some memory strategies)
pip install "nucleusiq[clustering]"
```

## Verify installation

```python
from importlib.metadata import version

print(version("nucleusiq"))
```

## Environment variables

### OpenAI provider

```bash
export OPENAI_API_KEY=sk-...
# Or create a .env file in your project root
```

NucleusIQ automatically loads `.env` files from the project root.

## Package architecture

NucleusIQ is a monorepo with independently installable packages:

| Package | Description |
|---------|-------------|
| `nucleusiq` | Core framework (agents, tools, memory, plugins) |
| `nucleusiq-openai` | OpenAI provider |

Each provider depends on `nucleusiq>=0.4.0`—install the core first, then add providers as needed.

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
```

See [CONTRIBUTING.md](https://github.com/nucleusbox/NucleusIQ/blob/main/CONTRIBUTING.md) for full details.

---

Now that you have NucleusIQ installed, follow the [Quickstart](quickstart.md) to build your first agent.
