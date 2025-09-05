# MangaPlace

![version](https://img.shields.io/badge/version-1.0.2-blue.svg)
![license](https://img.shields.io/badge/license-MIT-green.svg)
[![AUR](https://img.shields.io/aur/version/mangaplace.svg)](https://aur.archlinux.org/packages/mangaplace)

**MangaPlace** is a command-line interface (CLI) tool that lets you search, download, and retrieve information about manga using a single command. It's designed to be simple and easy to use for all manga enthusiasts who love accessing their favorite manga through the terminal.

## Features

- Search for manga by title.
- Get the list of trending manga.
- Download manga chapters.
- Retrieve detailed information and descriptions of manga.

## Installation

### From AUR (Arch Linux)

You can install `mangaplace` from the AUR:

```bash
yay -S mangaplace
```

### Manual Installation

1. Download the latest release from the [GitHub releases page](https://github.com/uttamkn/mangaplace/releases).
2. Install the tool by placing it in your `$PATH`:
   ```bash
   sudo install -Dm755 mangaplace /usr/bin/mangaplace
   ```

## Usage

To use **MangaPlace**, type one of the following commands in your terminal:

- **Search for a manga:**

  ```bash
  mangaplace search "One Piece"
  ```

- **Get the list of trending manga:**

  ```bash
  mangaplace top
  ```

- **Download a manga:**

  ```bash
  mangaplace download "Naruto"
  ```

- **Get information about a manga:**
  ```bash
  mangaplace info "Attack on Titan"
  ```

### Command Options

- `search` : Search for mangas by title.
- `top` : Get the list of trending manga.
- `download` : Download a manga by title.
- `info` : Get the description of a manga by title.

## API

**MangaPlace** relies on the **[comick api](https://api.comick.fun/docs/static/index.html)** API to provide manga search, download, and information services. Special thanks to the creators of this API for making their service available.

## Contributing

Feel free to open issues or submit pull requests. All contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/uttamkn/mangaplace)
- [AUR Package](https://aur.archlinux.org/packages/mangaplace)
