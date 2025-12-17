from storage.disk_storage import DiskStorage
from storage.inmemory_storage import InMemoryStorage


def get_storage(storage_type: str):
    if storage_type == "disk":
        return DiskStorage()
    return InMemoryStorage()
