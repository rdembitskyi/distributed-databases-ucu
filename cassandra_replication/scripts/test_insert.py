import logging
import uuid

from cassandra.cluster import Cluster

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

KEYSPACES = ["test_keyspace_1", "test_keyspace_2", "test_keyspace_3"]

cluster = Cluster(["localhost"], port=9042)
session = cluster.connect()


def clear_data():
    for keyspace in KEYSPACES:
        session.execute(f"TRUNCATE {keyspace}.fc")
    log.info("Tables truncated successfully")


def insert_data():
    clubs = [
        {
            "name": "AC Milan",
            "players": {
                "Paolo Maldini": "Defender",
                "Franco Baresi": "Defender",
                "Marco van Basten": "Forward",
                "Andriy Shevchenko": "Forward",
                "Kaka": "Midfielder",
            },
        },
        {
            "name": "Inter",
            "players": {
                "Javier Zanetti": "Defender",
                "Giuseppe Bergomi": "Defender",
                "Ronaldo": "Forward",
                "Lothar Matthaus": "Midfielder",
                "Giacinto Facchetti": "Defender",
            },
        },
        {
            "name": "Juventus",
            "players": {
                "Alessandro Del Piero": "Forward",
                "Gianluigi Buffon": "Goalkeeper",
                "Michel Platini": "Midfielder",
                "Roberto Baggio": "Forward",
                "Andrea Pirlo": "Midfielder",
            },
        },
    ]

    for keyspace in KEYSPACES:
        for club in clubs:
            session.execute(
                f"""
                INSERT INTO {keyspace}.fc (id, name, players)
                VALUES (%s, %s, %s)
                """,
                (uuid.uuid4(), club["name"], club["players"]),
            )

    log.info("Data inserted successfully")


def read_data():
    for keyspace in KEYSPACES:
        log.info(f"--- {keyspace} ---")
        rows = session.execute(f"SELECT id, name, players FROM {keyspace}.fc")
        for row in rows:
            log.info(f"  {row.name} (id={row.id})")
            for player, position in row.players.items():
                log.info(f"    - {player}: {position}")


clear_data()
insert_data()
read_data()

cluster.shutdown()