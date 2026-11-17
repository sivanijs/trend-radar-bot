import asyncio
from urllib.parse import quote


# Call the synchronous RSS downloader; asyncio.to_thread keeps it off the bot loop.
def _download_google_trends():
    from trendspyg import download_google_trends_rss

    return download_google_trends_rss(geo="IN", cache=False, normalize=True)


# Fetch the top five India searches and return the structure used by the bot.
async def get_trending_searches() -> list[dict[str, str]] | str:
    try:
        payload = await asyncio.to_thread(_download_google_trends)
        trends = payload.get("trends", []) if isinstance(payload, dict) else []
        results = []
        for trend in trends:
            term = trend.get("keyword", "").strip()
            if not term:
                continue
            results.append(
                {
                    "term": term,
                    "traffic": trend.get("volume_text") or "",
                    "link": f"https://www.google.com/search?q={quote(term, safe='')}",
                }
            )
            if len(results) == 5:
                break

        if results:
            return results
    except Exception:
        # Return the same friendly response if the package or feed fails.
        pass

    return "Sorry, I couldn't fetch Google Trends right now. Please try again later."
