import asyncio
import logging
from io import BytesIO
from typing import List

import aiohttp
from fastapi import HTTPException
from PIL import Image
from pydantic import TypeAdapter

from models import (
    Chapter,
    ChapterResults,
    Images,
    ListImages,
    MangaResult,
    SearchResults,
    MangaTitle,
)


async def search_manga(query: str) -> List[MangaResult]:
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
                if response.status == 200:
                    data = await response.json()
                    search_results = TypeAdapter(SearchResults).validate_python(
                        {"results": data}
                    )
                    return search_results.results
                elif response.status == 403:
                    error_text = await response.text()
                    logging.error(f"403 Forbidden error. Response body: {error_text}")
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access forbidden. Server response: {error_text}",
                    )
                else:
                    error_text = await response.text()
                    logging.error(
                        f"Unexpected status code: {response.status}. Response body: {error_text}"
                    )
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to fetch comics: {error_text}",
                    )
        except aiohttp.ClientError as e:
            logging.error(f"Request failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to make request: {str(e)}"
            )


async def get_title_list(mangas: List[MangaResult]) -> List[MangaTitle]:
    res: List[MangaTitle] = []
    for manga in mangas:
        res.append(MangaTitle(hid=manga.hid, title=manga.title))
    return res


async def get_chapter_list(hid: str) -> List[Chapter]:
    url = f"https://api.comick.fun/comic/{hid}/chapters?lang=en&limit=99999&tachiyomi=true"
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
                if response.status == 200:
                    data = await response.json()
                    formatted_data = TypeAdapter(ChapterResults).validate_python(data)
                    return formatted_data.chapters
                elif response.status == 403:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access forbidden. Server response: {error_text}",
                    )
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to fetch chapters: {error_text}",
                    )
        except aiohttp.ClientError as e:
            logging.error(f"Request failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to make request: {str(e)}"
            )


async def get_image_list(hid: str) -> List[Images]:
    url = f"https://api.comick.fun/chapter/{hid}/get_images?tachiyomi=true"
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
                if response.status == 200:
                    data = await response.json()
                    search_results = TypeAdapter(ListImages).validate_python(
                        {"images": data}
                    )
                    return search_results.images
                elif response.status == 403:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access forbidden. Server response: {error_text}",
                    )
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to fetch images: {error_text}",
                    )
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to make request: {str(e)}"
            )


async def download_image(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        else:
            raise Exception(
                f"Failed to download image from {url}, status: {response.status}"
            )


async def fetch_and_combine_images(output_pdf: str, image_names: List[str]):
    image_urls = [
        f"https://meo3.comick.pictures/{image_name}" for image_name in image_names
    ]

    images = []

    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url) for url in image_urls]
        image_bytes = await asyncio.gather(*tasks)

        for image_data in image_bytes:
            image = Image.open(BytesIO(image_data)).convert("RGB")
            images.append(image)

    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])
        print(f"PDF saved as {output_pdf}")
    else:
        print("No images to combine.")
