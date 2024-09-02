import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import aiohttp
import json
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, TypeAdapter


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
    rating: str
    bayesian_rating: str
    rating_count: int
    follow_count: int
    desc: Optional[str] = None
    status: int
    last_chapter: Optional[int] = None
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

class SearchResults(BaseModel):
    results: List[MangaResult]

# Usage example:
# from pydantic import parse_obj_as
#
# # Assuming 'data' is your JSON data
# search_results = parse_obj_as(SearchResults, data)

app = FastAPI()
logging.basicConfig(level=logging.INFO)

async def fetch_comics(query: str):
    url = f"https://api.comick.fun/v1.0/search?q={query}&tachiyomi=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://comick.fun/",
        "Origin": "https://comick.fun",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logging.info(f"Request URL: {url}")
                logging.info(f"Request headers: {headers}")
                logging.info(f"Response status: {response.status}")
                logging.info(f"Response headers: {response.headers}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 403:
                    error_text = await response.text()
                    logging.error(f"403 Forbidden error. Response body: {error_text}")
                    raise HTTPException(status_code=403, detail=f"Access forbidden. Server response: {error_text}")
                else:
                    error_text = await response.text()
                    logging.error(f"Unexpected status code: {response.status}. Response body: {error_text}")
                    raise HTTPException(status_code=response.status, detail=f"Failed to fetch comics: {error_text}")
        except aiohttp.ClientError as e:
            logging.error(f"Request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to make request: {str(e)}")

async def search_comics(query: str):
    try:
        response = await fetch_comics(query)
        data = json.loads(response)
        adapter = TypeAdapter(MangaResult)
        manga_results = adapter.validate_json(data, many=True)
        titles = [manga_result.title for manga_result in manga_results]
        top_10 = response[:10] if isinstance(response, list) else response
        return {"results": top_10}
    except HTTPException as e:
        return {"error": str(e)}

def get_comic_hids(comics: MangaResult) -> str:
    return comics.hid
