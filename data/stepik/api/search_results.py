from dataclasses import dataclass
from typing import List, Optional

from data.common_api.response import PageRequestParams, Object, PageResponse


@dataclass
class SearchResultsRequestParams(PageRequestParams):
    query: str = ""
    is_popular: bool = True
    type: str = "course"


@dataclass
class SearchResult(Object):
    course: int
    course_title: str
    id: int
    position: int
    score: float
    target_id: int
    target_type: str
    course_owner: int
    course_slug: str
    course_cover: Optional[str] = ""


@dataclass
class SearchResultsResponse(PageResponse):
    search_results: List[SearchResult]

    def get_objects(self) -> List[SearchResult]:
        return self.search_results
