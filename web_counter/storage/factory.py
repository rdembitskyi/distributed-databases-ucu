from storage.disk_storage import DiskStorage
from storage.inmemory_storage import InMemoryStorage
from storage.postgres import PostgresStorage


def get_storage(storage_type: str):
    if storage_type == "disk":
        return DiskStorage()
    elif storage_type == "postgres":
        return PostgresStorage()
    return InMemoryStorage()
