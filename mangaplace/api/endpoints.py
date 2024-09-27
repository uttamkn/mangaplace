"""
 This file contains the functions that interact with the api.comick.fun API.
"""

from typing import List
from aiohttp import ClientError, ClientSession
from pydantic import ValidationError
from mangaplace.config import BASE_API_URL, HEADERS
from mangaplace.models import Chapter, ChapterResults, Images, ListImages, MangaResult, SearchResults


async def fetch_data(url: str):
    """
    Fetch data from the given URL using aiohttp's session.
    """
    async with ClientSession() as session:
        try:
            async with session.get(url, headers=HEADERS) as response:
                if response.status == 200:
                    return await response.json()
                error_text = await response.text()
                if response.status == 403:
                    raise PermissionError(f"Access forbidden: {error_text}")
                raise ValueError(f"Failed to fetch: {error_text} (status: {response.status})")
        except ClientError as e:
            raise ConnectionError(f"Request failed: {str(e)}")


async def search_manga(query: str) -> List[MangaResult]:
    """
    Search for manga using the given query.
    """
    url = f"{BASE_API_URL}/v1.0/search?q={query}&tachiyomi=true"
    data = await fetch_data(url)
    try:
        search_results = SearchResults.model_validate({"results": data})
        return search_results.results
    except ValidationError as e:
        raise ValueError(f"Data validation failed: {e}")


async def get_chapter_list(hid: str) -> List[Chapter]:
    """
    Get the list of chapters for the given manga HID.
    """
    url = f"{BASE_API_URL}/comic/{hid}/chapters?lang=en&limit=99999&tachiyomi=true"
    data = await fetch_data(url)
    try:
        formatted_data = ChapterResults.model_validate(data)
        return formatted_data.chapters
    except ValidationError as e:
        raise ValueError(f"Data validation failed: {e}")


async def get_image_list(hid: str) -> List[Images]:
    """
    Get the list of images for the given chapter HID.
    """
    url = f"{BASE_API_URL}/chapter/{hid}/get_images?tachiyomi=true"
    data = await fetch_data(url)
    try:
        search_results = ListImages.model_validate({"images": data})
        return search_results.images
    except ValidationError as e:
        raise ValueError(f"Data validation failed: {e}")
