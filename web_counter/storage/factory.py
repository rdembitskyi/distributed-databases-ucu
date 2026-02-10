from storage.atomic_long import AtomicLongStorage
from storage.cassandra_storage import CassandraStorage
from storage.disk_storage import DiskStorage
from storage.inmemory_storage import InMemoryStorage
from storage.mongo import MongoDbStorage
from storage.postgres import PostgresStorage


def get_storage(storage_type: str):
    if storage_type == "disk":
        return DiskStorage()
    elif storage_type == "postgres":
        return PostgresStorage()
    elif storage_type == "hazelcast":
        return AtomicLongStorage()
    elif storage_type == "mongodb":
        return MongoDbStorage()
    elif storage_type == "cassandra":
        return CassandraStorage()
    return InMemoryStorage()
