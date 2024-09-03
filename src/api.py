import logging
from typing import List
from models import MangaResult, SearchResults, SelectNameOfManga

import aiohttp
from fastapi import HTTPException, Query
from pydantic import BaseModel, Field, TypeAdapter

async def fetch_comics(query: str) -> List[MangaResult]:
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
				if response.status == 200:
					data =  await response.json()
					search_results = TypeAdapter(SearchResults).validate_python({"results": data})
					return search_results.results
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

async def get_select_name(mangas: List[MangaResult]) -> SelectNameOfManga:
	res: List[SelectNameOfManga] = []
	for manga in mangas:
		res.append(SelectNameOfManga(hid=manga.hid, title=manga.title))
	return res