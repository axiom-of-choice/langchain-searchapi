from importlib import metadata
from typing import List

from langchain_searchapi._utilities import SearchApiAPIWrapper
from langchain_searchapi.retrievers import SearchApiRetriever
from langchain_searchapi.tools import SearchApiSearch

try:
    __version__: str = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = ""
del metadata

__all__: List[str] = [
    "SearchApiAPIWrapper",
    "SearchApiRetriever",
    "SearchApiSearch",
    "__version__",
]
