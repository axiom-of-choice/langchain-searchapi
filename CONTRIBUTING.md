# Contributing to langchain-searchapi

Thanks for your interest in contributing! This guide will help you get set up.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/axiom-of-choice/langchain-searchapi.git
cd langchain-searchapi

# Install dependencies (requires Poetry)
poetry install --with dev,test

# Verify everything works
make all
```

## Branching Strategy

This project uses a two-branch model:

- **`main`** — production branch. Always reflects what is published on PyPI. Never push directly to `main`.
- **`develop`** — integration branch. All feature work merges here first.

### Workflow

1. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/your-feature
   ```
2. Make your changes, commit, push, and open a PR targeting `develop`.
3. Once reviewed and CI passes, merge into `develop`.
4. When ready to release, a maintainer opens a PR from `develop` to `main` and tags the release.

### Branch naming conventions

- `feat/` — new features or engines
- `fix/` — bug fixes
- `docs/` — documentation only
- `ci/` — CI/CD changes

## Releases and Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **PATCH** (0.1.x) — bug fixes, documentation
- **MINOR** (0.x.0) — new features, new engines, backwards-compatible changes
- **MAJOR** (x.0.0) — breaking API changes

### Release process

1. Merge `develop` into `main` via PR.
2. Update the version in `pyproject.toml`.
3. Create a git tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```
4. Build and publish:
   ```bash
   poetry build
   poetry publish --username __token__ --password $PYPI_TOKEN
   ```

## Running Tests

```bash
# Unit tests (no API key needed)
make test

# Integration tests (requires SEARCHAPI_API_KEY)
export SEARCHAPI_API_KEY="your-key"
make test-integration
```

## Code Quality

All contributions must pass CI before merge:

```bash
# Lint
make lint

# Type checking
make type-check

# Format (auto-fix)
make format

# Run all checks
make all
```

## Making Changes

1. Fork the repo and create a feature branch from `develop`
2. Make your changes
3. Add tests for new functionality
4. Run `make all` to verify lint, types, and tests pass
5. Submit a pull request targeting `develop`

## Architecture

```
langchain_searchapi/
├── __init__.py          # Public API exports
├── _utilities.py        # SearchApiAPIWrapper (HTTP layer)
├── tools.py             # SearchApiSearch (BaseTool for agents)
├── retrievers.py        # SearchApiRetriever (BaseRetriever for RAG)
└── py.typed             # PEP 561 marker
```

### Design Principles

- **Follow langchain-tavily patterns** — this package mirrors the architecture of established LangChain integration packages
- **Minimal dependencies** — only `langchain-core`, `requests`, and `aiohttp`
- **Full type coverage** — mypy strict mode, all public functions annotated
- **Sync + Async** — every public method has an async counterpart

## Adding a New Engine

SearchApi.io adds new engines periodically. To support a new one:

1. Add the engine value to the `ENGINE_TYPE` literal in `_utilities.py`
2. If the engine returns results under a new key (not `organic_results`), add snippet extraction logic in `_extract_snippets()`
3. If relevant for the retriever, add document conversion logic in `_results_to_documents()`
4. Add integration tests
5. Update the "Supported Engines" table in README.md

## Reporting Issues

Please include:
- Python version
- `langchain-searchapi` version
- The engine you're using
- Minimal reproduction code
