"""SearchApi.io retriever for LangChain RAG chains."""

from typing import Any, Dict, List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field

from langchain_searchapi._utilities import SearchApiAPIWrapper


class SearchApiRetriever(BaseRetriever):
    """Retriever that uses SearchApi.io to fetch documents.

    Returns search results as LangChain Documents, suitable for
    RAG pipelines and chains that consume retrievers.
    """

    api_wrapper: SearchApiAPIWrapper = Field(default=None, exclude=True)  # type: ignore[assignment]
    engine: str = "google"
    num: int = 5
    gl: Optional[str] = None
    hl: Optional[str] = None
    location: Optional[str] = None
    searchapi_api_key: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    def __init__(self, **kwargs: Any) -> None:
        api_key = kwargs.pop("searchapi_api_key", None)
        engine = kwargs.get("engine", "google")

        super().__init__(**kwargs)

        wrapper_kwargs: Dict[str, Any] = {"engine": engine}
        if api_key:
            wrapper_kwargs["searchapi_api_key"] = api_key

        self.api_wrapper = SearchApiAPIWrapper(**wrapper_kwargs)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """Retrieve documents from SearchApi."""
        results = self.api_wrapper.results(
            query, num=self.num, gl=self.gl, hl=self.hl, location=self.location
        )
        return self._results_to_documents(results)

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """Retrieve documents from SearchApi asynchronously."""
        results = await self.api_wrapper.aresults(
            query, num=self.num, gl=self.gl, hl=self.hl, location=self.location
        )
        return self._results_to_documents(results)

    @staticmethod
    def _results_to_documents(results: Dict[str, Any]) -> List[Document]:
        """Convert SearchApi results to LangChain Documents."""
        docs: List[Document] = []

        for result in results.get("organic_results", []):
            content = result.get("snippet", "")
            metadata = {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "source": "searchapi",
            }
            if result.get("position"):
                metadata["position"] = result["position"]
            if content:
                docs.append(Document(page_content=content, metadata=metadata))

        for result in results.get("news_results", []):
            content = result.get("snippet", "")
            metadata = {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "source": "searchapi",
                "type": "news",
            }
            if result.get("date"):
                metadata["date"] = result["date"]
            if content:
                docs.append(Document(page_content=content, metadata=metadata))

        for result in results.get("videos", []):
            title = result.get("title", "")
            metadata = {
                "title": title,
                "link": result.get("link", ""),
                "source": "searchapi",
                "type": "video",
            }
            if title:
                docs.append(Document(page_content=title, metadata=metadata))

        return docs
