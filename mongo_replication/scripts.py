import logging
import time

logging.basicConfig(level=logging.INFO)
from pymongo import ReadPreference, WriteConcern
from pymongo.read_concern import ReadConcern

from mongo_replication.client.connect import get_client

log = logging.getLogger(__name__)



def write_to_collection(message: str, w: str | int = "majority", wtimeout: int = 0):
    client = get_client()
    db = client["test_db"]
    start_time = time.monotonic()
    collection = db.get_collection(
        "replication_testing",
        write_concern=WriteConcern(w=w, wtimeout=wtimeout),
    )
    result = collection.insert_one({"message": message})
    end_time = time.monotonic()
    log.info(f"Inserted {result.inserted_id} in {end_time - start_time} seconds")

    return result


def clear_collection():
    client = get_client()
    db = client["test_db"]
    collection = db.get_collection("replication_testing")
    result = collection.delete_many({})
    log.info(f"Deleted {result.deleted_count} documents")


def read_from_collection(read_concern: str = "majority", read_preference=ReadPreference.NEAREST):
    client = get_client()
    db = client["test_db"]

    start_time = time.monotonic()
    collection = db.get_collection(
        "replication_testing",
        read_concern=ReadConcern(level=read_concern),
        read_preference=read_preference,
    )
    result = list(collection.find())
    end_time = time.monotonic()
    log.info(f"Found {len(result)} documents in {end_time - start_time} seconds")
    return result


if __name__ == "__main__":
    # clear_collection()
    # write_to_collection(message="delay 1", wtimeout=5000)

    records = read_from_collection(read_concern="linearizable")
    for record in records:
        log.info("Record found: %s", record)
