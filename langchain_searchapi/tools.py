"""SearchApi.io tool for LangChain agents."""

from typing import Any, Dict, Literal, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

from langchain_searchapi._utilities import SearchApiAPIWrapper


class SearchApiSearchInput(BaseModel):
    """Input schema for SearchApi search tool."""

    query: str = Field(description="The search query to execute.")
    engine: Optional[str] = Field(
        default=None,
        description=(
            "Search engine to use. Options: google, google_news, google_shopping, "
            "google_jobs, google_scholar, youtube, bing, baidu. "
            "Defaults to the engine configured at initialization."
        ),
    )
    num: Optional[int] = Field(
        default=None, description="Number of results to return."
    )

    model_config = ConfigDict(extra="allow")


class SearchApiSearch(BaseTool):
    """Tool that queries the SearchApi.io search API.

    Supports multiple search engines (Google, Bing, Baidu, YouTube, etc.)
    via the `engine` parameter.
    """

    name: str = "searchapi"
    description: str = (
        "A search engine API provided by SearchApi.io. "
        "Supports multiple engines: Google, Google News, Google Shopping, "
        "Google Jobs, YouTube, Bing, and Baidu. "
        "Use this when you need to find information on the internet."
    )
    args_schema: Type[BaseModel] = SearchApiSearchInput
    handle_tool_error: bool = True

    api_wrapper: SearchApiAPIWrapper = Field(default=None, exclude=True)  # type: ignore[assignment]

    engine: Optional[
        Literal[
            "google",
            "google_news",
            "google_shopping",
            "google_jobs",
            "google_scholar",
            "youtube",
            "bing",
            "baidu",
        ]
    ] = "google"
    num: Optional[int] = None
    gl: Optional[str] = None
    hl: Optional[str] = None
    location: Optional[str] = None

    searchapi_api_key: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    def __init__(self, **kwargs: Any) -> None:
        api_key = kwargs.pop("searchapi_api_key", None)
        engine = kwargs.get("engine", "google")

        super().__init__(**kwargs)

        wrapper_kwargs: Dict[str, Any] = {"engine": engine or "google"}
        if api_key:
            wrapper_kwargs["searchapi_api_key"] = api_key

        self.api_wrapper = SearchApiAPIWrapper(**wrapper_kwargs)

    def _run(
        self,
        query: str,
        engine: Optional[str] = None,
        num: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a search and return structured results."""
        return self.api_wrapper.results(
            query,
            engine=engine,
            num=num or self.num,
            gl=self.gl,
            hl=self.hl,
            location=self.location,
            **kwargs,
        )

    async def _arun(
        self,
        query: str,
        engine: Optional[str] = None,
        num: Optional[int] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a search asynchronously and return structured results."""
        return await self.api_wrapper.aresults(
            query,
            engine=engine,
            num=num or self.num,
            gl=self.gl,
            hl=self.hl,
            location=self.location,
            **kwargs,
        )
