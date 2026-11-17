import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


# Run the supplied source functions together and preserve individual failures.
async def gather_all_sources(
    *source_functions: Callable[[], Awaitable[Any]],
) -> list[Any]:
    return await asyncio.gather(
        *(source_function() for source_function in source_functions),
        return_exceptions=True,
    )
