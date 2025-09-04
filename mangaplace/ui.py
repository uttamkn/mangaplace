"""This module contains all the UI functions."""

import asyncio

from iterfzf import iterfzf
from rich.console import Console
from rich.live import Live
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TextColumn
from rich.prompt import Prompt
from mangaplace.endpoints import get_chapter_list, get_image_list
from mangaplace.image_utils import fetch_and_combine_images
from mangaplace.utils import get_path

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


def show_top_manga_list(mangas):
    """Returns a list of top mangas with index."""
    if not mangas:
        console.print("[yellow]No results found.[/yellow]")
        return None

    manga_options = []
    for index, manga in enumerate(mangas):
        manga_options.append(f"{index} - {manga.title}")

    return manga_options


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

    console.print("[green]You selected:[/green]")
    for idx in selected_indices:
        console.print(f"{chapter_options[idx]}")

    confirm = Prompt.ask(
        "[cyan]Do you want to proceed with downloading the selected chapter(s)?[/cyan]",
        choices=["yes", "no"],
    )

    if confirm == "yes":
        asyncio.run(
            download_multiple_chapters_concurrently(
                selected_hids, manga_name, selected_indices
            )
        )
    else:
        console.print("[yellow]Operation cancelled by user.[/yellow]")


async def download_multiple_chapters_concurrently(
    selected_hids: list, manga_name: str, selected_indices: list
):
    """Download multiple chapters concurrently."""

    download_dir_path = await get_path()

    chapter_progress = Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        console=console,
    )

    tasks = []
    for selected_hid, selected_index in zip(selected_hids, selected_indices):
        chapter_task_id = chapter_progress.add_task(
            f"Chapter {selected_index + 1}", total=1
        )
        tasks.append(
            download_chapter(
                selected_hid,
                manga_name,
                selected_index,
                download_dir_path,
                chapter_progress,
                chapter_task_id,
            )
        )

    with Live(chapter_progress, refresh_per_second=10, console=console):
        await asyncio.gather(*tasks)


async def download_chapter(
    hid: str,
    pdf_name: str,
    index: int,
    download_dir_path: str,
    chapter_progress: Progress,
    chapter_task_id: TaskID,
):
    """Download a chapter and combine images into a PDF."""
    pdf_path = f"{download_dir_path}{pdf_name}_{index + 1}.pdf"

    images_list = await get_image_list(hid)
    image_names = [image.b2key for image in images_list]

    if image_names:
        await fetch_and_combine_images(
            pdf_path, image_names, chapter_progress, chapter_task_id
        )

        chapter_progress.update(chapter_task_id, completed=True)

        console.print(
            f"[green]Chapter {index + 1} downloaded successfully![/green] Saved as {pdf_path}"
        )
    else:
        console.print(
            f"[red]No images found for Chapter {index + 1}. Skipping...[/red]"
        )
        chapter_progress.update(chapter_task_id, visible=False)
