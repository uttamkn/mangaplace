import typer
import asyncio
import subprocess
from rich.console import Console
from rich.table import Table
from api import search_manga, get_chapter_list, get_image_list, fetch_and_combine_images

app = typer.Typer()
console = Console()


@app.command()
def search(query: str):
    """Search for manga by title and select one to download using fzf."""
    mangas = asyncio.run(search_manga(query))
    if not mangas:
        console.print("[yellow]No results found.[/yellow]")
        return
    manga_options = [f"{manga.hid} - {manga.title}" for manga in mangas]
    fzf_process = subprocess.Popen(
        ["fzf"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    manga_input = "\n".join(manga_options)
    selected, _ = fzf_process.communicate(input=manga_input)
    if not selected:
        console.print("[yellow]No manga selected.[/yellow]")
        return
    selected_hid = selected.split(" - ")[0].strip()
    search_chapter(selected_hid)

def search_chapter(hid: str):
    """Search for chapter by number and select one to download using fzf."""
    chapters = asyncio.run(get_chapter_list(hid))
    if not chapters:
        console.print("[yellow]No chapters found for this manga.[/yellow]")
        return
    chapter_options = [f"{chapter.hid} - {chapter.title}" for chapter in chapters]
    fzf_process = subprocess.Popen(
        ["fzf"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    manga_input = "\n".join(chapter_options)
    selected, _ = fzf_process.communicate(input=manga_input)
    if not selected:
        console.print("[yellow]No manga selected.[/yellow]")
        return
    selected_hid = selected.split(" - ")[0].strip()
    asyncio.run(download(selected_hid))

async def download(hid: str):
    console.print(f"Downloading chapter...")
    imagesList = await get_image_list(hid)
    image_name = []
    for image in imagesList:
        print(image.b2key)
        image_name.append(image.b2key)
    await fetch_and_combine_images("output.pdf", image_name)



if __name__ == "__main__":
    app()

