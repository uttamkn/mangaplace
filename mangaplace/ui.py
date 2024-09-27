"""This module contains all the UI functions."""

import asyncio

from endpoints import get_chapter_list, get_image_list
from image_utils import fetch_and_combine_images
from iterfzf import iterfzf
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from utils import get_path

console = Console()


def show_manga_list(mangas):
    """Returns a list of mangas with index."""
    if not mangas:
        console.print("[yellow]No results found.[/yellow]")
        return None

    index_to_hid = {}
    manga_options = []
    for index, manga in enumerate(mangas):
        index_to_hid[index] = manga.hid
        manga_options.append(f"{index} - {manga.title}")

    return manga_options, index_to_hid


def select_manga(manga_options):
    """Use fzf to allow the user to select a manga."""
    selected: list[str] = iterfzf(manga_options)  # type: ignore
    if not selected:
        console.print("[yellow]No manga selected.[/yellow]")
        return None
    selected_index = int(selected[0].split(" - ", maxsplit=1)[0].strip())
    return selected_index


def search_chapter(hid: str, manga_name: str):
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

    selected = iterfzf(chapter_options, multi=True)  # type: ignore

    if not selected:
        console.print("[yellow]No chapter selected.[/yellow]")
        return

    selected_indices = [int(s.split(" - ", maxsplit=1)[0].strip()) for s in selected]  # type: ignore
    selected_hids = [index_to_hid[i] for i in selected_indices]

    for idx in selected_indices:
        console.print(f"[green]You selected chapter:[/green] {chapter_options[idx]}")

    confirm = Prompt.ask(
        "[cyan]Do you want to proceed with downloading the selected chapter(s)? (yes/no)[/cyan]",
        choices=["yes", "no"],
    )

    if confirm == "yes":
        for selected_index, selected_hid in zip(selected_indices, selected_hids):
            asyncio.run(download_chapter(selected_hid, manga_name, selected_index))
    else:
        console.print("[yellow]Operation cancelled by user.[/yellow]")


async def download_chapter(hid: str, pdf_name: str, index: int):
    """UI for downloading the chapter."""
    console.print(f"[cyan]Downloading chapter...[/cyan]")
    download_dir_path = await get_path()
    pdf_path = download_dir_path + pdf_name + "_" + str(index + 1) + ".pdf"

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
            await fetch_and_combine_images(pdf_path, image_names)
            progress.update(task, completed=True)
            console.print(f"[green]Download complete! Saved as {pdf_name}[/green]")
        else:
            console.print("[red]No images found to download.[/red]")
            return
