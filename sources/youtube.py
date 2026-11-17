import os

import httpx
from dotenv import load_dotenv


VIDEO_CATEGORY_ID = "28"
# Other YouTube category IDs include 10 Music, 20 Gaming, and 25 News & Politics.


# Load the local environment file so this source can also be used on its own.
load_dotenv()


# Fetch the five most popular YouTube videos in India.
async def get_trending_videos() -> list[dict[str, str | int]] | str:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return "Sorry, YouTube trends are unavailable because the API key is missing."

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "key": api_key,
                "chart": "mostPopular",
                "part": "snippet,statistics",
                "maxResults": 5,
                "regionCode": "IN",
            }
            response = await client.get(
                url,
                params={**params, "videoCategoryId": VIDEO_CATEGORY_ID},
            )
            # Retry without a category if YouTube rejects the category-specific request.
            if response.is_error:
                response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict) and payload.get("error"):
                response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()

        return [
            {
                "title": video["snippet"]["title"],
                "channel": video["snippet"]["channelTitle"],
                "views": int(video["statistics"].get("viewCount", 0)),
                "link": f"https://www.youtube.com/watch?v={video['id']}",
            }
            for video in payload["items"]
        ]
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return "Sorry, I couldn't fetch YouTube trends right now. Please try again later."
