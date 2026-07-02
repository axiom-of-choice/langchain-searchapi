"""Integration tests for SearchApiRetriever (requires SEARCHAPI_API_KEY)."""

import pytest

from langchain_searchapi.retrievers import SearchApiRetriever


@pytest.fixture
def retriever() -> SearchApiRetriever:
    return SearchApiRetriever(num=3)


class TestSearchApiRetrieverIntegration:
    def test_retrieve_documents(self, retriever: SearchApiRetriever) -> None:
        docs = retriever.invoke("python programming")
        assert len(docs) > 0
        assert docs[0].page_content
        assert docs[0].metadata["title"]
        assert docs[0].metadata["link"]
        assert docs[0].metadata["source"] == "searchapi"

    def test_retrieve_news(self) -> None:
        retriever = SearchApiRetriever(engine="google_news", num=3)
        docs = retriever.invoke("technology news")
        assert len(docs) > 0
        assert docs[0].page_content
        assert docs[0].metadata["source"] == "searchapi"

    @pytest.mark.asyncio
    async def test_async_retrieve(self) -> None:
        retriever = SearchApiRetriever(num=3)
        docs = await retriever.ainvoke("async search test")
        assert len(docs) > 0
        assert docs[0].page_content
