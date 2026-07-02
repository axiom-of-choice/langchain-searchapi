# langchain-searchapi

[![PyPI version](https://badge.fury.io/py/langchain-searchapi.svg)](https://pypi.org/project/langchain-searchapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

An integration package connecting [SearchApi.io](https://www.searchapi.io) and [LangChain](https://github.com/langchain-ai/langchain).

## Why this package?

LangChain's original SearchApi integration lives in `langchain_community` (merged in 2023) but was never ported to the modern standalone package architecture. It lacks:

- **Multi-engine selection at call time** — the old tool only accepts a query string; agents can't switch engines dynamically
- **Retriever for RAG** — no way to use SearchApi results in retrieval chains
- **Secret management** — API key stored as plain string, visible in logs/repr
- **Structured output** — returns stringified results instead of typed dicts

This package (`langchain-searchapi`) is a modern, standalone replacement following the same architecture as [`langchain-tavily`](https://github.com/tavily-ai/langchain-tavily). It provides a Tool for agents, a Retriever for RAG, and full async support.

## Installation

```bash
pip install langchain-searchapi
```

## Setup

Set your API key as an environment variable:

```bash
export SEARCHAPI_API_KEY="your-api-key"
```

Get your key at [searchapi.io](https://www.searchapi.io).

## Quick Start

### Tool (for agents)

```python
from langchain_searchapi import SearchApiSearch

# Default Google search
tool = SearchApiSearch()
results = tool.invoke({"query": "latest AI news"})

# Switch engines at call time
results = tool.invoke({"query": "python tutorial", "engine": "youtube"})

# Configure defaults at initialization
tool = SearchApiSearch(engine="google_news", num=5, gl="us", hl="en")
results = tool.invoke({"query": "technology"})
```

### With a LangChain Agent

```python
from langchain_searchapi import SearchApiSearch
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o")
tools = [SearchApiSearch()]

agent = create_react_agent(llm, tools)
response = agent.invoke({"messages": [("user", "What happened in tech news today?")]})
```

### Retriever (for RAG)

```python
from langchain_searchapi import SearchApiRetriever

retriever = SearchApiRetriever(engine="google", num=5)
docs = retriever.invoke("machine learning frameworks comparison")

for doc in docs:
    print(f"{doc.metadata['title']}: {doc.page_content}")
```

### In a RAG Chain

```python
from langchain_searchapi import SearchApiRetriever
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

retriever = SearchApiRetriever(num=5)
llm = ChatOpenAI(model="gpt-4o")

prompt = ChatPromptTemplate.from_template(
    "Answer the question based on the context:\n\n{context}\n\nQuestion: {question}"
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("What are the best Python web frameworks in 2024?")
```

## Supported Engines

| Engine | Value | Description |
|--------|-------|-------------|
| Google | `google` | Web search (default) |
| Google News | `google_news` | News articles |
| Google Shopping | `google_shopping` | Product listings |
| Google Jobs | `google_jobs` | Job postings |
| Google Scholar | `google_scholar` | Academic papers |
| YouTube | `youtube` | Video search |
| Bing | `bing` | Microsoft Bing |
| Baidu | `baidu` | Chinese search engine |

## API Reference

### SearchApiSearch

Tool for use with LangChain agents. Agents can select the engine and number of results dynamically via the tool's input schema.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `searchapi_api_key` | str | env `SEARCHAPI_API_KEY` | Your SearchApi.io API key |
| `engine` | str | `"google"` | Default search engine |
| `num` | int | None | Number of results |
| `gl` | str | None | Country code (e.g., `"us"`) |
| `hl` | str | None | Language code (e.g., `"en"`) |
| `location` | str | None | Location for localized results |

### SearchApiRetriever

Retriever for RAG chains. Returns search results as LangChain `Document` objects with metadata (title, link, source, position).

Same parameters as `SearchApiSearch`.

### SearchApiAPIWrapper

Low-level wrapper if you need direct API access. Provides `raw_results()`, `results()` (metadata-stripped), and `run()` (text snippets).

## Migrating from langchain_community

If you're using the deprecated `langchain_community.utilities.SearchApiAPIWrapper`:

```python
# Before (deprecated)
from langchain_community.utilities import SearchApiAPIWrapper
wrapper = SearchApiAPIWrapper()
result = wrapper.run("query")

# After
from langchain_searchapi import SearchApiAPIWrapper
wrapper = SearchApiAPIWrapper()
result = wrapper.run("query")
```

The new package is a drop-in replacement for basic usage, with additional features (multi-engine tool schema, retriever, SecretStr key management).

## Related

- [SearchApi.io Documentation](https://www.searchapi.io/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [`langchain_community` SearchApi (deprecated)](https://github.com/langchain-ai/langchain-community) — the old integration this package replaces

## License

MIT — see [LICENSE](LICENSE) for details.
