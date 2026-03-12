from cassandra.cluster import Cluster


def create_tables():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect()

    for keyspace in ["test_keyspace_1", "test_keyspace_2", "test_keyspace_3"]:
        session.execute(f"""
            CREATE TABLE IF NOT EXISTS {keyspace}.fc (
                id UUID,
                name TEXT,
                players MAP<TEXT, TEXT>,
                PRIMARY KEY (name, id)
            )
        """)

    print("Tables were created successfully")

    cluster.shutdown()


if __name__ == "__main__":
    create_tables()