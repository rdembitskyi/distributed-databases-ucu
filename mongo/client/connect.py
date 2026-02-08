import logging

from pymongo import MongoClient

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_client(host="localhost", port=27017):
    client = MongoClient(host, port)
    client.admin.command("ping")
    log.info("Connected to MongoDB successfully")
    return client


if __name__ == "__main__":
    client = get_client()
    log.info("Databases: %s", client.list_database_names())
