import typer
import asyncio
import subprocess
from rich.console import Console
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
    index_to_hid = {}
    manga_options = []
    for index, manga in enumerate(mangas):
        index_to_hid[index] = manga.hid
        manga_options.append(f"{index} - {manga.title}")
    try:
        fzf_process = subprocess.Popen(
            ["fzf"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        manga_input = "\n".join(manga_options)
        selected, _ = fzf_process.communicate(input=manga_input)
    except Exception as e:
        console.print(f"[red]Error running fzf: {e}[/red]")
        return

    if not selected:
        console.print("[yellow]No manga selected.[/yellow]")
        return

    selected_index = int(selected.split(" - ")[0].strip())
    selected_hid = index_to_hid[selected_index]
    search_chapter(selected_hid)

def search_chapter(hid: str):
    """Search for chapter by number and select one to download using fzf."""
    chapters = asyncio.run(get_chapter_list(hid))
    if not chapters:
        console.print("[yellow]No results found.[/yellow]")
        return
    index_to_hid = {}
    chapter_options = []
    for index, chapter in enumerate(chapters):
        index_to_hid[index] = chapter.hid
        chapter_options.append(f"{index} - {chapter.title}")
    try:
        fzf_process = subprocess.Popen(
            ["fzf"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        chapter_input = "\n".join(chapter_options)
        selected, _ = fzf_process.communicate(input=chapter_input)
    except Exception as e:
        console.print(f"[red]Error running fzf: {e}[/red]")
        return

    if not selected:
        console.print("[yellow]No chapter selected.[/yellow]")
        return

    selected_index = int(selected.split(" - ")[0].strip())
    selected_hid = index_to_hid[selected_index]
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

