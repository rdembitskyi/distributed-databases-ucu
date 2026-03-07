import asyncio

from neo4j import GraphDatabase
from storage.storage import CounterStorage
from utils.singletone import singleton


@singleton
class Neo4jStorage(CounterStorage):
    def __init__(self):
        self.driver = None

    async def initialize(self):
        uri = "bolt://localhost:7687"
        auth = ("neo4j", "password")
        self.driver = GraphDatabase.driver(uri, auth=auth)

        with self.driver.session() as s:
            s.run(
                """
                MERGE (c:Counter {name: 'default'})
                ON CREATE SET c.value = 0
                """
            )

    async def increment(self) -> int:
        def _increment(tx):
            result = tx.run(
                """
                MATCH (c:Counter {name: 'default'})
                SET c.value = c.value + 1
                RETURN c.value AS count
                """
            )
            return result.single()["count"]

        with self.driver.session() as s:
            return s.execute_write(_increment)

    async def get_count(self) -> int:
        def _get(tx):
            result = tx.run(
                """
                MATCH (c:Counter {name: 'default'})
                RETURN c.value AS count
                """
            )
            return result.single()["count"]

        with self.driver.session() as s:
            return s.execute_read(_get)

    async def close(self):
        self.driver.close()
