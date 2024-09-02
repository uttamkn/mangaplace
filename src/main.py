import asyncio
from api import fetch_comics, MangaResult, get_select_name

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
    hid = sel_name[id-1].hid

asyncio.run(main())