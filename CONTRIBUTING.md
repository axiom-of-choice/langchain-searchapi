# Contributing to langchain-searchapi

Thanks for your interest in contributing! This guide will help you get set up.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/isaacvander/langchain-searchapi.git
cd langchain-searchapi

# Install dependencies (requires Poetry)
poetry install --with dev,test

# Verify everything works
make all
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

All contributions must pass:

```bash
# Lint
make lint

# Type checking
make type-check

# Format (auto-fix)
make format
```

## Making Changes

1. Fork the repo and create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Run `make all` to verify lint, types, and tests pass
5. Submit a pull request

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
