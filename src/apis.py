import asyncio

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

async def fetch_comics(query: str):
    url = f"https://api.comick.fun/v1.0/search?q={query}&tachiyomi=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise HTTPException(status_code=response.status, detail="Failed to fetch comics")

@app.get("/comics")
async def search_comics(query: str = Query(..., description="Search query for comics")):
    try:
        response = await fetch_comics(query)
        top_10 = response[:10] if isinstance(response, list) else response
        return {"results": top_10}
    except HTTPException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("apis:app", host="0.0.0.0", port=8000, reload=True)
