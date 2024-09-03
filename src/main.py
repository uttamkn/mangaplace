import asyncio

from api import (
    fetch_and_combine_images,
    search_manga,
    get_image_list,
    get_title_list,
    get_chapter_list
)


async def main():
    print("hello world")
    print("give a anime name so that i can get you the pdf")
    anime_name = input("anime name: ")
    res = await search_manga(anime_name)
    title_list = await get_title_list(res)
    i = 0
    for result in title_list:
        print(f"{i+1} {result.title} - {result.hid}")
        i += 1
    print("give the id no of the anime you want chapters for")
    manga_id = int(input("anime id: "))
    print(f"you have chosen {title_list[manga_id - 1].title}")
    print(f"description: {title_list[manga_id - 1].desc}")
    hid = title_list[manga_id - 1].hid
    print(hid)
    print("the chapters available for that are as follows")
    chapters = await get_chapter_list(hid)
    i = 0
    for chapter in chapters:
        print(f"{i+1} {chapter.title}")
        i += 1
    print("select the chapter for which you want images")
    chapid = int(input("chapter id: "))
    chapter_hid = chapters[chapid - 1].hid
    print(chapter_hid)
    imagesList = await get_image_list(chapter_hid)
    image_name = []
    for image in imagesList:
        print(image.b2key)
        image_name.append(image.b2key)
    await fetch_and_combine_images("output.pdf", image_name)


asyncio.run(main())
