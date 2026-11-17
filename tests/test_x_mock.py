import asyncio

from sources.x_mock import XProvider


def test_mock_provider_returns_five_complete_trends():
    trends = asyncio.run(XProvider().get_trends())

    assert len(trends) == 5
    for trend in trends:
        assert trend["title"]
        assert trend["extra"]
        assert trend["link"].startswith("https://x.com/search?q=")
