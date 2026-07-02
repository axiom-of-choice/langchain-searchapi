"""Unit tests for SearchApiSearch tool."""

from unittest.mock import MagicMock, patch

import pytest

from langchain_searchapi.tools import SearchApiSearch


@pytest.fixture(autouse=True)
def mock_validate(request: pytest.FixtureRequest) -> MagicMock:
    patcher = patch(
        "langchain_searchapi._utilities.SearchApiAPIWrapper.validate_environment"
    )
    mock = patcher.start()
    mock.side_effect = lambda values: values
    request.addfinalizer(patcher.stop)
    return mock


class TestSearchApiSearch:
    def test_initialization_defaults(self) -> None:
        tool = SearchApiSearch(searchapi_api_key="fake_key")
        assert tool.name == "searchapi"
        assert tool.engine == "google"
        assert tool.api_wrapper is not None

    def test_initialization_custom_engine(self) -> None:
        tool = SearchApiSearch(searchapi_api_key="fake_key", engine="youtube")
        assert tool.engine == "youtube"

    def test_args_schema(self) -> None:
        tool = SearchApiSearch(searchapi_api_key="fake_key")
        schema = tool.args_schema.model_json_schema()
        assert "query" in schema["properties"]
        assert "engine" in schema["properties"]
        assert "num" in schema["properties"]

    @patch("langchain_searchapi._utilities.requests.get")
    def test_run(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic_results": [
                {"title": "Test", "snippet": "Test snippet", "link": "https://test.com"}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        tool = SearchApiSearch(searchapi_api_key="fake_key")
        result = tool.invoke({"query": "test query"})

        assert "organic_results" in result
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["q"] == "test query"
        assert call_kwargs[1]["params"]["engine"] == "google"

    @patch("langchain_searchapi._utilities.requests.get")
    def test_run_with_engine_override(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"news_results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        tool = SearchApiSearch(searchapi_api_key="fake_key")
        tool.invoke({"query": "test", "engine": "google_news"})

        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["engine"] == "google_news"

    @patch("langchain_searchapi._utilities.requests.get")
    def test_run_with_num(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"organic_results": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        tool = SearchApiSearch(searchapi_api_key="fake_key", num=3)
        tool.invoke({"query": "test"})

        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["num"] == 3


class TestSearchApiSearchApiKeyHidden:
    def test_api_key_not_visible_in_repr(self) -> None:
        tool = SearchApiSearch(searchapi_api_key="secret_key_123")
        assert "secret_key_123" not in repr(tool)
