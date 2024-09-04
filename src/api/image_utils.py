"""
This module contains utility functions for downloading and combining images.
"""

import asyncio
from io import BytesIO
from typing import List

from aiohttp import ClientSession
from PIL import Image


async def download_image(url: str) -> bytes:
    """
    Download an image from the given URL.
    """
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            raise Exception(
                f"Failed to download image from {url}, status: {response.status}"
            )


async def fetch_and_combine_images(output_pdf: str, image_names: List[str]):
    """
    Fetch and combine images into a PDF file.
    """
    image_urls = [
        f"https://meo3.comick.pictures/{image_name}" for image_name in image_names
    ]
    images = []

    tasks = [download_image(url) for url in image_urls]
    image_bytes = await asyncio.gather(*tasks)

    for image_data in image_bytes:
        image = Image.open(BytesIO(image_data)).convert("RGB")
        images.append(image)

    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])
        print(f"PDF saved as {output_pdf}")
    else:
        print("No images to combine.")
