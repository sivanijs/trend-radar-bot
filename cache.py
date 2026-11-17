from cachetools import TTLCache


# Keep up to four source results for five minutes.
_results = TTLCache(maxsize=4, ttl=300)


# Return a cached result, or fetch and cache a successful result.
async def get_cached(source_name: str, source_function):
    if source_name in _results:
        print(f"cache hit: {source_name}")
        return _results[source_name]

    print(f"cache miss: {source_name}")
    result = await source_function()
    # Source functions use strings for friendly errors, so only cache non-error results.
    if result and not isinstance(result, str):
        _results[source_name] = result
    return result
