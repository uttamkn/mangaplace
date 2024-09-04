import asyncio

from iterfzf import iterfzf
from rich.console import Console

from api.endpoints import search_manga

console = Console()


def search(manga_name: str):
    """Search for manga by title and select one to download using fzf."""
    console.print(f"[cyan]Searching for mangas with title:[/cyan] '{manga_name}'")
    mangas = asyncio.run(search_manga(manga_name))

    if not mangas:
        console.print("[yellow]No results found.[/yellow]")
        return

    index_to_hid = {}
    manga_options = []
    for index, manga in enumerate(mangas):
        index_to_hid[index] = manga.hid
        manga_options.append(f"{index} - {manga.title}")

    selected = iterfzf(manga_options, multi=True)
    console.print(f"[green]You selected chapter:[/green] {selected}")

    # if not selected:
    #     console.print("[yellow]No chapter selected.[/yellow]")
    #     return
    # # selected_title - selected.split(" - ")[1].strip()
    # selected_index = int(selected.split(" - ", maxsplit=1)[0].strip())
    # selected_hid = index_to_hid[selected_index]
    #
    # console.print(
    #     f"[green]You selected chapter:[/green] {chapter_options[selected_index]}"
    # )


search("one piece")
