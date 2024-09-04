"""
main.py
"""

import asyncio
import subprocess

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from api.endpoints import get_chapter_list, get_image_list, search_manga
from api.image_utils import fetch_and_combine_images

app = typer.Typer()
console = Console()


@app.command()
def search(query: str):
    """Search for manga by title and select one to download using fzf."""
    console.print(f"[cyan]Searching for mangas with title:[/cyan] '{query}'")
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
        with subprocess.Popen(
            ["fzf"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as fzf_process:
            manga_input = "\n".join(manga_options)
            selected, _ = fzf_process.communicate(input=manga_input)
    except Exception as e:
        console.print(f"[red]Error running fzf: {e}[/red]")
        return

    if not selected:
        console.print("[yellow]No manga selected.[/yellow]")
        return

    selected_index = int(selected.split(" - ", maxsplit=1)[0].strip())
    selected_hid = index_to_hid[selected_index]

    console.print(f"[green]You selected:[/green] {manga_options[selected_index]}")

    confirm = Prompt.ask(
        "[cyan]Do you want to proceed with this manga? (yes/no)[/cyan]",
        choices=["yes", "no"],
    )
    if confirm == "yes":
        search_chapter(selected_hid)
    else:
        console.print("[yellow]Operation cancelled by user.[/yellow]")


def search_chapter(hid: str):
    """Search for chapter by number and select one to download using fzf."""
    console.print("[cyan]Fetching chapters...[/cyan]")
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
            text=True,
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

    console.print(
        f"[green]You selected chapter:[/green] {chapter_options[selected_index]}"
    )

    confirm = Prompt.ask(
        "[cyan]Do you want to proceed with this chapter? (yes/no)[/cyan]",
        choices=["yes", "no"],
    )
    if confirm == "yes":
        asyncio.run(download(selected_hid))
    else:
        console.print("[yellow]Operation cancelled by user.[/yellow]")


async def download(hid: str):
    console.print(f"[cyan]Downloading chapter...[/cyan]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(description="Fetching images", total=None)

        images_list = await get_image_list(hid)
        image_names = [image.b2key for image in images_list]

        progress.update(task, description="Combining images into PDF", total=None)

        if image_names:
            await fetch_and_combine_images("output.pdf", image_names)
            progress.update(task, completed=True)
            console.print(f"[green]Download complete! Saved as output.pdf[/green]")
        else:
            console.print("[red]No images found to download.[/red]")
            return


if __name__ == "__main__":
    app()
