import logging
import uuid

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

KEYSPACES_CL = {
    "test_keyspace_1": [ConsistencyLevel.ONE],
    "test_keyspace_2": [ConsistencyLevel.ONE, ConsistencyLevel.TWO],
    "test_keyspace_3": [ConsistencyLevel.ONE, ConsistencyLevel.TWO, ConsistencyLevel.THREE],
}

CL_NAMES = {
    ConsistencyLevel.ONE: "ONE",
    ConsistencyLevel.TWO: "TWO",
    ConsistencyLevel.THREE: "THREE",
}


def test_write(session, keyspace, cl):
    stmt = SimpleStatement(
        f"INSERT INTO {keyspace}.fc (id, name, players) VALUES (%s, %s, %s)",
        consistency_level=cl,
    )
    session.execute(stmt, (uuid.uuid4(), "TestClub", {"Player": "Forward"}))


def test_read(session, keyspace, cl):
    stmt = SimpleStatement(
        f"SELECT * FROM {keyspace}.fc LIMIT 1",
        consistency_level=cl,
    )
    session.execute(stmt)


if __name__ == "__main__":
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect()

    for keyspace, levels in KEYSPACES_CL.items():
        rf = len(levels)
        log.info(f"=== {keyspace} (RF={rf}) ===")
        for cl in levels:
            cl_name = CL_NAMES[cl]

            # Test write
            try:
                test_write(session, keyspace, cl)
                log.info(f"  WRITE CL={cl_name}: OK")
            except Exception as e:
                log.info(f"  WRITE CL={cl_name}: FAILED - {e}")

            # Test read
            try:
                test_read(session, keyspace, cl)
                log.info(f"  READ  CL={cl_name}: OK")
            except Exception as e:
                log.info(f"  READ  CL={cl_name}: FAILED - {e}")

    cluster.shutdown()