# mangaplace

- Full fledged cli app for all your comic needs

## Installation

1. Clone the repo

```bash
git clone https://github.com/uttamkn/mangaplace.git
```

2. Create a virtual environment and install the requirements

```bash
uv venv
source ./venv/bin/activate
uv sync
```
3. create an alias

```bash
alias manga='python $HOME/mangaplace/mangaplace/main.py'

```

## Todo

- [x] test out every endpoint using curl and see if you are able to get images and pdfs
- [x] write a few functions that will give you the pdf if you give the name of the manga or something
- [x] bring typer in and make all the interacting happen
- [x] make chapter number as output with the manga title
- [x] ask him what dir should we store things in
- [x] have a json config file to read from
- [x] add iterfzf instead of bare fzf dependancy
