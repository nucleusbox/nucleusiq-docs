# Documentation Maintenance

This repository publishes docs from `documentation/` via MkDocs.

## Local workflow

From repository root:

```bash
pip install .
python scripts/check_docs.py
python -m mkdocs serve
```

Open `http://127.0.0.1:8000`.

## Build validation

```bash
python scripts/check_docs.py
python -m mkdocs build --strict
```

## Publishing

Docs are deployed by GitHub Actions from `main` using `.github/workflows/docs.yml`.
The published URL is defined by `site_url` in `mkdocs.yml`:

- https://nucleusbox.github.io/NucleusIQ/
