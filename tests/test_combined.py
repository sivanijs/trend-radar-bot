import asyncio

from sources.combined import gather_all_sources


def test_one_failed_source_does_not_block_the_other_results():
    async def anime():
        return ["anime result"]

    async def youtube():
        raise RuntimeError("simulated source failure")

    async def google():
        return ["Google result"]

    async def x():
        return ["X result"]

    results = asyncio.run(gather_all_sources(anime, youtube, google, x))

    assert results[0] == ["anime result"]
    assert isinstance(results[1], RuntimeError)
    assert results[2] == ["Google result"]
    assert results[3] == ["X result"]
