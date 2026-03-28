# NucleusIQ Docs

<p align="center">
  <img src="documentation/assets/images/nucleusiq-logo.png" alt="NucleusIQ Logo" width="280" />
</p>

Documentation project for NucleusIQ, built with MkDocs and Material for MkDocs. Dependencies are declared in `pyproject.toml` and locked with **Poetry** (`poetry.lock`).

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation) (recommended), or use `pip install poetry` inside your environment

## Local setup

### 1) Create and activate a virtual environment (optional but recommended)

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2) Install dependencies

From the repository root:

```bash
poetry install --no-interaction
```

This installs MkDocs and related packages from the lockfile into Poetry’s virtualenv.

**Without Poetry:** you can install the same toolchain with pip (PEP 517) if needed:

```bash
pip install .
```

### 3) Run docs checks

```bash
poetry run python scripts/check_docs.py
poetry run python -m mkdocs build --strict
```

### 4) Start local docs server

```bash
poetry run python -m mkdocs serve
```

Open: `http://127.0.0.1:8000/nucleusiq-docs/`

If you used `pip install .` instead of Poetry, run the same commands without the `poetry run` prefix.
