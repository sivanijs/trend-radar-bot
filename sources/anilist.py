import httpx


# Query AniList for the five anime with the highest current trend ranking.
async def get_trending_anime() -> list[dict[str, str | int | None]] | str:
    query = """
    query {
      Page(page: 1, perPage: 5) {
        media(type: ANIME, sort: TRENDING_DESC) {
          title { english romaji }
          averageScore
          siteUrl
        }
      }
    }
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://graphql.anilist.co",
                json={"query": query},
            )
            response.raise_for_status()
            payload = response.json()

        if payload.get("errors"):
            return "Sorry, AniList is having trouble right now. Please try again later."

        media = payload["data"]["Page"]["media"]
        return [
            {
                "title": anime["title"]["english"] or anime["title"]["romaji"] or "Untitled",
                "score": anime["averageScore"],
                "link": anime["siteUrl"],
            }
            for anime in media
        ]
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return "Sorry, I couldn't fetch anime trends right now. Please try again later."
