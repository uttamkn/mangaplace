"""
 This file contains the functions that interact with the api.comick.fun API.
"""

import logging
from typing import List

from aiohttp import ClientError, ClientSession
from fastapi import HTTPException
from pydantic import TypeAdapter

from config import BASE_API_URL, HEADERS
from models import (
    Chapter,
    ChapterResults,
    Images,
    ListImages,
    MangaResult,
    SearchResults,
)


async def fetch_data(url: str):
    """
    Fetch data from the given URL using the provided session.
    """
    async with ClientSession() as session:
        try:
            async with session.get(url, headers=HEADERS) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                if response.status == 403:
                    raise HTTPException(
                        status_code=403, detail=f"Access forbidden: {error_text}"
                    )
                raise HTTPException(
                    status_code=response.status, detail=f"Failed to fetch: {error_text}"
                )
        except ClientError as e:
            logging.error(f"Request failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to make request: {str(e)}"
            )


async def search_manga(query: str) -> List[MangaResult]:
    """
    Search for manga using the given query.
    """
    url = f"{BASE_API_URL}/v1.0/search?q={query}&tachiyomi=true"
    data = await fetch_data(url)
    search_results = TypeAdapter(SearchResults).validate_python({"results": data})
    return search_results.results


async def get_chapter_list(hid: str) -> List[Chapter]:
    """
    Get the list of chapters for the given manga HID.
    """
    url = f"{BASE_API_URL}/comic/{hid}/chapters?lang=en&limit=99999&tachiyomi=true"
    data = await fetch_data(url)
    formatted_data = TypeAdapter(ChapterResults).validate_python(data)
    return formatted_data.chapters


async def get_image_list(hid: str) -> List[Images]:
    """
    Get the list of images for the given chapter HID.
    """
    url = f"{BASE_API_URL}/chapter/{hid}/get_images?tachiyomi=true"
    data = await fetch_data(url)
    search_results = TypeAdapter(ListImages).validate_python({"images": data})
    return search_results.images
