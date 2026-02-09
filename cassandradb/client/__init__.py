from cassandra.cluster import Cluster


def init_cluster():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect()

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS test_keyspace
        WITH REPLICATION = {
            'class': 'SimpleStrategy',
            'replication_factor': 3
        }
    """)

    print("Keyspace 'test_keyspace' created successfully")

    cluster.shutdown()
