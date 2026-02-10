import asyncio

from cassandra.cluster import Cluster
from storage.storage import CounterStorage
from utils.singletone import singleton


@singleton
class CassandraStorage(CounterStorage):
    def __init__(self):
        self.cluster = None
        self.session = None

    async def initialize(self):
        self.cluster = Cluster(["localhost"], port=9042)
        self.session = await asyncio.to_thread(self.cluster.connect)

        await asyncio.to_thread(
            self.session.execute,
            """
            CREATE KEYSPACE IF NOT EXISTS web_counter
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
            """,
        )

        await asyncio.to_thread(self.session.execute, "USE web_counter")

        await asyncio.to_thread(
            self.session.execute,
            """
            CREATE TABLE IF NOT EXISTS counter (
                id TEXT PRIMARY KEY,
                count COUNTER
            )
            """,
        )

        await asyncio.to_thread(self.session.execute, "TRUNCATE counter")

    async def increment(self) -> int:
        await asyncio.to_thread(
            self.session.execute,
            "UPDATE counter SET count = count + 1 WHERE id = 'counter'",
        )
        # just to speed up things
        return 0

    async def get_count(self) -> int:
        row = await asyncio.to_thread(
            self.session.execute,
            "SELECT count FROM counter WHERE id = 'counter'",
        )
        result = row.one()
        print(result)
        return result.count if result else 0

    async def close(self):
        if self.cluster:
            await asyncio.to_thread(self.cluster.shutdown)
