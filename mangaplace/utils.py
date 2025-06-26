"""utils"""

import json
import os
from typing import DefaultDict

from rich.console import Console
from rich.prompt import Prompt

console = Console()


async def get_path() -> str:
    """Get the download path from the settings file."""
    xdg_config = os.getenv("XDG_CONFIG")

    if not xdg_config:
        xdg_config = os.path.join(str(os.getenv("HOME")), ".config/")
    json_file_path = os.path.join(xdg_config, "mangaplace", "settings.json")

    if not os.path.exists(os.path.dirname(json_file_path)):
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
        console.print(
            f"[green]Created directory: {os.path.dirname(json_file_path)}[/green]"
        )

    data = DefaultDict(str)

    if not os.path.exists(json_file_path):
        console.print("[yellow]Settings file not found. Creating a new one.[/yellow]")
        with open(json_file_path, "w") as f:
            json.dump(data, f)
            console.print(f"[green]Created a file at {json_file_path}[/green]")
    else:
        with open(json_file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                console.print(
                    f"[red]Error decoding JSON: {e}. Creating a new file.[/red]"
                )
                data = DefaultDict(str)
                with open(json_file_path, "w") as f:
                    json.dump(data, f)

    if "download_path" not in data:
        dir = Prompt.ask(
            "[yellow]Give fully qualified path of the directory \
            where you want to store your files: [/yellow]"
        )
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
            data["download_path"] = dir
            with open(json_file_path, "w") as f:
                json.dump(data, f)
        except FileNotFoundError:
            console.print(
                "[red]You gave the wrong path. Please provide the fully qualified path.[/red]"
            )
        except json.JSONDecodeError as e:
            console.print(f"[red]Error decoding JSON: {e}[/red]")
        return dir

    return data["download_path"]
