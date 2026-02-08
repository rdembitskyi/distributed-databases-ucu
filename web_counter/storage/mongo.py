import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument, WriteConcern
from storage.storage import CounterStorage
from utils.singletone import singleton


@singleton
class MongoDbStorage(CounterStorage):
    def __init__(self):
        self.client = None
        self.collection = None
        self._lock = asyncio.Lock()

    async def initialize(self):
        self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = self.client["web_counter"]
        self.collection = db.get_collection(
            "counter", write_concern=WriteConcern(w=1, j=True)
        )

        if await self.collection.count_documents({"_id": "counter"}) == 0:
            await self.collection.insert_one({"_id": "counter", "count": 0})

    async def increment(self) -> int:
        async with self._lock:
            result = await self.collection.find_one_and_update(
                {"_id": "counter"},
                {"$inc": {"count": 1}},
                return_document=ReturnDocument.AFTER,
            )
            return result["count"]

    async def get_count(self) -> int:
        async with self._lock:
            result = await self.collection.find_one({"_id": "counter"})
            return result["count"]

    async def close(self):
        self.client.close()
