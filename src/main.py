import asyncio

from api import (
    MangaResult,
    fetch_and_combine_images,
    fetch_chapters,
    fetch_comics,
    fetch_images,
    get_select_name,
)


async def main():
    print("hello world")
    print("give a anime name so that i can get you the pdf")
    anime_name = input("anime name: ")
    res = await fetch_comics(anime_name)
    sel_name = await get_select_name(res)
    i = 0
    for result in sel_name:
        print(f"{i+1} {result.title} - {result.hid}")
        i += 1
    print("give the id no of the anime you want chapters for")
    id = int(input("anime id: "))
    print(f"you have chosen {sel_name[id-1].title}")
    hid = sel_name[id - 1].hid
    print(hid)
    print("the chapters available for that are as follows")
    chapters = await fetch_chapters(hid)
    i = 0
    for chapter in chapters:
        print(f"{i+1} {chapter.title}")
        i += 1
    print("select the chapter for which you want images")
    chapid = int(input("chapter id: "))
    chapter_hid = chapters[chapid - 1].hid
    print(chapter_hid)
    imagesList = await fetch_images(chapter_hid)
    image_name = []
    for image in imagesList:
        print(image.b2key)
        image_name.append(image.b2key)
    await fetch_and_combine_images("output.pdf", image_name)


asyncio.run(main())
