import asyncio

import hazelcast
from storage.storage import CounterStorage
from utils.singletone import singleton


@singleton
class AtomicLongStorage(CounterStorage):
    def __init__(self):
        self.client = hazelcast.HazelcastClient(cluster_name="storage")
        self.counter = self.client.cp_subsystem.get_atomic_long("counter")

    async def increment(self) -> int:
        """Async increment"""
        return await asyncio.to_thread(self.counter.increment_and_get().result)

    async def get_count(self) -> int:
        """Async get count"""
        return await asyncio.to_thread(self.counter.get().result)
