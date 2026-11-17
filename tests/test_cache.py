import asyncio

from cache import _results, get_cached


def test_second_call_uses_cached_result():
    source_name = "test:cache-success"
    _results.pop(source_name, None)
    calls = 0

    async def source():
        nonlocal calls
        calls += 1
        return [{"title": "sample"}]

    first = asyncio.run(get_cached(source_name, source))
    second = asyncio.run(get_cached(source_name, source))

    assert first == second == [{"title": "sample"}]
    assert calls == 1


def test_error_string_is_not_cached():
    source_name = "test:cache-error"
    _results.pop(source_name, None)
    calls = 0

    async def source():
        nonlocal calls
        calls += 1
        if calls == 1:
            return "A friendly error"
        return [{"title": "recovered"}]

    first = asyncio.run(get_cached(source_name, source))
    second = asyncio.run(get_cached(source_name, source))

    assert first == "A friendly error"
    assert second == [{"title": "recovered"}]
    assert calls == 2
