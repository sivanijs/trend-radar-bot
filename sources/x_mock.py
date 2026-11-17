from urllib.parse import quote


class XProvider:
    """Mock X provider with a stable method for a future real provider."""

    # Keep this method interface when replacing the sample data with a real provider.
    async def get_trends(self) -> list[dict[str, str]]:
        samples = [
            ("#CricketFinal", "12K posts"),
            ("New Anime Season", "8.4K posts"),
            ("Weekend Plans", "6.1K posts"),
            ("Tech Updates", "4.7K posts"),
            ("Music Awards", "3.2K posts"),
        ]
        return [
            {
                "title": title,
                "extra": extra,
                "link": f"https://x.com/search?q={quote(title, safe='')}",
            }
            for title, extra in samples
        ]
