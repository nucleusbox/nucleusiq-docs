# Documentation Maintenance

This repository publishes docs from `documentation/` via MkDocs. Dependencies are managed with **Poetry** (`pyproject.toml` + `poetry.lock`).

## Local workflow

From repository root:

```bash
poetry install --no-interaction
poetry run python scripts/check_docs.py
poetry run python -m mkdocs serve
```

Open `http://127.0.0.1:8000/nucleusiq-docs/` (path may match `site_url` in `mkdocs.yml`).

Alternative without Poetry: `pip install .` then run `python scripts/check_docs.py` and `python -m mkdocs serve`.

## Build validation

```bash
poetry run python scripts/check_docs.py
poetry run python -m mkdocs build --strict
```

## After a NucleusIQ release

Sync the user-facing **version callouts** and **[reference changelog](reference/changelog.md)** with the main repo’s `CHANGELOG.md`, and scan for incomplete `Agent(` snippets (every runnable example needs `prompt=` since v0.7.6).

## Publishing

Docs are deployed by GitHub Actions from `main` using `.github/workflows/docs.yml`.
The published URL is defined by `site_url` in `mkdocs.yml`:

- https://nucleusbox.github.io/nucleusiq-docs/
