from cassandra.cluster import Cluster


def init_cluster():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect()

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS test_keyspace_1
        WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': 1 }
    """)

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS test_keyspace_2
        WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': 2 }
    """)

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS test_keyspace_3
        WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': 3 }
    """)

    print("Keyspaces were created successfully")

    cluster.shutdown()


if __name__ == "__main__":
    init_cluster()
