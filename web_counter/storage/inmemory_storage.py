import asyncio

from storage.storage import CounterStorage
from utils.singletone import singleton


@singleton
class InMemoryStorage(CounterStorage):
    """In-memory implementation of counter storage."""

    def __init__(self) -> None:
        self._count: int = 0
        self._lock = asyncio.Lock()

    async def increment(self) -> int:
        async with self._lock:
            self._count += 1
            return self._count

    async def get_count(self) -> int:
        async with self._lock:
            return self._count
