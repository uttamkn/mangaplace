import asyncio
import logging

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()
logging.basicConfig(level=logging.INFO)

async def fetch_comics(query: str):
    url = f"https://api.comick.fun/v1.0/search?q={query}&tachiyomi=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://comick.fun/",
        "Origin": "https://comick.fun",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logging.info(f"Request URL: {url}")
                logging.info(f"Request headers: {headers}")
                logging.info(f"Response status: {response.status}")
                logging.info(f"Response headers: {response.headers}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 403:
                    error_text = await response.text()
                    logging.error(f"403 Forbidden error. Response body: {error_text}")
                    raise HTTPException(status_code=403, detail=f"Access forbidden. Server response: {error_text}")
                else:
                    error_text = await response.text()
                    logging.error(f"Unexpected status code: {response.status}. Response body: {error_text}")
                    raise HTTPException(status_code=response.status, detail=f"Failed to fetch comics: {error_text}")
        except aiohttp.ClientError as e:
            logging.error(f"Request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to make request: {str(e)}")

@app.get("/comics")
async def search_comics(query: str = Query(..., description="Search query for comics")):
    try:
        response = await fetch_comics(query)
        # Limit to top 10 results
        top_10 = response[:10] if isinstance(response, list) else response
        return {"results": top_10}
    except HTTPException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
