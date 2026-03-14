# NucleusIQ Docs

<p align="center">
  <img src="documentation/assets/images/nucleusiq-logo.png" alt="NucleusIQ Logo" width="280" />
</p>

Documentation project for NucleusIQ, built with MkDocs and Material for MkDocs.

## Local setup

### 1) Create and activate a virtual environment

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

### 2) Install project dependencies

```bash
pip install .
```

### 3) Run docs checks

```bash
python scripts/check_docs.py
python -m mkdocs build --strict
```

### 4) Start local docs server

```bash
python -m mkdocs serve
```

Open: `http://127.0.0.1:8000/nucleusiq-docs/`
