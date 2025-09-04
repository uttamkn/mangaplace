"""
main.py
"""

import os
import asyncio

import typer
import certifi
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from mangaplace.endpoints import get_top_list, search_manga
from mangaplace.ui import (
    search_chapter,
    select_manga,
    show_manga_list,
    show_top_manga_list,
)

os.environ["SSL_CERT_FILE"] = certifi.where()

app = typer.Typer()
console = Console()


def handle_error(e: Exception):
    """Handles and displays errors."""
    console.print(
        Panel(f"[bold red]An error occurred:[/bold red] {e}", border_style="red")
    )


def display_manga_results(manga_result):
    """Helper function to display manga search results."""
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Index", style="dim", width=6)
    table.add_column("Results", style="green")

    for index, manga_option in enumerate(manga_result[:10]):
        table.add_row(str(index + 1), manga_option[4:])

    console.print(table)


@app.command()
def search(search_string: str):
    """Search for manga by title"""
    try:
        mangas = asyncio.run(search_manga(search_string))
    except (ConnectionError, PermissionError, ValueError) as e:
        handle_error(e)
        return

    manga_result = show_manga_list(mangas)
    if not manga_result:
        console.print("[red]No manga found.[/red]")
        return

    display_manga_results(manga_result[0])


@app.command()
def download(download_query: str):
    """Download a manga by title"""
    try:
        mangas = asyncio.run(search_manga(download_query))
    except (ConnectionError, PermissionError, ValueError) as e:
        handle_error(e)
        return

    manga_result = show_manga_list(mangas)
    if not manga_result:
        console.print("[red]No manga found.[/red]")
        return

    manga_options, index_to_hid = manga_result
    selected_index = select_manga(manga_options)
    if selected_index is None:
        console.print("[yellow]Operation cancelled by user.[/yellow]")
        return

    selected_hid = index_to_hid[selected_index]
    console.print(f"[green]You selected:[/green] {manga_options[selected_index]}")

    confirm = Prompt.ask(
        "[cyan]Do you want to proceed with this manga?[/cyan]",
        choices=["yes", "no"],
    )
    if confirm == "yes":
        search_chapter(selected_hid, manga_options[selected_index])
    else:
        console.print("[yellow]Operation cancelled by user.[/yellow]")


@app.command()
def info(info_query: str):
    """Get information of a manga by title"""
    try:
        mangas = asyncio.run(search_manga(info_query))
    except (ConnectionError, PermissionError, ValueError) as e:
        handle_error(e)
        return

    manga_result = show_manga_list(mangas)
    if not manga_result:
        console.print("[red]No manga found.[/red]")
        return

    manga_options, index_to_hid = manga_result
    selected_index = select_manga(manga_options)
    if selected_index is None:
        console.print("[yellow]Operation cancelled by user.[/yellow]")
        return

    selected_hid = index_to_hid[selected_index]
    console.print(f"[green]Title:[/green] {manga_options[selected_index][4:]}")

    for manga in mangas:
        if manga.hid == selected_hid and manga.desc:
            description_box = Panel(
                manga.desc.split("---")[0].rstrip("\n"),
                title="Manga Description",
                title_align="left",
                border_style="green",
            )
            console.print(description_box)
            break


@app.command()
def top():
    """Get top manga list"""
    try:
        mangas = asyncio.run(get_top_list())
    except (ConnectionError, PermissionError, ValueError) as e:
        handle_error(e)
        return

    manga_result = show_top_manga_list(mangas)
    if not manga_result:
        console.print("[red]No manga found.[/red]")
        return

    display_manga_results(manga_result)


if __name__ == "__main__":
    app()
