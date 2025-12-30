import psycopg
import os
from storage.storage import CounterStorage
from utils.singletone import singleton
from psycopg_pool import AsyncConnectionPool


@singleton
class PostgresStorage(CounterStorage):
    def __init__(self):
        self.pool = None

    async def initialize(self):
        """Initialize connection pool"""
        self.pool = AsyncConnectionPool(
            conninfo="host=localhost dbname=mydb user=postgres password=postgres",
            min_size=5,
            max_size=20,
        )
        await self.pool.wait()

    async def increment(self) -> int:
        """Async increment"""
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE user_count SET count = count + 1 WHERE user_id = %s RETURNING count",
                    (1,),
                )
                result = await cursor.fetchone()
                return result[0]

    async def get_count(self) -> int:
        """Async get count"""
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT count FROM user_count WHERE user_id = %s", (1,)
                )
                result = await cursor.fetchone()
                return result[0]

    async def close(self):
        """Close pool"""
        await self.pool.close()
