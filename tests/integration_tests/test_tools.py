"""Integration tests for SearchApiSearch tool (requires SEARCHAPI_API_KEY)."""

import pytest

from langchain_searchapi.tools import SearchApiSearch


@pytest.fixture
def tool() -> SearchApiSearch:
    return SearchApiSearch()


class TestSearchApiSearchIntegration:
    def test_google_search(self, tool: SearchApiSearch) -> None:
        result = tool.invoke({"query": "python programming language"})
        assert isinstance(result, dict)
        assert "organic_results" in result
        assert len(result["organic_results"]) > 0

    def test_google_news(self, tool: SearchApiSearch) -> None:
        result = tool.invoke({"query": "technology", "engine": "google_news"})
        assert isinstance(result, dict)
        assert "organic_results" in result or "news_results" in result

    def test_youtube_search(self, tool: SearchApiSearch) -> None:
        result = tool.invoke({"query": "python tutorial", "engine": "youtube"})
        assert isinstance(result, dict)
        assert "videos" in result or "video_results" in result

    def test_num_results(self, tool: SearchApiSearch) -> None:
        result = tool.invoke({"query": "test", "num": 3})
        assert isinstance(result, dict)
        if "organic_results" in result:
            assert len(result["organic_results"]) <= 3

    @pytest.mark.asyncio
    async def test_async_search(self) -> None:
        tool = SearchApiSearch()
        result = await tool.ainvoke({"query": "async test"})
        assert isinstance(result, dict)
        assert "organic_results" in result
