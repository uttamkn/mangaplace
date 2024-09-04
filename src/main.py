"""
main.py
"""

import asyncio
import json
import os
import subprocess
from typing import DefaultDict

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

    selecte_name = selected.split(" - ", maxsplit=1)[1].strip() #extracted manga name
    selected_index = int(selected.split(" - ", maxsplit=1)[0].strip())
    selected_hid = index_to_hid[selected_index]

    console.print(f"[green]You selected:[/green] {manga_options[selected_index]}")

    confirm = Prompt.ask(
        "[cyan]Do you want to proceed with this manga? (yes/no)[/cyan]",
        choices=["yes", "no"],
    )

    if confirm == "yes":
        search_chapter(selected_hid, selecte_name) # passed it to select_chapter
    else:
        console.print("[yellow]Operation cancelled by user.[/yellow]")


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
    # also extract the manga name from here so that we can use it to name the pdf file with the chapter no
    # selected_title - selected.split(" - ")[1].strip()
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
        asyncio.run(download(selected_hid, manga_name, selected_index)) # passed it to download because you will use this to name chapters
    else:
        console.print("[yellow]Operation cancelled by user.[/yellow]")


async def download(hid: str, pdf_name: str, index: int):
    console.print(f"[cyan]Downloading chapter...[/cyan]")
    download_dir_path = await get_path()
    pdf_path = (download_dir_path + pdf_name + "_" +str(index + 1) + ".pdf")

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

async def get_path() -> str:
    
    xdg_config = os.getenv("XDG_CONFIG")

    if not xdg_config or xdg_config == "":
        xdg_config = os.path.join(str(os.getenv("HOME")), ".config/")
    console.print(f"Configuration directory: {xdg_config}")
    json_file_path = os.path.join(xdg_config, "mangaplace", "settings.json")

    if not os.path.exists(os.path.dirname(json_file_path)):
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
        console.print(f"[green]Created directory: {os.path.dirname(json_file_path)}[/green]")

    data = DefaultDict(str)

    if not os.path.exists(json_file_path):
        console.print(f"[yellow]Settings file not found. Creating a new one.[/yellow]")
        with open(json_file_path, "w") as f:
            json.dump(data, f)
            console.print(f"[green]Created a file at {json_file_path}[/green]")
    else:
        with open(json_file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error decoding JSON: {e}. Creating a new file.[/red]")
                data = DefaultDict(str)
                with open(json_file_path, "w") as f:
                    json.dump(data, f)
    
    if "download_path" not in data or not data["download_path"]:
        dir = Prompt.ask("[yellow]Give fully qualified path of the directory where you want to store your files: [/yellow]")
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
            data["download_path"] = dir
            with open(json_file_path, "w") as f:
                json.dump(data, f)
        except FileNotFoundError:
            console.print("[red]You gave the wrong path. Please provide the fully qualified path.[/red]")
        except json.JSONDecodeError as e:
            console.print(f"[red]Error decoding JSON: {e}[/red]")
        return dir

    return data["download_path"]

if __name__ == "__main__":
    app()
