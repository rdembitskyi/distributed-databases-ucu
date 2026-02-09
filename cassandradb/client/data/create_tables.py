from cassandra.cluster import Cluster


def create_tables():
    cluster = Cluster(["localhost"], port=9042)
    session = cluster.connect("test_keyspace")
    session.default_timeout = 60

    session.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id UUID,
            name TEXT,
            category TEXT,
            price DECIMAL,
            producer TEXT,
            properties MAP<TEXT, TEXT>,
            PRIMARY KEY (category, price, producer, id)
        ) WITH CLUSTERING ORDER BY (price ASC, producer ASC, id ASC)
    """)

    session.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_properties
        ON items (ENTRIES(properties))
    """)

    session.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_properties_keys
        ON items (KEYS(properties))
    """)

    session.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_name
        ON items (name)
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id UUID,
            customer_name TEXT,
            order_date TIMESTAMP,
            item_id UUID,
            quantity INT,
            total_price DECIMAL,
            status TEXT,
            PRIMARY KEY (id, order_date)
        ) WITH CLUSTERING ORDER BY (order_date DESC)
    """)

    print("Tables 'items' and 'orders' created successfully")

    cluster.shutdown()


if __name__ == "__main__":
    create_tables()
