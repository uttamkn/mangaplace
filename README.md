 mangaplace cli app

## ( this project is still under development )

- desc: full fledged cli app for all your comic needs

## important things to remember

1. api.comick.fun/v1.0/search?q=${query}&tachiyomi=true - (get manga)
2. api.comick.fun/comic/${hid}/chapters?lang=en&limit=99999&tachiyomi=true - hid that you got from above
3. api.comick.fun/chapter/${hid}/get_images?tachiyomi=true - hid that you got from above ( be careful there are 2 hids )
4. <https://meo3.comick.pictures/${b2key}> - b2key that you got from above

## roadmap

### todo

- [x] test out every endpoint using curl and see if you are able to get images and pdfs
- [x] write a few functions that will give you the pdf if you give the name of the manga or something
- [x] bring typer in and make all the interacting happen
- [ ] give him options to select top 10 normally or all options in fzf and handle the case where he doesn't have fzf like check /usr/bin/fzf
- [ ] make chapter number as output with the manga title
