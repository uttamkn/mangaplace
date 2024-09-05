"""
main.py
"""

import asyncio

import typer
from rich.console import Console
from rich.prompt import Prompt

from api.endpoints import search_manga
from ui import search_chapter, select_manga, show_manga_list

app = typer.Typer()
console = Console()


@app.command()
def main(
    search_string: str = typer.Option(
        None, "--search", "-s", help="Search for mangas by title"
    ),
    download_query: str = typer.Option(
        None, "--download", "-d", help="Download a manga by title"
    ),
    info_query: str = typer.Option(
        None, "--info", "-i", help="Get the description of a manga by title"
    ),
):
    """Search, download, or get information of a manga using a single command."""

    if search_string:
        mangas = asyncio.run(search_manga(search_string))

        manga_result = show_manga_list(mangas)
        if not manga_result:
            return

        manga_options, _ = manga_result
        if manga_options:
            # TODO: Show this more nicely
            for index, manga_option in enumerate(manga_options[:10]):
                console.print(f"[blue]{index}[/blue] - [green]{manga_option}[/green]")

    elif download_query:
        mangas = asyncio.run(search_manga(download_query))
        manga_result = show_manga_list(mangas)
        if not manga_result:
            return

        manga_options, index_to_hid = manga_result
        if not manga_options:
            return

        selected_index = select_manga(manga_options)
        if selected_index is None:
            return

        selected_hid = index_to_hid[selected_index]
        console.print(f"[green]You selected:[/green] {manga_options[selected_index]}")

        confirm = Prompt.ask(
            "[cyan]Do you want to proceed with this manga? (yes/no)[/cyan]",
            choices=["yes", "no"],
        )
        if confirm == "yes":
            search_chapter(selected_hid, manga_options[selected_index])
        else:
            console.print("[yellow]Operation cancelled by user.[/yellow]")

    elif info_query:
        mangas = asyncio.run(search_manga(info_query))
        manga_result = show_manga_list(mangas)
        if not manga_result:
            return

        manga_options, index_to_hid = manga_result
        if not manga_options:
            return

        selected_index = select_manga(manga_options)
        if selected_index is None:
            return

        selected_hid = index_to_hid[selected_index]
        console.print(f"[green]Title:[/green] {manga_options[selected_index]}")

        # Show manga description
        for manga in mangas:
            if manga.hid == selected_hid:
                console.print(f"[green]Description:[/green] {manga.desc}")
                break
    else:
        console.print(
            "[red]You must provide either --search, --download, or --info flag.[/red]"
        )


if __name__ == "__main__":
    app()
