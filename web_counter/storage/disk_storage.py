import asyncio
import os
import pathlib

import aiofiles
from storage.storage import CounterStorage


class DiskStorage(CounterStorage):
    def __init__(self, file_path: str = "counter.txt"):
        self._file_path = file_path
        self._lock = asyncio.Lock()

    async def _ensure_file_exists(self):
        if not pathlib.Path(self._file_path).exists():
            async with aiofiles.open(self._file_path, "w") as f:
                await f.write("0")

    async def increment(self) -> int:
        async with self._lock:
            await self._ensure_file_exists()

            # Read current value
            async with aiofiles.open(self._file_path) as f:
                count = int(await f.read())

            count += 1

            # Write atomically (temp + rename)
            temp = f"{self._file_path}.tmp"
            async with aiofiles.open(temp, "w") as f:
                await f.write(str(count))
                await f.flush()
                os.fsync(f.fileno())
            pathlib.Path(temp).replace(self._file_path)

            return count

    async def get_count(self) -> int:
        async with self._lock:
            await self._ensure_file_exists()
            async with aiofiles.open(self._file_path) as f:
                return int(await f.read())
