"""
This module contains utility functions for downloading and combining images.
"""

import asyncio
from io import BytesIO
from typing import List

import aiohttp
from PIL import Image
from rich.progress import Progress, TaskID

from config import IMAGE_BASE_URL


async def download_image(session: aiohttp.ClientSession, url: str):
    """
    Download an image from the given URL asynchronously.
    """
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        return None


async def fetch_and_combine_images(
    output_pdf: str,
    image_names: List[str],
    chapter_progress: Progress,
    chapter_task_id: TaskID,
):
    """
    Fetch and combine images into a PDF file asynchronously using aiohttp.
    """
    image_urls = [f"{IMAGE_BASE_URL}/{image_name}" for image_name in image_names]
    images = []

    chapter_progress.update(chapter_task_id, description="Downloading images")
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url) for url in image_urls]

        semaphore = asyncio.Semaphore(10)

        async def limited_download(task):
            async with semaphore:
                return await task

        image_bytes = await asyncio.gather(*[limited_download(task) for task in tasks])

    for image_data in image_bytes:
        if image_data:
            image = Image.open(BytesIO(image_data)).convert("RGB")
            images.append(image)
    chapter_progress.update(chapter_task_id, description="Combining images into PDF")
    if images:
        save_images_as_pdf(images, output_pdf)
    else:
        print("No images to combine.")


def save_images_as_pdf(images, output_pdf):
    """
    Function to save images as a PDF. This is run in a separate thread using ThreadPoolExecutor.
    """
    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])
