"""Unit tests for SearchApiRetriever."""

from unittest.mock import MagicMock, patch

import pytest

from langchain_searchapi.retrievers import SearchApiRetriever


@pytest.fixture(autouse=True)
def mock_validate(request: pytest.FixtureRequest) -> MagicMock:
    patcher = patch(
        "langchain_searchapi._utilities.SearchApiAPIWrapper.validate_environment"
    )
    mock = patcher.start()
    mock.side_effect = lambda values: values
    request.addfinalizer(patcher.stop)
    return mock


class TestSearchApiRetriever:
    def test_initialization(self) -> None:
        retriever = SearchApiRetriever(searchapi_api_key="fake_key")
        assert retriever.engine == "google"
        assert retriever.num == 5
        assert retriever.api_wrapper is not None

    def test_initialization_custom_params(self) -> None:
        retriever = SearchApiRetriever(
            searchapi_api_key="fake_key",
            engine="google_news",
            num=10,
            gl="us",
            hl="en",
        )
        assert retriever.engine == "google_news"
        assert retriever.num == 10
        assert retriever.gl == "us"
        assert retriever.hl == "en"

    @patch("langchain_searchapi._utilities.requests.get")
    def test_get_relevant_documents(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic_results": [
                {
                    "title": "Result 1",
                    "snippet": "First result snippet",
                    "link": "https://example.com/1",
                    "position": 1,
                },
                {
                    "title": "Result 2",
                    "snippet": "Second result snippet",
                    "link": "https://example.com/2",
                    "position": 2,
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        retriever = SearchApiRetriever(searchapi_api_key="fake_key")
        docs = retriever.invoke("test query")

        assert len(docs) == 2
        assert docs[0].page_content == "First result snippet"
        assert docs[0].metadata["title"] == "Result 1"
        assert docs[0].metadata["link"] == "https://example.com/1"
        assert docs[0].metadata["source"] == "searchapi"
        assert docs[0].metadata["position"] == 1

    @patch("langchain_searchapi._utilities.requests.get")
    def test_news_results_to_documents(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "news_results": [
                {
                    "title": "News 1",
                    "snippet": "News snippet",
                    "link": "https://news.com/1",
                    "date": "2024-01-01",
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        retriever = SearchApiRetriever(
            searchapi_api_key="fake_key", engine="google_news"
        )
        docs = retriever.invoke("test")

        assert len(docs) == 1
        assert docs[0].metadata["type"] == "news"
        assert docs[0].metadata["date"] == "2024-01-01"

    @patch("langchain_searchapi._utilities.requests.get")
    def test_empty_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        retriever = SearchApiRetriever(searchapi_api_key="fake_key")
        docs = retriever.invoke("test")

        assert docs == []
