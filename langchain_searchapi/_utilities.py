"""Wrapper around the SearchApi.io API."""

import json
from typing import Any, Dict, List, Literal, Optional

import aiohttp
import requests
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"

ENGINE_TYPE = Literal[
    "google",
    "google_news",
    "google_shopping",
    "google_jobs",
    "google_scholar",
    "youtube",
    "bing",
    "baidu",
]

METADATA_KEYS = {"search_metadata", "search_parameters", "pagination"}


class SearchApiAPIWrapper(BaseModel):
    """Wrapper for SearchApi.io search API."""

    searchapi_api_key: SecretStr
    engine: ENGINE_TYPE = "google"

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        searchapi_api_key = get_from_dict_or_env(
            values, "searchapi_api_key", "SEARCHAPI_API_KEY"
        )
        values["searchapi_api_key"] = searchapi_api_key
        return values

    def _build_request(
        self,
        query: str,
        engine: Optional[str] = None,
        num: Optional[int] = None,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
        location: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "engine": engine or self.engine,
            "q": query,
        }
        if num is not None:
            params["num"] = num
        if gl is not None:
            params["gl"] = gl
        if hl is not None:
            params["hl"] = hl
        if location is not None:
            params["location"] = location
        params.update({k: v for k, v in kwargs.items() if v is not None})

        return {
            "url": SEARCHAPI_BASE_URL,
            "headers": {
                "Authorization": f"Bearer {self.searchapi_api_key.get_secret_value()}",
            },
            "params": params,
        }

    def raw_results(
        self,
        query: str,
        engine: Optional[str] = None,
        num: Optional[int] = None,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
        location: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get raw JSON results from SearchApi."""
        req = self._build_request(
            query, engine=engine, num=num, gl=gl, hl=hl, location=location, **kwargs
        )
        response = requests.get(
            url=req["url"],
            params=req["params"],
            headers=req["headers"],
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    async def raw_results_async(
        self,
        query: str,
        engine: Optional[str] = None,
        num: Optional[int] = None,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
        location: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get raw JSON results from SearchApi asynchronously."""
        req = self._build_request(
            query, engine=engine, num=num, gl=gl, hl=hl, location=location, **kwargs
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=req["url"],
                params=req["params"],
                headers=req["headers"],
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                text = await response.text()
                return json.loads(text)

    def results(
        self,
        query: str,
        engine: Optional[str] = None,
        num: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get cleaned results (metadata stripped)."""
        raw = self.raw_results(query, engine=engine, num=num, **kwargs)
        return {k: v for k, v in raw.items() if k not in METADATA_KEYS}

    async def aresults(
        self,
        query: str,
        engine: Optional[str] = None,
        num: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get cleaned results asynchronously."""
        raw = await self.raw_results_async(query, engine=engine, num=num, **kwargs)
        return {k: v for k, v in raw.items() if k not in METADATA_KEYS}

    @staticmethod
    def _extract_snippets(results: Dict[str, Any]) -> List[str]:
        """Extract text snippets from engine-specific result keys."""
        snippets: List[str] = []

        if "answer_box" in results:
            ab = results["answer_box"]
            if "answer" in ab:
                snippets.append(ab["answer"])
            elif "snippet" in ab:
                snippets.append(ab["snippet"])

        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            if "description" in kg:
                snippets.append(kg["description"])

        if "organic_results" in results:
            for r in results["organic_results"]:
                if "snippet" in r:
                    snippets.append(r["snippet"])

        if "news_results" in results:
            for r in results["news_results"]:
                if "snippet" in r:
                    snippets.append(r["snippet"])

        if "shopping_results" in results:
            for r in results["shopping_results"]:
                parts = []
                if "title" in r:
                    parts.append(r["title"])
                if "price" in r:
                    parts.append(r["price"])
                if parts:
                    snippets.append(" - ".join(parts))

        if "jobs" in results:
            for r in results["jobs"]:
                if "description" in r:
                    snippets.append(r["description"])

        if "videos" in results:
            for r in results["videos"]:
                if "title" in r:
                    link = r.get("link", "")
                    snippets.append(f'{r["title"]} {link}'.strip())

        return snippets

    def run(self, query: str, **kwargs: Any) -> str:
        """Run a search and return concatenated snippet text."""
        results = self.results(query, **kwargs)
        snippets = self._extract_snippets(results)
        return "\n\n".join(snippets) if snippets else "No results found."

    async def arun(self, query: str, **kwargs: Any) -> str:
        """Run a search asynchronously and return concatenated snippet text."""
        results = await self.aresults(query, **kwargs)
        snippets = self._extract_snippets(results)
        return "\n\n".join(snippets) if snippets else "No results found."
