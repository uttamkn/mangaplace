# mangaplace cli app

## ( this project is still under development )

- desc: full fledged cli app for all your comic needs

## important things to remember
1. api.comick.fun/v1.0/search?q=solo&tachiyomi=true - (get manga)
2. api.comick.fun/comic/${hid}/chapters?lang=en&limit=99999&tachiyomi=true - hid that you got from above
3. api.comick.fun/chapter/${hid}/get_images?tachiyomi=true - hid that you got from above ( be careful there are 2 hids )
4. https://meo3.comick.pictures/{b2key} --that you got from above

## roadmap

### first checkpoint
- test out every endpoint using curl and see if you are able to get images and pdfs
- write a few functions that will give you the pdf if you give the name of the manga or something
- just write a switch statement to get the geners and popular ones and get option to download chapters and shit
- if this all are working you can go to next phase
