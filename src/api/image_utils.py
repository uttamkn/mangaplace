"""
This module contains utility functions for downloading and combining images.
"""

import asyncio
from io import BytesIO
from typing import List

import aiohttp
from PIL import Image


async def download_image(session: aiohttp.ClientSession, url: str):
    """
    Download an image from the given URL asynchronously.
    """
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        return None


async def fetch_and_combine_images(output_pdf: str, image_names: List[str]):
    """
    Fetch and combine images into a PDF file asynchronously using aiohttp.
    """
    image_urls = [
        f"https://meo3.comick.pictures/{image_name}" for image_name in image_names
    ]
    images = []

    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url) for url in image_urls]

        # Limit the number of concurrent downloads to 10 (increase if you want)
        semaphore = asyncio.Semaphore(10)

        async def limited_download(task):
            async with semaphore:
                return await task

        image_bytes = await asyncio.gather(*[limited_download(task) for task in tasks])

    for image_data in image_bytes:
        if image_data:
            image = Image.open(BytesIO(image_data)).convert("RGB")
            images.append(image)

    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])
        print(f"PDF saved as {output_pdf}")
    else:
        print("No images to combine.")
