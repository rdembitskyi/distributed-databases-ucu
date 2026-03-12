import logging
import uuid

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

KEYSPACE = "test_keyspace_3"
FIXED_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

nodes = [
    {"host": "localhost", "port": 9042, "name": "node-1"},
    {"host": "localhost", "port": 9043, "name": "node-2"},
    {"host": "localhost", "port": 9044, "name": "node-3"},
]

# LWT INSERT: add Real Madrid with Zidane (IF NOT EXISTS)
log.info("=== LWT INSERT (IF NOT EXISTS) ===")
for node in nodes:
    try:
        cluster = Cluster([node["host"]], port=node["port"])
        session = cluster.connect()

        stmt = SimpleStatement(
            f"INSERT INTO {KEYSPACE}.fc (id, name, players) VALUES (%s, %s, %s) IF NOT EXISTS",
            consistency_level=ConsistencyLevel.ONE,
        )
        result = session.execute(stmt, (FIXED_ID, "Real Madrid", {"Zinedine Zidane": "Midfielder"}))
        applied = result.one().applied
        log.info(f"  {node['name']}: applied={applied}")

        cluster.shutdown()
    except Exception as e:
        log.info(f"  {node['name']}: FAILED - {e}")

# LWT UPDATE: add Raul only if current players match
log.info("=== LWT UPDATE (IF condition) ===")
for node in nodes:
    try:
        cluster = Cluster([node["host"]], port=node["port"])
        session = cluster.connect()

        stmt = SimpleStatement(
            f"UPDATE {KEYSPACE}.fc SET players = %s WHERE name = %s AND id = %s IF players = %s",
            consistency_level=ConsistencyLevel.ONE,
        )
        current_players = {"Zinedine Zidane": "Midfielder"}
        new_players = {"Zinedine Zidane": "Midfielder", "Raul": "Forward"}
        result = session.execute(stmt, (new_players, "Real Madrid", FIXED_ID, current_players))
        applied = result.one().applied
        log.info(f"  {node['name']}: applied={applied}")

        cluster.shutdown()
    except Exception as e:
        log.info(f"  {node['name']}: FAILED - {e}")

# Read from each node
log.info("=== Reading from each node ===")
for node in nodes:
    try:
        cluster = Cluster([node["host"]], port=node["port"])
        session = cluster.connect()

        stmt = SimpleStatement(
            f"SELECT * FROM {KEYSPACE}.fc WHERE name = 'Real Madrid' AND id = {FIXED_ID}",
            consistency_level=ConsistencyLevel.ONE,
        )
        rows = session.execute(stmt)
        for row in rows:
            log.info(f"  {node['name']}: {row.players}")

        cluster.shutdown()
    except Exception as e:
        log.info(f"  {node['name']}: FAILED - {e}")