"""Unit tests for SearchApiAPIWrapper."""

from unittest.mock import MagicMock, patch

import pytest

from langchain_searchapi._utilities import SearchApiAPIWrapper


@pytest.fixture(autouse=True)
def mock_validate(request: pytest.FixtureRequest) -> MagicMock:
    patcher = patch(
        "langchain_searchapi._utilities.SearchApiAPIWrapper.validate_environment"
    )
    mock = patcher.start()
    mock.side_effect = lambda values: values
    request.addfinalizer(patcher.stop)
    return mock


class TestSearchApiAPIWrapper:
    def test_initialization(self) -> None:
        wrapper = SearchApiAPIWrapper(searchapi_api_key="test_key")
        assert wrapper.engine == "google"

    def test_api_key_hidden(self) -> None:
        wrapper = SearchApiAPIWrapper(searchapi_api_key="secret123")
        assert "secret123" not in repr(wrapper)

    @patch("langchain_searchapi._utilities.requests.get")
    def test_raw_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "search_metadata": {"id": "123"},
            "search_parameters": {"q": "test"},
            "organic_results": [{"title": "Test", "snippet": "Snippet"}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        wrapper = SearchApiAPIWrapper(searchapi_api_key="test_key")
        results = wrapper.raw_results("test")

        assert "search_metadata" in results
        assert "organic_results" in results

    @patch("langchain_searchapi._utilities.requests.get")
    def test_results_strips_metadata(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "search_metadata": {"id": "123"},
            "search_parameters": {"q": "test"},
            "pagination": {"next": "..."},
            "organic_results": [{"title": "Test", "snippet": "Snippet"}],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        wrapper = SearchApiAPIWrapper(searchapi_api_key="test_key")
        results = wrapper.results("test")

        assert "search_metadata" not in results
        assert "search_parameters" not in results
        assert "pagination" not in results
        assert "organic_results" in results

    @patch("langchain_searchapi._utilities.requests.get")
    def test_run_returns_snippets(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic_results": [
                {"title": "R1", "snippet": "First snippet"},
                {"title": "R2", "snippet": "Second snippet"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        wrapper = SearchApiAPIWrapper(searchapi_api_key="test_key")
        text = wrapper.run("test")

        assert "First snippet" in text
        assert "Second snippet" in text

    @patch("langchain_searchapi._utilities.requests.get")
    def test_run_answer_box(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answer_box": {"answer": "42"},
            "organic_results": [],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        wrapper = SearchApiAPIWrapper(searchapi_api_key="test_key")
        text = wrapper.run("meaning of life")

        assert "42" in text

    @patch("langchain_searchapi._utilities.requests.get")
    def test_engine_override(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"videos": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        wrapper = SearchApiAPIWrapper(searchapi_api_key="test_key", engine="google")
        wrapper.results("test", engine="youtube")

        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["engine"] == "youtube"

    def test_extract_snippets_empty(self) -> None:
        snippets = SearchApiAPIWrapper._extract_snippets({})
        assert snippets == []

    @patch("langchain_searchapi._utilities.requests.get")
    def test_no_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        wrapper = SearchApiAPIWrapper(searchapi_api_key="test_key")
        text = wrapper.run("test")

        assert text == "No results found."
