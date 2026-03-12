import logging
import uuid

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.policies import WhiteListRoundRobinPolicy
from cassandra.query import SimpleStatement

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

KEYSPACE = "test_keyspace_3"
FIXED_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

nodes = [
    {"host": "localhost", "port": 9042, "name": "node-1"},
    {"host": "localhost", "port": 9043, "name": "node-2"},
    {"host": "localhost", "port": 9044, "name": "node-3"},
]

# First, disconnect nodes from each other so writes don't replicate
log.info("=== Make sure nodes are disconnected from each other! ===")

conflicting_data = [
    {"name": "ConflictClub", "players": {"Player1": "Goalkeeper"}},
    {"name": "ConflictClub", "players": {"Player2": "Defender"}},
    {"name": "ConflictClub", "players": {"Player3": "Forward"}},
]

# Write different data to each node
for i, node in enumerate(nodes):
    try:
        cluster = Cluster([node["host"]], port=node["port"])
        session = cluster.connect()

        stmt = SimpleStatement(
            f"INSERT INTO {KEYSPACE}.fc (id, name, players) VALUES (%s, %s, %s)",
            consistency_level=ConsistencyLevel.ONE,
        )
        data = conflicting_data[i]
        session.execute(stmt, (FIXED_ID, data["name"], data["players"]))
        log.info(f"WRITE to {node['name']}: {data['players']}")

        cluster.shutdown()
    except Exception as e:
        log.info(f"WRITE to {node['name']}: FAILED - {e}")

log.info("=== Now reconnect nodes ===")

input("Press Enter after reconnecting nodes...")

# Read from each node to see what they return
log.info("=== Reading from each node ===")
for node in nodes:
    try:
        cluster = Cluster([node["host"]], port=node["port"])
        session = cluster.connect()

        stmt = SimpleStatement(
            f"SELECT * FROM {KEYSPACE}.fc WHERE name = 'ConflictClub' AND id = {FIXED_ID}",
            consistency_level=ConsistencyLevel.ONE,
        )
        rows = session.execute(stmt)
        for row in rows:
            log.info(f"READ from {node['name']}: {row.players}")

        cluster.shutdown()
    except Exception as e:
        log.info(f"READ from {node['name']}: FAILED - {e}")