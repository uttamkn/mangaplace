from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel


class MuComics(BaseModel):
    year: Optional[int] = None


class MdTitle(BaseModel):
    title: str


class MdCover(BaseModel):
    w: int
    h: int
    b2key: str


class MangaResult(BaseModel):
    id: int
    hid: str
    slug: str
    title: str
    country: str
    rating: Optional[str] = None
    bayesian_rating: Optional[str] = None
    rating_count: int
    follow_count: int
    desc: Optional[str] = None
    status: int
    last_chapter: Optional[Union[int, float]] = None
    translation_completed: Optional[bool] = None
    view_count: int
    content_rating: str
    demographic: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    genres: List[int]
    created_at: datetime
    user_follow_count: int
    year: Optional[int] = None
    mu_comics: Optional[MuComics] = None
    md_titles: List[MdTitle]
    md_covers: List[MdCover]
    highlight: Optional[str] = None
    cover_url: str


class SelectNameOfManga(BaseModel):
    hid: str
    title: str


class SearchResults(BaseModel):
    results: List[MangaResult]


class Chapter(BaseModel):
    id: int
    hid: str
    title: Optional[str] = None
    lang: str


class ChapterResults(BaseModel):
    chapters: List[Chapter]
    total: int
    limit: int


class Images(BaseModel):
    h: int
    w: int
    b2key: str


class ListImages(BaseModel):
    images: List[Images]
